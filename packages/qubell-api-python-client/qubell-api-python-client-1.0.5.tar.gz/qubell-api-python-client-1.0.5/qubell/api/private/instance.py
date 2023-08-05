# Copyright (c) 2013 Qubell Inc., http://qubell.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = "Vasyl Khomenko"
__copyright__ = "Copyright 2013, Qubell.com"
__license__ = "Apache"
__version__ = "1.0.5"
__email__ = "vkhomenko@qubell.com"

import logging as log
import requests
import simplejson as json

from qubell.api.tools import retry
from qubell.api.private import application


class Instance(application.Application):
    """
    Base class for application instance. Manifest required.
    """
    rawRespose = None
    _setatus = None

    def __parse(self, values):
        ret = {}
        for val in values:
            ret[val['id']] = val['value']
        return ret

    def __init__(self, context, id=None):
        self.instanceId = id
        self.context = context
        self.context.instanceId = self.instanceId
        self.name = self.name
        self._status = 'Init'

    def __getattr__(self, key):
        url = self.context.api+'/organizations/'+self.context.organizationId+'/instances/'+self.instanceId+'.json'
        resp = requests.get(url, cookies=self.context.cookies, data="{}", verify=False)
        log.debug(resp.text)
        self.rawRespose = resp
        if resp.status_code == 200:
            # return same way old_public api does
            if key in ['returnValues', ]:
                return self.__parse(resp.json()[key])
            else:
                return resp.json()[key]
        else:
            return None

    def waitForStatus(self, final='Running', accepted=['Requested'], timeout=[20, 10, 1]):
        log.debug('Waiting status: %s' % final)
        import time #TODO: We have to wait, because privious status takes time to change to new one
        time.sleep(10)
        @retry(*timeout) # ask status 20 times every 10 sec.
        def waiter():
            cur_status = self.status
            if cur_status in final:
                log.info('Got status: %s, continue' % cur_status)
                return True
            elif cur_status in accepted:
                log.info('Current status: %s, waiting...' % cur_status)
                return False
            else:
                log.error('Got unexpected instance status: %s' % cur_status)
                return True # Let retry exit

        waiter()
        # We here, means we reached timeout or got status we are waiting for.
        # Check it again to be sure

        cur_status = self.status
        self._status = self.status
        log.info('Final status: %s' % cur_status)
        if cur_status in final:
            return True
        else:
            return False


    def ready(self, timeout=3):  # Shortcut for convinience. Temeout = 3 min (ask timeout*6 times every 10 sec)
        return self.waitForStatus(final='Running', accepted=['Launching', 'Requested', 'Executing', 'Unknown'], timeout=[timeout*6, 10, 1])
        # TODO: Unknown status  should be removed

        #TODO: not available
    def destroyed(self, timeout=3):  # Shortcut for convinience. Temeout = 3 min (ask timeout*6 times every 10 sec)
        return self.waitForStatus(final='Destroyed', accepted=['Destroying', 'Running'], timeout=[timeout*6, 10, 1])

    def runWorkflow(self, name, parameters={}):
        log.info("Running workflow %s" % name)

        url = self.context.api+'/organizations/'+self.context.organizationId+'/instances/'+self.instanceId+'/workflows/'+name+'.json'
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps(parameters)
        resp = requests.post(url, cookies=self.context.cookies, data=payload, verify=False, headers=headers)
        log.debug(resp.text)
        self.rawResponse = resp
        if resp.status_code == 200:
            return True
        else:
            log.error('Cannot execute workflow %s, got error: %s' % (name, resp.content))
            return False


    def getManifest(self):
        url = self.context.api+'/organizations/'+self.context.organizationId+'/applications/'+self.context.applicationId+'/refreshManifest.json'
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps({})
        resp = requests.post(url, cookies=self.context.cookies, data=payload, verify=False, headers=headers)
        log.debug(resp.text)
        self.rawRespose = resp
        if resp.status_code == 200:
            return resp.json()
        else:
            return False



    def reconfigure(self, name='reconfigured', **kwargs):
        revisionId = kwargs.get('revisionId', '')
        parameters = kwargs.get('parameters', {})
        submodules = kwargs.get('submodules', {})
        url = self.context.api+'/organizations/'+self.context.organizationId+'/instances/'+self.instanceId+'/configure.json'
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps({
                   'parameters': parameters,
                   'submodules': submodules,
                   'revisionId': revisionId,
                   'instanceName': name})
        resp = requests.put(url, cookies=self.context.cookies, data=payload, verify=False, headers=headers)

        log.debug('--- INSTANCE RECONFIGUREATION REQUEST ---')
        log.debug('REQUEST HEADERS: %s' % resp.request.headers)
        log.debug('REQUEST: %s' % resp.request.body)
        log.debug('RESPONSE: %s' % resp.text)
        self.rawRespose = resp
        if resp.status_code == 200:
            return resp.json()
        else:
            return False


    def delete(self):
        return self.destroy()

    def destroy(self):
        log.info("Destroying")
        url = self.context.api+'/organizations/'+self.context.organizationId+'/instances/'+self.instanceId+'/workflows/destroy.json'
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url, cookies=self.context.cookies, data=json.dumps({}), verify=False, headers=headers)
        log.debug(resp.text)
        self.rawRespose = resp
        if resp.status_code == 200:
            self._status = None
            return resp.json()
        else:
            return False

    def __del__(self):
        pass
        #if self._status:
        #    self.destroy()
