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

class ErroneusResponseException(Exception):
    def __init__(self,status,message):
        self.status = status
        self.message = message

class Resource:
    def __init__(self,endpoint,token,silent=False):
        self.silent = silent
        self.endpoint = endpoint
        self.token = token

    def retrieve(self,resource,method='GET',body='',params={},contentType='application/json; charset=UTF-8',accepts='application/json'):
        param_string = self.urlparams(params)
        headers = {
                'Accept': accepts,
                'Content-Type': contentType,
            'Authorization': 'Bearer '+self.token
        }
        target = self.endpoint+resource+param_string
        h = http.Http()
        if not self.silent:
            self.print_request(target,method,body)
        response, content = h.request(target,method,body,headers)
        if not self.silent:
            self.print_response(response)
        status = int(response['status'])
        if status >= 400:
            print content
            content = json.loads(content)
            message=""
            if content.has_key('message'):
                message = content['message']
            raise ErroneusResponseException(status,message)
        if content:
            return json.loads(content)
        else:
            return None

    def urlparams(self,d):
        if len(d)==0:
            return ''
        tab = []
        for k,v in d.items():
            tab += ["%s=%s"%(k,v2) for v2 in v]
        return '?'+'&'.join(tab)

    def print_request(self,target,method,body):
        print "> "+method+" "+target
        print "> "+body

    def print_response(self,response):
        print "< "+response['status']
