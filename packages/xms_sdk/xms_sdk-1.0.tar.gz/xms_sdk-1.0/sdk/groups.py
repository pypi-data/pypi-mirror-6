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
from base_resource import Resource

class Groups(Resource):
    base = '/groups/'

    def get(self,id):
        return self.retrieve(Groups.base+id)

    def delete(self,id):
        return self.retrieve(Groups.base+id,'DELETE')

    def getUsers(self,id):
        return self.retrieve(Groups.base+id+'/users')

    def addUser(self,id,user):
        return self.retrieve(Groups.base+id+'/users','POST',json.dumps(user))

    def deleteUser(self,id,userId):
        return self.retrieve(Groups.base+id+'/users/'+userId,'DELETE')

    def assignUser(self,id,userId):
        return self.retrieve(Groups.base+id+'/users/'+userId,'PUT')

    def listEntitlements(self,id):
        return self.retrieve(Groups.base+id+'/entitlements')

    def addEntitlement(self,id,entitlement):
        return self.retrieve(Groups.base+id+'/entitlements','POST',json.dumps(entitlement))

    def deleteEntitlement(self,id,entId):
        return self.retrieve(Groups.base+id+'/entitlements/'+entId,'DELETE')

    def putEntitlements(self,id,entitlements):
        return self.retrieve(Groups.base+id+'/entitlements','PUT',json.dumps(entitlements))
        

