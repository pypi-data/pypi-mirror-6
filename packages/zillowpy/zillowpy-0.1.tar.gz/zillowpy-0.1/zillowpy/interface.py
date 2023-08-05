
import urllib.request

API_URL_FORMAT = "http://www.zillow.com/webservice/{}.htm?{}"

def get(api, param):
	"""
	"""
	reqString = API_URL_FORMAT.format(api, urllib.parse.urlencode(param))
	return urllib.request.urlopen(reqString).read()
