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

class Projects(Resource):
    base = '/projects/'

    def listProjects(self):
        return self.retrieve(Projects.base)

    def get(self,id):
        return self.retrieve(Projects.base+id)

    def delete(self,id):
        return self.retrieve(Projects.base+id,'DELETE')

    def getUsers(self,id):
        return self.retrieve(Projects.base+id+'/users')

    def addUser(self,id,user):
        return self.retrieve(Projects.base+id+'/users','POST',json.dumps(user))

    def removeUser(self,id,userId):
        return self.retrieve(Projects.base+id+'/users/'+userId,'DELETE')

    def assignUser(self,id,userId):
        return self.retrieve(Projects.base+id+'/users/'+userId,'PUT')

    def getStacks(self,id):
        return self.retrieve(Projects.base+id+'/stacks')

    def addStack(self,id,stack,blueprintId=None):
        if blueprintId:
            return self.retrieve(Projects.base+id+'/stacks','POST',json.dumps(stack),{'blueprintId':[blueprintId]})
        else:
            return self.retrieve(Projects.base+id+'/stacks/freehand','POST',json.dumps(stack))

    def addRawStack(self,id,name,template):
        return self.retrieve(Projects.base+id+'/stacks','POST',json.dumps(template),{"stackName":[name]},'template/json; charset=UTF-8','template/json')

    def addLayers(self,id,stackName,layers):
        return self.retrieve(Projects.base+id+'/layers','POST',json.dumps(layers),{"stackName":[stackName]})

    def addRawLayer(self,id,stackName,template):
        return self.retrieve(Projects.base+id+'/layers','POST',json.dumps(template),{"stackName":[stackName]},'template/json; charset=UTF-8','template/json')

    def getNetworkConfiguration(self,id):
        return self.retrieve(Projects.base+id+'/subnets')
    
    def addSubnet(self,id,subnet):
        return self.retrieve(Projects.base+id+'/subnets','POST',json.dumps(subnet))

    def removeSubnet(self,id,subnetUUID):
        return self.retrieve(Projects.base+id+'/subnets/'+subnetUUID,'DELETE')

    def listLeases(self, id):
        return self.retrieve(Projects.base+id+'/leases/')

    def createLease(self,id,lease):
        return self.retrieve(Projects.base+id+'/leases/', 'POST', json.dumps(lease))
    
    def updateLease(self,id,leaseId,lease):
        return self.retrieve(Projects.base+id+'/leases/'+leaseId, 'PUT', json.dumps(lease))

    def getLease(self, id, leaseId):
        return self.retrieve(Projects.base+id+'/leases/'+leaseId)

    def deleteLease(self, id, leaseId):
        return self.retrieve(Projects.base+id+'/leases/'+leaseId, 'DELETE'); 
