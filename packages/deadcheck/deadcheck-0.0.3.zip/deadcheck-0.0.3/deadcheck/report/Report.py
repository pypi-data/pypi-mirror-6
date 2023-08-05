'''
Created on Dec 12, 2013

@author: harsnara
'''
__version__ = "0.0.1"
__author__ = "Harsha Narayana"
__date__ = "Dec 12, 2013"

import os
import re 

class Report(object):
    '''
    classdocs
    f = open('../templates/table.template')
        print f.read()
    '''

    def __init__(self, dataSet, outFile, templatePath):
        '''
        Constructor
        '''
        self.__dataSet = dataSet
        self.__outFile = outFile 
        self.__outDir = None
        if ( templatePath == None):
            self.__templatePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Templates')
        else:
            self.__templatePath = templatePath 
        #self.__setOutDir()
        
    def __setOutDir(self):
        self.__outDir = os.path.dirname(self.__outFile)
    
    def __getTemplatePath(self):
        return self.__templatePath
        
    def getOutDir(self):
        return self.__outDir
    
    def getOutFile(self):
        return self.__outFile
    
    def getDataSet(self):
        return self.__dataSet
    
    def generate(self):
        self.__generateHead()
        obj = self.getDataSet()
        self.__writeTableData(obj)
        self.__generateTail(obj)
        return self.getOutFile()
    
    def __writeTableData(self, obj):
        template = self.__getTableTemplate()
        outFile = self.getOutFile()
        with open(outFile, 'a') as oStream:
            for element in obj.getChildren():
                info = element.getReportInfo()
                info = [ str(item) for item in info]
                for line in template:
                    line = line.lstrip().rstrip()
                    if ( '$cLinkUrl' in line ):
                        line = re.sub('\$cLinkUrl', info[0], line)
                    
                    if ( '$cLinkTitle' in line ):
                        line = re.sub('\$cLinkTitle', info[1], line)
                        
                    if ( '$pLinkUrl' in line ):
                        line = re.sub('\$pLinkUrl', info[2], line)
                    
                    if ( '$pLinkTitle' in line ):
                        line = re.sub('\$pLinkTitle', info[3], line)
                    
                    if ( '$statusInfo' in line ):
                        line = re.sub('.*', info[4], line)
                    
                    if ( '$isProcessed' in line ):
                        line = re.sub('.*', info[5], line)
                        
                    if ( '$isBroken' in line ):
                        line = re.sub('.*', info[6], line)
                    
                    if ( '$linkType' in line):
                        line  = re.sub('\$linkType', info[7], line)
                        
                    if ( '$fileSize' in line ):
                        line = re.sub('\$fileSize', info[8], line)
                    
                    if ( '$downTime' in line ):
                        line = re.sub('\$downTime', info[9], line)
                        
                    if ( '$lastChanged' in line ):
                        line = re.sub('\$lastChanged', info[10], line)
                        
                    if ( '$processTime' in line ):
                        line = re.sub( '\$processTime', info[11], line)
                        
                    if ( '$addInfo' in line ):
                        line = re.sub( '\$addInfo', info[12], line)
                    oStream.write('%s' %(line))
            oStream.close()
                
    def __getTableTemplate(self):
        template = []
        tableFile = os.path.abspath(os.path.join(self.__getTemplatePath(), 'table.template')) 
        with open(tableFile, 'r') as iStream:
            for line in iStream:
                line = line.lstrip().rstrip()
                template.append(line)
                
        return template
    
    def __generateHead(self):
        cssPath = os.path.abspath(os.path.join(self.__getTemplatePath(), 'Report.css'))
        headFile = os.path.abspath(os.path.join(self.__getTemplatePath(), 'head.template'))
        outFile = self.getOutFile()
        with open(outFile, 'w') as oStream:
            with open(headFile, 'r') as iSteam:
                for line in iSteam:
                    if ( '$cssFilePath' in line):
                        line = re.sub('\$cssFilePath', repr(cssPath), line.lstrip().rstrip())
                    line = line.lstrip().rstrip()
                    oStream.write('%s\n' %(line))
        
        oStream.close()
        iSteam.close()
        
    def __generateTail(self, obj):
        iCount = obj.getCount()
        iCount = [str(item) for item in iCount]
        tailFile = os.path.abspath(os.path.join(self.__getTemplatePath(), 'tail.template'))
        outFile = self.getOutFile()
        with open(outFile,'a') as oStream:
            with open(tailFile, 'r') as iStream:
                for line in iStream:
                    line = line.lstrip().rstrip()
                    if ( '$totalLinkCount' in line):
                        line = re.sub('\$totalLinkCount', iCount[0], line)
                    
                    if ( '$totalErrorCount' in line):
                        line = re.sub('\$totalErrorCount', iCount[1], line)
                        
                    if ( '$totalWarningCount' in line):
                        line = re.sub('\$totalWarningCount', iCount[2], line)
                        
                    if ( '$totalExemptCount' in line):
                        line = re.sub('\$totalExemptCount', iCount[3], line)
                        
                    if ( '$totalSkipCount' in line):
                        line = re.sub('\$totalSkipCount', iCount[4], line)
                        
                    if ( '$totalTimeCount' in line):
                        line = re.sub('\$totalTimeCount', iCount[5], line)
                        
                    oStream.write('%s' %(line))
        oStream.close()
        iStream.close()
        
    