'''
Created on Oct 19, 2012
the L(config) module contains the L(FedExConfig) class, which is passed to the fedex api calls. it stores
the information about the ups security key and account information for subsequent calls
@author: PabloH
'''
import os
import sys

class UPSConfig(object):
    '''
    Base Configuration class that is used for the different UPS Soap calls
    These are generally passed to the fedex request classes as arguments,
    You may instantiate a L(FedExConfig)  object with minimal C{ke} and C password arguments and set the instance variable documented
    below '''
    
    def __init__(self,key,username,password,upsaccount,wsdl_path=None,endpoint=None):
        """
        @type key: L{str}
        @param key: UPS Developer Key
        @type username: L{str}
        @param username: UPS Developer username
        @type password: L{str}
        @param username: UPS Developer Password
        @type wsdl_path: L{str}
        @param username: UPS location of webserver
        @type endpoint: L{str}
        @param username: UPS url location
        """
        self.key = key
        """@ivar: Developer test key"""
        self.username = username
        """@ivar: username"""
        self.password = password
        """@ivar: password"""
        self.wsdl = wsdl_path
        """@ivar:wsdl location"""
        self.endpoint = endpoint
        """@ivar:endpoint information"""
        self.upsAccount = upsaccount
        """@ivar:upsAccount for the Shipper"""
        
        if wsdl_path==None:
            self.wsdl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'wsdl')
        else:
            self.wsdl_path = wsdl_path
             
                                
    
