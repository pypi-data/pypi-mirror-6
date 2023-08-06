#!/user/env

# Copyright 2014 Cameron Brown. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import os
import re

from props import prop as prop

class entity():
    def create(self):
        if os.path.isfile(self.path + '/' + self.name + '.json') != True:
            entity = open(self.path + '/' + self.name + '.json', 'w')
            entity.write('{\n   "%s":{\n\n    } \n}' % self.name)
            entity.close()
            print 'Entity "' + self.name + '" created!'

    def insert(self, values, key):
        if type(values) == type([]):
            z = 0
            data = []
            for i in values:
                data.append(values[z].__dict__)
                z = z + 1 
        elif type(values) == type(str()): 
            data = values
        else:
            data = values.__dict__
        read = json.load(open(self.path + 
                        '/' + self.name + '.json', 'r')) 
        read[self.name][key] = data
        to_transfer = json.dumps(read, sort_keys=True,
                       indent=4, separators=(',', ': '))
        entity = open(self.path + 
                        '/' + self.name + '.json', 'w+')
        entity.write(to_transfer)
        entity.close()

        print 'Data written to "' + self.name + '"!'

    def delete(self, key):
        data = json.load(open(self.path + 
                    '/' + self.name + '.json', 'r'))
        data[self.name].pop(key)
        open(self.path + 
                    '/' + self.name + '.json', 'w+').write(json.dumps(data))

        print 'Data removed from "' + self.name + '"!'
 
    def read(self, key):
        read_entity = open(self.path + '/' + self.name + '.json', 'r')
        entity_data = json.load(read_entity)
        print 'Data retrived from "' + self.name + '"!'
        return self.deep_search(key, entity_data)
 
    def deep_search(self, needles, haystack):
        found = {}
        if type(needles) != type([]):
            needles = [needles]

        if type(haystack) == type(dict()):
            for needle in needles:
                if needle in haystack.keys():
                    found[needle] = haystack[needle]
                elif len(haystack.keys()) > 0:
                    for key in haystack.keys():
                        result = self.deep_search(needle, haystack[key])
                        if result:
                            for k, v in result.items():
                                found[k] = v
        elif type(haystack) == type([]):
            for node in haystack:
                result = self.deep_search(needles, node)
                if result:
                    for k, v in result.items():
                        found[k] = v
        return found

    def __init__(self, name, parent, path):
        self.name = name
        self.parent = parent
        self.path = path
        self.create()
