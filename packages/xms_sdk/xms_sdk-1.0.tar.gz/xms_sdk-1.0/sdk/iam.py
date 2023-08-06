# Copyright 2012 AMG.lab, a Bull Group Company
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import httplib2 as http
import base64

class Iam:
    def __init__(self,endpoint,oauth_user,oauth_pass):
        self.endpoint = endpoint
        self.oauth_user = oauth_user
        self.oauth_pass = oauth_pass

    def getHeaders(self):
        auth = base64.encodestring(self.oauth_user+':'+self.oauth_pass)
        return {'Authorization':'Basic '+auth}

    def login(self,username,password):
        target = self.endpoint+"/xlc-services/oauth2/tokens"
        method = 'POST'
        parameters = ([
            'realm=xlc',
            'grant_type=password',
            'username='+username,
            'password='+password,
            'scope=userScoped'])
        body = "&".join(parameters)
        h = http.Http()
        response, content = h.request(target,method,body,self.getHeaders())
        try:
            token = json.loads(content)['access_token']
        except ValueError:
            raise Exception("Cannot login to xlcloud")
        return token
