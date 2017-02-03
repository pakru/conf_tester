import config
import time
import sys
#import os
#import subprocess
import hc_module.ecss_config_http_commands as HT
import colorama
from colorama import Fore, Back, Style
import xml.etree.ElementTree as ET
#import requests
#import signal
#from http.server import BaseHTTPRequestHandler, HTTPServer
#from threading import Thread
import json

testConfigFile = open('conf_test.json')
config.testConfigJson = json.loads(testConfigFile.read())
testConfigFile.close()

import pjSIP_py.pjUA as pjua
import ssh_cocon.ssh_cocon as ccn

'''
login = str(os.environ.get('COCON_USER'))
password = str(os.environ.get('COCON_PASS'))

host = str(os.environ.get('SSW_IP'))
port = int(os.environ.get('COCON_PORT'))
'''

#testingDomain = str(os.environ.get('SS_TEST_DOMAIN_NAME'))
testingDomain = config.testConfigJson['DomainName']
testingDomainSIPport = config.testConfigJson['sipListenPort']
testingDomainSIPaddr = config.testConfigJson['Cocon'][0]['Host']
sipUsersCfgJson = config.testConfigJson['Users']

'''
coreNode='core1@ecss1'
sipNode='sip1@ecss1'
dsNode='ds1@ecss1'
'''

#sippPath = str(os.environ.get('SIPP_PATH'))
sippListenAddress=testingDomainSIPaddr
sippListenPort='15076'
sippMediaListenPort='16016'
sippMediaListenPortTrunk='17016'

subscrCount = len(config.testConfigJson['Users'])
subscrNum = []

print('Users:')
# print('Quantity: ' + str(subscrCount))
for sipUser in sipUsersCfgJson:
	print('\t' + sipUser['Number'])

#print(config.testConfigJson['Users'][1])
'''
for i in range(subscrCount):
	subscrNum.append( str(int(str(os.environ.get('SS_SUBSCR1')))+i))	
'''


for sipUser in sipUsersCfgJson:
	subscrNum.append(str(sipUser['Number']))


#subscrSIPpass = str(config.testConfigJson['Users'][0]['Password'])
#SIPgroup = str(config.testConfigJson['Users'][0]['SipGroup'])

confNum='*71#'


#restHost = str(os.environ.get('TC_REST_HOST'))
#restPort = str(os.environ.get('TC_REST_PORT'))
#testTemplateName=str(os.environ.get('TC_TEMPLATE_NAME'))

colorama.init(autoreset=True)

def ssActivate():
	if not ccn.ssEnable(dom=testingDomain,subscrNum=subscrNum[0],ssNames ='conference chold ctr call_recording clip cnip'):
		return False
	if not ccn.ssEnable(dom=testingDomain,subscrNum=subscrNum[1],ssNames ='chold ctr call_recording cnip clip'):
		return False
	if not ccn.ssEnable(dom=testingDomain,subscrNum=subscrNum[2],ssNames ='chold ctr call_recording cnip clip'):
		return False

	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[0],ssName = 'chold',ssOptions='dtmf_sequence_as_flash = false'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[0],ssName='ctr'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[0],ssName='cnip'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[0],ssName='clip'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[0],ssName='conference'):
		return False
	#if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[0],ssName='call_recording',ssOptions='mode = always_on'):
	#	return False

	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[1],ssName='chold',ssOptions='dtmf_sequence_as_flash = false'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[1],ssName='ctr'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[1],ssName='cnip'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[1],ssName='clip'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[1],ssName='call_recording',ssOptions='mode = always_on'):
		return False

	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[2],ssName='chold',ssOptions='dtmf_sequence_as_flash = false'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[2],ssName='ctr'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[2],ssName='cnip'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[2],ssName='clip'):
		return False
	if not ccn.ssActivation(dom=testingDomain,subscrNum=subscrNum[2],ssName='call_recording',ssOptions='mode = always_on'):
		return False

	return True


def preconfigure():
	global 	subscrUA

	subscrUA = []

	if ccn.domainDeclare(testingDomain,removeIfExists = False) :
		print(Fore.GREEN + 'Successful domain declare')
	else :
		print(Fore.RED + 'Smthing happen wrong with domain declaration...')
		return False

	cnt = 0
	time.sleep(2)
	while not ccn.checkDomainInit(testingDomain):					# проверяем инициализацию домена
		print(Fore.YELLOW + 'Not inited yet...')	
		cnt += 1
		if cnt > 5:
			print(Fore.RED + "Test domain wasn't inited :(")
			return False
		time.sleep(2)

	if ccn.sipTransportSetup(dom=testingDomain,sipIP=testingDomainSIPaddr,sipPort=testingDomainSIPport):
		print(Fore.GREEN + 'Successful SIP transport declare')
	else :
		print(Fore.RED + 'Smthing happen wrong with SIP network setup...')
		return False

	#time.sleep(2)
	if ccn.setTraceMode(dom=testingDomain,traceMode='full_compressed'):
		print(Fore.GREEN + 'Core traces successfully enabled')
	else:
		print(Fore.RED + 'Smthing happen wrong with changing core trace mode...')


	if ccn.subscribersCreate(dom=testingDomain,sipNumber='{'+sipUsersCfgJson[0]['Number']+'-'+sipUsersCfgJson[subscrCount-1]['Number']+'}',
							sipPass=sipUsersCfgJson[0]['Password'], sipGroup=sipUsersCfgJson[0]['SipGroup'], routingCTX='default_routing'):
		print(Fore.GREEN + 'Successful Subscriber creation')
	else:
		print(Fore.RED + 'Smthing happen wrong with subscribers creation...')
		return False
	'''
	if ccn.subscribersCreate(dom=testingDomain,sipNumber=subscrNum2,sipPass=subscrSIPpass,sipGroup=SIPgroup,routingCTX='default_routing'):
	 	print(Fore.GREEN + 'Successful Subscriber creation')
	else:
		print(Fore.RED + 'Smthing happen wrong with subscribers creation...')
		return False

	if ccn.subscribersCreate(dom=testingDomain,sipNumber=subscrNum3,sipPass=subscrSIPpass,sipGroup=SIPgroup,routingCTX='default_routing'):
	 	print(Fore.GREEN + 'Successful Subscriber creation')
	else:
		print(Fore.RED + 'Smthing happen wrong with subscribers creation...')
		return False
	'''
	if ccn.setTraceMode(dom=testingDomain,traceMode='full_compressed'):
		print(Fore.GREEN + 'core traces successfully enabled')
	else:
		print(Fore.RED + 'Smthing happen wrong with changing core trace mode...')

	if not ccn.ssAddAccessAll(dom=testingDomain):
		return False

	if not ssActivate():
		print('Smthing gappen worng during ss activation')
		return False


	#####################################
	sippListenAddress='192.168.118.12' ############################!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	######################################

	#'''
	for sipUser in sipUsersCfgJson:
		print(sipUser['Login'])
		print(sipUser['Password'])
		subscrUA.append(pjua.SubscriberUA(domain=testingDomain, username=str(sipUser['Login']), passwd=str(sipUser['Password']),
										  sipProxy=testingDomainSIPaddr + ':' + testingDomainSIPport,
										  displayName='Subscriber ' + str(sipUser['UserId']), uaIP=sippListenAddress,
										  regExpiresTimeout=300))
	#'''

	return True


def makeConf(releaseType = 'byMaster'):

	# check registration status

	for i in range(subscrCount):
		if subscrUA[i].uaAccountInfo.reg_status != 200:
			print(Fore.RED + 'UA failed to register!')
			print(str(subscrUA[i].uaAccountInfo.uri) + ' state: ' + str(subscrUA[i].uaAccountInfo.reg_status) + ' - ' + str(subscrUA[i].uaAccountInfo.reg_reason))
			return False

	print('Calling to *71#')
	subscrUA[0].makeCall(phoneURI=confNum+'@'+testingDomain)

	print('waiting for answer from conf')
	cnt = 0
	Answered = False
	while cnt < 50:		
		time.sleep(0.1)
		if subscrUA[0].uaCurrentCallInfo.state == 5:
			Answered = True
			break			
		print('.',end='')		
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')

	confDialog = subscrUA[0].uaCurrentCall

	time.sleep(2)
	print('Putting on hold conf')
	subscrUA[0].uaCurrentCall.hold()
	time.sleep(2)


	print('Calling to subscriber B')
	subscrUA[0].makeCall(phoneURI=subscrNum[1]+'@'+testingDomain)

	print('waiting for answer at B party')
	cnt = 0
	Answered = False
	while cnt < 50:		
		time.sleep(0.1)
		if subscrUA[1].uaCurrentCallInfo.state == 5:
			Answered = True
			break			
		print('.',end='')		
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')


	time.sleep(2)

	print('Transfering subscriber B to conf')
	subscrUA[0].ctr_request(dstURI=confNum+'@'+testingDomain, currentCall=subscrUA[0].uaCurrentCall)
	time.sleep(1)
	print('hanging up...')
	subscrUA[0].uaCurrentCall.hangup(code=200, reason='Release after transfer')

	print('Return master to conf')
	confDialog.unhold()
	time.sleep(2)

	cnt=0 # timer
	confDuration = 10 

	while cnt < confDuration:		
		time.sleep(1)
		print('.',end='')
		cnt += 1
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
		if subscrUA[1].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber B '+ str(i) + ' in wrong state: ' + str(subscrNum[1].uaAccountInfo.uri) + ' ' + subscrNum[1].uaCurrentCallInfo.state_text)



	print('Putting on hold conf')
	confDialog.hold()
	time.sleep(2)

	print('Calling to subscriber C')
	subscrUA[0].makeCall(phoneURI=subscrNum[2]+'@'+testingDomain)

	print('waiting for answer at C party')
	cnt = 0
	Answered = False
	while cnt < 50:		
		time.sleep(0.1)
		if subscrUA[2].uaCurrentCallInfo.state == 5:
			Answered = True
			break			
		print('.',end='')		
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')

	time.sleep(2)

	print('Transfering subscriber 3 to conf')
	subscrUA[0].ctr_request(dstURI=confNum+'@'+testingDomain, currentCall=subscrUA[0].uaCurrentCall)
	time.sleep(1)
	print('hanging up...')
	subscrUA[0].uaCurrentCall.hangup(code=200, reason='Release after transfer')

	print('Return master to conf')
	confDialog.unhold()
	time.sleep(2)

	cnt=0 # timer
	confDuration = 10 

	while cnt < confDuration:		
		time.sleep(1)
		print('.',end='')
		cnt += 1
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
		if subscrUA[1].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber B '+ str(i) + ' in wrong state: ' + str(subscrNum[1].uaAccountInfo.uri) + ' ' + subscrNum[1].uaCurrentCallInfo.state_text)
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)


	print('Putting on hold conf')
	confDialog.hold()
	time.sleep(2)

	print('Calling to subscriber D')
	subscrUA[0].makeCall(phoneURI=subscrNum[3]+'@'+testingDomain)

	print('waiting for answer at D party')
	cnt = 0
	Answered = False
	while cnt < 50:		
		time.sleep(0.1)
		if subscrUA[3].uaCurrentCallInfo.state == 5:
			Answered = True
			break			
		print('.',end='')		
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')

	time.sleep(2)

	print('Transfering subscriber 4 to conf')
	subscrUA[0].ctr_request(dstURI=confNum+'@'+testingDomain,currentCall=subscrUA[0].uaCurrentCall)
	time.sleep(1)
	print('hanging up...')
	subscrUA[0].uaCurrentCall.hangup(code=200, reason='Release after transfer')


	print('Return master to conf')
	confDialog.unhold()
	time.sleep(2)


	cnt=0 # timer
	confDuration = 10 

	Released = False

	while cnt < confDuration:		
		time.sleep(1)
		print('.',end='')
		cnt += 1
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = True
		if subscrUA[1].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber B '+ str(i) + ' in wrong state: ' + str(subscrNum[1].uaAccountInfo.uri) + ' ' + subscrNum[1].uaCurrentCallInfo.state_text)
			Released = True
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)
			Released = True
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = True

	if Released:
		print('Some subscribers were in wrong call state')
		confDialog.hangup(code=500, reason='Failure!')
		for i in range(1,4):
			subscrUA[i].uaCurrentCall.hangup(code=500, reason='Failure!')
		return False


	if releaseType is 'byMaster':
		print('Releasing conf')
		confDialog.hangup(code=200, reason='Conf Finish!')

		cnt = 0
		Released = False
		while cnt < 50:
			time.sleep(0.1)
			if (subscrUA[1].uaCurrentCallInfo.state != 5) and (subscrUA[2].uaCurrentCallInfo.state != 5) and (subscrUA[3].uaCurrentCallInfo.state != 5):
				Released = True
				break
			print('.',end='')
			cnt += 1

		if not Released:
			print(Fore.RED + 'Call not released')
			return False
		else:
			print(Fore.GREEN + 'Call released')

	elif releaseType is 'byUsers':
		print('Releasing subscribers from conf')
		print('Hangup subsciber B')
		subscrUA[1].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup subsciber C')
		subscrUA[2].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		subscrUA[3].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup conf master')
		confDialog.hangup(code=200, reason='Conf Finish!')

		time.sleep(1)

		if not Released:
			print(Fore.RED + 'Some calls wrong released')
			return False
		else:
			print(Fore.GREEN + 'Calls successful released')


	elif releaseType is 'halfUsers':
		print('Releasing subscribers from conf')
		print('Hangup subsciber B')
		subscrUA[1].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup subsciber C')
		subscrUA[2].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup conf master')
		confDialog.hangup(code=200, reason='Conf Finish!')

		cnt = 0
		Released = False
		while cnt < 50:
			time.sleep(0.1)
			if (subscrUA[1].uaCurrentCallInfo.state != 5) and (subscrUA[2].uaCurrentCallInfo.state != 5) and (subscrUA[3].uaCurrentCallInfo.state != 5):
				Released = True
				break
			print('.',end='')
			cnt += 1

		if not Released:
			print(Fore.RED + 'Some calls wrong released')
			return False
		else:
			print(Fore.GREEN + 'Calls successful released')

	return True

def makeConf2(releaseType = 'byMaster'):
	for i in range(subscrCount):
		if subscrUA[i].uaAccountInfo.reg_status != 200:
			print(Fore.RED + 'UA failed to register!')
			print(str(subscrUA[i].uaAccountInfo.uri) + ' state: ' + str(subscrUA[i].uaAccountInfo.reg_status) + ' - ' + str(subscrUA[i].uaAccountInfo.reg_reason))
			return False

	print('Calling to subscriber B')
	subscrUA[0].makeCall(phoneURI=subscrNum[1]+'@'+testingDomain)

	print('waiting for answer at B party')
	cnt = 0
	Answered = False
	while cnt < 50:		
		time.sleep(0.1)
		if subscrUA[1].uaCurrentCallInfo.state == 5:
			Answered = True
			break			
		print('.',end='')		
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')
	time.sleep(2)

	print('Putting on hold B party')
	subscrUA[0].uaCurrentCall.hold()
	time.sleep(2)

	ADialog = subscrUA[0].uaCurrentCall

	print('Calling to subscriber C')
	subscrUA[0].makeCall(phoneURI=subscrNum[2]+'@'+testingDomain)

	print('waiting for answer at C party')
	cnt = 0
	Answered = False
	while cnt < 50:		
		time.sleep(0.1)
		if subscrUA[2].uaCurrentCallInfo.state == 5:
			Answered = True
			break			
		print('.',end='')		
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')
	time.sleep(2)

	print('Putting on hold C party')
	subscrUA[0].uaCurrentCall.hold()
	time.sleep(2)

	BDialog = subscrUA[0].uaCurrentCall

	print('Calling to *71#')
	subscrUA[0].makeCall(phoneURI=confNum+'@'+testingDomain)

	print('waiting for answer from conf')
	cnt = 0
	Answered = False
	while cnt < 50:		
		time.sleep(0.1)
		if subscrUA[0].uaCurrentCallInfo.state == 5:
			Answered = True
			break			
		print('.',end='')		
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')

	confDialog = subscrUA[0].uaCurrentCall

	print('Transfering subscriber B to conf')
	subscrUA[0].ctr_request(dstURI=confNum+'@'+testingDomain, currentCall = ADialog)
	time.sleep(1)
	print('hanging up...')
	ADialog.hangup(code=200, reason='Release after transfer')

	print('Transfering subscriber C to conf')
	subscrUA[0].ctr_request(dstURI=confNum+'@'+testingDomain, currentCall = BDialog)
	time.sleep(1)
	print('hanging up...')
	BDialog.hangup(code=200, reason='Release after transfer')

	cnt=0 # timer
	confDuration = 10 

	while cnt < confDuration:		
		time.sleep(1)
		print('.',end='')
		cnt += 1
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
		if subscrUA[1].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber B '+ str(i) + ' in wrong state: ' + str(subscrNum[1].uaAccountInfo.uri) + ' ' + subscrNum[1].uaCurrentCallInfo.state_text)
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)

	print('Add one more subscriber to conf')

	print('Putting on hold conf')
	confDialog.hold()
	time.sleep(2)

	print('Calling to subscriber D')
	subscrUA[0].makeCall(phoneURI=subscrNum[3]+'@'+testingDomain)

	print('waiting for answer at D party')
	cnt = 0
	Answered = False
	while cnt < 50:
		time.sleep(0.1)
		if subscrUA[3].uaCurrentCallInfo.state == 5:
			Answered = True
			break
		print('.',end='')
		cnt += 1

	if not Answered:
		print('Call not recieved')
		return False
	else:
		print('Call answered')

	time.sleep(2)

	print('Transfering subscriber D to conf')
	subscrUA[0].ctr_request(dstURI=confNum+'@'+testingDomain,currentCall=subscrUA[0].uaCurrentCall)
	time.sleep(1)
	print('hanging up...')
	subscrUA[0].uaCurrentCall.hangup(code=200, reason='Release after transfer')


	print('Return master to conf')
	confDialog.unhold()
	time.sleep(2)

	cnt=0 # timer
	confDuration = 10

	Released = False

	while cnt < confDuration:
		time.sleep(1)
		print('.',end='')
		cnt += 1
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = True
		if subscrUA[1].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber B '+ str(i) + ' in wrong state: ' + str(subscrNum[1].uaAccountInfo.uri) + ' ' + subscrNum[1].uaCurrentCallInfo.state_text)
			Released = True
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)
			Released = True
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = True

	if Released:
		print('Some subscribers were in wrong call state')
		confDialog.hangup(code=500, reason='Failure!')
		for i in range(1,4):
			subscrUA[i].uaCurrentCall.hangup(code=500, reason='Failure!')
		return False



	if releaseType is 'byMaster':
		print('Releasing conf')
		confDialog.hangup(code=200, reason='Conf Finish!')

		cnt = 0
		Released = False
		while cnt < 50:
			time.sleep(0.1)
			if (subscrUA[1].uaCurrentCallInfo.state != 5) and (subscrUA[2].uaCurrentCallInfo.state != 5):
				Released = True
				break
			print('.',end='')
			cnt += 1

		if not Released:
			print(Fore.RED + 'Call not released')
			return False
		else:
			print(Fore.GREEN + 'Call released')


	elif releaseType is 'byUsers':
		print('Releasing subscribers from conf')
		print('Hangup subsciber B')
		subscrUA[1].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup subsciber C')
		subscrUA[2].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		subscrUA[3].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup conf master')
		confDialog.hangup(code=200, reason='Conf Finish!')

		time.sleep(1)

		if not Released:
			print(Fore.RED + 'Some calls wrong released')
			return False
		else:
			print(Fore.GREEN + 'Calls successful released')

	elif releaseType is 'halfUsers':
		print('Releasing subscribers from conf')
		print('Hangup subsciber B')
		subscrUA[1].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[2].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber C '+ str(i) + ' in wrong state: ' + str(subscrNum[2].uaAccountInfo.uri) + ' ' + subscrNum[2].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup subsciber C')
		subscrUA[2].uaCurrentCall.hangup(code=200, reason='Leaving conf')
		time.sleep(3)

		Released = True
		if confDialog.info().state != 5:
			print(Fore.YELLOW +'Subscriber A '+ str(i) + ' in wrong state: ' + str(subscrNum[0].uaAccountInfo.uri) + ' ' + subscrNum[0].uaCurrentCallInfo.state_text)
			Released = False
		if subscrUA[3].uaCurrentCallInfo.state != 5:
			print(Fore.YELLOW +'Subscriber D '+ str(i) + ' in wrong state: ' + str(subscrNum[3].uaAccountInfo.uri) + ' ' + subscrNum[3].uaCurrentCallInfo.state_text)
			Released = False

		print('Hangup conf master')
		confDialog.hangup(code=200, reason='Conf Finish!')

		cnt = 0
		Released = False
		while cnt < 50:
			time.sleep(0.1)
			if (subscrUA[1].uaCurrentCallInfo.state != 5) and (subscrUA[2].uaCurrentCallInfo.state != 5) and (subscrUA[3].uaCurrentCallInfo.state != 5):
				Released = True
				break
			print('.',end='')
			cnt += 1

		if not Released:
			print(Fore.RED + 'Some calls wrong released')
			return False
		else:
			print(Fore.GREEN + 'Calls successful released')


	return True



#######################################################################

testFailure = False


preconfigure()

'''
if makeConf(releaseType='byMaster'):
	print('Conf test: Release by master - OK ')
else:
	print('Conf test: Release by master - FAILED! ')
	testFailure = True
'''

'''
if makeConf(releaseType='byUsers'):
	print('Conf test: Release by users - OK ')
else:
	print('Conf test: Release by users - FAILED! ')
	testFailure = True

if makeConf(releaseType='halfUsers'):0
	print('Conf test: Release by half users and master - OK ')
else:
	print('Conf test: Release by half users and master - FAILED! ')
	testFailure = True
'''

if makeConf2(releaseType='byMaster'):
	print('Conf test: Release by master - OK ')
else:
	print('Conf test: Release by master - FAILED! ')
	testFailure = True

if makeConf2(releaseType='byUsers'):
	print('Conf test: Release by master - OK ')
else:
	print('Conf test: Release by master - FAILED! ')
	testFailure = True

if makeConf2(releaseType='halfUsers'):
	print('Conf test: Release by master - OK ')
else:
	print('Conf test: Release by master - FAILED! ')
	testFailure = True


ccn.coconInt.eventForStop.set()

sys.exit(0)