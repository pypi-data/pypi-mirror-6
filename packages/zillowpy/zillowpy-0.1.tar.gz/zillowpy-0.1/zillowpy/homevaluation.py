from zillowpy import interface


class HomeValuation(object):
	"""
	Search results list, Zestimate®, Rent Zestimate®, home valuations,
	home valuation charts, comparable houses, and market trend charts.
	"""

	def __init__(self, zws_id):
		self._zws_id = zws_id

	def getZestimate(self, zpid):
		"""
		For a specified Zillow property identifier (zpid), the GetZestimate 
		API returns:

		* The most recent property Zestimate
		* The date the Zestimate was computed
		* The valuation range
	    * The Zestimate ranking within the property's ZIP code.
		* The full property address and geographic location (latitude/longitude)
		  and a set of identifiers that uniquely represent the region (ZIP code,
		  city, county & state) in which the property exists.

		The GetZestimate API will only surface properties for which a Zestimate
		exists. If a request is made for a property that has no Zestimate,
		an error code is returned. Zillow doesn't have Zestimates for all the
		homes in its database. For such properties, we do have tax assessment
		data, but that is not provided through the API. For more information,
		see our Zestimate coverage.

		Parameters:

		- `zpid`: The Zillow Property ID for the property for which to obtain
				  information. The parameter type is an integer.
		
		"""

		api = "GetZestimate"
		param = [("zws-id", self._zws_id),
				 ("zpid", zpid)]
		print(interface.get(api, param))

	def getSearchResults(self, address, citystatezip):
		"""
		"""
		api = "GetSearchResults"
		param = [("zws-id", self._zws_id),
				 ("address", address),
				 ("citystatezip", citystatezip)]
		print(interface.get(api, param))

	def getChart(self, zpid, unit_type, width=None, height=None,
				 chartDuration=None):
		"""
		"""
		api = "GetChart"
		param = [("zws-id", self._zws_id),
				 ("zpid", zpid),
				 ("unit-type", unit_type)]
		if width:
			param.append(("width", width))
		if height:
			param.append(("height", height))
		if chartDuration:
			param.append(("chartDuration", chartDuration))

		print(interface.get(api, param))

	def getComps(self, zpid, count, rentzestimate=False):
		"""
		"""
		api = "GetComps"
		param = [("zws-id", self._zws_id),
				 ("zpid", zpid),
				 ("count", count)]
		if rentzestimate:
			param.append("rentzestimate", rentzestimate)

		print(interface.get(api, param))
