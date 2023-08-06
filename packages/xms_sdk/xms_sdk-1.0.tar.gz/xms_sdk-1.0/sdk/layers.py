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

class Layers(Resource):
    base = '/layers/'

    def get(self,id):
        return self.retrieve(Layers.base+id)

    def remove(self,id):
        return self.retrieve(Layers.base+id,'DELETE')

    def getParams(self,id):
        return self.retrieve(Layers.base+id+'/parameters-values')

    def putParams(self,id,parameters):
        return self.retrieve(Layers.base+id+'/parameters-values','PUT',json.dumps(parameters))

    def updateLayerTemplate(self,id,template):
        return self.retrieve(Layers.base+id,'PUT',json.dumps(template),{},'template/json; charset=UTF-8','template/json')

    def createInstance(self,id,instance,scalable=True):
        scalable = "true" if scalable else "false"
        return self.retrieve(Layers.base+id+'/instances','POST',json.dumps(instance),{'scalable':[scalable]})

    def updateLifecyclePhase(self,id,phase,recipeNames, attributeValues):
        recipes = []
        attributes = []
        
        for recipeName in recipeNames:
            recipes.append({'name' : recipeName})
            
        for attibuteValue in attributeValues:
            keyValue = attibuteValue.split("=")
            attributes.append({'key' : keyValue[0], 'value' : keyValue[1]})
            
        runlist = json.dumps({'phase' : phase, 'recipes' : recipes, 'attributes' : attributes})
        print runlist
        return self.retrieve(Layers.base+id+'/runlists?phase='+phase,'PUT',runlist)
        
    def createApplicationDeployment(self,id,application_deployment):
        return self.retrieve(Layers.base+id+'/deployments','POST',json.dumps(application_deployment))

    def removeApplicationDeployment(self,id,deployment_id):
        return self.retrieve(Layers.base+id+'/deployments/'+deployment_id,'DELETE')

    def listApplicationDeployments(self,id):
        return self.retrieve(Layers.base+id+'/deployments')
        
