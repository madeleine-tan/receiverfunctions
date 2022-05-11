#!/usr/bin/env python3

# Download data from IRIS as SAC files
# Required: Obspy

import os

from obspy.clients.fdsn           import Client
from obspy                        import UTCDateTime
from obspy.geodetics.flinnengdahl import FlinnEngdahl
from obspy.taup                   import TauPyModel

#-- distance and azimuth on an ellipsoid
import pyproj
geodesic = pyproj.Geod(ellps='WGS84')


#-------------------------
#-- Parameters
#-------------------------
#
#-- time interval
t_min = UTCDateTime("2012-11-14T00:00:01.000")
t_max = UTCDateTime("2014-12-31T23:59:59.999")

#-- earthquake magnitude range
magn_min = 6.5; magn_max = 8.0

#-- epicentral distance range
#gcarc_min = 35; gcarc_max = 85
gcarc_min = 30; gcarc_max = 90

#-- trace time window = [O, O + duration]
#-- O = earthquake origin time
duration = 1500


#-------------------------
#-- Stations
#-------------------------
#
client = Client("IRIS")

#-- Lake Erie region: network codes "US" (includes AAM, ERPA, GLMI), "N4" (includes I45A,L48A,K50A,I49A,M51A,J47A,M50A,M52A)
#US_network  = "US";
#US_stations = "AAM,ERPA,GLMI"
#N4_network  = "N4";
#N4_stations = "I45A,L48A,K50A,I49A,M51A,J47A,M50A,M52A"
US_network = "TA";
US_stations = "C40A,D41A,E40A,E41A,E42A,E43A,E44A,E45A,E46A,F43A,F44A,F45A,F46A,G43A,G45A,G46A,G47A,H45A,H46A,H47A,H48A,I45A,I46A,I47A,I48A,I49A,J45A,J46A,J47A,J48A,J49A,K46A,K47A,K48A,K49A,K50A,L46A,L48A,L49A";
networks = US_network
stations = US_stations

#networks    = US_network  + ',' + N4_network
#stations    = US_stations + ',' + N4_stations
#-------------------------
#-- Events
#-------------------------
#
client = Client("USGS")
#-- event between 30 and 100 degrees from [43N, -83E]
#cat = client.get_events( starttime=t_min, endtime=t_max,
						# minmagnitude=magn_min, maxmagnitude=magn_max,
						# latitude=43, longitude=-83, minradius=30, maxradius=100)
cat = client.get_events( starttime=t_min, endtime=t_max,
						minmagnitude=magn_min, maxmagnitude=magn_max,
						latitude=44, longitude=-84, minradius=20, maxradius=100)

#-------------------------
#-- Waveforms
#-------------------------
#
client = Client("IRIS")

#-- LOOP OVER EVENT in CAT
for event in cat:

   prfrd_origin = event.preferred_origin()
   wavef_dir    = prfrd_origin.time.strftime('Event_%Y_%m_%d_%H_%M_%S')
   if not os.path.exists( wavef_dir ):
      os.mkdir( wavef_dir )
   else:
      print ("Directory: ", wavef_dir, " already exists. Continuing to next event ..." )
      continue

   evla         = prfrd_origin.latitude
   evlo         = prfrd_origin.longitude
   evdp         = prfrd_origin.depth / 1000.   # depth in km
   t1           = prfrd_origin.time            # trace begin time = origin time
   t2           = t1 + duration                # trace end time   = origin time + duration
   region       = FlinnEngdahl().get_region( evlo, evla )

   prfrd_magntd = event.preferred_magnitude()
   M            = prfrd_magntd.mag

   print ( "\n-- ",  region )
   print ( "Origin time= ", t1 )
   print ( "Hypocenter= {0:.2f} {1:.2f} {2:.0f}km M= {3:.1f}".format( evla,evlo,evdp,M ) )


   try:
      #-- get inventory (metadata)
	  #inv = client.get_stations(  network=networks, station=stations, channel="BH?", level="response", starttime=t1, endtime=t2 )
      inv = client.get_stations( network=networks, station=stations, channel="BH?", level="response", starttime=t1, endtime=t2 )
      wvf = client.get_waveforms( network=networks, station=stations,  location="*", channel="BH?", starttime=t1, endtime=t2 )
   except:
      print( "Failing to run get_station() or get_waveforms(). Continuing to next event ..." )
      continue


   #-- loop over traces in w(a)v(e)f(orms)
   for tr in wvf:

      #-- origin time (=o) (relative to starttime) (i.e. O in SAC)
      o = t1 - tr.stats.starttime
      #-- endtime relative to starttime (i.e., E in SAC)
      e = tr.stats.endtime - tr.stats.starttime
      #-- making sure that trace is long enough:
      #--    a) origin time should not be later than 200 s ater trace starttime
      #--    b) end time time should not be earier than (duration - 100 sec) after origin time
      if o < -200.  or  (e-o) < duration-100.:
         continue

      tmp_dict = inv.get_channel_metadata( tr.id )
      tr.stats['sac'] = {}
      stla = tmp_dict['latitude']
      stlo = tmp_dict['longitude']
      #-- gcarc
      az, baz, gcarc  = geodesic.inv( evlo,evla, stlo,stla )
      gcarc = gcarc /  111194.926 # m to degrees
      if gcarc < gcarc_min  or  gcarc > gcarc_max:
         continue


      try:
         #-- remove instrument response
         print( '{0:18s}  O= {1:7.2f}  E= {2:8.2f}  Gcarc= {3:6.1f}  Lat= {4:6.1f} Lon= {5:6.1f}'.format( tr.id, o, e, gcarc, stla, stlo ) )
         tr.remove_response( inventory=inv, pre_filt=( 0.005, 0.01, 3.0, 5.0), output="VEL" )

         #-- fill SAC header variables
         #-- t0 = P-wave arrival time
         P_time = TauPyModel(model="ak135").get_ray_paths( evdp, gcarc, phase_list='P' )
         tr.stats['sac']['t0']     = P_time[0].time
         tr.stats['sac']['evla']   = evla
         tr.stats['sac']['evlo']   = evlo
         tr.stats['sac']['evdp']   = evdp
         tr.stats['sac']['lcalda'] = True
         tr.stats['sac']['kevnm']  = region
         tr.stats['sac']['o']      = o
         tr.stats['sac']['stla']   = stla
         tr.stats['sac']['stlo']   = stlo
         tr.stats['sac']['stel']   = tmp_dict['elevation']
         tr.stats['sac']['stdp']   = tmp_dict['local_depth']
         tr.stats['sac']['cmpaz']  = tmp_dict['azimuth']
         tr.stats['sac']['cmpinc'] = tmp_dict['dip'] + 90.  #-- cmpinc = dip + 90
         tr.stats['sac']['gcarc']  = gcarc

         #-- write SAC file
         tr.write( wavef_dir + '/' + tr.id + ".sac", format="SAC" )

      except:
         print( "Failing to write data. Continuing ..." )
         pass
