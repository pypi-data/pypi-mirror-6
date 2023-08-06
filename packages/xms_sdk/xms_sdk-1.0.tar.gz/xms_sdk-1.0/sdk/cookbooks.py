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

class Cookbooks(Resource):
    base = '/cookbooks/'

    def get(self,id,with_dep=False):
        dep_param = '?recursive-dependencies=true' if with_dep else ''
        return self.retrieve(Cookbooks.base+id+dep_param)

    def listRecipes(self,id):
        return self.retrieve('/recipes?name=rabbitmq')

    def list(self):
        return self.retrieve(Cookbooks.base)

