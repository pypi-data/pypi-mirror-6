'''
Created on Nov 19, 2012
Ship Service Module
====================
This package contains the shipping methods defined by Endicia's 
Other Service WSDL File. each is encapsulated in a class for easy access
for more details on each, refer to the respective class's documentation
@author: Pablo Hernandez
'''
from datetime import datetime
from suds.sax.element import Element
from suds.plugin import MessagePlugin
from ..base_service import EndiciaBaseService

class EndiciaSCANRequest(EndiciaBaseService):
    def __init__(self,config_obj, *args, **kwargs):
        """
        The optional keyword args detailed on L(EndiciaBaseService)
        apply here as well
        
        @type config_obj:  L{EndiciaConfig}
        @param config_obj: a Valid Endicia Config object
        """
        self._config_obj = config_obj
        
        self.RequestedSCANRequest = None
        """@ivar : Holds the requested shipment WSDL Object"""
        super(EndiciaSCANRequest,self).__init__(self._config_obj,'ELSServices.cfc?wsdl',*args,**kwargs)    
    def _prepare_wsdl_objects(self):
        self.RequestedSCANRequest = self.create_wsdl_object_of_type('SCANRequest')
        self.RequestedSCANRequest.AccountID = self._config_obj.endiciaAccount
        self.RequestedSCANRequest.RequesterID = self._config_obj.key
        self.RequestedSCANRequest.PassPhrase = self._config_obj.password
        self.RequestedSCANRequest.FormType = '5630'
        
        
    def _assemble_and_send_request(self):
        
        response = self.client.service.SCANRequest(self.RequestedSCANRequest)
        
        return response            