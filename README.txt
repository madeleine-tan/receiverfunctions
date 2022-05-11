Codes for receiver function analysis, 2022
  Madeleine Tan
  Univ. Michigan, Dept. of Earth and Environmental Sciences
  mmtan@umich.edu
  
 get_data_feb2022.py
 - download data as SAC files
 
 rf_plot.py
 - reads in receiver functions by station
 - generate 3 subplots: record section by back azimuth, scatter plot of back azimuths, stack of record section
 
 rf_QC.py
 - reads in receiver functions by station
 - prompts user to select three bad traces from the selected station's record station
 - when user reruns script, any saved bad events are excluded from record section
