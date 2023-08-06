
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

import unittest
from proctorserv_api import ProctorservApi 
from hashed_authenticator import HashedAuthenticator
from exception import MissingRequiredParameterException
from exception import InvalidClientException
from exception import InvalidSignatureException
from exception import InvalidIpException
from rest_request_client import RestRequestClient
from datetime import timedelta
import time
import datetime
import calendar
import collections
from array import *
import json


#  Note:
#   - In order to run this spec you must have a local server running the proctorserv app on port 3000
#   - cd into the directory this file is contained in and use the command (python test.py) 
#
class ProctorservApiTests(unittest.TestCase):
 
  def test_passing_improper_credentials(self):
    """ raises an invalid_client_exception when api_identifier is wrong """
    proctorserv = ProctorservApi("FAKE", "shared_secret", 'http', "localhost:3000")
    
    options                     = collections.OrderedDict()
    options['lower_bound']      = datetime.datetime.utcnow()
    options['upper_bound']      = datetime.datetime.utcnow() + timedelta(hours = 10)
    options['session_duration'] = 60

    self.assertRaises(InvalidClientException, proctorserv.get_available_timeslots_between, options)


  def test_invalid_signature_exception(self):
    """ raises an invalid_signature_exception when shared_secret is wrong """
    proctorserv = ProctorservApi("test", "wrong", 'http', "localhost:3000")

    options                     = collections.OrderedDict()
    options['lower_bound']      = datetime.datetime.utcnow()
    options['upper_bound']      = datetime.datetime.utcnow() + timedelta(hours = 10)
    options['session_duration'] = 60

    self.assertRaises(InvalidSignatureException, proctorserv.get_available_timeslots_between, options)



class GetAvailableTimeslotsBetweenTest(unittest.TestCase):

  def test_require_lower_bound(self):
    """
    raises missing_required_parameter_exception when not passed
    lower_bound, upper_bound, and session_duration in options hash
    """
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                     = collections.OrderedDict()
    options['upper_bound']      = datetime.datetime.utcnow() + timedelta(hours = 10)
    options['session_duration'] = 60

    self.assertRaises(MissingRequiredParameterException, proctorserv.get_available_timeslots_between, options)


  def test_require_upper_bound(self):
    """
    raises missing_required_parameter_exception when not passed
    lower_bound, upper_bound, and session_duration in options hash
    """
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                     = collections.OrderedDict()
    options['lower_bound']      = datetime.datetime.utcnow() + timedelta(hours = 10)
    options['session_duration'] = 60

    self.assertRaises(MissingRequiredParameterException, proctorserv.get_available_timeslots_between, options)

  def test_require_session_duration(self):
    """
    raises missing_required_parameter_exception when not passed
    lower_bound, upper_bound, and session_duration in options hash
    """
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                     = collections.OrderedDict()
    options['lower_bound']      = datetime.datetime.utcnow() 
    options['upper_bound']      = datetime.datetime.utcnow() + timedelta(hours = 10)

    self.assertRaises(MissingRequiredParameterException, proctorserv.get_available_timeslots_between, options)

  def test_successful_call(self):
    """returns a list of schedulable timeslots when passed required parameters"""
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    nest = {"nest": 10}

    options                     = collections.OrderedDict()
    options['lower_bound']      = datetime.datetime.utcnow() 
    options['upper_bound']      = datetime.datetime.utcnow() + timedelta(hours = 10)
    options['session_duration'] = 60
    options['AAAAAA']           = json.dumps(nest)

    response = proctorserv.get_available_timeslots_between(options)

    self.assertTrue(len(response) > 0)
    self.assertTrue(isinstance(response, list))


class GetAvailableTimeslotsAroundTest(unittest.TestCase):

  def test_require_session_duration(self):
    """
    raises missing_required_parameter_exception when not passed time,
    num_slots, and session_duration in options hash
    """
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options              = collections.OrderedDict()
    options['time']      = datetime.datetime.utcnow() + timedelta(hours = 10)
    options['num_slots'] = 60

    self.assertRaises(MissingRequiredParameterException, proctorserv.get_available_timeslots_between, options)


  def test_require_num_slots(self):
    """
    raises missing_required_parameter_exception when not passed time,
    num_slots, and session_duration in options hash
    """
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                     = collections.OrderedDict()
    options['time']             = datetime.datetime.utcnow() + timedelta(hours = 10)
    options['session_duration'] = 60

    self.assertRaises(MissingRequiredParameterException, proctorserv.get_available_timeslots_around, options)

  def test_require_time(self):
    """
    raises missing_required_parameter_exception when not passed time,
    num_slots, and session_duration in options hash
    """
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                     = collections.OrderedDict()
    options['session_duration'] = 60
    options['num_slots']        = 4

    self.assertRaises(MissingRequiredParameterException, proctorserv.get_available_timeslots_around, options)

  def test_successful_call(self):
    """returns a list of schedulable timeslots when passed required parameters"""
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                     = collections.OrderedDict()
    options['time']             = datetime.datetime.utcnow() + timedelta(hours = 12)
    options['num_slots']        = 4
    options['session_duration'] = 60

    response = proctorserv.get_available_timeslots_around(options)

    self.assertTrue(len(response) == 4)
    self.assertTrue(isinstance(response, list))


class MakeReservationTest(unittest.TestCase):

  def test_require_time_param(self):
    """raises missing_required_parameter_exception when not all required params are included"""

    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['session_duration']           = 60
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'

    self.assertRaises(MissingRequiredParameterException, proctorserv.make_reservation, options)

  def test_successful_call(self):
    """returns an int value representing session_id when provided a schedulable time and all required parameters"""
    
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['session_duration']           = 60
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'
    options['time']                       = datetime.datetime(2013, 1, 1, 15, 0, 0, 0) 

    response = proctorserv.make_reservation(options)

    self.assertTrue( response > 0)


class MakeImmediateReservationTest(unittest.TestCase):

  def test_require_session_duration_param(self):
    """raises missing_required_parameter_exception when not all required params are included"""

    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'

    self.assertRaises(MissingRequiredParameterException, proctorserv.make_immediate_reservation, options)

  def test_successful_call(self):
    """returns an int value representing session_id when provided a schedulable time and all required parameters"""
    
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['session_duration']           = 60
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'

    response = proctorserv.make_immediate_reservation(options)

    self.assertTrue( response > 0)


class CancelReservationTest(unittest.TestCase):

  def test_require_session_id(self):
    """raises missing_required_parameter_exception when not all required params are included"""

    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")
    options     = collections.OrderedDict()

    self.assertRaises(MissingRequiredParameterException, proctorserv.cancel_reservation, options)

  def test_cancel_when_not_cancellable(self):
    "returns false when passed a session_id that that this client owns that is no longer cancelable"

    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['session_duration']           = 60
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'
    options['time']                       = datetime.datetime(2013, 1, 1, 15, 0, 0, 0) 

    session_id = proctorserv.make_reservation(options)

    options               = collections.OrderedDict()
    options['session_id'] = session_id

   
    self.assertFalse(proctorserv.cancel_reservation(options))

  def test_cancel_when_not_users_session(self):
    """returns false when passed a session_id that doesn't correspond with a session id in the system"""
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options               = collections.OrderedDict()
    options['session_id'] = 2323233
    response = proctorserv.cancel_reservation(options)

    self.assertFalse(response)


  def test_successful_call(self):
    "returns True when passed a session_id that that this client owns and can cancel"

    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['session_duration']           = 60
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'
    options['time']                       = datetime.datetime.utcnow() + timedelta(hours = 2) 

    session_id = proctorserv.make_reservation(options)

    options               = collections.OrderedDict()
    options['session_id'] = session_id

   
    self.assertTrue(proctorserv.cancel_reservation(options))


class GenSecureURLTest(unittest.TestCase):

  def test_require_params(self): 
    """raises missing_required_parameter_exception when not all required params are included"""
    
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")
    options     = collections.OrderedDict()

    self.assertRaises(MissingRequiredParameterException, proctorserv.generate_secure_review_url, options)

  def test_successful_call(self):
    """generate a secure token that can be used to grant temporary access to
       a session for a web browser user to review a session.
    """
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['session_duration']           = 60
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'
    options['time']                       = datetime.datetime.utcnow() + timedelta(hours = 2)

    session_id            = proctorserv.make_reservation(options)
    options               = collections.OrderedDict()
    options['session_id'] = session_id
    options['proctor_id'] = "proctor"
    url = proctorserv.generate_secure_review_url(options)

    self.assertEqual(url[-1] , session_id[-1])


class CreateSessionEventTest(unittest.TestCase):

  def test_require_params(self): 
    """raises missing_required_parameter_exception when not all required params are included"""
    
    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")
    options     = collections.OrderedDict()

    self.assertRaises(MissingRequiredParameterException, proctorserv.create_session_event, options)

  def test_successful_call(self):
    """returns true if it generates a session event for a testing session if options hash contains correct values"""

    proctorserv = ProctorservApi("test", "shared_secret", 'http', "localhost:3000")

    options                               = collections.OrderedDict()
    options['customer_subject_id']        = 'c_sub_1'
    options['customer_client_subject_id'] = 'c_c_sub_1'
    options['client_code']                = 'c_code'
    options['reservation_id']             = 'res_id'
    options['session_duration']           = 60
    options['exam_code']                  = 'e-code-15a'
    options['first_name']                 = 'Ryan'
    options['last_name']                  = 'last'
    options['complete_url']               = 'http://www.techcrunch.com'
    options['time']                       = datetime.datetime.utcnow() + timedelta(hours = 2)

    session_id = proctorserv.make_reservation(options)

    options               = collections.OrderedDict()
    options['session_id'] = session_id
    options['event_type'] = "Finshed Test"

    response = proctorserv.create_session_event(options)

    self.assertTrue(response)

class DataRetrievalsTest(unittest.TestCase):


  def test_successful_call(self):
    """returns true if it generates a session event for a testing session if options hash contains correct values"""

    proctorserv = ProctorservApi("Test", "shared_secret", 'http', "localhost:3000")
    options     = collections.OrderedDict()

    options               = collections.OrderedDict()
    options['ids']        = [1540]
    options["elements"]   = ['review_url','video_url']
    options["test"]       = collections.OrderedDict([('apple',4), ('pear',2)])
    options["boolean"]    = False  
    

    response = proctorserv.data_retrievals(options)
    get_id   = response["data_retrieval"][0]["data_retrieval"]["id"]

    self.assertEqual(get_id, 1540)

class DataDeletionsTest(unittest.TestCase):


  def test_successful_call(self):
    """returns true if it generates a session event for a testing session if options hash contains correct values"""

    proctorserv = ProctorservApi("Test", "shared_secret", 'http', "localhost:3000")

    options        = collections.OrderedDict()
    options['ids'] = [1540]
    

    response = proctorserv.data_deletions(options)

    self.assertFalse(response)

class AccessCodeTest(unittest.TestCase):

  def test_successful_get_access_code_call(self):
    """returns true if it generates a session event for a testing session if options hash contains correct values"""

    proctorserv = ProctorservApi("Test", "shared_secret", 'http', "localhost:3000")

    options        = collections.OrderedDict()
    options['session_id'] = 1700
    

    response = proctorserv.get_access_code(options)
    print response
    self.assertFalse(response)

  def test_successful_reset_access_code_call(self):
    """returns true if it generates a session event for a testing session if options hash contains correct values"""

    proctorserv = ProctorservApi("Test", "shared_secret", 'http', "localhost:3000")

    options        = collections.OrderedDict()
    options['session_id'] = 1700
    

    response = proctorserv.reset_access_code(options)
    print response
    self.assertFalse(response)




if __name__ == '__main__':
  unittest.main()