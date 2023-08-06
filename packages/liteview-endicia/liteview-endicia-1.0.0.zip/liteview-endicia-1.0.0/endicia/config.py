'''
Created on Oct 19, 2012
the L(config) module contains the L(EndiciaConfig) class, which is passed to the endicia api calls. it stores
the information about the endicia account information for subsequent calls
@author: PabloH
'''
import os
import sys

class EndiciaConfig(object):
    '''
    Base Configuration class that is used for the different Endicia Soap calls
    These are generally passed to the Endicia request classes as arguments,
    You may instantiate a L(EndiciaConfig)  object with minimal C{ke} and C password arguments and set the instance variable documented
    below '''
    
    def __init__(self,key,username,password,endicia_account,wsdl_path=None,endpoint=None):
        """
        @type key: L{str}
        @param key: Endicia Partner Key
        @type username: L{str}
        @param username: Edicia Developer username
        @type password: L{str}
        @param username: Endicia Developer Password
        @type wsdl_path: L{str}
        @param username: Endicia location of webserver
        @type endpoint: L{str}
        @param username: Endicia url location
        """
        self.key = key
        """@ivar: Developer key or program making the call to Endicia"""
        self.username = username
        """@ivar: username"""
        self.password = password
        """@ivar: password"""
        self.wsdl = wsdl_path
        """@ivar:wsdl location"""
        self.endpoint = endpoint
        """@ivar:endpoint information"""
        self.endiciaAccount = endicia_account
        """@ivar:endiciaAccount for the Shipper sending the package"""
        
        if wsdl_path==None:
            self.wsdl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'wsdl')
        else:
            self.wsdl_path = wsdl_path
             
                                
    
