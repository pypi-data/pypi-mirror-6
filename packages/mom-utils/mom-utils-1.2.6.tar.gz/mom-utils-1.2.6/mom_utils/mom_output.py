# -*- coding: utf-8 -*-

class FMSOutput(object):
    """

        - self.keys(): Return a list of all variables available, like
            [...]
        
        - data coverage, min|max dates
        - 

        - self['SSH', 'latitude >= -3 & latitude <= 3']
        - self.filter('latitude'


        3 levels:
          1 - Parse one filem, like 20070101.ocean_transport.nc
          2 - Join related sequential files *.ocean_transport.nc
                Need to guarantee that join in order.
          3 - Join all files from all experiments

        When ask keys on level three it only collects the .keys() from level
          two, which collects the .keys() from level 1.

        Level 1 must keep track of how the data is mapped, i.e. it is
          (time, lon, lat) or (time, lat, lon), and where are the arrays
          that carry the dimension values.
    """
