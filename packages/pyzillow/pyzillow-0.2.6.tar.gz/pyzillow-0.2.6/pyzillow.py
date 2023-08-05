import requests
import sys
from requests.exceptions import (ConnectionError, TooManyRedirects, 
                                Timeout, HTTPError)

from xml.etree import cElementTree as ElementTree  # for zillow API

from django.contrib.gis.geos.error import GEOSException

from pyzillowerrors import ZillowError, ZillowFail, ZillowNoResults
from __version__ import VERSION


class ZillowWrapper(object):
    """
    """

    def __init__(self, api_key=None):
        """

        """
        self.api_key = api_key

    def get_deep_search_results(self, address, zipcode):
        """
        GetDeepSearchResults API
        """

        url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm'
        params = {
            'address': address,
            'citystatezip': zipcode,
            'zws-id': self.api_key 
            }
        return self.get_data(url, params)

    def get_updated_property_details(self, zpid):
        """
        GetUpdatedPropertyDetails API
        """
        url = 'http://www.zillow.com/webservice/GetUpdatedPropertyDetails.htm'

        params = {
            'zpid': zpid,
            'zws-id': self.api_key 
            }
        return self.get_data(url, params)

    # @omnimethod
    def get_data(self, url, params):
        """
        """

        try:
            request = requests.get(
                url = url,
                params = params,
                headers = {
                    'User-Agent': 'pyzillow/' + VERSION + ' (Python)'
                })
            print request.url
        except (ConnectionError, TooManyRedirects, Timeout):
            raise ZillowFail

        try:
            request.raise_for_status()
        except HTTPError:
            raise ZillowFail

        try:
            response = ElementTree.fromstring(request.text)
        except ParseError:
            print "Zillow response is not a valid XML" # (%s)" % (params['address'])
            raise ZillowFail

        if not response.findall('response'):
            print "Zillow returned no results" # (%s)" % (params['address'])
            raise ZillowNoResults

        if response.findall('message/code')[0].text is not '0':
            raise ZillowError(int(code)) 
        else:
            return response


class ZillowResults(object):
    """
    """

    attribute_mapping = {}

    def get_attr(self, attr):
        """
        """
        try:
            return self.data.find(self.attribute_mapping[attr]).text
        except AttributeError:
            return None

    def __unicode__(self):
        return self.zillow_id

    if sys.version_info[0] >= 3:  # Python 3
        def __str__(self):
            return self.__unicode__()

    else:  # Python 2
        def __str__(self):
            return self.__unicode__().encode('utf8')

    @property
    def coordinates(self):
        """
        Return a (latitude, longitude) coordinate pair of the current result
        """
        from django.contrib.gis.geos import fromstr
        try:
            return fromstr('POINT(%s %s)' %(self.latitude, self.longitude), srid=4326)
        except GEOSException:
            return None

    @property
    def area_unit(self):
        """
        lotSizeSqFt
        """
        return u'SqFt'

    @property
    def last_sold_price_currency(self):
        """
        lastSoldPrice currency
        """
        return self.data.find(self.attribute_mapping['last_sold_price']).attrib["currency"]


class GetDeepSearchResults(ZillowResults):
    """
    """
    attribute_mapping = {
        'zillow_id':        'result/zpid',
        'home_type':        'result/useCode',
        'home_detail_link': 'result/links/homedetails',
        'graph_data_link':  'result/links/graphsanddata',
        'map_this_home_link': 'result/links/mapthishome',
        'latitude':         'result/address/latitude',
        'longitude':        'result/address/longitude',
        'tax_year':         'result/taxAssessmentYear',
        'tax_value':        'result/taxAssessment',
        'year_built':       'result/yearBuilt',
        'property_size':    'result/lotSizeSqFt',
        'home_size':        'result/finishedSqFt',
        'bathrooms':        'result/bathrooms',
        'bedrooms':         'result/bedrooms',
        'last_sold_date':   'result/lastSoldDate',
        # 'last_sold_price_currency': 'result/lastSoldPrice',
        'last_sold_price':  'result/lastSoldPrice',
    }

    def __init__(self, data, *args, **kwargs):
        """
        #### Creates instance of GeocoderResult from the provided XML data array
        """
        self.data = data.findall('response/results')[0]
        for attr in self.attribute_mapping.__iter__():
            # print 'loading %s > %s' % (attr, self.get_attr(attr))
            try:
                self.__setattr__(attr, self.get_attr(attr))
            except AttributeError:
                print 'AttributeError with %s' %attr

class GetUpdatedPropertyDetails(ZillowResults):
    """
    """
    attribute_mapping = {
        # attributes in common with GetDeepSearchResults
        'zillow_id':        'zpid', 
        'home_type':        'editedFacts/useCode',
        'home_detail_link': 'links/homeDetails',
        'graph_data_link':  '',
        'map_this_home_link': '',
        'latitude':         'address/latitude',
        'longitude':        'address/longitude',
        'tax_year':         '',
        'tax_value':        '',
        'year_built':       'editedFacts/yearBuilt',
        'property_size':    'editedFacts/lotSizeSqFt',
        'home_size':        'editedFacts/finishedSqFt',
        'bathrooms':        'editedFacts/bathrooms',
        'bedrooms':         'editedFacts/bedrooms',
        'last_sold_date':   '',
        # 'last_sold_price_currency': '',
        'last_sold_price':  '',
        # new attributes in GetUpdatedPropertyDetails
        'photo_gallery':    'links/photoGallery',
        'home_info':        'links/homeInfo',
        'year_updated':     'editedFacts/yearUpdated', 
        'floor_material':   'editedFacts/floorCovering', 
        'num_floors':       'editedFacts/numFloors', 
        'basement':         'editedFacts/basement', 
        'roof':             'editedFacts/roof',
        'view':             'editedFacts/view', 
        'parking_type':     'editedFacts/parkingType',
        'heating_sources':  'editedFacts/heatingSources', 
        'heating_system':   'editedFacts/heatingSystem', 
        'rooms':            'editedFacts/rooms', 
        'appliances':       'editedFacts/appliances', 
        'neighborhood':     'neighborhood', 
        'school_district':  'schoolDistrict', 
        'home_description': 'homeDescription', 
    }



    def __init__(self, data, *args, **kwargs):
        """
        #### Creates instance of GeocoderResult from the provided XML data array
        """
        self.data = data.findall('response')[0]
        for attr in self.attribute_mapping.__iter__():
            # print 'loading %s > %s' % (attr, self.get_attr(attr))
            try:
                self.__setattr__(attr, self.get_attr(attr))
            except AttributeError:
                print 'AttributeError with %s' %attr





