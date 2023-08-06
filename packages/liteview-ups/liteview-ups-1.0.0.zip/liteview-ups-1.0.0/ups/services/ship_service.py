'''
Created on Oct 23, 2012
Ship Service Module
====================
This package contains the shipping methods defined by UPS's 
Ship Service WSDL File. each is encapsulated in a class for easy access
for more details on each, refer to the respective class's documentation
@author: PabloH
'''
from datetime import datetime
from suds.sax.element import Element
from suds.plugin import MessagePlugin
from ..base_service import UPSBaseService

class MyPlugInUPSShipment(MessagePlugin):
    def sending(self,context):
        context.envelope = context.envelope.replace('ns1:Request','ns0:Request')        
    def marshalled(self, context):
        hdr = context.envelope.childAtPath('Body/ShipmentRequest/Request')
        hdr.setPrefix('ns0')
        hdr = context.envelope.childAtPath('Body')
        hdr.setPrefix('SOAP-ENV')
        
class MyPlugInVoidUPSShipment(MessagePlugin):
    def sending(self,context):
        context.envelope = context.envelope.replace('ns1:Request','ns0:Request')        
    def marshalled(self, context):
        hdr = context.envelope.childAtPath('Body/VoidShipmentRequest/Request')
        hdr.setPrefix('ns0')
        hdr = context.envelope.childAtPath('Body')
        hdr.setPrefix('SOAP-ENV')        

class UPSProcessShipmentRequest(UPSBaseService):
    
    def __init__(self,config_obj, *args, **kwargs):
        """
        The optional keyword args detailed on L(UPSBaseService)
        apply here as well
        
        @type config_obj:  L{UPSConfig}
        @param config_obj: a Valid UPS Config object
        """
        self._config_obj = config_obj
        
        self.create_ups_security(self._config_obj.username, self._config_obj.password, self._config_obj.key)
        self.RequestedShipment = None
        """@ivar : Holds the requested shipment WSDL Object"""
        super(UPSProcessShipmentRequest,self).__init__(self._config_obj,'Ship.wsdl',massage=MyPlugInUPSShipment(),*args,**kwargs)
        
    def create_ups_security(self,username='xxxxxx',password='xxxxxxx',key='xxxxxxxxxx'):
        upss = ('ns3','http://www.ups.com/XMLSchema/XOLTWS/UPSS/v1.0')
        #Create the UPS Security Element
        UpsSecurity = Element('UPSSecurity',ns=upss)
        UPSUserToken = Element('UsernameToken',ns=upss)
        u = Element('Username',ns=upss).setText(username)
        p = Element('Password',ns=upss).setText(password)
        l = Element('AccessLicenseNumber',ns=upss).setText(key)
        UPSLicenseToken = Element('ServiceAccessToken',ns=upss)
        UpsSecurity.append(UPSUserToken)
        UpsSecurity.append(UPSLicenseToken)
        UPSUserToken.append(u)
        UPSUserToken.append(p)
        UPSLicenseToken.append(l)
        self._UPSWebAuthentication =  UpsSecurity 
                
    def _prepare_wsdl_objects(self):
        """
        This is the data that will be used to create your shpment. Create
        the data structure and get it ready for the WSDL request. 
        """
        self.RequestedShipment = self.create_wsdl_object_of_type('ns0:RequestType')
        
        self.Shipment = self.create_wsdl_object_of_type('ns3:ShipmentType')
        
        self._Shipper = self.create_wsdl_object_of_type('ns3:ShipperType')
        #set up the account for the shpipments as the shipper
        self._Shipper.ShipperNumber = self.config_obj.upsAccount
        
        self._ShipFrom  = self.create_wsdl_object_of_type('ns3:ShipFromType')
        
        self._ShipTo = self.create_wsdl_object_of_type('ns3:ShipToType')
        
        self._PaymentInfo = self.create_wsdl_object_of_type('ns3:PaymentInfoType')
        
        self.LabelSpecification = self.create_wsdl_object_of_type('ns3:LabelSpecificationType')
        
        self.ReceiptSpecification = self.create_wsdl_object_of_type('ns3:ReceiptSpecificationType')
        
        self.Shipment.Shipper = self._Shipper
        
        
        self.Shipment.ShipTo = self._ShipTo
        
        self.Shipment.ShipFrom = self._ShipFrom
                
        self.client.set_options(soapheaders=self.UPSAuthenticationDetail)     
        
           
        
    
    def _assemble_and_send_request(self):
        """
        Fires off the FedEx request
        
        """
        #Fire off the query
        
        response = self.client.service.ProcessShipment(self.RequestedShipment,self.Shipment,self.LabelSpecification)
        
        return response
    
class UPSDeleteShipmentRequest(UPSBaseService):
    """
    This class allows you to delete a shpment, given a tracking number
    """
    
    def __init__(self,config_obj,*args,**kwargs):
        """
        Deletes a shipment via a tracking number or shipment id
        """
        self._config_obj = config_obj
        """@ivar : Holds the details for the tracking information"""
        self.TrackingId = None
        """@ivar : Holds the tracking number itself"""
        
        super(UPSDeleteShipmentRequest,self).__init__(self._config_obj,
                                                      'Void.wsdl',
                                                      massage=MyPlugInVoidUPSShipment(),
                                                      *args, **kwargs)
        
    def _prepare_wsdl_objects(self):
        """
        Preps the WSDL Data Structure for the user
        """
        self.voidInfo = self.client.factory.create('ns2:VoidShipment')
        
        self.requestType = self.client.factory.create('ns0:RequestType')
        self.requestType.RequestOption.append('1')
        self.client.set_options(soapheaders=self.UPSAuthenticationDetail)    
        
    def _assemble_and_send_request(self):
        """
        Fires off UPS Void Request
        """
        self.voidInfo.ShipmentIdentificationNumber = self.TrackingId
        client = self.client
        
        response = client.service.ProcessVoid(self.requestType,self.voidInfo)
        
        return response
        
        
        
    

    

        
        
