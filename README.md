A project to demo RADARAPI and DBAPI compatibility.

RADARAPI was built to be compatible with DBAPI, so that it can be used as a drop-in replacement for DBAPI.

The script NWD_Reservoir_Bulletin_1Day.py is a simplified example of how DBAPI is actually used in the field to acquire data and format it into a pdf report.

That script opens a connection to the database (CwmsDb) and retrieves a list of pathnames.
It then iterates throught the pathnames and uses some property files to determine the timeseries for which it will issue either a get() call or a read() call.

The script compare.py was built as an even further simplified test.

To use this project:

* Checkout this project
* Do a maven build.
* Use "mvn dependency:copy-dependencies" to copy the dependencies to a "target" folder.
* Create an input.csv file
* Run script against DBAPI
* Rename output.csv to input.csv
* Run script against RADARAPI
* Examine output for differences


Compare.py takes as input a csv file.    The csv file contains a list of requests and attributes about the expected responses to those requests.

Compare.py iterates through the csv file and issues the requests.   It then compares the responses to the expected responses and logs WARNING messages for any detected differences.
The script then writes output.csv - a file in the same format as the input except that it contains the actual responses instead of the expected responses.

The columns in the input csv file are:

* office,
* ts,
* method,
* start,
* end,
* timezone,
* type,
* length,
* units,
* firstTime,
* lastTime

The first 6 columns (office,ts,method,start,end,timezone) are used to build the request.   The remaining columns are used to compare the response to the expected response.

In order to build an input.csv with the expected responses:

* Create a new input.csv file with the first line containing the following columns:
  office,ts,method,start,end,timezone,type,length,units,firstTime,lastTime
* Then add a line for each desired request.
  These lines should contain information for the first 6 columns.
  The method column should be either "get" or "read".
  For lines that use the "read" method, the start and end columns can be empty.


To configure the script to use DBAPI enter the connection information in config/properties/dbi.conf

and config/properties/dbi.properties


To configure the script to use RADARAPI add "--use-radar --radar-url=http://localhost:7000/swt-data/" to the command line arguements.


run.bat has an example of how to run the script in a Windows environment.

The file input.csv contains an example input file configured to use SWT and some timeseries from that office.
The file input_nwdm.csv contains an example input file based on the requests issued by the NWD_Reservoir_Bulletin_1Day.py script.
The needed timeseries are not available in the national database so it was not possible to test against this file and it is provided as a starting place for tests to be run from a system with access to the NWDM office.


