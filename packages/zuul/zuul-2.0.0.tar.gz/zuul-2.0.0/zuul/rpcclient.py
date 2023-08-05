# Copyright 2013 OpenStack Foundation
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
import time

import gear


class RPCFailure(Exception):
    pass


class RPCClient(object):
    log = logging.getLogger("zuul.RPCClient")

    def __init__(self, server, port):
        self.log.debug("Connecting to gearman at %s:%s" % (server, port))
        self.gearman = gear.Client()
        self.gearman.addServer(server, port)
        self.log.debug("Waiting for gearman")
        self.gearman.waitForServer()

    def submitJob(self, name, data):
        self.log.debug("Submitting job %s with data %s" % (name, data))
        job = gear.Job(name,
                       json.dumps(data),
                       unique=str(time.time()))
        self.gearman.submitJob(job)

        self.log.debug("Waiting for job completion")
        while not job.complete:
            time.sleep(0.1)
        if job.exception:
            raise RPCFailure(job.exception)
        self.log.debug("Job complete, success: %s" % (not job.failure))
        return (not job.failure)

    def enqueue(self, pipeline, project, trigger, change, patchset):
        data = {'pipeline': pipeline,
                'project': project,
                'trigger': trigger,
                'change': change,
                'patchset': patchset,
                }
        return self.submitJob('zuul:enqueue', data)

    def shutdown(self):
        self.gearman.shutdown()
