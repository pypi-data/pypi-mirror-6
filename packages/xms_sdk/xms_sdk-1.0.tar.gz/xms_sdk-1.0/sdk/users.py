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

class Users(Resource):
    base = '/users/'

    def listUsers(self):
        return self.retrieve(Users.base)

    def addUser(self,user):
        return self.retrieve(Users.base,'POST',json.dumps(user))

    def get(self,id):
        return self.retrieve(Users.base+id)

    def delete(self,id):
        return self.retrieve(Users.base+id,'DELETE')

    def update(self,id,user):
        return self.retrieve(Users.base+id,'PUT',json.dumps(user))

    def getGroups(self,id):
        return self.retrieve(Users.base+id+'/groups')

    def listAccessTokens(self,id):
        return self.retrieve(Users.base+id+'/access-tokens')

    def listEntitlements(self,id):
        return self.retrieve(Users.base+id+'/entitlements')

    def addEntitlement(self,id,entitlement):
        return self.retrieve(Users.base+id+'/entitlements','POST',json.dumps(entitlement))

    def deleteEntitlement(self,id,entId):
        return self.retrieve(Users.base+id+'/entitlements/'+entId,'DELETE')

    def putEntitlements(self,id,entitlements):
        return self.retrieve(Users.base+id+'/entitlements','PUT',json.dumps(entitlements))

    def listProjects(self,id):
        return self.retrieve(Users.base+id+'/projects')

    def getOsCredentials(self,id,projectId):
        return self.retrieve(Users.base+id+'/os-credentials',params={'projectId':[projectId]})

    def listKeypairs(self,id):
        return self.retrieve(Users.base+id+'/os-keypairs')
    
    def getKeypair(self,id,name):
        return self.retrieve(Users.base+id+'/os-keypairs/'+name)
    
    def generateKeypair(self,id,name):
        return self.retrieve(Users.base+id+'/os-keypairs/'+name,'POST')
    
    def importKeypair(self,id,keypair):
        return self.retrieve(Users.base+id+'/os-keypairs','POST',json.dumps(keypair))
    
    def deleteKeypair(self,id,name):
        return self.retrieve(Users.base+id+'/os-keypairs/'+name,'DELETE')
  

