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

class Images(Resource):
    base = '/images/'

    def listImages(self):
        return self.retrieve(Images.base)

    def createImage(self,image):
        return self.retrieve(Images.base,'POST',json.dumps(image))

    def getImage(self,id):
        return self.retrieve(Images.base+id)

    def deleteImage(self,id):
        return self.retrieve(Images.base+id,'DELETE')

    def postData(self,id,data):
        return self.retrieve(Images.base+id+'/data','POST',data,contentType='application/octet-stream')


