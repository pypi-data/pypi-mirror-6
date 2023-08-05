'''
Created on Dec 2, 2013

@author: harsnara
'''
# Imports necessary for Running the script.

import argparse
from deadcheck import deadcheck

argParse = argparse.ArgumentParser(description='Parse Command-line arguments for deadcheck.')

argParse.add_argument('-url', action='store', type=str, dest='-url',
                      metavar='BaseURLToAnalyze', required=True, help='Base URL of the Website on which the script is to be run to check for Deadlinks')

argParse.add_argument('-proxy', action='store', type=str, dest='-proxy',
                      metavar='ProxyURL', help='Proxy URL in http(s)://<proxyAddress>:<port> format.')

argParse.add_argument('-username', action='store', type=str, dest='-username',
                      metavar='UserName', help='User Name to be used for accessing password protected page.')

argParse.add_argument('-password', action='store', type=str, dest='-password',
                      metavar='Passwrord', help='Password to be used for accessing password protected page.')

argParse.add_argument('-baseurl', action='store', type=str, dest='-baseurl',
                      metavar='BaseURL', help='Super URL to be used for Protected pages. If Not provided, the Base URL of the page being analyzed is used as base URL for Authorization.')

argParse.add_argument('-out', action='store', type=argparse.FileType('w'), dest='-out',
                      metavar='OutputFile', help='Output file to which the data is to be dumped in HTML foramt.')

argParse.add_argument('-exempt', action='store', type=str, dest='-exempt',
                      metavar='ExemptionsFile', help='File containing a list of links that are to be excluded from analysis. One link per line.')

argParse.add_argument('-log', action='store', type=str, dest='-log',
                      metavar='LogFile', help='Log file that needs to be used for dumping the log contents.')

argParse.add_argument('-cli', action='store', type=bool, dest='-cli',
                      default=True, metavar='TRUE|FALSE', help='True | False based on the CLI input. Defaults to True when run from CLI. Can be set to FALSE. This will disable message dispaly.')

args = argParse.parse_args()
deadcheck.init(args.__dict__)
deadcheck.process()
links = deadcheck.analyze()