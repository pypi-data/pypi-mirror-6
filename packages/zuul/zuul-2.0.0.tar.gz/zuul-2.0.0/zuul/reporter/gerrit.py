# Copyright 2013 Rackspace Australia
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

import logging


class Reporter(object):
    """Sends off reports to Gerrit."""

    name = 'gerrit'
    log = logging.getLogger("zuul.reporter.gerrit.Reporter")

    def __init__(self, trigger):
        """Set up the reporter."""
        self.gerrit = trigger.gerrit
        self.trigger = trigger

    def report(self, change, message, params):
        """Send a message to gerrit."""
        self.log.debug("Report change %s, params %s, message: %s" %
                       (change, params, message))
        if not params:
            self.log.debug("Not reporting change %s: No params specified." %
                           change)
            return
        changeid = '%s,%s' % (change.number, change.patchset)
        change._ref_sha = self.trigger.getRefSha(change.project.name,
                                                 'refs/heads/' + change.branch)
        return self.gerrit.review(change.project.name, changeid, message,
                                  params)

    def getSubmitAllowNeeds(self, params):
        """Get a list of code review labels that are allowed to be
        "needed" in the submit records for a change, with respect
        to this queue.  In other words, the list of review labels
        this reporter itself is likely to set before submitting.
        """
        return params
