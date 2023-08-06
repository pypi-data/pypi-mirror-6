from urllib.parse import urlencode
from urllib.request import urlopen

from zillowpy.common import ZILLOW_URL

class ZillowRequest():
    """
    The ZillowRequest object will interface with the Zillow API.

    Parameters:
        call_obj: A child of any key inside "categories"
        arguments: A list of key-value pairs that complement call_obj
        response_callback: Callback to handle the response
    """
    def __init__(self):
        pass

    def __call__(self, apiCall, param):
        return self.response_callback(self.get(apiCall, param))

    def get(self, apiCall, param):
        """
        """
        reqString = ZILLOW_URL.format(apiCall, urlencode(param))
        return urlopen(reqString).read()

    def response_callback(self, response):
        """
        Redefine
        """
        return response

if __name__ == "__main__":
    from os.path import expanduser, isfile
    import json

    configFile = expanduser("~") + "/.zillowpy"
    if isfile(configFile):
        try:
            with open(configFile) as f:
                zwsid = json.loads(f.read())["zws-id"]
        except IOError:
            print("ERROR: ~/.zillowpy can't be read.", file=sys.stderr)
    else:
        zwsid = input("Enter in your zws-id:")

    zreq = ZillowRequest()
    print(zreq("GetSearchResults", [("zws-id", zwsid),
                                    ("address", "2746 Scottsdale Dr"),
                                    ("citystatezip", "San Jose, CA 95148")]))