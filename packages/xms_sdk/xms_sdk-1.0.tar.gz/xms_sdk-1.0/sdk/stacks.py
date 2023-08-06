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

class Stacks(Resource):
    base = '/stacks/'

    def listStacks(self):
        return self.retrieve(Stacks.base)

    def get(self,id):
        return self.retrieve(Stacks.base+id)

    def remove(self,id):
        return self.retrieve(Stacks.base+id,'DELETE')

    def getParams(self,id):
        return self.retrieve(Stacks.base+id+'/parameters-values')

    def putParams(self,id,parameters):
        return self.retrieve(Stacks.base+id+'/parameters-values','PUT',json.dumps(parameters))

    def provision(self,id):
        return self.retrieve(Stacks.base+id+'/sessions','POST')

    def getCurrentSession(self,id):
        return self.retrieve(Stacks.base+id+'/sessions/current')

    def stop(self,id):
        return self.retrieve(Stacks.base+id+'/sessions/current','DELETE')

    def updateSession(self,id,session):
        return self.retrieve(Stacks.base+id+'/sessions/current','PUT',json.dumps(session))

    def updateStackTemplate(self,id,template):
        return self.retrieve(Stacks.base+id,'PUT',json.dumps(template),{},'template/json; charset=UTF-8','template/json')

    def createLayer(self,id,name,blueprintId=None):
        layer = {'name':name}
        if blueprintId:
            return self.retrieve(Stacks.base+id+'/layers','POST',json.dumps(layer),{'blueprintId':[blueprintId]})
        else:
            return self.retrieve(Stacks.base+id+'/layers/freehand','POST',json.dumps(layer))

