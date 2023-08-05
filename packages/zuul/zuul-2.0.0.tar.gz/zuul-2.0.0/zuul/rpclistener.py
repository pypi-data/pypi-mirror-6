# Copyright 2012 Hewlett-Packard Development Company, L.P.
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
import threading
import traceback

import gear

import model


class RPCListener(object):
    log = logging.getLogger("zuul.RPCListener")

    def __init__(self, config, sched):
        self.config = config
        self.sched = sched

    def start(self):
        self._running = True
        server = self.config.get('gearman', 'server')
        if self.config.has_option('gearman', 'port'):
            port = self.config.get('gearman', 'port')
        else:
            port = 4730
        self.worker = gear.Worker('Zuul RPC Listener')
        self.worker.addServer(server, port)
        self.register()
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()

    def register(self):
        self.worker.registerFunction("zuul:enqueue")

    def stop(self):
        self.log.debug("Stopping")
        self._running = False
        self.worker.shutdown()
        self.log.debug("Stopped")

    def join(self):
        self.thread.join()

    def run(self):
        while self._running:
            try:
                job = self.worker.getJob()
                z, jobname = job.name.split(':')
                attrname = 'handle_' + jobname
                if hasattr(self, attrname):
                    f = getattr(self, attrname)
                    if callable(f):
                        try:
                            f(job)
                        except Exception:
                            self.log.exception("Exception while running job")
                            job.sendWorkException(traceback.format_exc())
                    else:
                        job.sendWorkFail()
                else:
                    job.sendWorkFail()
            except Exception:
                self.log.exception("Exception while getting job")

    def handle_enqueue(self, job):
        args = json.loads(job.arguments)
        event = model.TriggerEvent()
        errors = ''

        trigger = self.sched.triggers.get(args['trigger'])
        if trigger:
            event.trigger_name = args['trigger']
        else:
            errors += 'Invalid trigger: %s\n' % args['trigger']

        project = self.sched.layout.projects.get(args['project'])
        if project:
            event.project_name = args['project']
        else:
            errors += 'Invalid project: %s\n' % args['project']

        pipeline = self.sched.layout.pipelines.get(args['pipeline'])
        if pipeline:
            event.forced_pipeline = args['pipeline']
        else:
            errors += 'Invalid pipeline: %s\n' % args['pipeline']

        if not errors:
            event.change_number = args['change']
            event.patch_number = args['patchset']
            try:
                event.getChange(project, trigger)
            except Exception:
                errors += 'Invalid change: %s,%s\n' % (
                    args['change'], args['patchset'])

        if errors:
            job.sendWorkException(errors.encode('utf8'))
        else:
            self.sched.addEvent(event)
            job.sendWorkComplete()
