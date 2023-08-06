import json

from os.path import isfile
from os.path import expanduser

from zillowpy.request import ZillowRequest
from zillowpy.minify_json import json_minify

class ZillowPyInstantiationError(Exception):
    pass


class Zillow(ZillowRequest):
    def __init__(self, zwsid=None):
        if not zwsid:
            # Read zws-id from ~/.zillowpy
            config_file = expanduser("~") + "/.zillowpy"
            if isfile(config_file):
                with open(config_file) as f:
                    try:
                        zwsid = json.loads(f.read())["zws-id"]
                    except KeyError:
                        raise ZillowPyInstantiationError("No zws-id given")

        self.zwsid = zwsid

    def setup_from_file(self, filepath):
        """
        Pass in criteria for Zillow API access from file.
        """
        with open(filepath) as f:
            json_string = f.read()

        # Strip comments from json file
        json_string = json_minify(json_string)
        json_obj = json.loads(json_string)

        api_call = json_obj["request"]["api_call"]
        param = [("zws-id", self.zwsid)] + list(json_obj["request"]["parameters"].items())
        return api_call, param

    def __call__(self, filepath):
        api_call, param = self.setup_from_file(filepath)
        return super().__call__(api_call, param)


if __name__ == "__main__":
    import zillowpy
    from os.path import dirname, join, realpath
    z = Zillow()
    directory = dirname(realpath(zillowpy.__file__))
    filepath = join(directory, "CriteriaExample.json")
    print(z(filepath))




