================
metoffer v.1.2.0
================

metoffer is a simple wrapper for the API provided by the British
`Met Office <http://www.metoffice.gov.uk>`_ known as DataPoint. It
can be used to retrieve weather observations and forecasts. At its
heart is the ``MetOffer`` class which has methods to retrieve data
available through the API and make them available as Python objects.
Also included are a couple of functions and classes useful for
interpretting the data.

Example
-------

Get forecast for Met Office site closest to supplied latitude and
longitude, the forecast to be given in three-hourly intervals::

	>>> import metoffer
	>>> api_key = '01234567-89ab-cdef-0123-456789abcdef'
	>>> M = metoffer.MetOffer(api_key)
	>>> x = M.nearest_loc_forecast(51.4033, -0.3375, metoffer.THREE_HOURLY)

*It's worth noting here that, if you expect many requests for forecast data
to be made, it is probably better to use the functions called by this
convenience function so that data that does not change often (e.g. data
about Met Office sites) may be cached.*

Parse this data into a ``metoffer.Weather`` instance::

	>>> y = metoffer.parse_val(x)
	>>> y.name
	'HAMPTON COURT PALACE'
	>>> y.country
	'ENGLAND'
	>>> y.continent
	'EUROPE'
	>>> y.lat
	51.4007
	>>> y.lon
	-0.3337
	>>> y.elevation
	4.0
	>>> y.ident # The Met Office site ident
	'351747'
	>>> y.data_date
	'2013-05-16T14:00:00Z'
	>>> y.dtype
	'Forecast'
	>>> import pprint
	>>> pprint.pprint(y.data)
	[{'Feels Like Temperature': (9, 'C'),
	  'Max UV Index': (3, ''),
	  'Precipitation Probability': (1, '%'),
	  'Screen Relative Humidity': (83, '%'),
	  'Temperature': (10, 'C'),
	  'Visibility': ('GO', ''),
	  'Weather Type': (3, ''),
	  'Wind Direction': ('E', 'compass'),
	  'Wind Gust': (11, 'mph'),
	  'Wind Speed': (4, 'mph'),
	  'timestamp': (datetime.datetime(2013, 5, 16, 9, 0), '')},
	 {'Feels Like Temperature': (11, 'C'),
	  'Max UV Index': (4, ''),
	  'Precipitation Probability': (5, '%'),
	
	[...]
	
	  'Wind Direction': ('N', 'compass'),
	  'Wind Gust': (22, 'mph'),
	  'Wind Speed': (11, 'mph'),
	  'timestamp': (datetime.datetime(2013, 5, 20, 21, 0), '')}]

Interpret the data further::

	>>> for i in y.data:
	...     print('{} - {}'.format(i['timestamp'][0].strftime('%d %b, %H:%M'), metof
	fer.WEATHER_CODES[i['Weather Type'][0]]))
	... 
	16 May, 09:00 - Partly cloudy (day)
	16 May, 12:00 - Partly cloudy (day)
	16 May, 15:00 - Heavy rain shower (day)
	16 May, 18:00 - Cloudy
	16 May, 21:00 - Cloudy
	17 May, 00:00 - Cloudy
	17 May, 03:00 - Cloudy
	
	[...]
	
	20 May, 06:00 - Cloudy
	20 May, 09:00 - Overcast
	20 May, 12:00 - Light rain shower (day)
	20 May, 15:00 - Light rain
	20 May, 18:00 - Light rain
	20 May, 21:00 - Overcast
	>>> metoffer.VISIBILITY[y.data[0]['Visibility'][0]]
	'Good - Between 10-20 km'
	>>> metoffer.guidance_UV(y.data[0]['Max UV Index'][0])
	'Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen'

The MetOffer Class
------------------

Available methods:

* ``loc_forecast``. Return location-specific forecast data (including lists of
  available sites and time capabilities) for given time step.

* ``nearest_loc_forecast``. Work out nearest possible site to lat & lon
  coordinates and return its forecast data for the given time step.

* ``loc_observations``. Return location-specific observation data, including a
  list of available sites (time step will be HOURLY).

* ``nearest_loc_obs``. Work out nearest possible site to lat & lon coordinates
  and return observation data for it.

* ``text_forecast``. Return textual forecast data for regions, national parks
  or mountain areas.

* ``text_uk_extremes``. Return textual data of UK extremes.

* ``stand_alone_imagery``. Returns capabilities data for stand alone imagery and
  includes URIs for the images.

* ``map_overlay_forecast``. Returns capabilities data for forecast map overlays.

* ``map_overlay_obs``. Returns capabilities data for observation map overlays.

The Site Class
--------------

Describes object to hold site metadata.  Also describes method
(``distance_to_coords``) to return a Site instance's 'distance' from any given
lat & lon coordinates.  This 'distance' is a value which is used to guide
``MetOffer.nearest_loc_forecast`` and ``MetOffer.nearest_loc_obs``. It simply
calculates the difference between the two sets of coordinates and arrives at a
value through Pythagorean theorem.

The Weather Class
-----------------

A hold-all for returned weather data, including associated metadata.

Useful Functions
----------------

* ``parse_sitelist``. Return list of Site instances from retrieved sitelist data.

* ``get_nearest_site``. Return a list of strings (site IDs) which can be used as 'request' in calls to
  ``loc_forecast`` and ``loc_observations``.

* ``parse_val``. Parse returned dict of MetOffer location-specific data into a
  Weather instance. Data must be of multiple time steps. There are a couple of
  points to note:

  * All dict keys have a tuple, even where there is no obvious need, such as
    with 'timestamp' and 'Weather Type'. This is a feature.

  * When the Met Office does not have a recorded observation against a category,
    metoffer will return None.

  * For parsed DAILY forecasts, the hours and minutes of the 'timestamp'
    datetime.datetime object are superfluous. In fact, it would be misleading
    to follow them. Rather, this time there is a sensible entry in the second
    part of the tuple. This alternates between 'Day' and 'Night' with each
    successive dict. The categories are often specific to the time of day.
    This is how the API provides it. Take note; it may catch you out.

*  ``guidance_UV``. Return Met Office guidance regarding UV exposure based on UV
   index.

Feedback & Bug Reports
----------------------

Get in touch: Stephen B. Murray <sbm199@gmail.com>

Legal
-----

Copyright 2012 & 2013 Stephen B. Murray

Distributed under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

You should have received a copy of the GNU General Public License along with
this package. If not, see <http://www.gnu.org/licenses/>
