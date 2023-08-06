'''
Created on Nov 19, 2012
Ship Service Module
====================
This package contains the shipping methods defined by Endicia's 
Ship Service WSDL File. each is encapsulated in a class for easy access
for more details on each, refer to the respective class's documentation
@author: Pablo Hernandez
'''
from datetime import datetime
from suds.sax.element import Element
from suds.plugin import MessagePlugin
from ..base_service import EndiciaBaseService

class EndiciaGetPostageLabelRequest(EndiciaBaseService):
    
    def __init__(self,config_obj, *args, **kwargs):
        """
        The optional keyword args detailed on L(EndiciaBaseService)
        apply here as well
        
        @type config_obj:  L{EndiciaConfig}
        @param config_obj: a Valid Endicia Config object
        """
        self._config_obj = config_obj
        
        self.RequestedPostageLabel = None
        """@ivar : Holds the requested shipment WSDL Object"""
        super(EndiciaGetPostageLabelRequest,self).__init__(self._config_obj,'EwsLabelService.asmx?WSDL',*args,**kwargs)
        
    def _prepare_wsdl_objects(self):
        self.RequestedPostageLabel = self.create_wsdl_object_of_type('LabelRequest')
        self.RequestedPostageLabel.AccountID = self._config_obj.endiciaAccount
        self.RequestedPostageLabel.RequesterID = self._config_obj.key
        self.RequestedPostageLabel.PassPhrase = self._config_obj.password
        
    def _assemble_and_send_request(self):
        
        response = self.client.service.GetPostageLabel(self.RequestedPostageLabel)
        
        return response
        
        
class EndiciaChangePassPhrase(EndiciaBaseService):
    def __init__(self,config_obj, *args, **kwargs):
        """
        The optional keyword args detailed on L(EndiciaBaseService)
        apply here as well
        
        @type config_obj:  L{EndiciaConfig}
        @param config_obj: a Valid Endicia Config object
        """
        self._config_obj = config_obj
        
        self.RequestedChangePassPhrase = None
        """@ivar : Holds the requested shipment WSDL Object"""
        super(EndiciaChangePassPhrase,self).__init__(self._config_obj,'EwsLabelService.asmx?WSDL',*args,**kwargs)
        
    def _prepare_wsdl_objects(self):
        self.RequestedChangePassPhrase = self.create_wsdl_object_of_type('ChangePassPhraseRequest')
        self.RequestedChangePassPhrase.RequesterID = self._config_obj.key
        self.RequestedChangePassPhrase.CertifiedIntermediary.AccountID = self._config_obj.endiciaAccount
        self.RequestedChangePassPhrase.CertifiedIntermediary.PassPhrase = self._config_obj.password
        
    def _assemble_and_send_request(self):
        
        response = self.client.service.ChangePassPhrase(self.RequestedChangePassPhrase)
        
        return response        
        

        
class EndiciaBuyPostage(EndiciaBaseService):
    def __init__(self,config_obj, *args, **kwargs):
        """
        The optional keyword args detailed on L(EndiciaBaseService)
        apply here as well
        
        @type config_obj:  L{EndiciaConfig}
        @param config_obj: a Valid Endicia Config object
        """
        self._config_obj = config_obj
        
        self.RequestedBuyPostage = None
        """@ivar : Holds the requested shipment WSDL Object"""
        super(EndiciaBuyPostage,self).__init__(self._config_obj,'EwsLabelService.asmx?WSDL',*args,**kwargs)        
    def _prepare_wsdl_objects(self):
        self.RequestedBuyPostage = self.create_wsdl_object_of_type('RecreditRequest')
        self.RequestedBuyPostage.RequesterID = self._config_obj.key
        self.RequestedBuyPostage.CertifiedIntermediary.AccountID = self._config_obj.endiciaAccount
        self.RequestedBuyPostage.CertifiedIntermediary.PassPhrase = self._config_obj.password    
        
    def _assemble_and_send_request(self):
        
        response =self.client.service.BuyPostage(self.RequestedBuyPostage)
        
        return response            
    
class EndiciaRefundRequest(EndiciaBaseService):
    def __init__(self,config_obj, *args, **kwargs):
        """
        The optional keyword args detailed on L(EndiciaBaseService)
        apply here as well
        
        @type config_obj:  L{EndiciaConfig}
        @param config_obj: a Valid Endicia Config object
        """
        self._config_obj = config_obj
        
        self.RequestEndiciaRefund = None
        """@ivar : Holds the requested shipment WSDL Object"""
        super(EndiciaRefundRequest,self).__init__(self._config_obj,'EwsLabelService.asmx?WSDL',*args,**kwargs)    

    def _prepare_wsdl_objects(self):
        self.RequestEndiciaRefund = self.create_wsdl_object_of_type('RefundRequest')
        self.RequestEndiciaRefund.RequesterID = self._config_obj.key
        self.RequestEndiciaRefund.CertifiedIntermediary.AccountID = self._config_obj.endiciaAccount
        self.RequestEndiciaRefund.CertifiedIntermediary.PassPhrase = self._config_obj.password   

    def _assemble_and_send_request(self):
        
        response =self.client.service.GetRefund(self.RequestEndiciaRefund)
        
       
        return response              
        
    
            
    