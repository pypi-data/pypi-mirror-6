
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

from hashed_authenticator import HashedAuthenticator
import requests
import json

class RestRequestClient:

  def make_get_request(self, url, customer_identifier, shared_secret, params):
    """ Makes a HTTP GET request with the proper user information """
    HashedAuthenticator.apply_reverse_guid_and_sign(params, customer_identifier, shared_secret)
    response = requests.get(url, params=params, headers={'Content-type': 'application/json', 'Accept': 'application/json'} )
    return response


  def make_post_request(self, url, customer_identifier, shared_secret, params):
    """ Makes a HTTP POST request with the proper user information """
    HashedAuthenticator.apply_reverse_guid_and_sign(params, customer_identifier, shared_secret)
    response = requests.post(url, data=json.dumps(params), headers={'Content-type': 'application/json', 'Accept': 'application/json'} )
    return response