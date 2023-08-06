
# ProctorServ Python API - A Python Wrapper for ProctorCam's Proctoring Services
# Copyright (C) 2013 ProctorCam Inc.
#
# This file is part of ProctorServ Python API.
#
# ProctorServ Python API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# ProctorServ Python API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with ProctorServ Python API.  If not, see <http://www.gnu.org/licenses/>.

import requests
import random
import hashlib
import time
import json
from collections import OrderedDict

class HashedAuthenticator(object):

  @classmethod
  def apply_reverse_guid_and_sign(cls, params, customer_identifier, shared_secret):
    params['guid']        = str(random.getrandbits(64))
    params['customer_id'] = customer_identifier
    query_string          = cls.create_complex_query_string(params) + shared_secret
    params['guid']        = params['guid'][::-1]
    params['signature']   = hashlib.sha256(query_string).hexdigest() 
    return params['signature']

  # In the case of a complex data type(hash or array)
  # create_complex_query_string parses through each 
  # value in the request params and creates a query string
  # with the values, else it will create a standard query string
  # with the associated key value pair
  #
  @classmethod  
  def create_complex_query_string(cls, options):
    query_string = []

    for key, value in options.iteritems():
      if isinstance(value, list): 
        query_string.append(cls.create_array_uri(value, key))
      elif isinstance(value, dict):
        query_string.append(cls.create_hash_uri(value, key))
      else:
        query_string.append(cls.create_string_uri(value, key)) 
    return "&".join(query_string)

  # create a query string if the request params are
  # one dimensional array
  # example: params = { "ids" => [1,2,3,] }
  # result: "ids[]=1&ids[]=2&ids[]=3"
  #
  @classmethod
  def create_array_uri(cls, options, key):
    combined_options = []

    for v in options:
      str_v  = str(v)
      string = "%s[]=%s" %(key, str_v)
      combined_options.append(string)

    return "&".join(combined_options)

  # create a query string if the request params are
  # one dimensional dictionaries
  # example: params = { "name" => {"first_name" => "Joe", "last_name" => "Smith"}  }
  # result: "name[first_name]=Joe&name[last_name]=Smith"
  #
  @classmethod
  def create_hash_uri(cls, options, key):
    combined_options = []

    for k, v in options.iteritems():
      str_k  = str(k) 
      str_v  = str(v)
      string = "%s[%s]=%s" %(key, str_k, str_v)
      combined_options.append(string)

    return "&".join(combined_options)
  
  # create a standard query string if the request params are
  # simple data types (eg booleans, string, int etc..)
  # example: params = { "session_duration" => 60, "num_slots" => 10, "exam_code" => "exam_1" }
  # result: "session_duration=60&num_slots=10&exam_code=exam_1"
  #
  @classmethod
  def create_string_uri(cls, value, key):
    combined_options = []

    sval = str(value).lower() if isinstance(value, bool) else str(value)
    combined_options.append(key + '=' + sval)

    return "&".join(combined_options)