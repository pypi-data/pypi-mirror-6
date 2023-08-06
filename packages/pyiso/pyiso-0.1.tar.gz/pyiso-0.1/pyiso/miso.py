import requests
import copy
from dateutil.parser import parse as dateutil_parse
import pytz
from pyiso.base import BaseClient


class MISOClient(BaseClient):
    def __init__(self):
        self.ba_name = 'MISO'
        
        self.base_url = 'https://www.misoenergy.org/ria/'
        
        self.fuels = {
            'Coal': 'coal',
            'Natural Gas': 'natgas',
            'Nuclear': 'nuclear',
            'Other': 'other',
            'Wind': 'wind',
        }
                
    def _utcify(self, naive_local_timestamp):
        # MISO is always on Eastern Standard Time, even during DST
        # ie UTC offset = -5 always
        aware_local_timestamp = pytz.timezone('America/New_York').localize(naive_local_timestamp, is_dst=False)
        aware_utc_timestamp = aware_local_timestamp.astimezone(pytz.utc)
        aware_utc_timestamp += aware_local_timestamp.dst() # adjust for EST
        return aware_utc_timestamp

    def get_generation(self, latest=False, **kwargs):
        # process args
        request_urls = []
        if latest:
            request_urls.append('FuelMix.aspx?CSV=True')

        else:
            raise ValueError('Latest must be True.')
            
        # set up storage
        raw_data = []
        parsed_data = []

        # collect raw data
        for request_url in request_urls:
            # set up request
            url = copy.deepcopy(self.base_url)
            url += request_url
            
            # carry out request
            response = requests.get(url).text
            
            # test for valid content
            if 'The page cannot be displayed' in response:
                self.logger.error('Error in source data for MISO generation')
                return parsed_data
            
            # preliminary parsing
            rows = response.split('\n')
            header = rows[0].split(',')
            for row in rows[1:]:
                raw_data.append(dict(zip(header, row.split(','))))
            
        # parse data
        for raw_dp in raw_data:
            # process timestamp
            aware_utc_timestamp = self._utcify(dateutil_parse(raw_dp['INTERVALEST']))

            # set up storage
            parsed_dp = {}
            
            # add values
            try:
                parsed_dp['timestamp'] = aware_utc_timestamp
                parsed_dp['gen_MW'] = float(raw_dp['ACT'])
                parsed_dp['fuel_name'] = self.fuels[raw_dp['CATEGORY']]
                parsed_dp['ba_name'] = self.ba_name
                parsed_dp['market'] = self.MARKET_CHOICES.fivemin
                parsed_dp['freq'] = self.FREQUENCY_CHOICES.fivemin
            except KeyError: # blank last line
                continue
            
            # add to full storage
            parsed_data.append(parsed_dp)
            
        return parsed_data
