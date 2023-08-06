import json
import requests

from .exceptions import TrakIOException
from .exceptions import TrakIOServiceException

class TrakIOClient(object):
	def __init__(self, token, base_address='api.trak.io', version=1, secure=True):
		self.token=token
		self.base_url="http{secure}://{address}/v{version}".format(
	    	secure='s' if secure else '',
	    	address=base_address,
	    	version=version
    	)

	def _request(self, method, data):
		target_url="{base_url}/{method}".format(base_url=self.base_url, method=method)

		response=requests.post(
		    url=target_url,
		    data=json.dumps({'data':data}),
		    headers={
		    	'X-TOKEN':self.token,
		    	'Content-Type':'application/json'
	    	},
		    verify=True
		)

		if not 'application/json' in response.headers.get('content-type'):
			raise TrakIOException('Service responded with a non JSON response and a ' + str(response.status_code) + ' status code: ' + response.text)

		response_data=response.json()

		if response_data['status'] == 'error':
			raise TrakIOServiceException(response_data['message'], response_data['exception'], response_data['details'])

		return response_data

	def identify(self, distinct_id, properties):
		return self._request('identify', {
			'distinct_id': distinct_id,
			'properties': properties
		})

	def alias(self, distinct_id, alias):
		return self._request('alias', {
			'distinct_id': distinct_id,
			'alias': alias
		})

	def annotate(self, event, properties=None, channel=None):
		return self._request('annotate', {
			'event': event,
			'channel': 'web_site' if channel is None else channel,
			'properties': {} if properties is None else properties
		})

	def track(self, distinct_id, event, channel=None, properties=None, time=None):
		return self._request('track', {
			'distinct_id': distinct_id,
			'event': event,
			'channel': 'web_site' if channel is None else channel,
			'properties': {} if properties is None else properties
		})