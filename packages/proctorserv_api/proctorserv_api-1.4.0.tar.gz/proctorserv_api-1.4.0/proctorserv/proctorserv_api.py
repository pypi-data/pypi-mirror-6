
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

class ProctorservApi(object):
  """ Creates ProctorservApi instances """
  def __init__(self, api_identifier, shared_secret, service_protocol='https', service_url='service.proctorcam.com'):
    self.api_identifier = api_identifier
    self.service_protocol = service_protocol
    self.service_url = service_url
    self.shared_secret = shared_secret

  # Get a list of schedulable timeslots (represented as Time objects) between two
  # times for a given exam that needs to be scheduled. This API request takes the
  # provided session_duration into account when comparing Proctorserve business hours.
  # The timeslots returned are specific for an exam of duration provided.
  #
  # This method will raise exceptions related to authentication (InvalidClientException, InvalidSignatureException, InvalidIpException) or not providing required data (MissingRequiredParameterException)
  #
  # options = OrderedDict([(String, specified_data_type)]) 
  #   Required:
  #    - 'lower_bound' (DateTime object) - the earlier of two timestamps to find available timeslots between
  #    - 'upper_bound' (DateTime object) - the later of two timestamps to find available timeslots between
  #    - 'session_duration' (string) - is the length in minutes alloted for this examination
  # returns [List<Time>] list of Time objects that represent schedulable timeslots in Proctorserve for an exam of length session_duration between lower_bound and upper_bound
  def get_available_timeslots_between(self, options):
    self.requires_of(options, ['lower_bound', 'upper_bound', 'session_duration'])   
    url = "%s://%s/api/scheduling/get_available_timeslots_between" %(self.service_protocol, self.service_url) 

    options['lower_bound'] = self.convert_times_to_integer(options['lower_bound'])
    options['upper_bound'] = self.convert_times_to_integer(options['upper_bound'])

    rest = RestRequestClient()
    response = rest.make_get_request(url, self.api_identifier, self.shared_secret, options) 

    return self.time_slot_responses(response)
    
  # Get a list of schedulable timeslots (represented as Time objects) around the
  # time for a given exam that needs to be scheduled. This API request takes the
  # provided session_duration into account when comparing Proctorserve business hours.
  # The timeslots returned are specific for an exam of duration provided. At most
  # 20 slots will be returned
  #
  # This method will raise exceptions related to authentication (InvalidClientException, InvalidSignatureException, InvalidIpException) or not providing required data (MissingRequiredParameterException)
  #
  # options = OrderedDict([(String, specified_data_type)]) 
  #   Required:
  #    - 'time' (DateTime object) - time around which to find schedulable slots
  #    - 'num_slots' (string) - number of slots to return
  #    - 'session_duration' (string) - length in minutes alloted for this examination
  # returns [List<Time>] list (length num_slots or 20) of Time objects that represent schedulable timeslots in Proctorserve for an exam of length session_duration around time passed in options hash
  def get_available_timeslots_around(self, options):
    self.requires_of(options, ['time', 'num_slots', 'session_duration'])
    url = "%s://%s/api/scheduling/get_available_timeslots_around" %(self.service_protocol, self.service_url)

    options['time'] = self.convert_times_to_integer(options['time'])

    rest = RestRequestClient()
    response = rest.make_get_request(url, self.api_identifier, self.shared_secret, options) 

    return self.time_slot_responses(response)

  # get_access_code
  #   Will return a object containing access code and its expiration date time based
  #   on a session ID provided in the request
  #
  #   required parameters:
  #   - session_id     Integer
  #
  def get_access_code(self, options):
    self.requires_of(options, ['session_id'])
    url = "%s://%s/api/access_code/get_access_code" %(self.service_protocol, self.service_url)

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options) 

    return self.get_access_code_responses(response)

  # reset_access_code
  #   Will return an object containing new access code for a session
  #   based on a session ID provided in the request
  #
  #   required parameters:
  #   - session_id     Integer
  #
  def reset_access_code(self, options):
    self.requires_of(options, ['session_id'])
    url = "%s://%s/api/access_code/reset_access_code" %(self.service_protocol, self.service_url)

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options) 

    return self.reset_access_code_responses(response)




  ## data_retrievals
  #
  #   Will return data associated with a list of sessions. 
  #   The information returned is dependant on the elements
  #   provided in the request
  #
  #   required parameters:
  #     - ids (session id's you would like to obtain data from)                        - Array of IDs (string)
  #     - elements (the type of data that you would like to retrieve for each session) - Array of elements (string)
  #
  #   optional elements:     Select one or more elements to receive data, if left blank no data will be returned
  #     - review_url         (url to proctorcam to review the past session)
  #     - video_url          (url to download the sessions video)
  #     - id_photo_url       (url to download the photo of the id provided by the sessions test taker)
  #     - headshot_photo_url (url to download the photo of test taker)
  #     - session_activity   (an array of all session events associated with the session)
  #
  #    example:
  #     - params = {"ids" => ["393", "392"], "elements" => ["id_photo_url", "headshot_photo_url", "session_activity", "video_url"]}
  #
  def data_retrievals(self,options):
    self.requires_of(options, ['ids', 'elements'])
    url = "%s://%s/api/data_retrievals/sessions" %(self.service_protocol, self.service_url)

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options)

    return self.data_retrievals_response(response)

  ## dataDeletions
  #
  #   Will delete all identifying data associated with a set of sessions
  #   that are scoped to the smallest possible set by any of the following parameters
  #   optional parameters:
  #     - ids (only delete from this list) eg [123,124,125]
  #     - customer_subject_id (only delete sessions associated with a customer's subject id)
  #     - customer_client_subject_id (only delete sessions associated with a customer's client's subject id)
  #     - client_code (API identifier for customer client)
  #     - exam_code
  #     - lower_bound - UTC Datetime Object (UTC seconds since epoch after which to delete sessions by reservation time. Defaults to 0)
  #     - upper_bound - UTC Datetime Object (UTC seconds since epoch before which to delete sessions by reservation time.
  #                                          Defaults to max 32 bit unsigned int)
  #
  #   Note that if no parameters are passed, no sessions will be deleted.
  #
  #   returns an array of session ids that were successfully deleted 
  #
  def data_deletions(self, options):
    url = "%s://%s/api/data_deletions/sessions" %(self.service_protocol, self.service_url)

    # API accepts UTC Datetime Object so we must convert it to 
    # UTC seconds as that is what is required by the proctorserve api

    if options.has_key('lower_bound'):
      options['lower_bound'] = self.convert_times_to_integer(options['lower_bound']) 
    
    if options.has_key('upper_bound'):
      options['upper_bound'] = self.convert_times_to_integer(options['upper_bound']) 

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options)

    return self.data_deletions_response(response)


  # Makes a reservation for a session if the time passed in options is a schedulable time.
  #
  # This method will raise exceptions related to authentication (InvalidClientException, InvalidSignatureException, InvalidIpException) or not providing required data (MissingRequiredParameterException)
  #
  # options = OrderedDict([(String, specified_data_type)]) 
  #   Required:
  #    - 'time' (DateTime object) - Scheduable time for examination, as obtained by get_available_timeslots_between or get_available_timeslots_around
  #    - 'customer_subject_id' (String) - Unique identifier in API customer's system for the person taking this exam
  #    - 'customer_client_subject_id' (String) - Unique identifier in API customer's client's system for the person taking this exam
  #    - 'client_code' (String) - Unique identifier for API customer's client
  #    - 'reservation_id' (String) - Unique identifier representing this exam instance in API customer's system
  #    - 'session_duration' (Integer) - Session length in minutes
  #    - 'exam_code' (String) - Unique identifier representing the group of exams this specific exam instance belongs to
  #   Optional:
  #    - 'complete_url' (String) - URL that the candidate is redirected to after exam completion
  #    - 'first_name' (String) - First name of the candidate taking the exam
  #    - 'last_name' (String) - Last name of the candidate taking the exam
  # returns [Integer] session_id - the Proctorserve id for the created session. Will return -1 if the time passed is not schedulable.
  def make_reservation(self, options):
    self.requires_of(options, ['time', 'customer_subject_id', 'customer_client_subject_id', 'client_code', 'reservation_id', 'session_duration', 'exam_code'])
    url = "%s://%s/api/scheduling/make_reservation" %(self.service_protocol, self.service_url)

    options['time'] = self.convert_times_to_integer(options['time'])

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options)

    return self.reservation_responses(response)

  # Makes a reservation for a session if now is a schedulable time.
  #
  # This method will raise exceptions related to authentication (InvalidClientException, InvalidSignatureException, InvalidIpException) or not providing required data (MissingRequiredParameterException)
  #
  # options = OrderedDict([(String, specified_data_type)]) 
  #   Required:
  #    - 'customer_subject_id' (String) - Unique identifier in API customer's system for the person taking this exam
  #    - 'customer_client_subject_id' (String) - Unique identifier in API customer's client's system for the person taking this exam
  #    - 'client_code' (String) - Unique identifier for API customer's client
  #    - 'reservation_id' (String) - Unique identifier representing this exam instance in API customer's system
  #    - 'session_duration' (Integer) - Session length in minutes
  #    - 'exam_code' (String) - Unique identifier representing the group of exams this specific exam instance belongs to
  #   Optional:
  #    - 'complete_url' (String) - URL that the candidate is redirected to after exam completion
  #    - 'first_name' (String) - First name of the candidate taking the exam
  #    - 'last_name' (String) - Last name of the candidate taking the exam
  # returns [Integer] session_id - the Proctorserve id for the created session. Will return -1 if the time passed is not schedulable.
  def make_immediate_reservation(self, options):
    self.requires_of(options, ['customer_subject_id', 'customer_client_subject_id', 'client_code', 'reservation_id', 'session_duration', 'exam_code'])
    url = "%s://%s/api/scheduling/make_immediate_reservation" %(self.service_protocol, self.service_url)
    options['time'] = int(time.time())

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options)

    return self.reservation_responses(response)

  # Cancels a reservation for a specific session_id. A session is no longer cancelable if it has already begun or the scheduled time has passed.
  #
  # This method will raise exceptions related to authentication (InvalidClientException, InvalidSignatureException, InvalidIpException) or not providing required data (MissingRequiredParameterException)
  #
  # options = OrderedDict([(String, Integer)]) 
  #   Required:
  #    - 'session_id' (Integer) Proctorserve id for the session to be canceled
  # returns [Boolean] whether or not the exam was successfully canceled.
  def cancel_reservation(self, options):
    self.requires_of(options, ["session_id"])
    url = "%s://%s/api/scheduling/cancel_reservation" %(self.service_protocol, self.service_url)

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options)

    return self.cancellation_reponse(response)

  # Generate a secure token that can be used to grant temporary jsonp access to a session for a web browser user to take a session.
  #
  # options = OrderedDict([(String, specified_data_type)]) 
  #   Required:
  #    - 'session_id' (string) Proctorserve id for the session to grant access to
  #   Optional:
  #    - 'duration' (Integer) Number of minutes to grant access for (defaults to 1 hour, maximum 3 hours)
  # returns [String] the jsonp token
  def generate_jsonp_token(self, options):
    self.requires_of(options, ['session_id'])
    options['time'] = int(time.time())
    options['duration'] = self.determine_jsonp_duration(options)

    HashedAuthenticator.apply_reverse_guid_and_sign(options, self.api_identifier, self.shared_secret)
    combined_options = self.combine_options(options)
    
    return '%26'.join(combined_options)

  # Generate a secure token that can be used to grant temporary access to a session for a web browser user to review a session.
  # Can be loaded in an iframe or a new window to grant secure access to a single user for a specified period of time
  #
  # options = OrderedDict([(String, specified_data_type)]) 
  #   Required:
  #    - 'session_id' (String) Proctorserve id for the session to grant review access to
  #    - 'proctor_id' (String) unique identifier representing the user to grant access to. This will determine the user's display name in Proctorserve interfaces.
  #   Optional:
  #    - 'duration' (Integer) Number of minutes link stays active for (defaults to 5 minutes)
  #   returns [String] a URL to review the session
  def generate_secure_review_url(self, options):
    self.requires_of(options, ['proctor_id', 'session_id'])
    options['time'] = int(time.time())
    options['duration'] = self.determine_review_duration(options)

    HashedAuthenticator.apply_reverse_guid_and_sign(options, self.api_identifier, self.shared_secret)
    combined_options = self.combine_options(options)

    return '%s://%s/review?secure_token=' %(self.service_protocol, self.service_url) + '%26'.join(combined_options) + '#watch/%s' %options['session_id']
    
  # Generate a session event for a testing session.
  #
  # options = OrderedDict([(String, specified_data_type)]) 
  #   Required:
  #    - 'session_id' (int) - Proctorserve id for the session the event will be added to
  #    - 'event_type'(String) The event to be added, acceptable events are contained in SessionEvent.rb
  #   Optional:
  #    - 'proctor_id' (String) - Unique identifier representing the user to grant access to. This will determine the user's display name in Proctorserve interfaces.
  #    - 'time' (String) (Time or int seconds since epoch) Date and Time that the session event happened at
  #    - 'severity' (int) (Defaults to 0) The severity of the session_event being created.
  #      - 0: Lowest severity
  #      - 1: Highest Severity, may be used for events like exam revoked or emergency.
  #      - 2: Medium Severity, the session needs to be reviewed.
  #      - 3: Low Severity, common events like going through the system check.
  #  @return [Boolean] whether or not the session event was successfully created.  
  def create_session_event(self, options):
    self.requires_of(options, ['session_id', 'event_type'])
    options['time'] = self.convert_times_to_integer(datetime.datetime.utcnow())
    url = '%s://%s/api/session_events/create' %(self.service_protocol, self.service_url)

    rest = RestRequestClient()
    response = rest.make_post_request(url, self.api_identifier, self.shared_secret, options) 

    return self.session_event_response(response)
    
  
  def raise_exception_if_necessary(self, response):
    """ parses through an http response for error messages and raises appropriate exception """
    error_message = str(response['message'])
    if error_message == 'Not a valid client':
      raise InvalidClientException("The api_identifier for this instance of ProctorservApi does not match up with any for the service.")
    elif error_message == 'Signature hash is invalid':
      raise InvalidSignatureException("Authentication failed for the ProctorservApi request. It is most likely that the shared_secret does not match up with the Proctorserve record for your API client.")
    elif error_message == "Request coming from invalid IP":
      raise InvalidIpException("Authentication failed for the ProctorservApi request because the IP address of this machine is not whitelisted for this API client in Proctorserve.")

  
  def requires_of(self, dictionary, req_arguments): 
    """ verifies that the required parameters are included with each http request """
    for list_item in req_arguments:
      if list_item not in dictionary:
        raise MissingRequiredParameterException("%s is a required parameter" %list_item)
    

  def combine_options(self, options):
    """ helper function that joins keys and values from a dictoinary to be used later """ 
    combined_options = []
    for key, value in options.iteritems():
      combined_options.append(key + '%3D' + str(value))
    return combined_options
    


  def convert_times_to_integer(self, time):
    """ converts a datetime object to seconds past epoch """
    time_tuple = time.utctimetuple()
    time = int(calendar.timegm(time_tuple))
    
    return time


  def time_slot_responses(self, response):
    """ parses through an http response for timestamps and returns them in a list """
    parsed_response = response.json()
    if response.status_code != 200:   
      self.raise_exception_if_necessary(parsed_response)
    else:
      timestamps = []

      for timestamp in parsed_response:
        timestamps.append(datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))

    return timestamps


  def reservation_responses(self, response):
    """ parses through an http response, returns
        test takers session ID or raises an exception """
    parsed_response = response.json()
    
    if response.status_code == 200: 
      return str(parsed_response["session_id"])
    elif response.status_code == 404:
      return -1 
    else:
      self.raise_exception_if_necessary(parsed_response)

  def data_retrievals_response(self, response):
    """ parses through an http response, returns
    requested session information or raises an exception """
    parsed_response = response.json()
    
    if response.status_code == 200: 
      return parsed_response
    else:
      self.raise_exception_if_necessary(parsed_response)

  def data_deletions_response(self, response):
    """ parses through an http response, returns
    session ids associated with deleted session data or raises an exception """
    parsed_response = response.json()

    if response.status_code == 201:
      return parsed_response
    else:
      self.raise_exception_if_necessary(parsed_response)

  def get_access_code_responses(self, response):
    """ parses through an http response, returns a 
    access_code, error message, or raises an exception """
    parsed_response = response.json()

    if response.status_code != 200:  
      return self.raise_exception_if_necessary(parsed_response)
    elif "message" in parsed_response:
      return parsed_response
      
    return parsed_response["access_code"]

  def reset_access_code_responses(self, response):
    """ parses through an http response, returns a new
    access_code, error message, or raises an exception """
    parsed_response = response.json()

    if response.status_code != 200:  
      return self.raise_exception_if_necessary(parsed_response)
    elif "message" in parsed_response:
      return parsed_response
     
    return parsed_response["access_code"]


  def cancellation_reponse(self, response):
    """ parses through an http response, returns confirmation
        of session cancellation or raises an exception """
    if response.status_code == 204:  
      return True
    elif response.status_code != 200:
      parsed_response = response.json()
      self.raise_exception_if_necessary(parsed_response)
    
    return False


  def session_event_response(self, response):
    """ parses through an http response, returns confirmation 
        of a session event creation or raises an exception """
    parsed_response = response

    if response.status_code == 201:  
      return True
    elif response.status_code != 200: 
      self.raise_exception_if_necessary(parsed_response)
    else:
      return False


  def determine_jsonp_duration(self, options):
    """ determines the amount of time (in minutes) a user has 
        access to a link which grants access a proctoring session  """
    if options.get("duration") == None:  
      return 60
    if options.get("duration") > 180:
      return 180
    if options.get("duration") <= 180:
      return int(options["duration"])


  def determine_review_duration(self, options):
    """ determines the amount of time (in minutes) a user has 
        access to a link to review a session """
    if options.get("duration") == None: 
      return 5
    if options.get("duration") > 180:
      return 180
    if options.get("duration") <= 180:
      return options["duration"]