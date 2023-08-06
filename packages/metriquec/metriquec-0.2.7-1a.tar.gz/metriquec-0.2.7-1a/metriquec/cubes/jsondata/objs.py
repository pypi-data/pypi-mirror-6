#!/usr/bin/env python
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
# Author: "Chris Ward <cward@redhat.com>

'''
metriquec.cubes.jsondata.objs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains the generic metrique cube used
for exctacting data from JSON data.
'''

import logging
try:
    import simplejson as json
except ImportError:
    import json

from metrique import pyclient

logger = logging.getLogger(__name__)


# FIXME: USE pandas read_json!
class Objs(pyclient):
    """
    Object used for extracting data in JSON format from files on disk.
    """
    name = 'jsondata_objs'

    def get_objects(self, uri, **kwargs):
        objects = self.load(uri)
        objects = super(Objs, self).get_objects(objects, **kwargs)
        return objects

    def load(self, path, strict=False):
        '''
        Given a string of valid JSON, load it into memory.

        No strict loading (DEFAULT); ignore control characters
        '''
        # 'strict=False: control characters will be allowed in strings'
        with open(path) as f:
            return json.load(f, strict=strict)

    def loads(self, json_str, strict=False):
        '''
        Given a string of valid JSON, load it into memory.

        No strict loading (DEFAULT); ignore control characters
        '''
        # 'strict=False: control characters will be allowed in strings'
        return json.loads(json_str, strict=strict)

    def loadi(self, json_iter):
        '''
        Given an iterator object, convert it to simple
        joined string, then try to load the json
        as as a string.
        '''
        return self.loads(''.join(json_iter))
