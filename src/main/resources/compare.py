import argparse
import csv
import JULHandler
import logging
import hec.io.TimeSeriesContainer as TimeSeriesContainer
import hec.hecmath.TimeSeriesMath as TimeSeriesMath

logging.getLogger().addHandler(JULHandler.JULHandler())
logger = logging.getLogger()
logger.setLevel(logging.INFO)

import sys, os

import RADARAPI
import DBAPI

def read_list(filename):
	retval = []
	with open(filename, 'r') as f:
		data = f.read()
		if data:
			retval = data.split("\n")
	return retval

def write_list(filename, list):
	with open(filename, 'w') as f:
		for item in list:
			f.writelines(item + '\n')

def perform(input_dict, cwms_db):
	retval = {}
	retval['method'] = input_dict['method']
	path = input_dict["ts"]
	retval["ts"] = path
	retval["office"] = input_dict["office"]
	
	if input_dict['timezone'] is not None:
		cwms_db.setTimeZone(input_dict['timezone'])
	else:
		cwms_db.setTimeZone('US/Central')
		
	retval['timezone'] = cwms_db.getTimeZoneName()
	
	if input_dict['method'] == "get":
		start = input_dict["start"]
		end = input_dict["end"]
		response = cwms_db.get(path, start, end)
		
	elif input_dict['method'] == "read":
		start = ""
		end = ""
		response = cwms_db.read(path)

	retval["start"] = start
	retval["end"] = end
	retval['type'] = type(response)
	
	tsc = None
	if isinstance(response, TimeSeriesContainer):
		tsc = response
	elif isinstance(response, TimeSeriesMath):
		tsc = response.getData()
	
	if tsc is not None:
		retval['length'] = tsc.numberValues
		retval['units'] = tsc.units
		retval['firstTime'] = tsc.times[0]
		retval['lastTime'] = tsc.times[-1]
	else:
		retval['length'] = ""
		retval['units'] = ""
		retval['firstTime'] = ""
		retval['lastTime'] = ""
	
	return retval

# Compare the input and output dictionaries and log any differences
def warn_about_differences(input_dict, output_dict):
	for k in input_dict.keys():
		# warn if output_dict doesn't have the key
		if k not in output_dict:
			logger.warning("Output dictionary doesn't have key %s" % (k))
			continue
		if str(input_dict[k]) != str(output_dict[k]):
			logger.warning('Difference in %s: %s != %s' % (k, input_dict[k], output_dict[k]))
			

def capture(infile, outfile, use_radar, radar_url, cache_pathnames):
	input_reader = csv.DictReader(infile)

	input_dicts = [row for row in input_reader]
	first_dict = input_dicts[0]
	
	used_ts = [row['ts'] for row in input_dicts]
	
	start_tw_str = first_dict['start']
	end_tw_str = first_dict['end']
	office = first_dict['office']
	tz = first_dict['timezone']
	
	if use_radar:
		cwms_db = RADARAPI.open(url=radar_url, office=office)
		cwms_db.setTimeZone(tz)
		cwms_db.setTimeWindow(start_tw_str, end_tw_str)
		cwms_db.setTrimMissing(False)
	else:
		# This uses the old DBAPI and references values in config/properties
		cwms_db = DBAPI.open()
		cwms_db.setOfficeId(office)
		cwms_db.setTimeZone(tz)
		cwms_db.setTimeWindow(start_tw_str, end_tw_str)
		cwms_db.setTrimMissing(False)

	# The pathname fetch can be slow so if repeatedly running this script
	# it can be useful to save the list of pathnames to a file.
	if cache_pathnames:
		path_cache = "pathnames-%s.txt" % (office)
		if os.path.exists(path_cache):
			pathnames = read_list(path_cache)
		else:
			# Get list of pathnames in database
			pathnames = cwms_db.getPathnameList()
			if pathnames is not None and len(pathnames) > 0:
				write_list(path_cache, pathnames)
	else:
		pathnames = cwms_db.getPathnameList()
	
	logger.info('Got pathnames length:%s' % (len(pathnames)))
	
	missing = set(used_ts).difference(set(pathnames))
	if len(missing) > 0:
		logger.warning("Missing required pathnames: %s" % (missing))
	
	output_writer = csv.writer(outfile)
	output_writer.writerow(input_reader.fieldnames)
	for row in input_dicts:
		d = perform(row, cwms_db)
		output_writer.writerow([d[k] for k in input_reader.fieldnames])
		warn_about_differences(row, d)
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Collect CWMS data and compare to expected results.')
	parser.add_argument('--use-radar', action='store_true', help='Use RADAR API instead of DBAPI', default=True)
	parser.add_argument('--cache-pathnames', action='store_true', help='Potentially skip the pathname retrieve', default=False)
	parser.add_argument('--radar-url', help='The url to the Radar server.', default="https://cwms-data.usace.army.mil/cwms-data/")
	parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
	                    default="input.csv")
	parser.add_argument('outfile', nargs='?', type=argparse.FileType('wb'),
	                    default="output.csv")
	
	args = parser.parse_args()
	capture(args.infile, args.outfile, args.use_radar, args.radar_url, args.cache_pathnames)
	
	# hec-metrics can potentially hang on a non-daemon thread
	exit(0)