Description.
------------

This library uses yql queries to get the weather from Yahoo.

Installation.
-------------

The easy way to install is:


    pip install pyql-weather

or

Download the pyql-weather-0.1.tar.gz file, decompress it, and run:


    python setup.py install


Examples:
=========

Here we have 2 ways to use this library.

Example 1.
----------
::

    from pyql.weather.models import Weather
    # Pass the WOEID:
    w = Weather(24553062)
    # Read the results:
    print "Temperatura: %sc. Estatus: (%s) %s"%(w.get_temperature(), w.get_status_code(), w.get_status_text())


Example 2.
----------
::

    from pyql.weather.models import Weather, GeoData
    # Get an GeoData object passing latitude and longitude:
    latitude = "20.982994"
    longitude = "-89.617710"
    geo = GeoData(latitude, longitude) # Inicializamos el objeto
    # Pass the WOEID:
    w = Weather(geo.get_woeid())
    # Read the results:
    print "Temperatura: %sc. Estatus: %s"%(w.get_temperature(), w.get_status_text())


=======
Author:
=======

Alex Dzul. 
Python & Django Developer.


1. http://alexdzul.como
2. http://github.com/alexdzul
3. http://twitter.com/alexjs88






