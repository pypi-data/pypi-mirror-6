# -*- coding: utf-8 -*-
import json, logging, platform

from nap.url import Url

from gestus_client import __version__ as client_version
from gestus_client import logging_handler, egg_finder

ENVIRONMENT_KIND_CHOICES = (
    ('integration', 'Integration'),
    ('production', 'Production'),
)

## The Following part is duplicated from nap.url because it is required to override 
## the ``JsonApi._new_url`` stuff
#import sys

#_PY3 = sys.version_info >= (3, 0)

## For Python 3 compatibility
#if _PY3:
    #from urllib.parse import urljoin
#else:
    #from urlparse import urljoin

#class JsonApi(Url):
    #"""
    #Fork and pull request 'nap' to push the enhances when done
    #"""
    ##def after_request(self, response):
        ##"""
        ##Doesn't used until i find how i can add an option to permit to not 
        ##allways return the Json response, sometime it will be needed to 
        ##have something like the raw() response
        ##"""
        ##if response.status_code != 200:
            ##response.raise_for_status()

        ##return response.json()

    #def _new_url(self, relative_url):
        #"""
        #Create new Url which points to new url.
        
        #TODO : We should find a way to change the used class and not hardcoded 
        #like this
        #"""
        #return JsonApi(
            #urljoin(self._base_url, relative_url),
            #**self._default_kwargs
        #)

class GestusClient(object):
    """
    
    TODO: * Use a decorator to check _connected for some class methods (like register)
          * Write ``gestus.conf`` INI file to store paramaters config for current project
          * Writing ``gestus.conf`` file is optionnal
    """
    _connected = False
    _websites_map = {}
    
    client_headers = {
        'client_agent': 'gestus-client/{0}'.format(client_version),
        'content-type': 'application/json',
    }
    
    endpoint_eggs_path = 'eggs/'
    endpoint_websites_path = 'websites/'
    endpoint_environments_path = 'environments/'
    
    website_id = None
    website_name = None
    website_url = None
    
    environment_id = None
    environment_name = None
    environment_server = None
    environment_eggs = ''
    
    def __init__(self, root_url, auth_settings, debug_requests=True):
        self.logger = logging.getLogger('gestus_client')
        
        self.root_url = root_url
        self.auth_settings = auth_settings
        
        self.debug_requests = debug_requests
    
    def connect(self, dry_run=False):
        """
        Connecting to endpoints
        """
        #self.api_base = JsonApi(self.root_url, auth=self.auth_settings)
        self.api_base = Url(self.root_url, auth=self.auth_settings)
        
        self.api_endpoint_eggs = self.api_base.join(self.endpoint_eggs_path)
        self.api_endpoint_websites = self.api_base.join(self.endpoint_websites_path)
        self.api_endpoint_environments = self.api_base.join(self.endpoint_environments_path)
        
        # Trying to connect to the base to check if the service is reachable
        if not dry_run:
            self.logger.info("Connecting to Gestus service on: %s", self.root_url)
            response = self.api_base.get()
            if response.status_code != 200:
                response.raise_for_status()
            self.map_websites()
            
        self._connected = True
    
    def map_websites(self):
        """
        Get the websites list and map it to a dict
        """
        self.logger.debug("Getting the website list")
        websites = self.api_endpoint_websites.get().json()

        #print websites.get('results')

        for item in websites.get('results'):
            self._websites_map[item.get('name')] = item
    
    def _post_json(self, endpoint, payload):
        """
        Just a shortcut for endpoint.post to avoid to redo headers, json dump, etc..
        
        ``endpoint`` is the the api endpoint Url (a nap.Url object), payload is the 
        dict of data to POST.
        """
        resp = endpoint.post(data=json.dumps(payload), headers=self.client_headers)
        return resp.json()
    
    def _register_website(self, website_id, name=None, url=None):
        self.website_id = website_id
        self.website_name = name
        self.website_url = url
        self.website_detail_url = self.api_endpoint_websites.join('{0}/'.format(self.website_id))
    
    def _register_environment(self, environment_id, name=None, server=None):
        self.environment_id = environment_id
        self.environment_name = name
        self.environment_server = server
        self.environment_detail_url = self.api_endpoint_environments.join('{0}/'.format(self.environment_id))
    
    def register(self, name, url, environment_name, environment_server=platform.node()):
        """
        Register the website environment
        
        Required arguments:
        
        @name: website name to search or create
        @url: website url to use for creating a new website entry
        @environment_name: website environment name to search or create
        @environment_server: website environment server to use for creating a new environment entry
        """
        # Determine the hostname
        environment_server = environment_server or 'unknow'
        # Get or create the website
        if name not in self._websites_map:
            self.logger.info("Creating new website entry for: {0}".format(name))
            payload = {'name':name, 'url':url, 'enabled':True}
            entry = self._post_json(self.api_endpoint_websites, payload)
        else:
            entry = self._websites_map[name]
            self.logger.debug("Website entry '{0}' allready exists".format(name))
        
        self._register_website(entry['id'], entry['name'], entry['url'])
        
        # Get or create the environment
        finder = lambda x: x['name']==environment_name
        envs = self.website_detail_url.get().json()['environments']
        try:
            environment = filter(finder, envs)[0]
        except IndexError:
            self.logger.info("Creating new environment entry for: {0}".format(environment_name))
            payload = {'name': environment_name, 'server': environment_server, 'website': self.website_id, 'enabled':True}
            environment = self._post_json(self.api_endpoint_environments, payload)
        else:
            self.logger.debug("Environment entry '{0}' allready exists".format(environment_name))
        
        self._register_environment(environment['id'], environment['name'], environment['server'])
        
        return self.website_id, self.environment_id
    
    def register_eggs(self, egg_dir, commit=True):
        """
        Send the installed eggs infos for the registred environment
        """
        self.logger.debug("Scanning for eggs in directory: {0}".format(egg_dir))
        finder = egg_finder.BuildoutEggdirFinder(egg_dir)
        finder.crawl()
        egg_list = finder.render()
        
        if commit:
            self.logger.info("Sending eggs ({0} items)".format(len(finder.eggs)))
            resp = self.environment_detail_url.patch(data=json.dumps({'egg_list': egg_list}), headers=self.client_headers)
        
        return egg_list
    
    def update(self, website_kwargs={}, environment_kwargs={}, egg_dir=None):
        """
        Update a registered website and its environment
        """
        if website_kwargs:
            response = self.website_detail_url.patch(data=json.dumps(website_kwargs), headers=self.client_headers)
            if response.status_code != 200:
                if self.debug_requests:
                    print response.json()
                response.raise_for_status()
        
        # If egg directory is given, add the egg list to the update
        if egg_dir:
            environment_kwargs.update({'egg_list':self.register_eggs(egg_dir, commit=False)})
            
        if environment_kwargs:
            response = self.environment_detail_url.patch(data=json.dumps(environment_kwargs), headers=self.client_headers)
            if response.status_code != 200:
                if self.debug_requests:
                    print response.json()
                response.raise_for_status()
        


# Testing
if __name__ == "__main__":
    API_ROOT_URL = 'http://192.168.0.103:8001/gestus/rest/'

    con = GestusClient(API_ROOT_URL, ('emencia', 'django324'))
    con.connect()

    ## Allready exists
    #con.register('Parrot.com', 'http://foobar.com', 'integration')

    ## New one
    ##con.register('foobar', 'http://foobar.com', 'integration')
    #website_id, environment_id = con.register('extranet', 'http://dev.extranet.emencia.net', 'integration')
    #con.register_eggs('../../../eggs')
    
    # Update an existing website+environment
    con._register_website(4)
    con._register_environment(4)
    
    con.update(
        website_kwargs={
            'name': 'Emencia Extranet'
        },
        environment_kwargs={
            'server': 'cocolapin'
        }, 
        egg_dir='../../../eggs'
    )
