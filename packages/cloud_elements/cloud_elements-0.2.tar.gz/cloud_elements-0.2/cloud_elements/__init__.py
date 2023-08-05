import requests
import json
import urllib

'''
This class is a wrapper around the elements api, similiar to the ElementsConnector
Java class shown in the docs.
'''
class ElementsConnector():
    def __init__(self, API_ENDPOINT='https://console.cloud-elements.com/elements/api-v1'):
        self.API_ENDPOINT = API_ENDPOINT # Api endpoint to use, defaults to localhost:8081 for now
        self.session = requests.Session() # Request session object to send http requests

    '''
    This method construct the complete url for the current request
    '''
    def _construct_url(self, providerName, providerVersion, apiMethodName, params):
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
    This method send the http request using the url constructed by the user.
    It determines if it's a GET or POST request by the existence of a payload.
    '''
    def _request(self, httpMethod, url, payload, files):
        if files:
            file_dict = {}
            for f in files:
                file_dict[f] = (f, open(f, 'rb'))
        if payload and files:
            req = self.session.request(httpMethod, url, files=file_dict, data=payload)
        elif payload:
            req = self.session.request(httpMethod, url, data=json.dumps(payload))
        elif files:
            req = self.session.request(httpMethod, url, files=file_dict)
        else:
            req = self.session.request(httpMethod, url)
        return self._process_request(req)

    '''
    This is the method exposed to the users. It invokes the elements API using all of the parameters
    sent by the user. It constructs the url, sets the http request headers, calls the request method
    and returns the json response, if any.
    '''
    def invoke(self, httpMethod, providerName, elementToken, apiMethodName, providerVersion='1', params=None, payload=None, files=None):
        # Construct the url using the necessary parameters
        url = self._construct_url(providerName, providerVersion, apiMethodName, params)

        # Update the headers to include the elementToken
        elementToken = 'Element %s' % elementToken
        headers = {
            'Authorization': elementToken,
        }
        self.session.headers = dict(self.session.headers.items())
        self.session.headers.update(dict(headers.items()))

        # Return the json response of the request
        return self._request(httpMethod, url, payload, files)


