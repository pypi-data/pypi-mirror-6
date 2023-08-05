'''
Created on Dec 3, 2013

@author: harshanarayana

@change:     2013-12-03    Initial Draft. A custom URLLinks class to Store and access information pertaining to a Single URL in Question
             2013-12-10    Addditional Functionality included to Support the Report Generation in HTML Format

'''

__version__ = "0.0.2"
__date__ = "06th December 2013"
__author__ = "Harsha Narayana"

import re

class URLLinks(object):
    '''
    A custom Class created for storing the information of the URL that is extracted and processed. 
    An object of this type is created for Each link that was extracted and processed from the Base URL that was given as input.   
    '''


    def __init__(self, parentLink, parentTitle, childLink, childTitle, isProcessed = False, isBroken = False, size = 0, dlTime = 0, 
                 checkTime = 0, lastModified = None, info = None, status = None, lType = None):
        '''
        Constructor with default values provided for some of the parameters. These values are later set while processing the contents. 
        '''
        self.__parentLink = parentLink
        self.__childLink = childLink
        self.__parentTitle = parentTitle
        self.__childTitle = childTitle
        self.__isProcessed = isProcessed
        self.__isBroken = isBroken
        self.__size = size
        self.__dlTime = dlTime
        self.__checkTime = checkTime
        self.__lastModified = lastModified
        self.__info = info
        self.__status = status
        self.__lType = lType
        self.__childURLs = []
    
    def addChild(self, value):
        '''
        Method created for adding a new Object of the type URLLinks into self.__childURLs
        Each element added is a URL extracted from the current page being processed. Valid / Invalid both will be 
        present. Status of Validity is changed later on based on the code. 
        '''
        self.__childURLs.append(value)
                    
    def getChildren(self):
        '''
        Method used for returning all child URL object. 
        Return type is a list of URLLinks object. 
        '''
        return self.__childURLs
    
    def getParentLink(self):
        '''
        Get Method for __parentLink param. 
        
        @return: URLLinks.__parentLink
        '''    
        return self.__parentLink
    
    def getParentTitle(self):
        '''
        Get method for __parentTitle param
        
        @return: URLLinks.__parentTitle
        '''
        return self.__parentTitle
    
    def getChildLink(self):
        '''
        Get method for __childLink param
        
        @return: URLLinks.__childLink
        '''
        return self.__childLink
    
    def getChildTitle(self):
        '''
        Get method for __childTitle param
        
        @return: URLLinks.__childTitle
        '''
        return self.__childTitle
    
    def isProcessed(self):
        '''
        Get method that returns the Processed state of the Link. 
        
        @return: URLLinks.__isProcessed         True : Processed     False : Not Processed
        '''
        return self.__isProcessed
    
    def isBroken(self):
        '''
        Get method that returns the Broken state of the Link. 
        
        @return: URLLinks.__isBroken         True : Broken     False : Not Broken
        '''
        return self.__isBroken
    
    def getSize(self):
        '''
        Get method that returns the file size for the Link being processed. 
        
        @return:  URLLinks.__size
        '''
        return self.__size
    
    def getDLTime(self):
        '''
        Get Method that returns the time taken to download the link being processed. 
        
        @return:    URLLinks.__dlTime
        '''
        return self.__dlTime 
    
    def getCheckTime(self):
        '''
        Get method that returns the Tiem taken to perform the check on that specific link. 
        
        @return: URLLinks.__checkTime
        '''
        return self.__checkTime
    
    def getLastModified(self):
        '''
        Get method that returns that last modified date of the file that is represented by the entity self.__childLink
        
        @return: URLLinks.__lastModified    eg : 'Wed, 11 Aug 2010 22:40:44 GMT'
        '''
        return self.__lastModified
    
    def getInfo(self):
        '''
        Get method that returns the info string that belongs to the Object. Usually an Exception / any other entity that is pertaining to the link. 
        
        @return:  URLLinks.__info
        '''
        return self.__info
    
    def getStatus(self):
        '''
        Get Method that returns the Status of the Link under Question. 
        
        @return: URLLinks.__status     Values = Valid / Warning / Error 
        '''
        return self.__status   
    
    def getType(self):
        '''
        Get method that returns the type of the link that is being processed. 
        
        @return: URLLinks.__lType
        '''
        return self.__lType
    
    def getParents(self):
        '''
        Get method that returns the Parent Link information in the form of a Tuple. 
        
        @return: (URLLinks.__parentLink, URLLinks.__parentTitle)
        '''
        return(self.__parentLink, self.__parentTitle)
    
    def get(self):
        '''
        Get method that returns the link information in the form of a tuple. 
        
        @return: (URLLinks.__childLink, URLLinks.__childTitle)
        '''
        return(self.__childLink, self.__childTitle)
    
    def setParentLink(self, parentLink):
        self.__parentLink = parentLink
        
    def setParentTitle(self, parentTitle):
        self.__parentTitle = parentTitle
        
    def setChildLink(self, childLink):
        self.__childLink = childLink
        
    def setChildTitle(self, childTitle):
        self.__childTitle = childTitle
        
    def setProcessed(self, isProcessed):
        self.__isProcessed = isProcessed
        
    def setBroken(self, isBroken):
        self.__isBroken = isBroken
    
    def setSize(self, size):
        self.__size = size
        
    def setDLTime(self, dlTime):
        self.__dlTime = dlTime
    
    def setCheckTime(self, checkTime):
        self.__checkTime = checkTime
        
    def setLastModified(self, lastModified):
        self.__lastModified = lastModified
        
    def setInfo(self, info):
        self.__info = info
        
    def setStatus(self, status):
        self.__status = status
    
    def setType(self, lType):
        self.__lType = lType
            
    def setParent(self, parentLink, parentTitle):
        self.__parentLink = parentLink
        self.__parentTitle = parentTitle
    
    def set(self, childLink, childTitle):
        self.__childLink = childLink
        self.__childTitle = childTitle
        
    def info(self):
        '''
            Custom Function Writtten to extract Info from the Object that can be printed easily. 
        '''
        infoString = ''
        infoString += '\nCurrent URL           : ' + str(self.getChildLink())
        infoString += '\nCurrent URL Title     : ' + str(self.getChildTitle()) 
        infoString += '\nParent URL            : ' + str(self.getParentLink())
        infoString += '\nParent Title          : ' + str(self.getParentTitle())
        infoString += '\nStatus                : ' + str(self.getStatus())
        infoString += '\nIs Broken             : ' + str(self.isBroken())
        infoString += '\nIs Processed          : ' + str(self.isProcessed())
        infoString += '\nFile Size             : ' + str(self.getSize())
        infoString += '\nLink Type             : ' + str(self.getType())
        infoString += '\nDownload Time         : ' + str(self.getDLTime())
        infoString += '\nProcessing Time       : ' + str(self.getCheckTime())
        infoString += '\nLast Modified         : ' + str(self.getLastModified())
        infoString += '\nInfo                  : ' + str(self.getInfo())
        return infoString
    
    def getCount(self):
        retData = []
        __errCount = 0
        __warCount = 0
        __exeCount = 0
        __skiCount = 0
        __timCount = 0.0
        retData.append(len(self.getChildren()))
        for item in self.getChildren():
            if ( 'ERROR' in item.getStatus().upper()):
                __errCount += 1
            elif ( 'WARNING' in item.getStatus().upper()):
                __warCount += 1
            elif ( 'EXEMPTED' in item.getStatus().upper()):
                __exeCount += 1
            elif ( 'SKIPPED' in item.getStatus().upper()):
                __skiCount += 1
            else:
                pass
            
            if ( isinstance(item.getCheckTime(),float)):
                __timCount += item.getCheckTime() 
            
        retData.append(__errCount)
        retData.append(__warCount)
        retData.append(__exeCount)
        retData.append(__skiCount)
        retData.append(__timCount)
        return retData
    
    def __getStatusRow(self):
        rowString = '<td bgcolor="#FFFFCC" class="$rowClassName">$statusInfo</td>'
        statusInfo = self.getStatus().upper()

        if ( 'ERROR' in statusInfo and ':' in statusInfo):
            rowString = re.sub('\$rowClassName', 'error', rowString) 
        elif ( statusInfo == 'OK' ):
            rowString = re.sub('\$rowClassName', 'ok', rowString)
        else:
            rowString = re.sub('\$rowClassName', 'other', rowString)
            
        rowString = re.sub('\$statusInfo', statusInfo, rowString)
        return rowString
    
    def __getIsProcessed(self):
        rowString = '<td class="$rowClassName">$isProcessed</td>'
        if ( self.isProcessed()):
            rowString = re.sub('\$rowClassName', 'ok', rowString)
        else:
            rowString = re.sub('\$rowClassName', 'other', rowString)
            
        rowString = re.sub('\$isProcessed', str(self.isProcessed()), rowString)
        return rowString
    
    def __getIsBroken(self):
        rowString = '<td bgcolor="#FFFFCC" class="$rowClassName">$isBroken</td>'
        
        if ( self.isBroken()):
            rowString = re.sub('\$rowClassName', 'ok', rowString)
        else:
            rowString = re.sub('\$rowClassName', 'other', rowString)
            
        rowString = re.sub('\$isBroken', str(self.isBroken()), rowString)
        return rowString
    
    def getReportInfo(self):
        retData = []
        retData.append(self.getChildLink())
        retData.append(self.getChildTitle())
        retData.append(self.getParentLink())
        retData.append(self.getParentTitle())
        retData.append(self.__getStatusRow())
        retData.append(self.__getIsProcessed())
        retData.append(self.__getIsBroken())
        retData.append(self.getType())
        retData.append(self.getSize())
        retData.append(self.getDLTime())
        retData.append(self.getLastModified())
        retData.append(self.getCheckTime())
        retData.append(self.getInfo())
        return retData