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

from base_resource import Resource

class Recipes(Resource):
    base = '/recipes/'
    PARAM_RECIPES_NAME = "name"

    def get(self,id):
        return self.retrieve(Recipes.base+id)

    def listByNames(self,names):
        return self.retrieve(Recipes.base,params={Recipes.PARAM_RECIPES_NAME:names})
