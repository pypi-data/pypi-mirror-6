import requests, json

class Client:
    url = 'http://api.geocod.io/v1'
    api_key = ''

    def __init__(self, api_key):
        """ Initialize the class, setting the api_key to the class property """
        self.api_key = api_key

    def geocode(self, data):
        """ Clean facade for using the class """
        if type(data) is str:
            return self.get_address(data)
        elif type(data) is list:
            return self.bulk_post(data)
        else:
            raise InputError('Data must be either string or list')

    def bulk_post(self, data):
        """ The batch processing method requires the data to be submitted as a POST requests
            with the content-type set as application/json and the POST body to be a JSON array."""
        path = '/geocode'
        url = self.url + path + "?api_key=" + self.api_key
        payload = json.dumps(data)
        headers = { 'content-type': 'application/json' }
        return requests.post(url, data=payload, headers=headers)

    def get_address(self, data):
        """ The single address request is dirt-simple.  Just a GET request, with the address
            passed in as a string.  The parameters are urlencoded on the fly by the requests
            class ad the response returned. """
        d = {
            'q': data,
            'api_key': self.api_key
        }
        url = self.url + '/geocode'
        return requests.get(url, params=d)

    def parse(self, address):
        """ The parse method is just as easy, with the only difference being the target URL. """
        d = {
            'q': address,
            'api_key': self.api_key
        }
        url = self.url + '/parse'
        return requests.get(url, params=d)
