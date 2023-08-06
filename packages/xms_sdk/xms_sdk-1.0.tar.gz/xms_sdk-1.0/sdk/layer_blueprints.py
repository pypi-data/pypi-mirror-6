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

class LayerBlueprints(Resource):
    base = '/layer-blueprints/'

    def listPublic(self):
        return self.retrieve(LayerBlueprints.base)

    def get(self,id):
        return self.retrieve(LayerBlueprints.base+id)

    def delete(self,id):
        return self.retrieve(LayerBlueprints.base+id,'DELETE')

    def update(self,id,layerBlueprint):
        return self.retrieve(LayerBlueprints.base+id,'PUT',json.dumps(layerBlueprint))

    def export(self,id,layerBlueprint):
        return self.retrieve(LayerBlueprints.base+'export','POST',json.dumps(layerBlueprint),{"blueprintId":[id]})

    def promote(self,layerId,layerBlueprint):
        return self.retrieve(LayerBlueprints.base,'POST',json.dumps(layerBlueprint),{"layerId":[layerId]})
