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

class Accounts(Resource):
    base = '/accounts/'

    def listAccounts(self):
        return self.retrieve(Accounts.base)

    def add(self,account):
        return self.retrieve(Accounts.base,'POST',json.dumps(account))

    def get(self,id):
        return self.retrieve(Accounts.base+id)

    def delete(self,id):
        return self.retrieve(Accounts.base+id,'DELETE')

    def addGroup(self,id,group):
        return self.retrieve(Accounts.base+id+'/groups','POST',json.dumps(group))

    def getGroups(self,id):
        return self.retrieve(Accounts.base+id+'/groups')

    def addUser(self,id,user):
        return self.retrieve(Accounts.base+id+'/users','POST',json.dumps(user))

    def getUsers(self,id):
        return self.retrieve(Accounts.base+id+'/users')

    def getStacks(self,id):
        return self.retrieve(Accounts.base+id+'/stacks')

    def addProject(self,id,group):
        return self.retrieve(Accounts.base+id+'/projects','POST',json.dumps(group))

    def getProjects(self,id):
        return self.retrieve(Accounts.base+id+'/projects')

    def createImage(self,id,image):
        return self.retrieve(Accounts.base+id+'/images','POST',json.dumps(image))

    def listImages(self,id):
        return self.retrieve(Accounts.base+id+'/images')

    def createRepository(self,id,repository):
        return self.retrieve(Accounts.base+id+'/repositories','POST',json.dumps(repository))

    def listRepositories(self,id):
        return self.retrieve(Accounts.base+id+'/repositories')

    def listCookbooks(self,id):
        return self.retrieve(Accounts.base+id+'/cookbooks')
#
#    def createStackBlueprint(self,id,stackBlueprint):
#        return self.retrieve(Accounts.base+id+'/stack-blueprints','POST',json.dumps(stackBlueprint))

    def listLayerBlueprints(self,id):
        return self.retrieve(Accounts.base+id+'/layer-blueprints')

    def listStackBlueprints(self,id):
        return self.retrieve(Accounts.base+id+'/stack-blueprints')

    def promoteLayer(self,id,layerId,layerBlueprint):
        return self.retrieve(Accounts.base+id+'/layer-blueprints','POST',json.dumps(layerBlueprint),{"layerId":[layerId]})

    def promoteStack(self,id,stackId,stackBlueprint):
        return self.retrieve(Accounts.base+id+'/stack-blueprints','POST',json.dumps(stackBlueprint),{"stackId":[stackId]})

    def listRestrictions(self,id):
        return self.retrieve(Accounts.base+id+'/restrictions')

    def createRestriction(self,id,type,restriction):
        return self.retrieve(Accounts.base+id+'/restrictions','POST',json.dumps(restriction),{"type":[type]})

    def listQuotas(self,id):
        return self.retrieve(Accounts.base+id+'/quotas')

    def putQuotas(self,id,quotas):
        quotas = {"quota":[{"type":k,"limit":v} if v!=None else {"type":k} for k,v in quotas.items()]}
        return self.retrieve(Accounts.base+id+'/quotas','PUT',json.dumps(quotas))
