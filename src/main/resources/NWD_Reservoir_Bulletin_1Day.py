'''
Author: Ryan Larsen
Last Updated: 02-28-2019
Description: Create the MRBWM Reservoir Bulletin
'''

# -------------------------------------------------------------------
# Required imports
# -------------------------------------------------------------------
from com.itextpdf.text      import Document, DocumentException, Rectangle, Paragraph, Phrase, Chunk, Font, FontFactory, BaseColor, PageSize, Element, Image
from com.itextpdf.text.Font import FontFamily
from com.itextpdf.text.pdf  import PdfWriter, PdfPCell, PdfPTable, PdfPage, PdfName, PdfPageEventHelper, BaseFont
from hec.data.cwmsRating    import RatingSet
from hec.heclib.util        import HecTime
from hec.io                 import TimeSeriesContainer
from hec.script             import Constants, MessageBox
from java.awt.image         import BufferedImage
from java.io                import FileOutputStream, IOException
from java.lang              import System
from java.text              import NumberFormat
from java.util              import Locale
from time                   import mktime, localtime
from subprocess             import Popen
import java.lang
import os, sys, inspect, datetime, time, DBAPI, java

# -------------------------------------------------------------------
# Import database pathnames and plotting functions
# -------------------------------------------------------------------
# Determine if OS is Windows or Unix. Use PC pathnames if OS is Windows
OsName = java.lang.System.getProperty("os.name").lower()
print 'OsName = ', OsName
if OsName[ : 7] == 'windows' : 
    # PC pathnames
    CronjobsDirectory = "C:\\Users\\G0PDRJAB\\Documents\\cronjobs\\" # Used in the properties file to create pathname for Seals and Symbols
    BulletinsDirectory = CronjobsDirectory + 'Bulletins\\'
    ScriptDirectory = BulletinsDirectory + 'NWD_Reservoir\\'
    BulletinFilename = BulletinsDirectory + 'NWD_Reservoir_Bulletin.pdf'
    ArchiveBulletinFilename = BulletinsDirectory + 'MRBWM_Reservoir_%s.pdf'
    CsvFilename = BulletinsDirectory + 'NWD_Reservoir_Bulletin.csv'
    BulletinPropertiesPathname = ScriptDirectory + 'NWD_Reservoir_Bulletin_Properties.txt'
else :
    # Server pathnames
    ScriptDirectory = os.path.dirname(os.path.realpath(__file__))
    PathList = ScriptDirectory.split('/')
    BulletinsDirectory = '/'.join(PathList[: -1]) + '/'
    CronjobsDirectory = '/'.join(PathList[: -2]) + '/'
    ScriptDirectory += '/'
    BulletinFilename = BulletinsDirectory + 'NWD_Reservoir_Bulletin.pdf'
    ArchiveBulletinFilename = BulletinsDirectory + 'MRBWM_Reservoir_%s.pdf'
    CsvFilename = BulletinsDirectory + 'NWD_Reservoir_Bulletin.csv'
    BulletinPropertiesPathname = ScriptDirectory + 'NWD_Reservoir_Bulletin_Properties.txt'    

print 'BulletinsDirectory = ', BulletinsDirectory, '\tScript Directory = ', ScriptDirectory
print 'BulletinFilename = ', BulletinFilename, '\tBulletinPropertiesPathname = ', BulletinPropertiesPathname

if CronjobsDirectory not in sys.path : sys.path.append(CronjobsDirectory)
if BulletinsDirectory not in sys.path : sys.path.append(BulletinsDirectory)
if ScriptDirectory not in sys.path : sys.path.append(ScriptDirectory)

#
# Load DatabasePathnames.txt and BulletinProperties
#
while True :
    errorMessage = None
    DatabasePathnamesFile = os.path.join(CronjobsDirectory, "DatabasePathnames.txt")
    if not os.path.exists(DatabasePathnamesFile) :
        errorMessage = "DatabasePathnames.txt does not exist: %s" % DatabasePathnamesFile
    with open(DatabasePathnamesFile, "r") as f : exec(f.read())
    break
if errorMessage :
    print "ERROR : " + errorMessage
BulletinProperties = open(BulletinPropertiesPathname, "r"); exec(BulletinProperties)

# Import server utilities
import Server_Utils
reload(Server_Utils)
from Server_Utils import lineNo, outputDebug, retrieveLocationLevel, retrievePublicName

#
# Input
#
# Set debug = True to print all debug statements and = False to turn them off
debug = False

##################################################################################################################################
##################################################################################################################################

#
# Functions
#

#
# createCell Function   : Creates a PdfPCell for tables
# Author/Editor         : Ryan Larsen
# Last updated          : 12-20-2017
#
def createCell( debug,                  # Set to True to print all debug statments
                CellData,               # Data that will appear within the cell
                RowSpan,                # Specifies number of rows information within cell will span
                ColSpan,                # Specifies number of columns information within cell will span
                HorizontalAlignment,    # Specifies horizontal alignment: ALIGN_CENTER, ALIGN_LEFT, ALIGN_RIGHT
                VerticalAlignment,      # Specifies vertical alignment: ALIGN_CENTER, ALIGN_TOP, ALIGN_BOTTOM
                CellPadding,            # List of cell padding around text: [Top, Right, Bottom, Left]
                BorderColors,           # List of border colors: [Top, Right, Bottom, Left]
                BorderWidths,           # List of border widths: [Top, Right, Bottom, Left]
                VariableBorders,        # Allows or denies variable borders: True, False
                BackgroundColor         # Color of cell background
                ) :
    Cell = PdfPCell(CellData)
    Cell.setRowspan(RowSpan); Cell.setColspan(ColSpan)
    Cell.setHorizontalAlignment(HorizontalAlignment); Cell.setVerticalAlignment(VerticalAlignment)
    Cell.setPaddingTop(CellPadding[0]); Cell.setPaddingRight(CellPadding[1]); Cell.setPaddingBottom(CellPadding[2]); Cell.setPaddingLeft(CellPadding[3])
    Cell.setBorderColorTop(BorderColors[0]); Cell.setBorderColorRight(BorderColors[1]); Cell.setBorderColorBottom(BorderColors[2]); Cell.setBorderColorLeft(BorderColors[3])
    Cell.setBorderWidthTop(BorderWidths[0]); Cell.setBorderWidthRight(BorderWidths[1]); Cell.setBorderWidthBottom(BorderWidths[2]); Cell.setBorderWidthLeft(BorderWidths[3])
    Cell.setUseVariableBorders(VariableBorders)
    Cell.setBackgroundColor(BackgroundColor)

    return Cell

#
# table1Data Function   : Creates the Data1 block for Table1 in the bulletin
# Author/Editor         : Ryan Larsen
# Last updated          : 12-12-2017
#
def table1Data( debug,      # Set to True to print all debug statements
                Table,      # PdfPTable object
                TableName,  # String name for the table
                DataName,   # String name for data section of table
                CsvData,    # Csv data   
                ) :
    # Create name for TableData
    TableDataName = '%s%s' % (TableName, DataName)
    
    # Data Block Heading
    # createCell(debug, CellData, RowSpan, ColSpan, HorizontalAlignment, VerticalAlignment, CellPadding, BorderColors, BorderWidths, VariableBorders, BackgroundColor)
    Cell = createCell(debug, Phrase(Chunk(DataBlockDict['DataBlocks'][TableDataName]['Heading'], Font5)), TableLayoutDict[TableName]['RowSpan'], 
        Table1Columns, Element.ALIGN_LEFT, TableLayoutDict[TableName]['VerticalAlignment'], [2, 2, 3, 3], TableLayoutDict[TableName]['BorderColors'], 
        [0.25, 1, 0.25, 1], TableLayoutDict[TableName]['VariableBorders'], Color7)
    Table.addCell(Cell)
    
    # Add text to CsvData
    CellData = Phrase(Chunk(DataBlockDict['DataBlocks'][TableDataName]['Heading'], Font5))
    CsvData += str(CellData[0])
    CsvData += '\n'
    
    # Set variable x = 0 to use as an index for arrays in Table1 properties
    x = 0
        
    # Data
    for project in DataBlockDict['DataBlocks'][TableDataName]['ProjectList'] :
        
        # If adding the last project in the last data block, create a trigger to use a thick bottom border
        if DataName == DataBlocks[-1] and project == DataBlockDict['DataBlocks'][TableDataName]['ProjectList'][-1] :
            LastProject = True
        else : LastProject = False
        
        # Reset TotalColSpan to 0
        TotalColSpan = 0
        
        for data in DataOrder :
            outputDebug(debug, lineNo(), 'Adding %s to the row' % data)
            # Create a variable within the DataDict. This will allow the user to store all data to a dictionary and access the variables throughout
            #   the script
            DataBlockDict['DataBlocks'][TableDataName].setdefault(project, {}).setdefault(data, None)

            # Get column number
            ColumnKey = 'Column%d' % DataOrder.index(data)

            # Default cell properties. If there is a special case, the properties will be changed.
            TextFont = TableLayoutDict[TableName]['TextFont']
            RowSpan = TableLayoutDict[TableName]['RowSpan']; ColSpan = TableLayoutDict[TableName]['ColSpan']
            HorizontalAlignment = TableLayoutDict[TableName]['HorizontalAlignment']; VerticalAlignment = TableLayoutDict[TableName]['VerticalAlignment']
            CellPadding = TableLayoutDict[TableName]['CellPadding']
            BorderColors = TableLayoutDict[TableName]['BorderColors']
            BorderWidths = TableLayoutDict[TableName]['BorderWidths']
            VariableBorders = TableLayoutDict[TableName]['VariableBorders']
            BackgroundColor = TableLayoutDict[TableName]['BackgroundColor']
            
            # Project Bulletin Name
            if data == 'PublicName' :
                try :
                    IndexValue = DataBlockDict['DataBlocks'][TableDataName][data][x]
    
                    # Create a formatted string that will be added to the table
                    CellData = Phrase(Chunk(IndexValue, TextFont))
                    
                except :
                    IndexValue = Missing
                    # Create a formatted string that will be added to the table
                    CellData = Phrase(Chunk(Missing, TextFont))
                
                # Store value to DataDict
                DataBlockDict['DataBlocks'][TableDataName][project][data] = IndexValue

                # Change default cell properties
                HorizontalAlignment = Element.ALIGN_LEFT
                BorderColors = [Color2, Color3, Color2, Color2]
                if LastProject : BorderWidths = [0.25, 0.5, 1, 1]
                else : BorderWidths = [0.25, 0.5, 0.25, 1]
                CellPadding = [0, 2, 2, 3]                
            # Elevation
            elif data == 'Elevation' :
                try :
                    if DataBlockDict['DataBlocks'][TableDataName][data] % project in PathnameList :
                        Tsc = CwmsDb.read(DataBlockDict['DataBlocks'][TableDataName][data] % project).getData()
                    else : 
                        raise ValueError

                    PrevElev = Tsc.values[-1] # Previous day's midnight value
                    # If previous day's value is missing raise an exception and using the missing value
                    if PrevElev == Constants.UNDEFINED : raise ValueError
                    
                    # Create a formatted string that will be added to the table
                    CellData = Phrase(Chunk(TableLayoutDict[TableName][ColumnKey]['Format'] % PrevElev, TextFont))
                except :
                    PrevElev = Missing
                    # Create a formatted string that will be added to the table
                    CellData = Phrase(Chunk(Missing, TextFont))

                # Store value to DataDict
                outputDebug(debug, lineNo(), 'Set %s %s = ' % (project, data), PrevElev)
                DataBlockDict['DataBlocks'][TableDataName][project][data] = PrevElev

                # Change default cell properties
                if LastProject : BorderWidths = [0.25, 0.25, 1, 0.25]
            # Storage, Inflow, and Release
            elif data == 'Storage' or data == 'FlowIn' or data == 'FlowTotal' :
                try :
                    TscPathname = DataBlockDict['DataBlocks'][TableDataName][data] % project
                    # Set the database time zone if not in the specified list
                    if project not in ['FTPK', 'GARR', 'OAHE', 'BEND', 'FTRA', 'GAPT'] :
                        CwmsDb.setTimeZone('Etc/GMT+6')
                        Tsc = CwmsDb.get(TscPathname, TrimTwStr, EndTwStr) # Use TrimTwStr for daily data. Some daily data is ~1Day which won't return missing values
                                                                           #    since they are irregular time series. By using TrimTwStr, only 1 value will be returned
                    else :
                        Tsc = CwmsDb.get(TscPathname, TrimTwStr, EndTwStr) # Use TrimTwStr for daily data. Some daily data is ~1Day which won't return missing values
                                                                           #    since they are irregular time series. By using TrimTwStr, only 1 value will be returned

                    Value = Tsc.values[-1]
                    Value = round(Value, 0)
                    
                    # Reset database time zone to US/Central
                    CwmsDb.setTimeZone('US/Central')
                        
                    # If value is missing raise an exception and using the missing value
                    if Value == Constants.UNDEFINED : raise ValueError
    
                    # Create a formatted string that will be added to the table
                    if Value == Null : CellData = Phrase(Chunk(Null, TextFont))
                    else :  CellData = Phrase(Chunk(TableLayoutDict[TableName][ColumnKey]['Format'].format(int(Value)), TextFont)) # Uses Java formatting to get the 1000s comma separator
                except :
                    Value = Missing
                    # Create a formatted string that will be added to the table
                    CellData = Phrase(Chunk(Missing, TextFont))

                # Store value to DataDict
                outputDebug(debug, lineNo(), 'Set %s %s = ' % (project, data), Value)
                DataBlockDict['DataBlocks'][TableDataName][project][data] = Value

                # Change default cell properties
                if LastProject : BorderWidths = [0.25, 0.25, 1, 0.25]
                if data == 'FlowTotal' :
                    BorderColors = [Color2, Color3, Color2, Color2]
                    if LastProject : BorderWidths = [0.25, 0.5, 1, 0.25]
                    else : BorderWidths = [0.25, 0.5, 0.25, 0.25]

            
            # createCell(debug, CellData, RowSpan, ColSpan, HorizontalAlignment, VerticalAlignment, CellPadding, BorderColors, BorderWidths, VariableBorders, BackgroundColor)
            Cell = createCell(debug, CellData, RowSpan, ColSpan, HorizontalAlignment, VerticalAlignment, CellPadding, BorderColors, BorderWidths, VariableBorders, BackgroundColor)
            Table.addCell(Cell)

            # Add data to CsvData. Break data loop if column span reaches the total number columns before each data piece has been added to that table
            outputDebug(debug, lineNo(), 'ColSpan = ', ColSpan)
            TotalColSpan += ColSpan
            UnformattedData = str(CellData[0]).replace(',', '')
            CsvData += UnformattedData
            CsvData += ','
            outputDebug(debug, lineNo(), 'TotalColSpan = ', TotalColSpan)
            if TotalColSpan == Table.getNumberOfColumns() :
                CsvData += '\n'
                break
    
        # Increase variable x to use as an index for other arrays in Table2 properties
        x = x + 1
            
    return Table, CsvData

#
# Main Script
#
try :   
    try : 
        #
        # Date and Time Window Info
        #
        CurDateTime = datetime.datetime.now()
        CurDateTimeStr  = CurDateTime.strftime('%m-%d-%Y %H:%M') # Last updated time for bulletin formatted as mm-dd-yyyy hhmm
        if UseCurDate :
            Date = datetime.datetime.now() # Current date
            TimeObj = time.strptime(CurDateTimeStr, '%m-%d-%Y %H:%M')
        else :
            TimeObj = time.strptime(HistoricBulletinDate, '%d%b%Y %H%M')
            TimeObj = localtime(mktime(TimeObj)) # Convert TimeObj to local time so it includes the DST component
            Date    = datetime.datetime.fromtimestamp(mktime(TimeObj))
        
        StartTw             = Date - datetime.timedelta(2)
        MkcStartTw          = Date - datetime.timedelta(1)
        StartTwStr          = StartTw.strftime('%d%b%Y 2400') # Start of time window for the database formatted as ddmmmyyyy 2400
        MkcStartTwStr       = MkcStartTw.strftime('%d%b%Y 0600') # Start of time window for the database formatted as ddmmmyyyy 0600. Used for MKC projects
        EndTw               = Date - datetime.timedelta(1)
        MkcEndTw            = Date
        TrimTwStr           = EndTw.strftime('%d%b%Y 0100') # Trimmed time window for the database formatted as ddmmmyyyy 0100. Used for daily time series
        MkcTrimTwStr        = MkcEndTw.strftime('%d%b%Y 0100') # Trimmed time window for the database formatted as ddmmmyyyy 0100. Used for MKC daily time series
        EndTwStr            = EndTw.strftime('%d%b%Y 2400') # End of time window for the database formatted as ddmmmyyyy 2400
        MkcEndTwStr         = MkcEndTw.strftime('%d%b%Y 0600') # End of time window for the database formatted as ddmmmyyyy 0600. Used for MKC projects
        ProjectDateTimeStr  = CurDateTime.strftime('%m-%d-%Y 00:00') # Project date and time for bulletin formatted as mm-dd-yyyy 2400
        ArchiveDateTimeStr  = CurDateTime.strftime('%d%m%Y') # Last updated time for bulletin formatted as dd-mm-yyyy
        TimeSinceEpoch      = mktime(TimeObj) # Time object used for ratings
        outputDebug(debug, lineNo(), 'Start of Time Window = ', StartTwStr, '\tEnd of Time Window = ', EndTwStr, 
            '\tProject Date and Time = ', ProjectDateTimeStr, '\tTimeSinceEpoch = ', TimeSinceEpoch)
        
        #
        # Open database connection
        #
        CwmsDb = DBAPI.open()
        CwmsDb.setTimeZone('US/Central')
        CwmsDb.setTimeWindow(StartTwStr, EndTwStr)
        CwmsDb.setOfficeId('NWDM')
        CwmsDb.setTrimMissing(False)
        conn = CwmsDb.getConnection()# Create a java.sql.Connection
        # Get list of pathnames in database
        PathnameList = CwmsDb.getPathnameList()
        
        #
        # Create tables with a finite number of columns that will be written to the pdf file
        #
        # Table1: Contains all data and data headings
        Table1 = PdfPTable(Table1Columns)
        #
        # Specify column widths
        #
        # Table Columns and Order of Variables for Table1
        DataOrder, ColumnWidths = [], []
        for column in range(Table1Columns) :
            # Column Key
            ColumnKey = 'Column%d' % column
            
            DataOrder.append(TableLayoutDict['Table1'][ColumnKey]['Key'])
            ColumnWidths.append(TableLayoutDict['Table1'][ColumnKey]['ColumnWidth'])
        Table1.setWidths(ColumnWidths)
        
        CsvData = ''
        #
        # Add data to the data blocks for Table1
        #
        DataBlocks = ['Data1', 'Data2', 'Data3']
        for DataBlock in DataBlocks :
            Table1, CsvData = table1Data(debug, Table1, 'Table1', DataBlock, CsvData)
        
        #
        # Create Pdf file and write tables to create bulletin
        #
        filenames = [BulletinFilename, ArchiveBulletinFilename % ArchiveDateTimeStr]
        for filename in filenames :
            BulletinPdf = Document()
            Writer = PdfWriter.getInstance(BulletinPdf, FileOutputStream(filename))
            BulletinPdf.setPageSize(PageSize.LETTER) # Set the page size
            PageWidth = BulletinPdf.getPageSize().getWidth()
            BulletinPdf.setMargins(LeftMargin, RightMargin, TopMargin, BottomMargin) # Left, Right, Top, Bottom
            BulletinPdf.setMarginMirroring(True) 
            BulletinPdf.open()
            BulletinPdf.add(Table1) # Add Table1 to the PDF
            BulletinPdf.close()
            Writer.close()
            
        # 
        # Create csv file
        #
        CsvFile = open(CsvFilename, 'w')
        CsvFile.write(CsvData)

    except Exception, e : 
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
    except java.lang.Exception, e : 
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
finally :
    try : CwmsDb.done()
    except : pass
    try : conn.close()
    except : pass
    try : BulletinPdf.close()
    except : pass
    try : Writer.close()
    except : pass
    try : CsvFile.close()
    except : pass
    try : BulletinTsFile.close()
    except : pass
    try : BulletinProperties.close()
    except : pass