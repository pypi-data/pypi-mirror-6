# Copyright 2011 OpenStack, LLC.
# Copyright 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import logging
import pprint
import Queue
import select
import threading
import time

import paramiko


class GerritWatcher(object):
    log = logging.getLogger("gerrit.GerritWatcher")

    def __init__(
            self, gerrit, username=None, hostname=None, port=None,
            keyfile=None):
        """Create a GerritWatcher.

        :param gerrit: A Gerrit instance to pass events to.

        All other parameters are optional and if not supplied are sourced from
        the gerrit instance.
        """
        self.username = username or gerrit.username
        self.keyfile = keyfile or gerrit.keyfile
        self.hostname = hostname or gerrit.hostname
        self.port = port or gerrit.port
        self.gerrit = gerrit

    def _read(self, fd):
        l = fd.readline()
        data = json.loads(l)
        self.log.debug("Received data from Gerrit event stream: \n%s" %
                       pprint.pformat(data))
        self.gerrit.addEvent(data)

    def _listen(self, stdout, stderr):
        poll = select.poll()
        poll.register(stdout.channel)
        while True:
            ret = poll.poll()
            for (fd, event) in ret:
                if fd == stdout.channel.fileno():
                    if event == select.POLLIN:
                        self._read(stdout)
                    else:
                        raise Exception("event on ssh connection")

    def _run(self):
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.connect(self.hostname,
                           username=self.username,
                           port=self.port,
                           key_filename=self.keyfile)

            stdin, stdout, stderr = client.exec_command("gerrit stream-events")

            self._listen(stdout, stderr)

            ret = stdout.channel.recv_exit_status()
            self.log.debug("SSH exit status: %s" % ret)

            if ret:
                raise Exception("Gerrit error executing stream-events")
        except Exception:
            self.log.exception("Exception on ssh event stream:")
            time.sleep(5)

    def run(self):
        while True:
            self._run()


class Gerrit(object):
    log = logging.getLogger("gerrit.Gerrit")

    def __init__(self, hostname, username, port=29418, keyfile=None):
        self.username = username
        self.hostname = hostname
        self.port = port
        self.keyfile = keyfile
        self.watcher_thread = None
        self.event_queue = None

    def startWatching(self):
        self.event_queue = Queue.Queue()
        self.watcher_thread = threading.Thread(target=GerritWatcher(self).run)
        self.watcher_thread.daemon = True
        self.watcher_thread.start()

    def addEvent(self, data):
        return self.event_queue.put(data)

    def getEvent(self):
        return self.event_queue.get()

    def createGroup(self, group, visible_to_all=True, owner=None):
        cmd = 'gerrit create-group'
        if visible_to_all:
            cmd = '%s --visible-to-all' % cmd
        if owner:
            cmd = '%s --owner %s' % (cmd, owner)
        cmd = '%s %s' % (cmd, group)
        out, err = self._ssh(cmd)
        return err

    def createProject(self, project, require_change_id=True):
        cmd = 'gerrit create-project'
        if require_change_id:
            cmd = '%s --require-change-id' % cmd
        cmd = '%s --name %s' % (cmd, project)
        out, err = self._ssh(cmd)
        return err

    def listProjects(self):
        cmd = 'gerrit ls-projects'
        out, err = self._ssh(cmd)
        return out.split('\n')

    def listGroups(self):
        cmd = 'gerrit ls-groups'
        out, err = self._ssh(cmd)
        return out.split('\n')

    def replicate(self, project='--all'):
        cmd = 'gerrit replicate %s' % project
        out, err = self._ssh(cmd)
        return out.split('\n')

    def review(self, project, change, message, action={}):
        cmd = 'gerrit review %s --project %s' % (change, project)
        if message:
            cmd += ' --message "%s"' % message
        for k, v in action.items():
            if v is True:
                cmd += ' --%s' % k
            else:
                cmd += ' --%s %s' % (k, v)
        out, err = self._ssh(cmd)
        return err

    def query(self, change, commit_msg=False, comments=False):
        if commit_msg:
            if comments:
                cmd = ('gerrit query --format json --commit-message --comments'
                       ' %s"' % change)
            else:
                cmd = 'gerrit query --format json --commit-message %s"' % (
                    change)
        else:
            if comments:
                cmd = 'gerrit query --format json --comments %s"' % (change)
            else:
                cmd = 'gerrit query --format json %s"' % (change)
        out, err = self._ssh(cmd)
        if not out:
            return False
        lines = out.split('\n')
        if not lines:
            return False
        data = json.loads(lines[0])
        if not data:
            return False
        self.log.debug("Received data from Gerrit query: \n%s" % (
            pprint.pformat(data)))
        return data

    def bulk_query(self, query):
        cmd = 'gerrit query --format json %s"' % (
            query)
        out, err = self._ssh(cmd)
        if not out:
            return False
        lines = out.split('\n')
        if not lines:
            return False

        data = []
        for line in lines:
            if line:
                data.append(json.loads(line))
        if not data:
            return False
        self.log.debug("Received data from Gerrit query: \n%s" % (
            pprint.pformat(data)))
        return data

    def _ssh(self, command):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.connect(self.hostname,
                       username=self.username,
                       port=self.port,
                       key_filename=self.keyfile)

        self.log.debug("SSH command:\n%s" % command)
        stdin, stdout, stderr = client.exec_command(command)

        out = stdout.read()
        self.log.debug("SSH received stdout:\n%s" % out)

        ret = stdout.channel.recv_exit_status()
        self.log.debug("SSH exit status: %s" % ret)

        err = stderr.read()
        self.log.debug("SSH received stderr:\n%s" % err)
        if ret:
            raise Exception("Gerrit error executing %s" % command)
        return (out, err)
