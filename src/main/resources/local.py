import traceback

import logging

ERROR_LOG_FILENAME = "local-errors.log"
LOGGING_CONFIG = {
	"version": 1,
	"disable_existing_loggers": False,
	"formatters": {
		"default": {  # The formatter name, can be anything
			"format": "%(asctime)s:%(name)s:%(lineno)d " "%(levelname)s %(message)s",
			"datefmt": "%Y-%m-%d %H:%M:%S",  # How to display dates
		},
		"simple": {  # The formatter name
			"format": "%(message)s",  # As simple as possible!
		}
	},
	"handlers": {
		"logfile": {  # The handler name
			"formatter": "default",  # Refer to the formatter defined above
			"level": "ERROR",  # FILTER: Only ERROR and CRITICAL logs
			"class": "logging.handlers.RotatingFileHandler",  # OUTPUT: Which class to use
			"filename": ERROR_LOG_FILENAME,
			"backupCount": 2,
		},
		"verbose_output": {  # The handler name
			"formatter": "default",  # Refer to the formatter defined above
			"level": "DEBUG",  # FILTER: All logs
			"class": "logging.StreamHandler",  # OUTPUT: Which class to use
			"stream": "ext://sys.stdout",  # Param for class above. It means stream to console
		},
	},
	"loggers": {
		"LOCAL": {  # Name should match the module
			"level": "INFO",  # IF this is set at INFO it means INFO and above (so not DEBUG)
			"handlers": [
				"verbose_output",  # The handler defined above
			],
		},
	},
	"root": {  # All loggers (including RADARAPI)
		"level": "INFO",  # FILTER: only INFO logs onwards
		"handlers": [
			"logfile",  # Refer the handler defined above
		]
	}
}
logging.config.dictConfig(LOGGING_CONFIG)


import RADARAPI as DBAPI
from OrderedSet import OrderedSet

logger = logging.getLogger("LOCAL")

def readFromFile(filename):
	logger.info('reading list from file: %s' % (filename))
	filehandle = open(filename, "r")
	data = filehandle.read()
	
	return data.split("\n")

def writeToFile(filename, list):
	file = open(filename, 'w')
	for item in list:
		file.writelines(item + '\n')
	file.close()

def main():
	
	StartTwStr = "25Oct2022 0100"
	EndTwStr = "25Oct2022 2400"
	
	CwmsDb = DBAPI.open(url="http://localhost:7000/swt-data/", office="SWT")
	# CwmsDb.setTimeZone('US/Central')
	
	CwmsDb.setTimeWindow(StartTwStr, EndTwStr)
	CwmsDb.setTrimMissing(False)
	
	PathnameList = readFromFile("local.txt")
	
	# logger.info('Getting PathnameList')
	# Get list of pathnames in database
	# PathnameList = CwmsDb.getPathnameList()
	logger.info('Have PathnameList length:%s' % (len(PathnameList)))
	
	pathSet = OrderedSet(PathnameList)
	logger.info('pathSet length:%s' % (len(pathSet)))
	
	writeToFile("local.txt", PathnameList)
	
	for path in pathSet:
		logger.info('Getting TimeSeries for %s' % (path))
		Tsc = CwmsDb.get(path, StartTwStr, EndTwStr)
		logger.info('Got %s of type %s' %(path, type(Tsc)))
		
		
if __name__ == "__main__":
	main()