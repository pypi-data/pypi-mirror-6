'''
Created on Nov 29, 2013

@author: harshanarayana
'''
## Imports Necessary for Processing. 
import logging
import urllib2
from HTMLParser import HTMLParser

## File information. 
__verison__ = "0.0.1"

## Global Variables
    # Variables Used for Storing Arguments. 
args = {}

    # Variable Used for storing Parent Link Info. 
pLinkData = {}
pLinkData['__link'] = None
pLinkData['__title'] = None

__extractedLinks = []
## Custom Class For Handling URL Link Information. 
class URLLinks(object):
    
    def __init__(self, parentLink, parentTitle, childLink, childTitle, isProcessed = False, isBroken = False, linkType = None, info = None):
        self.parentLink = parentLink
        self.parentTitle = parentTitle
        self.childLink = childLink
        self.childTitle = childTitle
        self.isProcessed = isProcessed
        self.isBroken = isBroken
        self.linkType = linkType
        self.info = info
        
    def getParentInfo(self):
        return (self.parentLink, self.parentTitle)
    
    def getChildInfo(self):
        return (self.childLink, self.childTitle, self.linkType)
    
    def getIsBroken(self):
        return self.isBroken
    
    def getIsProcessed(self):
        return self.isProcessed
    
    def setBroken(self, value):
        self.isBroken = value
    
    def setProcessed(self, value):
        self.isProcessed = value
    
    def setLinkType(self, value):
        self.linkType = value
    
    def get(self):
        return self.__dict__
    
    def getInfo(self):
        return self.info
    
    def setInfo(self, info):
        self.info = info
        
## Custom Class For Parsing and Extracting Info from the URL 
class MyHTMLParser(HTMLParser):
    __startTitle = False
    __link = None
    __title = None
    __isLink = False
    def handle_starttag(self, tag, attrs):
        if ( tag.upper() == 'TITLE' and getParentData()[1] == None):
            MyHTMLParser.__startTitle = True
        if ( tag.upper() == 'A'):
            for att in attrs:
                if att[0].upper() == 'HREF':
                    MyHTMLParser.__link = att[1]
                    MyHTMLParser.__isLink = True
                    
    def handle_data(self, data):
        if ( getParentData()[1] == None and MyHTMLParser.__startTitle ):
            setParentTitle(data)
        if ( MyHTMLParser.__isLink and MyHTMLParser.__link != None):
            MyHTMLParser.__title = data
        
    def handle_endtag(self, tag):
        if ( getParentData()[1] != None and MyHTMLParser.__startTitle):
            MyHTMLParser.__startTitle = False
        if ( MyHTMLParser.__link != None and MyHTMLParser.__title != None and MyHTMLParser.__isLink):
            MyHTMLParser.__isLink = False
            createParsedLinkObject(MyHTMLParser.__link, MyHTMLParser.__title)

def createParsedLinkObject(cLink, cTitle):
    (pLink, pTitle) = getParentData()
    cLink.lstrip().rstrip()
    cTitle.lstrip().rstrip()
    if ( cTitle == None):
        cTitle = '<Unknown>'
    if ( cLink.startswith('/#') or cLink.startswith('#') or cLink.startswith('./') or cLink.startswith('../') or cLink.startswith('/') or pLink not in cLink):
        import urlparse
        cLink = urlparse.urljoin(pLink, cLink)
        
    urlObject = URLLinks(pLink, pTitle, cLink, cTitle)
    __extractedLinks.append(urlObject)
     
# Function To handle the Arguments. Will work both for Direct Import method / run from another script. 
def init(argList):
    
    if argList.has_key('-cli'):
        args['__cli'] = argList['-cli']
    else:
        args['__cli'] = False
        
    for key in argList.keys():
        if ( key == '-proxy'):
            args['__proxy'] = argList['-proxy']
        elif ( key == '-username'):
            args['__username'] = argList['-username']
        elif ( key == '-password'):
            args['__password'] = argList['-password']
        elif ( key == '-baseurl'):
            args['__auth_base'] = argList['-baseurl']
        elif ( key == '-url'):
            args['__url'] = argList['-url']
        elif ( key == '-out'):
            args['__output'] = argList['-out']
        elif ( key == '-exempt'):
            args['__exempt'] = argList['-exempt']
        elif ( key == '-log'):
            args['__log'] = argList['-log']
        elif ( key == '-cli'):
            args['__cli'] = argList['-cli']
        else:
            warning('Invalid argument %s . Skipping...' %(key))
                    
    checkAndSetLog()
    verifyAndValidateArgs()
    checkAndSetUrlLib()    
    
def checkKey(keyName):
    return args.has_key(keyName) and args[keyName] != None

def setParentLink(url):
    url = url.lstrip().rstrip()
    pLinkData['__link'] = url
    
def setParentTitle(title):
    title = title.lstrip().rstrip()
    if ( title == None):
        title = '<Unknown>'
    pLinkData['__title'] = title
    
def getParentData():
    return(pLinkData['__link'], pLinkData['__title'])

def verifyAndValidateArgs():
    if ( not checkKey('__url')):
        error('Please make sure input contains a key named \'-url\' and a value corresponding to it. This is used as the Base URL for Analysis.')
        exit(-1)
    
    if ( not checkKey('__proxy')):
        warning('No proxy information provided. If you are running this module on a machine that access internet through a Proxy, this test might fail.')

    if ( checkKey('__username') and checkKey('__password')):
        if ( not checkKey('__auth_base')):
            message('No base URL provided for Authentication purpose. Link being analyzed itself is set as base URL for Authentication purpose.')
    else:
        warning('Insufficient Login information provided for Authentication. All protected Links will be excluded from analysis.')
            
    if ( not checkKey('__log')):
        warning('No Logfile information provided. No log information will be generated.')
    
    if ( not checkKey('__output')):
        warning('No Outputfile information Provided, hence no report file will be generated.')
        
    if ( not checkKey('__exempt')):
        warning('No file containing list of Exempted links is provided. All the links are considered valid for analysis.')
    
    if ( not checkKey('__cli')):
        args['__cli'] = False
        
def checkAndSetLog():
    if ( checkKey('__log')):
        logging.basicConfig(filename=args['__log'], level=logging.DEBUG, format='%(name)s : %(levelname)s : %(message)s')
    else:
        logging.basicConfig(level=logging.DEBUG, format='%(name)s : %(levelname)s : %(message)s')
 
def checkAndSetUrlLib():
    proxy = None
    auth = None
    opener = None
    
    if ( checkKey('__proxy')):
        proxy = urllib2.ProxyHandler({'http':args['__proxy'], 'https' : args['__proxy']})
        opener = urllib2.build_opener(proxy)
    
    if ( checkKey('__username') and checkKey('__password') and args['__username'] != None and args['__password'] != None):
        passManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        if ( checkKey('__auth_base') and args['__auth_base'] != None):
            passManager.add_password(None, args['__auth_base'], args['__username'], args['__password'])
        else:
            passManager.add_password(None, args['__url'], args['__username'], args['__password'])
        auth = urllib2.HTTPBasicAuthHandler(passManager)
        opener = urllib2.build_opener(auth)
    
    if ( opener != None):
        urllib2.install_opener(opener)

def getData(url, level=1):
    try:
        data = urllib2.urlopen(url)
        return (data.read(),None)
    except urllib2.HTTPError, e:
        if ( level == 0 ):
            error('HTTPError = ' + str(e.code))
            exit(-1)
        else:
            return (None, str(e.code))
    except urllib2.URLError, e:
        if ( level == 0 ):
            error('URLError = ' + str(e.reason))
            exit(-1)
        else:
            return (None, str(e.reason))
    except Exception:
        import traceback
        if ( level == 0 ):
            error('generic exception: ' + traceback.format_exc())
            exit(-1)
        else:
            return (None, traceback.format_exc())
    
def process(urlToProcess = None):
    parser = MyHTMLParser()
    if ( urlToProcess == None):
        setParentLink(args['__url'])
        data = getData(args['__url'],0)
        parser.feed(data[0])
        return __extractedLinks
    else:
        setParentLink(urlToProcess)
        data = getData(urlToProcess)
        parser.feed(data[0])
        return __extractedLinks

def getLinks():
    return __extractedLinks

def analyze(url = None):
    if ( url == None):
        for link in __extractedLinks:
            l = link.getIsProcessed()
            if ( not l):
                data = ()
                childLink = link.getChildInfo()[0]
                if ( 'javascript' not in childLink.lower()):
                    data = getData(childLink)
                else:
                    data = ('None','Links within Javascript Callback are not yet handled.')
                    #link.setInfo('Links within Javascript Callback are not yet handled.')
                    warning('Links within Javascript Callback are not yet handled.')    
                if ( data[0] != None ):
                    link.setProcessed(True)
                    link.setBroken(False)
                else:
                    link.setProcessed(True)
                    link.setBroken(True)
                    link.setInfo(data[1])
        return __extractedLinks
    else:
        data = None
        data = getData(url)
        if ( data != None ):
            return False
        else:
            return True
        
# Message Display Functions using Logging.
def warning(message):
    if args['__cli'] :
        logging.warning(message)

def error(message):
#    if args['__cli'] :
    logging.error(message)

def message(message):
    if args['__cli'] :
        logging.info(message)
