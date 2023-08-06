import urllib, requests, json

from errors import NoApiTokenProvidedException, MissingArgumentException

"""
Fosbury Python Client
"""

__version__ = '0.9.6.1'
__author__ = 'Willem Spruijt <willem@fosbury.co>'

class Client():
    """Initialize the Fosbury client"""
    def __init__(self, api_token=None, endpoint=None):
      self.api_token = api_token
      self.endpoint = "https://app.fosbury.co/api/v1/" if endpoint == None else endpoint

    def get_templates(self):
      return self.get("templates")
    
    def get_campaigns(self):
      return self.get("campaigns")
    
    def get_passes(self):
      return self.get("passes")
    
    def get_template(self, id):
      return self.get("templates/" + str(id))
    
    def get_campaign(self, id):
      return self.get("campaigns/" + str(id))
    
    def get_pass(self, id):
      return self.get("passes/" + str(id))

    def create_template(self, name, style, options={}):
      options['name'] = name
      options['style'] = style

      return self.post("templates", options)

    def create_campaign(self, template_id, options={}):
      options['template_id'] = template_id
      return self.post("campaigns", options)

    def create_pass(self, campaign_id, options={}):
      if campaign_id is None:
        raise MissingArgumentException('Please provide a campaign_id')

      options['campaign_id'] = campaign_id
      return self.post("passes", options)

    def update_template(self, template_id, options={}):
      if template_id is None:
        raise MissingArgumentException('Please provide a template_id')

      return self.put("tempates/" + template_id, options)

    def update_campaign(self, campaign_id, options={}):
      if campaign_id is None:
        raise MissingArgumentException('Please provide a campaign_id')

      return self.put("campaigns/" + campaign_id, options)

    def update_pass(self, pass_id, options={}):
      if pass_id is None:
        raise MissingArgumentException('Please provide a pass_id')

      return self.put("passes/"+ str(pass_id), options)

    def delete_template(self, teplate_id):
      return self.delete("tempates/" + str(template_id))

    def delete_campaign(self, campaign_id):
      return self.delete("campaigns/" + str(template_id))

    def delete_pass(self, pass_id):
      return self.delete("passes/" + str(pass_id))

    def push_pass(self, pass_id, options={}):
      return self.put("passes/" + str(pass_id) + "/push", options)
  
    def archive_pass(self, pass_id):
      return self.post("passes/" + str(pass_id) + "/archive", {})

    def redeem_pass(self, pass_id):
      return self.post("passes/" + str(pass_id) + "/redeem", {})

    def distribute_campaign(self, campaign_id):
      return self.post("campaigns/" + str(campaign_id) + "/distribute")
    
    def get_campaign_locations(self, campaign_id):
      return self.get("/campaigns/" + str(campaign_id) + "/locations")

    def create_campaign_location(self, campaign_id, lat, lng, name, relevant_text, address=''):
      options = { 'campaign_id': campaign_id, 'lat': lat, 'long': lng, 'name': name, 'address': address, 'relevant_text': relevant_text }
      return self.post("campaigns/" + str(campaign_id) + "/locations", options)
    
    def delete_campaign_location(self, campaign_id, location_id):
      return self.delete("campaigns/" + str(campaign_id) + "/locations/" + str(location_id))
    
    def get_campaign_backfields(self, campaign_id):
      return self.get("campaigns/" + str(campaign_id) + "/backfields")
    
    def create_campaign_backfield(self, campaign_id, title, description):
      options = { 'title': title, 'description': description }
      return self.post("campaigns/" + str(campaign_id) + "/backfields", options)
    
    def delete_campaign_backfield(self, campaign_id, backfield_id):
      return self.delete("campaigns/" + str(campaign_id) + "/backfields/" + str(backfield_id))

    def get_campaign_beacons(self, campaign_id):
      if campaign_id is None:
        raise MissingArgumentException('Please provide a campaign_id')
      return self.get("campaigns/"+ str(campaign_id) + "/ibeacons")
    
    def create_campaign_beacon(self, campaign_id, proximity_uuid, relevant_text, major=None, minor=None):
      if campaign_id is None:
        raise MissingArgumentException('Please provide a campaign_id')

      options = { 'campaign_id': campaign_id, 'proximity_uuid': proximity_uuid, 'relevant_text': relevant_text}

      if major is not None:
        options['major'] = major

      if minor is not None:
        options['minor'] = minor

      return self.post("campaigns/" + str(campaign_id) + "/ibeacons", options)
    
    def delete_campaign_beacon(self, campaign_id, beacon_id):
      if campaign_id is None:
        raise MissingArgumentException('Please provide a campaign_id')
      if beacon_id is None:
        raise MissingArgumentException('Please provide a beacon_id')
      
      return self.delete("campaigns/" + str(campaign_id) + "/ibeacons/" + str(beacon_id))
    
    def get_programs(self):
      return self.get("programs")
    
    def get_program(self, id):
      return self.get("programs/" + str(id))
    
    def update_program(self, program_id, options={}):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      return self.put("programs/" + str(campaign_id), options)
        
    def push_program(self, program_id, options={}):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      return self.post("programs/" + str(program_id) + "/push_message", options)
    
    def get_program_members(self, program_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      return self.get("programs/" + str(program_id) + "/members")
    
    def get_program_member(self, program_id, member_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      if member_id is None:
        raise MissingArgumentException("Please provide a")

      return self.get("programs/" + str(program_id) + "/members/" + str(program_id))
    
    def create_program_member(self, program_id, customer_number, first_name, last_name):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      if customer_number is None:
        raise MissingArgumentException("Please provide a customer_number")

      if first_name is None:
        raise MissingArgumentException("Please provide a first_name")

      if last_name is None:
        raise MissingArgumentException("Please provide a last_name")

      options = { 'customer_number': customer_number, 'first_name': first_name, 'last_name': last_name}

      return self.post("programs/" + str(pogram_id) + "/members", options)
    
    def update_program_member(self, program_id, member_id, customer_number, first_name, last_name, email=nil):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      if member_id is None:
        raise MissingArgumentException("Please provide a")

      if customer_number is None:
        raise MissingArgumentException("Please provide a customer_number")

      if first_name is None:
        raise MissingArgumentException("Please provide a first_name")

      if last_name is None:
        raise MissingArgumentException("Please provide a last_name")

      options = { 'customer_number': customer_number, 'first_name': first_name, 'last_name': last_name, 'email': email}

      return self.put("programs/" + str(program_id) + "/members/" + str(member_id), options)
    
    def delete_program_member(self, program_id, member_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      if member_id is None:
        raise MissingArgumentException("Please provide a")

      return self.delete("programs/" + str(program_id) + "/members/" + str(member_id))
    
    def get_program_locations(self, program_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      return self.get("programs/" + str(program_id) + "/locations")
    
    def create_program_location(self, program_id, lat, long, name, relevant_text, address=''):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      options = { 'program_id': program_id, 'lat': lat, 'long': long, 'name': name, 'address': address, 'relevant_text': relevant_text }
      return self.post("programs/" + str(program_id) + "/locations", options)
    
    def delete_program_location(self, program_id, location_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      if location_id is None:
        raise MissingArgumentException("Please provide a location_id")
        
      return self.delete("programs/" + str(program_id) + "/locations/" + str(location_id))
    
    def get_program_backfields(self, program_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      return self.get("programs/ " + str(program_id) + " /backfields")
    
    def create_program_backfield(self, program_id, title, description):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      options = { title: title, description: description }
      return self.post("programs/" + str(program_id) + "/backfields", options)
    
    def delete_program_backfield(self, program_id, backfield_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      if backfield_id is None:
        raise MissingArgumentException("Please provide a backfield_id")

      return self.delete("/programs/" + str(program_id) + "/backfields/" + str(backfield_id))
    
    def get_program_beacons(self, program_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      return self.get("/programs/" + program_id + "/ibeacons")
    
    def create_program_beacon(self, program_id, proximity_uuid, relevant_text, major=None, minor=None):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      options = { 'program_id': program_id, 'proximity_uuid': proximity_uuid, 'relevant_text': relevant_text}
      
      if major is not None:
        options['major'] = major

      if minor is not None:
        options['minor'] = minor

      return self.post("programs/" + str(program_id) + "/ibeacons", options)
    
    def delete_program_beacon(self, program_id, beacon_id):
      if program_id is None:
        raise MissingArgumentException("Please provide a program_id")

      if beacon_id is None:
        raise MissingArgumentException("Please provide a beacon_id")

      return self.delete("/programs/" + str(program_id) + "/ibeacons/" + str(beacon_id))

    # Rest calls
    def get(self, url):
      r = requests.get(self.endpoint + url, headers=self.get_headers())
      return self.parse_json(r)

    def post(self, url, post_params):
      r = requests.post(self.endpoint + url, data=self.construct_payload(post_params), headers=self.get_headers())
      return self.parse_json(r)

    def put(self, url, post_params):
      r = requests.put(self.endpoint + url, data=self.construct_payload(post_params), headers=self.get_headers())
      return self.parse_json(r)

    def delete(self, url):
      r = requests.delete(self.endpoint + url, headers=self.get_headers())
      return self.parse_json(r)

    def construct_payload(self, params):
      return urllib.urlencode(params)

    def get_headers(self):
      if self.api_token is None:
        raise NoApiTokenProvidedException("No authentication token provided.") 
      return {'X-Fosbury-Token': self.api_token}

    def parse_json(self, response_object):
      if len(response_object.text.strip()) is not 0:
        return response_object.json()
      else:
        return json.dumps({})