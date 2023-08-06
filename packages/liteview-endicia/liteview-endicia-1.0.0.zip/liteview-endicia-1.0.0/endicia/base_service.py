'''
Created on Nov 15, 2012
the L(base service) module contains classes that form the low level foundations of the web service API, 
@author: Pablo Hernandez
'''
import os
import logging
import suds
from suds.client import Client
from suds.sax.element import Element

class EndiciaBaseServiceException(Exception):
    """
    Exception: Serves as the base exception that other service-related exception objects are sub-classed from
    """
    def __init__(self,error_code,value):
        self.error_code =error_code
        self.value = value
    def __unicode__(self):
        return "%s (Error Code: %s"% (repr(self.value),self.error_code)
    def __str__(self):
        return self.__unicode__()
    
class EndiciaFailure(EndiciaBaseServiceException):
    """
    Exception: the request could not be handled at this time, this is 
    generally a server problem
    """
    pass

class EndiciaError(EndiciaBaseServiceException):
    """
    Exception: These are generaly problems with the client provided data
    """
    pass

class SchemaValidationError(EndiciaBaseServiceException):
    """
    Exception there is probably a problem in the data you provided
    """
    def __init__(self):
        self.error_code = -1
        self.value = "suds encountered an error validating your data against this service's WSDL schema. Please double-check for missing or invalid values, filling all required fields."

class EndiciaBaseService(object):
    """
    This class is the master class for all Endicia request objects. It gets all of the common SOAP objects created
    via suds and populates them with
    valuues from a L{EndiciaConfig} objects, along with keyword arguments
    via L{__init__}.
    
    @note This object should never be used directly, use one of the included sub classes.
    """
    
    def __init__(self,config_obj,wsdl_name,massage=None, *args, **kwargs):
        """
        This constructor should only be called by children of the class, As is such, only
        the optional keyword arguments caught by C(**kwargs) will 
        be documented
        
        @type customer_transaction_id: L{str}
        @keyword customer_transaction_id:  A User specified identifier to 
        differentiate this transaction from others. This value will be returned with 
        the response from UPS
        """
        
        self.logger = logging.getLogger('endicia')
        """@ivar: Python logger instance with name 'ups'."""
        self.config_obj = config_obj
        """@ivar: The UPS Config OBJ to pull auth into from"""
        
        self.logger.info('Using Production Server.')
        self.wsdl_path  = os.path.join(config_obj.wsdl_path,wsdl_name)
        if massage:
            self.client = Client('%s' % self.wsdl_path,plugins=[massage])
        else:
            self.client = Client('%s' % self.wsdl_path)
        
        self.EndiciaAuthenticationDetail = None
        """@ivar: WSDL Oject holds the security information for UPS"""
        
        
        self._prepare_wsdl_objects()
        
        
    def __prepare_wsdl_objects(self):
        """
        This method should be over-ridden on each sub-class. It Instantiates
        any of the required WSDL objects so the user can just print their
        __str__() mthods and seee what they ned to fill in
        """
        pass
    
    def __check_response_for_endicia_error(self,Exception):
        
        if self.response.Status == 0:
            raise EndiciaFailure(self.response.Status,self.response.ErrorMessage)
        
            #for notification in self.response.Notifications:
                #if notification.Severity == 'Hard':
        #raise EndiciaFailure(Exception.fault.detail.Errors.ErrorDetail.PrimaryErrorCode.Code,Exception.fault.detail.Errors.ErrorDetail.PrimaryErrorCode.Description)
                    
    def _check_response_for_request_errors(self):
        
        pass
        #if self.response.Severity == 'Hard':
            #for notification in self.response.Notifications:
                #if notification.Severity == 'Hard':
                 #   raise UPSFailure(notification.Code,
                  #                   notification.Description)
                    
    def create_wsdl_object_of_type(self,type_name):
        return self.client.factory.create(type_name)
    
    def send_request(self,send_function=None):
        
        try:
            if send_function:
                self.response = send_function()
            else:
                self.response = self._assemble_and_send_request()
        except suds.WebFault,e:
            if e.fault != None:
                self.__check_response_for_endicia_error(e)
            else:
                raise SchemaValidationError()


                
        
        
        
        
        
        
        
        
        self.logger.debug('====Endicia QUERY RESULT===')
        self.logger.debug(self.response)
            
                
                
        
    
    
    
        
        
        
        
        
        
        
    
    
    