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

"""
This module contains methods to access REST API of XMS.
"""
import httplib2 as http
import urllib
from accounts import Accounts
from cookbooks import Cookbooks
from groups import Groups
from images import Images
from layer_blueprints import LayerBlueprints
from layers import Layers
from projects import Projects
from recipes import Recipes
from repositories import Repositories
from stack_blueprints import StackBlueprints
from stacks import Stacks
from restrictions import Restrictions
from tokens import Tokens
from users import Users
from iam import Iam
from leases import Leases
from base_resource import ErroneusResponseException

class Client:
    """
    Main class gathering all functionality of XMS' REST API together
    """
    def __init__(self,endpoint,token,silent=True):
        self.recipes = Recipes(endpoint,token,silent)
        self.cookbooks = Cookbooks(endpoint,token,silent)
        self.repositories = Repositories(endpoint,token,silent)
        self.images = Images(endpoint,token,silent)
        self.stackBlueprints = StackBlueprints(endpoint,token,silent)
        self.stacks = Stacks(endpoint,token,silent)
        self.accounts = Accounts(endpoint,token,silent)
        self.groups = Groups(endpoint,token,silent)
        self.users = Users(endpoint,token,silent)
        self.tokens = Tokens(endpoint,token,silent)
        self.projects = Projects(endpoint,token,silent)
        self.layers = Layers(endpoint,token,silent)
        self.layerBlueprints = LayerBlueprints(endpoint,token,silent)
        self.restrictions = Restrictions(endpoint,token,silent)
        self.leases = Leases(endpoint,token,silent)
