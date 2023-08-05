'''
Created on Nov 29, 2013

@author: harshanarayana

@change:    2013-11-29    Initial Draft
            2013-12-06    Re-Structured the Code to support Data suitable for liche output format. 
            2013-12-10    Minor Chnages made into the Script to support the Report Generation. 
'''

__version__ = "0.0.3"
__date__ = "06th December 2013"
__author__ = "Harsha Narayana"


from ErrorHandler import ArgumentMissingError
from ErrorCodes import ErrorCodes
import logging
import urllib2
from lxml import etree
from URLLinks import URLLinks
import time
import urlparse
import httplib
import re

class Deadcheck(object):
    
    __levelBasedLinks = {}
    __ProcessedLinks = {}
    __exemptedItems = []
        
    def __init__(self, url, proxy=None, username=None, password=None, auth_base=None, verbose=True, log=None, exempt=None, depth=1):
        self._url = url
        self._proxy = proxy
        self._username = username
        self._password = password
        self._auth_base = auth_base
        self._verbose = verbose
        self._log = log
        self._exempt = exempt
        self._depth = depth
        self.__verifyAndValidate()
        self.__checkAndSetUrlLib()
        self.__processBaseURL()

    def getAll(self):
        return Deadcheck.__levelBasedLinks
    
    def get_depth(self):
        return self._depth
    
    def set_depth(self,value):
        self._depth = value
        
    def del_depth(self):
        del self._depth
        
    def get_dict(self):
        return self.__dict__


    def get_url(self):
        return self.__url


    def get_proxy(self):
        return self.__proxy


    def get_verbose(self):
        return self.__verbose


    def get_log(self):
        return self.__log


    def get_exempt(self):
        return self.__exempt


    def __set_url(self, value):
        self.__url = value


    def __set_proxy(self, value):
        self.__proxy = value


    def __set_username(self, value):
        self.__username = value


    def __set_password(self, value):
        self.__password = value


    def __set_auth_base(self, value):
        self.__auth_base = value


    def set_verbose(self, value):
        self.__verbose = value


    def set_log(self, value):
        self.__log = value


    def set_exempt(self, value):
        self.__exempt = value

        
    def __verifyAndValidate(self):
        self.__checkAndSetLog()    
        if ( not self.__checkKey('_url')):
            raise ArgumentMissingError('Paramenter for argument \'-url\' is missing.','-url')
        
        if ( not self.__checkKey('_proxy')):
            self.__printWarning('No Proxy Information provided. If you are running the tool on a machine that accesses internet through Proxy, the check will fail.')
        
        if (self.__checkKey('_username') and self.__checkKey('_password')):
            if ( not self.__checkKey('_auth_base')):
                self.__printWarning('No super URL provided for Authenticating password Protected pages. Base URL will be used instead.')
        else:
            self.__printWarning('No password protected pages will be processed.')
        
        if ( not self.__checkKey('_exempt')):
            self.__printMessage('No exemptions file provided. All the links will be considered valid.')
            
    
    def __checkAndSetUrlLib(self):
        __proxy = None
        __auth = None
        __opener = None
        
        if ( self.__checkKey('_proxy')):
            __proxy = urllib2.ProxyHandler({'http':self.__dict__['_proxy'], 'https':self.__dict__['_proxy']})
            __opener = urllib2.build_opener(__proxy)
            
        if ( self.__checkKey('_username') and self.__checkKey('_password')):
            passManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            if ( self.__checkKey('_auth_base')):
                passManager.add_password(None, self.__dict__['_auth_base'], self.__dict__['_username'], self.__dict__['_password'])
            else:
                passManager.add_password(None, self.__dict__['_url'], self.__dict__['_username'], self.__dict__['_password'])
            
            __auth = urllib2.HTTPBasicAuthHandler(passManager)
            __opener = urllib2.build_opener(__auth)
            
        if ( __opener != None ):
            urllib2.install_opener(__opener)
            
    def __checkAndSetLog(self):
        if ( self.__checkKey('_verbose')):
            if ( self.__checkKey('_log')):
                logging.basicConfig(level=logging.DEBUG, filename=self.__dict__['_log'], format='%(name)s : %(levelname)s : %(message)s')
            else:
                logging.basicConfig(level=logging.DEBUG, format='%(name)s : %(levelname)s : %(message)s')
        else:
            logging.basicConfig(level=logging.ERROR)
    
    def __size(self, size):
        for x in ['bytes','KB','MB','GB']:
            if size < 1024.0 and size > -1024.0:
                return "%3.1f%s" % (size, x)
            size /= 1024.0
        return "%3.1f%s" % (size, 'TB')
     
    def __checkIfError(self, value):
        if ( 'HTTPError' in value or 'URLError' in value or 'HTTPException' in value or 'Generic Exception' in value):
            return True
        else:
            return False
    def __raiseError(self, value, *url):
        if ( value[0] == 'HTTPError'):
            eCode = ErrorCodes(int(value[1]))
            raise urllib2.HTTPError(url[0], int(value[1]), eCode.getError(), None, None)
        elif ( value[0] == 'URLError'):
            raise urllib2.URLError(value[1])
        elif ( value[0] == 'HTTPException'):
            raise httplib.HTTPException(value[1])
        elif ( value[0] == 'Generic Exception'):
            raise Exception(value[0] + ' : ' + value[1])
        
    def __processBaseURL(self):
        ts = time.time()
        handle = self.__getDataFromURL(self.__dict__['_url'])
        ted = time.time()
        dlTime = ted - ts
        if ( self.__checkIfError(handle)):
            if ( handle[0] == 'HTTPError'):
                eCode = ErrorCodes(int(handle[1]))
                einfo = eCode.getError()[1]
            else:
                einfo = handle[1]
            urlObject = URLLinks(self.__dict__['_url'], None, self.__dict__['_url'], None, isProcessed=True, isBroken=True, 
                                 size='<Unknown>', dlTime=dlTime, checkTime=dlTime, lastModified='<Unknwon>', info=einfo,status=handle[0] + ' : ' + handle[1], lType='<Unknwon>')
            self.__printError(handle[0] + ' : ' + handle[1] + ' : ' + einfo)
            self.__raiseError(handle, self.__dict__['_url'])
            return urlObject
        else:
            ts = time.time()
            htmlData = urllib2.urlopen(self.__dict__['_url'])
            ted = time.time()
            data = etree.HTML(htmlData.read())
            dlTime  =   ted - ts
            title = self.__getURLTitle(data)
            links = self.__links(data)
            (lTtype, lastChagned, size) = self.__getURLInfo(handle)
            status = 'OK'
            urlObj = URLLinks(self.__dict__['_url'], title, self.__dict__['_url'], title, isProcessed=True, isBroken=False, size=size, dlTime=dlTime, 
                              lastModified=lastChagned, info='Successfully Processed', status=status, lType=lTtype)
            
            for link in links:
                cLink = str(link.attrib['href']).lstrip().rstrip()
                if ( cLink.startswith('#') or cLink.startswith('.') or cLink.startswith('..') or self.__dict__['_url'] not in cLink):
                    cLink = urlparse.urljoin(self.__dict__['_url'], cLink)
                
                if ( self.__dict__['_url'] in cLink):
                    cTitle = link.text
                    temp = URLLinks(self.__dict__['_url'], title, cLink, cTitle)
                    urlObj.addChild(temp)
            te = time.time()
            cTime = te - ts
            urlObj.setCheckTime(cTime)
            Deadcheck.__levelBasedLinks[0] = []
            Deadcheck.__levelBasedLinks[0].append(urlObj)
    
    def __loadExempt(self):
        try:
            with open(str(self.__dict__['_exempt'])) as eFile:
                for line in eFile:
                    Deadcheck.__exemptedItems.append(line.lstrip().rstrip())
        except IOError:
            self.__printWarning('Unable to get information from the exceptions file.')
    
    def __checkExempt(self, url):
        exItem = Deadcheck.__exemptedItems
        if ( len(exItem) > 0 ):
            exItem = [ str(item) if not str(item).startswith('*') else '.'+str(item) for item in exItem]
            exItem = '|'.join(exItem)
            pattern = re.compile(exItem)
            match = pattern.match(url, re.I)
            if ( match != None):
                return True
            else:
                return False
        else:
            return False
        
    def process(self):
        self.__loadExempt()
        if ( self.get_depth() == 0 ):
            self.__analyze() 
        else:
            for level in range(self.get_depth()+1):
                Deadcheck.__levelBasedLinks[level+1] = []
                for vobj in self.getAll()[level]:
                    for obj in vobj.getChildren():
                        t1 = time.time()
                        (url, title) = obj.get()
                        if ( not Deadcheck.__ProcessedLinks.has_key(url) and not self.__checkExempt(url) and 'javascript' not in url.lower()):
                            Deadcheck.__ProcessedLinks[url] = 1
                            ts = time.time()
                            handle = self.__getDataFromURL(url)
                            ted = time.time()
                            if ( self.__checkIfError(handle)):
                                if ( handle[0] == 'HTTPError'):
                                    eCode = ErrorCodes(int(handle[1]))
                                    einfo = eCode.getError()[1]
                                else:
                                    einfo = handle[1]
                                obj.setInfo(einfo)
                                obj.setProcessed(True)
                                obj.setBroken(True)
                                obj.setStatus(handle[0] + ' : ' + str(handle[1]))
                                obj.setDLTime(ted-ts)
                                obj.setSize('<Unknown>')
                                obj.setLastModified('<Unknown>')
                                obj.setType('<Unknown>')
                                obj.setCheckTime(ted-ts)
                                
                                print 'Broken ' + str(obj.get()) 
                            else:
                                ts = time.time()
                                htmlData = urllib2.urlopen(url)
                                ted = time.time()
                                data = etree.HTML(htmlData.read())
                                dlTime = ted - ts
                                title = self.__getURLTitle(data)
                                links = self.__links(data)
                                (lTtype, lastChagned, size) = self.__getURLInfo(htmlData)
                                status = 'OK'
                                urlObj = URLLinks(url, title, url, title, isProcessed=True, isBroken=False, size=size, dlTime=dlTime, lastModified=lastChagned, 
                                                  info='Successfully Processed', status=status, lType=lTtype)
                                
                                for link in links:
                                    cLink = str(link.attrib['href']).lstrip().rstrip()
                                    if ( cLink.startswith('#') or cLink.startswith('.') or cLink.startswith('..') or url not in cLink):
                                        cLink = urlparse.urljoin(url, cLink)
                                    
                                    if ( self.__dict__['_url'] in cLink):
                                        cTitle = link.text
                                        temp = URLLinks(url, title, cLink, cTitle, status='UNPROCESSED')
                                        urlObj.addChild(temp)
                                te = time.time()
                                cTime = te - ts
                                urlObj.setCheckTime(cTime)
                                Deadcheck.__levelBasedLinks[level+1].append(urlObj)
                                t2 = time.time()
                                obj.setInfo('Successfully Processed.')
                                obj.setProcessed(True)
                                obj.setBroken(False)
                                obj.setStatus('OK')
                                obj.setDLTime(dlTime)
                                obj.setSize(size)
                                obj.setLastModified(lastChagned)
                                obj.setType(lTtype)
                                obj.setCheckTime(t2-t1)
                        else:
                                if ( self.__checkExempt(url)):
                                    obj.setInfo('Exempted based on the Input file : ' + self.__dict__['_exempt'])
                                    obj.setStatus('EXEMPTED')
                                elif ( 'javascript' in url ):
                                    obj.setInfo('Javascript Links are not processed. Implementation underway.')
                                    obj.setStatus('WARNING')
                                else:
                                    obj.setInfo('URL Already Processed. Will not be processed again.')
                                    obj.setStatus('SKIPPED')    
                                obj.setProcessed(True)
                                obj.setBroken(False)
                                obj.setDLTime(None)
                                obj.setSize(None)
                                obj.setLastModified(None)
                                obj.setType(None)
                                obj.setCheckTime(None)
    def __analyze(self):
        pass        
    def __getURLTitle(self, handle):
        if handle == None:
            title = '<Unknown>'
            return title
        tData = handle.find('.//title')
        if tData == None:
            title = '<Unknown>'
        else:
            title = tData.text
        
        return title
    
    def __getURLInfo(self, handle):
        if ( handle.info().dict.has_key('last-modified')):
            lastModified = handle.info()['last-modified']
        else:
            lastModified = '<Unknown>'
        
        if ( handle.info().dict.has_key('content-length')):
            size = self.__size(int(handle.info()['content-length']))
        else:
            size = '<Unknown>'
        
        linkType = handle.info().gettype()
        
        return (linkType, lastModified, size)
    
    def __links(self, handle):
        if handle == None:
            return []
        return handle.findall('.//*[@href]')
            
    def __getDataFromURL(self, urlLink):
        try:
            htmlData = urllib2.urlopen(urlLink, timeout=10)
            return (htmlData)
        except urllib2.HTTPError, e:
            error = ('HTTPError', str(e.getcode()))
            return error
        except urllib2.URLError, e:
            error = ('URLError', str(e.reason))
            return error
        except httplib.HTTPException, e:
            error = ('HTTPException', str(e.message))
            return error
        except Exception, e:
            error = ('Generic Exception', e.message)
            return error
            
    def __printMessage(self, message):
        logging.info(message)
        
    def __printWarning(self, message):
        logging.warning(message)
        
    def __printError(self, message):
        logging.error(message)
                    
    def __checkKey(self,key):
        return self.__dict__.has_key(key) and self.__dict__[key] != None        