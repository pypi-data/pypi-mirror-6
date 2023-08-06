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

class StackBlueprints(Resource):
    base = '/stack-blueprints/'

    def listStackBlueprints(self):
        return self.retrieve(StackBlueprints.base)

    def getStackBlueprint(self,id):
        return self.retrieve(StackBlueprints.base+id)

    def deleteStackBlueprint(self,id):
        return self.retrieve(StackBlueprints.base+id,'DELETE')

    def updateStackBlueprint(self,id,stackBlueprint):
        return self.retrieve(StackBlueprints.base+id,'PUT',json.dumps(stackBlueprint))

    def promote(self,stackId,stackBlueprint):
        return self.retrieve(StackBlueprints.base,'POST',json.dumps(stackBlueprint),{"stackId":[stackId]})

