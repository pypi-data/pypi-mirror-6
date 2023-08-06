import requests
import json
import urllib

'''
This class is a wrapper around the elements api, similiar to the ElementsConnector
Java class shown in the docs.
'''
class ElementsConnector():
    def __init__(self, API_ENDPOINT='https://console.cloud-elements.com/elements/api-v1'):
        self.API_ENDPOINT = API_ENDPOINT # Api endpoint to use
        self.session = requests.Session() # Request session object to send http requests

    '''
    This method construct the complete url for the current request
    '''
    def _construct_url(self, providerName, providerVersion, apiMethodName, params=None):
        if params:
            url = self.API_ENDPOINT+'/'+providerName+'/'+providerVersion+'/'+apiMethodName+'?%s' % urllib.urlencode(params)
        else:
            url = self.API_ENDPOINT+'/'+providerName+'/'+providerVersion+'/'+apiMethodName
        return url

    '''
    This method processes the http request. It currently raises an error in the request object
    if the response can not be parsed as a json object.
    '''
    def _process_request(self, request):
        try:
            return request.json()
        except ValueError:
            return request.raise_for_status()

    '''
    This is a helper method that takes a list of filenames and returns a dictionary that maps each
    filename to a tuple of the form (filename, open(filename)) which is used by the requests package
    to send file over http.
    '''
    def _open_files(self, files=[]):
        file_dict = {}
        for f in files:
            file_dict[f] = (f, open(f, 'rb'))
        return file_dict

    '''
    This method send the http request using the url constructed by the user.
    It sets up file data if necessary.
    '''
    def _request(self, httpMethod, url, payload=None, files=None):
        if not files and not payload:
            if httpMethod.lower() != 'get':
                raise ValueError('httpMethod should be get when no parameteres are present')
            req = self.session.request(httpMethod, url)
            return self._process_request(req)
        if httpMethod.lower() == 'get':
            raise ValueError('httpMethod should not be get with files or parameters present')
        if files:
            file_dict = self._open_files(files)
        if payload and files:
            req = self.session.request(httpMethod, url, files=file_dict, data=payload)
        elif payload:
            req = self.session.request(httpMethod, url, data=json.dumps(payload))
        elif files:
            req = self.session.request(httpMethod, url, files=file_dict)
        return self._process_request(req)

    '''
    This is the method exposed to the users. It invokes the elements API using all of the parameters
    sent by the user. It constructs the url, sets the http request headers, calls the request method
    and returns the json response, if any.
    '''
    def invoke(self, httpMethod, providerName, apiMethodName, providerVersion='1', params=None, payload=None, files=None, headers={}):
        # Construct the url using the necessary parameters
        url = self._construct_url(providerName, providerVersion, apiMethodName, params)

        # Update the headers to include necessary Authorization
        if headers.has_key('elementToken'):
            auth_string = 'Element %s' % headers['elementToken']
        elif headers.has_key('user_secret') and headers.has_key('organization_secret'):
            auth_string = 'User %s, Organization %s' % (headers['user_secret'], headers['organization_secret'])
        self.session.headers['Authorization'] = auth_string

        # Return the json response of the request
        return self._request(httpMethod, url, payload, files)


