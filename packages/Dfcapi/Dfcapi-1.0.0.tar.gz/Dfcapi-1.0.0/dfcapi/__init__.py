# -*- coding:utf-8 -*-

import sys
import os
import unittest


sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import unirest
#from inspect import getmembers
from pprint import pprint
from array import *
import json

api_url_checkkey          = 'http://api.debitfinance.co.uk/app/checkkey'
api_url_viewdd 		      = 'http://api.debitfinance.co.uk/app/viewdd'
api_url_viewdd_breakdown  = 'http://api.debitfinance.co.uk/app/viewddbreakdown'
api_url_createDirectDebit = 'http://api.debitfinance.co.uk/app/setupdd'
api_url_updateDirectDebit = 'http://api.debitfinance.co.uk/app/updatedd'
api_url_cancelDirectDebit = 'http://api.debitfinance.co.uk/app/canceldd'


api_url_checkkey          = 'http://httpbin.org/get'
api_url_viewdd 		      = 'http://httpbin.org/get'
api_url_viewdd_breakdown  = 'http://httpbin.org/get'
api_url_createDirectDebit = 'http://httpbin.org/post'
api_url_updateDirectDebit = 'http://httpbin.org/post'
api_url_cancelDirectDebit = 'http://httpbin.org/post'

#class dfcapi:

#  CHECKKEY
def checkApiKey(api_key,api_secret):
	response = unirest.get(api_url_checkkey, auth=(api_key,api_secret))
	return response
#  View Direct Debits
def ViewDirectDebits(api_key,api_secret,dfc_ref):
	response = unirest.get(api_url_viewdd,  params={"dfc_reference":dfc_ref},  auth=(api_key,api_secret)) 
	return response
#  View Direct Debits Breakdown
def ViewDirectDebitsBreakdown(api_key,api_secret,dfc_ref):
	response = unirest.get(api_url_viewdd_breakdown,  params={"dfc_reference":dfc_ref},  auth=(api_key,api_secret)) 
	return response
#  Create Direct Debits  
def createDirectDebit(api_key,api_secret,client_reference,reference,title,first_name,last_name,address1,address2,address3,town,county,postcode,amounts,email,account_number,sort_code,start_from,installments,frequency_unit,frequency_type,roll_status,birth_date,mobile_number,phone_number,no_email,service_description,bacs_reference,skip_check):
	authentication = {"apikey": api_key, "apisecret": api_secret, 'club_ref_no':client_reference}
	payer		   = {'title':title,'first_name':first_name,'last_name':last_name, 'birth_date':birth_date}
	address 	   = {'address1':address1,'address2':address2,'address3':address3,'town':town,'county':county,'postcode':postcode, 'skip_check':skip_check}
	contact		   = {'email':email,'mobile_number':mobile_number,'phone_number':phone_number,'no_email':no_email}
	bank		   = {"account_number": account_number, "sort_code": sort_code}
	subscription   = {'reference':reference,'service_description':service_description,'start_from':start_from,'amounts':amounts,'installments':installments,'bacs_reference':'','roll_status':roll_status}

	response = unirest.post(api_url_createDirectDebit, headers={ "Accept": "application/json", "Content-Type": "application/json" }, params=json.dumps({'authentication':authentication, 'payer':payer,'address':address,'contact':contact,'bank':bank,'subscription':subscription}) )
	return response
#  Update Direct Debits  
def UpdateDirectDebit(api_key,api_secret,dfc_ref,reference,title,first_name,last_name,address1,address2,address3,town,county,postcode,email,account_number,sort_code,birth_date,mobile_number,phone_number,paymentdate,applyfrom_paydate,installmentduedate,installmentamount, latepayment, applyfrom,newamount):
	authentication = {"apikey": api_key, "apisecret": api_secret, 'dfc_ref':dfc_ref}
	payer		   = {'title':title,'first_name':first_name,'last_name':last_name, 'birth_date':birth_date}
	address 	   = {'address1':address1,'address2':address2,'address3':address3,'town':town,'county':county,'postcode':postcode}
	contact		   = {'phone':phone_number,  'mobile':mobile_number, 'email':email}
	bank		   = {"account_number": account_number, "sort_code": sort_code}
	general        = {'yourref':reference,'paymentdate':paymentdate,'installmentduedate':installmentduedate,'installmentamount':installmentamount,'latepayment':latepayment,'applyfrom':applyfrom,'applyfrom_paydate':applyfrom_paydate,'newamount':newamount}
	
	response = unirest.post(api_url_updateDirectDebit, headers={ "Accept": "application/json", "Content-Type": "application/json" }, params=json.dumps({'authentication':authentication, 'payer':payer,'address':address,'contact':contact,'bank':bank, 'general':general}) )
	return response
#  Cancel Direct Debits
def CancelDirectDebit(api_key,api_secret,dfc_ref,apply_from):
	authentication = {"apikey": api_key, "apisecret": api_secret, 'dfc_ref':dfc_ref}
	cancel		   = {'apply_from':apply_from}
	response = unirest.post(api_url_cancelDirectDebit, headers={ "Accept": "application/json", "Content-Type": "application/json" }, params=json.dumps({'authentication':authentication, 'cancel':cancel}) )
	return response

 

