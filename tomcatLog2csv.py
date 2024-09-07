# Parses a Portal's catalina or localhost log file into a csv
# "C:\Program Files\ArcGIS\Server\framework\runtime\ArcGIS\bin\Python\Scripts\propy.bat" tomcatLog2csv.py C:\temp\localhost.2024-09-06.log

import sys 
import os
import datetime
import csv
import argparse
import re

def main(argv=None):
        
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', help=('A catalina or localhost log file name to parse'))
    args = parser.parse_args()
    logFileName = args.logfile
    
    # create output csv with same name	
    csvFileName = createCsvFileName(logFileName)

    # do the work
    parseTomcatLogFile(logFileName, csvFileName)
    print('File output: ' + csvFileName)
    
# create a matching csv name for the logfile
def createCsvFileName(logFileName):
    shortLogFileName = os.path.basename(logFileName)
    csvFileBaseName = shortLogFileName.replace('.log','.csv')
    thePath = os.path.dirname(logFileName)
    csvFileName = os.path.join(thePath,csvFileBaseName)
    return csvFileName


# do the log reading, parsing, and csv writing
def parseTomcatLogFile(logFileName, csvFileName):    
    # open csv for output
    with open (csvFileName, 'w', newline="") as csvFile:
        bKeysWritten = False

        # open log file for reading
        with open (logFileName,'r') as logFile:
            # read all lines
            lines = logFile.readlines()
            count = 0
            lastProcessedRecord = {} # a dictionary for one line
            
            #iterate through lines
            for line in lines:
                count += 1
                theDate = line[0:24]
                bIsDate = False
                try:
                    print(theDate)
                    d = datetime.datetime.strptime(theDate,'%d-%b-%Y %I:%M:%S.%f') 
                    bIsDate = True
                except:
                    bIsDate = False

                # if the line begins with a date, we have a new record to parse
                if bIsDate:
                    
                    # if we have an accumulated lastProcessedRecord, write it and re-initialize (because the start of this line indicates there is a new record to process.
                    if bool(lastProcessedRecord):
                        
                        # record the record
                        if bKeysWritten == False:
                            # if we've not yet written the header, do that and the first record
                            writer = csv.DictWriter(csvFile, lastProcessedRecord.keys())
                            writer.writeheader()
                            writer.writerow(lastProcessedRecord)
                            bKeysWritten = True
                        else:
                            # if the header exists, write the record
                            writer.writerow(lastProcessedRecord)
                            # note progress to stdout
                            if (count % 1000 == 0):
                                print('Record: ' + str(count) + ' written')
                        # re-initialize it
                        lastProcessedRecord = {}
                    
                    # parse the new log line ...
                    startOfType = line.find(' ',24) - 1
                    endOfType = line.find(' [',startOfType)
                    theType = line[(startOfType + 2):endOfType]
                    startOfModule = line.find('[',endOfType) -1
                    endOfModule = line.find('] ',startOfModule)
                    theModule = line[(startOfModule + 2):endOfModule]
                    startOfClass = line.find(' ',endOfModule) - 1
                    endOfClass = line.find(' ',startOfClass + 2)
                    theClass = line[(startOfClass + 2):endOfClass]
                    theMessage = line[(endOfClass + 1):(len(line))]
                    theMessage = theMessage.replace('\n',' ').replace('\r',' ')

                    
                    # start the dictionary for this line, it will either be appended to or written on the next iteration of the loop ...
                    lastProcessedRecord['lineNumber'] = str(count)
                    lastProcessedRecord['datetime'] = theDate
                    lastProcessedRecord['type'] = theType
                    lastProcessedRecord['module'] = theModule
                    lastProcessedRecord['class'] = theClass
                    lastProcessedRecord['message'] = theMessage
                
                # if the line doesn't begin with a date, we want to append this line's content to the lastProcessedRecord.message entity
                else:
                    lastProcessedRecord['message'] = lastProcessedRecord['message'] + ' ' + line.replace('\n',' ').replace('\r',' ')
                
                
                # #if count > 300:
                # #    break                     

            # write the last dictionary, if it has not already been written
            if bool(lastProcessedRecord):
                writer.writerow(lastProcessedRecord)
                print('Final record: ' + str(count) + ' written')
                
if __name__ == "__main__":
	sys.exit(main(sys.argv))
    
    