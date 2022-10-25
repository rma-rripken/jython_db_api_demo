@echo on

set JAVA_HOME=C:\Program Files\Java\jdk1.8.0_181

set PROJ_DIR=.\

set CP=%PROJ_DIR%\target\*;%PROJ_DIR%\src\main\resources

set JVM_OPTS=
set JVM_OPTS=%JVM_OPTS% -Dmetrics-enabled=true
set JVM_OPTS=%JVM_OPTS% -Dcwms.dbi.ConnectUsingUrl="http://localhost:7000/swt-data/"
set JVM_OPTS=%JVM_OPTS% -DCWMS_HOME="%PROJ_DIR%\src\test"
set JVM_OPTS=%JVM_OPTS% -Djava.util.logging.config.file=logging.properties

set MAIN_CLASS=org.python.util.jython
set JYTHON_SCRIPT=%PROJ_DIR%\src\main\resources\NWD_Reservoir_Bulletin_1Day.py

"%JAVA_HOME%\bin\java.exe" %JVM_OPTS% -cp "%CP%" %MAIN_CLASS% %JYTHON_SCRIPT%

rem > %temp%\out.log 2>&1
