import json
import os

import zillowpy

# Where the Zillow API lives
ZILLOW_URL = "http://www.zillow.com/webservice/{0}.htm?{1}"

# JSON object of support Zillow API calls
ZILLOW_API = None

try:
    directory = os.path.dirname(os.path.realpath(zillowpy.__file__))
    filepath =  os.path.join(directory, "ZillowAPI.json")
    with open(filepath) as f:
        ZILLOW_API = json.load(f)
except Exception as e:
    print("Can't open/read ZillowAPI.json")
    raise


if __name__ == "__main__":
    print(ZILLOW_API)