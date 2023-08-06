#!/usr/bin/env python
'''
Module to interact with Responsys Interact.
'''

import os
import sys
import time

from suds.client import Client
from suds import WebFault


def retry(func):
    ''' Only use this wrapper on methods of Interact '''
    def retry_on_webfault(*args, **kwargs):
        ''' If a soap WebFault is encountered, go through a series of
        retries before reraising the exception.
        This is for handling INVALID_SESSION_ID and timeout errors that
        can occasionally happen.
        '''
        tries = 0
        self = args[0]
        # Let's be a little generous here. Makes my life in web support
        # a bit easier.
        timeouts = [10, 20, 30, 60, 60, 60, 60]
        while True:
            try:
                return func(*args, **kwargs)
            # XXX Need to catch AccountFault specifically.
            except WebFault as e:
                print >>sys.stderr, 'Reconnecting...'
                time.sleep(timeouts[tries])
                self.connect(
                    self.username, 
                    self.password,
                    self.pod,
                    proxy=self.proxy,
                    timeout=timeouts[tries]
                )
                tries += 1
                if tries == len(timeouts):
                    print >>sys.stderr, 'WebFault.message: %s' % e.message
                    raise
    return retry_on_webfault


class Interact(object):
    '''
    Exposes Responsys Interact API in a convenient class.

    Common use case:
    interact = Interact()
    interact.connect(user, pass, pod)
    interact.merge_into_list('folder/listname', 
        [{'EMAIL_ADDRESS_': ...}, ...])
    interact.trigger_campaign('folder/campaign', 'folder/listname',
        [{'EMAIL_ADDRESS_':..., 'SOME_OPTIONALDATA':...}, ...])
    interact.disconnect()
    '''


    def __init__(self, exec_rc=True):
        ''' Create an Interact instance. '''
        self.client = None
        self.username = None
        self.password = None
        self.pod = None
        if exec_rc:
            self.exec_rc()

    def exec_rc(self):
        rc_path = os.path.join(
            os.getenv("HOME"), ".interact", "rc.py")
        if os.path.isfile(rc_path):
            execfile(rc_path)

    def config_creds(self, username, password, pod, config_path=None):
        self.pod = str(pod)
        assert self.pod in {'2', '5'}, 'Pod should be 2 or 5'
        if (
            username is None and 
            password is None and 
            config_path is None
        ):
            config_path = os.path.join(
                os.getenv('HOME'), '.interact', 'creds.py')
            assert os.path.isfile(config_path), 'No credentials found.'
        if config_path is not None:
            config_d = {}
            with open(config_path) as config_f:
                exec(config_f, config_d)
            # TODO: kind of nasty indirect access here...
            # probably best to move this into a brick config template
            self.username = config_d['credentials'][self.pod]['username']
            self.password = config_d['credentials'][self.pod]['password']
        else:
            self.username = username
            self.password = password
        assert all([self.username, self.password]), \
            'Username/Password undefined'

        
    def connect(self, username=None, password=None, pod=None,
        config_path=None, proxy=None, timeout=10):
        ''' Connect to Responsys Interact.
        Takes a username, password, and an integer "pod", which is
        5 for interact-5 and 2 for interact-2. You can see which it is
        in the WSDL URL you use.
        
        Advanced users can proxy through to our service for sniffing their
        web traffic and debugging. This is https, so you'll have to create
        a cert and private key, add it to your trusted certs, and then
        decrypt with the private key with something like wireshark.
        '''
        self.config_creds(username, password, pod, config_path=config_path)
        wsdl_url  = 'https://ws' + self.pod + \
            '.responsys.net/webservices/wsdl/ResponsysWS_Level1.wsdl'
        endpoint = 'https://ws' + self.pod + \
            '.responsys.net/webservices/services/ResponsysWSService'
        self.client = self._create_client(wsdl_url, endpoint, proxy=proxy)
        self.client.set_options(timeout=timeout)
        loginResponse = self.client.service.login(self.username,
            self.password)
        token = self.client.factory.create('SessionHeader')
        token.sessionId = loginResponse.sessionId
        self.client.set_options(soapheaders=token)
        self.proxy = proxy


    def disconnect(self):
        ''' Disconnect if you are done, otherwise you risk using all your
        allowed sessions.
        '''
        if self.client:
            self.client.service.logout()


    @retry
    def list_folders(self):
        ''' List folders for an account.
        Pretty pointless except to make sure you are connected, which is
        still pretty pointless since the logic will retry automatically.
        '''
        return self.client.service.listFolders()


    @retry
    def get_list_records(self, list_path, columns, ids, 
        match_column='EMAIL_ADDRESS_'):
        ''' Return records from a Profile List.
        Please pass in at least two field names and at least one id.
        '''
        int_obj = self._create_int_obj(list_path)
        
        if len(columns) > 1 and len(ids) > 0:
            return self.client.service.retrieveTableRecords(int_obj,
                match_column, columns, ids)
        # Gotcha! Thought you'd get some records didn't you! Not today.
        raise ValueError("Needs at least 2 fields and 1 id to retrieve.")
        
             
    def get_pet_records(self, list_path, columns, ids, 
        match_column='EMAIL_ADDRESS_'):
        ''' Retrieve records from a Profile Extension Table.
        Please pass in two columns and at least one id.
        '''
        # Create Campaign Object
        int_obj = self._create_int_obj(list_path)
        
        if len(columns) > 1 and len(ids) > 0:
            return self.client.service.retrieveProfileExtensionRecords(
                int_obj,
                match_column,
                columns,
                ids,
            )
        # Gotcha again.
        raise ValueError("Needs at least 2 fields and 1 id to retrieve.")
        
        
    def get_service(self):
        ''' Get the service which allows API calls '''
        return self.client.service


    def create(self, name):
        ''' Create an object from client factory '''
        return self.client.factory.create(name)


    def merge_into_table(self, table_path, records, insert=True, 
        update=True):
        ''' Merge into a supplemental table.
        Records is a container of dictionaries.
        '''
        table_obj = self._create_int_obj(table_path)
        record_data = self._create_record_data(records)
        update = 'REPLACE_ALL' if update else 'NO_UPDATE'
        return self.client.service.mergeTableRecordsWithPK(
            table_obj,
            record_data,
            insert,
            update,
        )
        

    def merge_into_list(self, list_path, records, 
        match_column='EMAIL_ADDRESS_'):
        ''' Merge data into your Profile Lists.
        Records is a container of dictionaries.
        '''
        list_obj = self._create_int_obj(list_path)
        record_data = self._create_record_data(records)
        merge_rule = self._create_merge_rule(match_column=match_column)
        return self.client.service.mergeListMembersRIID(
            list_obj,
            record_data,
            merge_rule
        )


    def delete_list_rows(self, list_path, ids, match_column='RIID'):
        ''' Deletes rows from a Profile List from the RIIDs
        or otherwise specified identifier (MOBILE_NUMBER, EMAIL_ADDRESS).
        '''
        list_obj = self._create_int_obj(list_path)
        return self.client.service.deleteListMembers(list_obj,
            match_column, ids)
 

    def query_list(self, list_path, columns, ids):
        ''' Returns columns from a Profile List given a set of IDs. '''
        int_obj = self._create_int_obj(list_path)
        return self.client.service.retrieveListMembers(
            int_obj,
            'EMAIL_ADDRESS',
            columns,
            ids
        )


    def merge_into_pet(self, pet_path, records,
        match_column='EMAIL_ADDRESS_'):
        ''' Merge a container of dicts into a Profile Extension Table. '''
        int_obj = self._create_int_obj(pet_path)
        record_data = self._create_record_data(records)
        return self.client.service.mergeIntoProfileExtension(
            int_obj,
            record_data, 
            match_column,
            'true', 
            'REPLACE_ALL',
        )


    def trigger_event(self, event_name, list_path, recipients):
        ''' Triggers a custom event to trigger Programs.
        You must provide the name of the event, the path to the Profile
        List, and a list of dicts that represent recipients.
        Each dict should specify an EMAIL_ADDRESS_, and it is recommended
        to specify a CUSTOMER_ID_ as well.
        '''
        list_obj = self._create_int_obj(list_path)
        event = self.client.factory.create('CustomEvent')
        event.eventName = event_name
        recipient_data = self._create_recipient_data(recipients, list_obj)
        return self.client.service.triggerCustomEvent(
            event,
            recipient_data,
        )


    def trigger_campaign(self, campaign_path, list_path, recipients):
        ''' Trigger a campaign to a list of recipients.
        Must specify a path to a campaign, the associated list, and a
        container of dictionaries which represent recipients.
        Each should have an EMAIL_ADDRESS_ and recommended to have a
        CUSTOMER_ID_.
        '''
        camp_obj = self._create_int_obj(campaign_path)
        list_obj = self._create_int_obj(list_path)
        recipient_data = self._create_recipient_data(recipients, list_obj)
        return self.client.service.triggerCampaignMessage(
            camp_obj,
            recipient_data,
        )


    def merge_trigger(self, campaign_path, records, opt_data, 
        match_column='EMAIL_ADDRESS_'): 
        camp_obj = self._create_int_obj(campaign_path)
        merge_rule = self._create_merge_rule(match_column=match_column)
        record_data = self._create_record_data(records)
        trig_data = self._create_trigger_data(opt_data)
        return self.client.service.mergeTriggerEmail(
            record_data,
            merge_rule,
            camp_obj,
            trig_data,
        )


    def _create_recipient_data(self, recipients, list_obj):
        ''' Creates SOAP objects out of recipient dicts and their list.
        '''
        # Check if all recipients have the same sets of key value pairs.
        keys = set()
        for recipient in recipients:
            keys |= set(recipient.keys())
        opt_data_keys = list(keys - {'EMAIL_ADDRESS_', 'CUSTOMER_ID_',
            'EMAIL_FORMAT'})
        recipient_datas = []
        for recipient in recipients:
            soap_recipient = self.client.factory.create('Recipient')
            soap_recipient.recipientId = recipient.get('RIID_', '')
            soap_recipient.emailAddress = recipient.get('EMAIL_ADDRESS_', '')
            soap_recipient.customerId = recipient.get('CUSTOMER_ID_', '')
            soap_recipient.listName = list_obj
            soap_recipient.emailFormat = recipient.get('EMAIL_FORMAT',
                'NO_FORMAT')
            opt_datas = []
            for opt_key in opt_data_keys:
                opt_data = self.client.factory.create('OptionalData')
                opt_data.name = opt_key
                opt_data.value = recipient.get(opt_key, '')
                opt_datas += [opt_data]
            recipient_data = self.client.factory.create('RecipientData')
            recipient_data.recipient = soap_recipient
            recipient_data.optionalData = opt_datas
            recipient_datas += [recipient_data]
        return recipient_datas
        
                    
    def _create_client(self, wsdl_url, endpoint, proxy=None):
        ''' Initialize client and set up proxy if it exists.
        proxy = (host_ip, port)
        '''
        return Client(
            wsdl_url, 
            location=endpoint, 
            proxy=proxy and { 
                'http': '%s:%d' % proxy, 
                'https': '%s:%d' % proxy 
            },
        )

                     
    def _create_int_obj(self, path):
        ''' Create a SOAP Interact Object from an object path.
        This is used for lists, campaigns, programs, etc.
        '''
        assert '/' in path, 'Must pass a path in the form of folder/object'
        folderName, objectName = path.split('/')
        interact_obj = self.client.factory.create('InteractObject')
        interact_obj.folderName = folderName
        interact_obj.objectName = objectName
        return interact_obj

    def _create_record_data(self, records):
        ''' This is a bit of a sloppy coercion of Python records into 
        record data. It is a bit redundant since every dict should share
        the same keys, but it's either that or dynamically create 
        namedtuples from a dev's list of field names and passing in a list
        of those. That's a possibility.
        Dicts are easier to think of initially for developers and I think
        it will make this more accessible to the general Python programmer.
        '''
        assert records, 'Must pass in records to create records.'
        keys = set()
        # Get the union of keys in each record.
        for record in records:
            keys |= set(record.keys())
        keys = list(keys)
        assert len(keys) > 1, 'Must pass in more than one field in records'
        record_data = self.client.factory.create('RecordData')
        record_data.fieldNames = keys
        record_data.records = []
        for record_d in records:
            record = self.client.factory.create('Record')
            for key in keys:
                record.fieldValues += [record_d.get(key, '')]
            record_data.records += [record]
        return record_data


    def _create_merge_rule(self, match_column='EMAIL_ADDRESS_',
        default_permission='OPTIN'):
        ''' Creates a mergeRule for certain API calls.
        This just inserts and replaces by default, the usual use-case.
        '''
        merge_rule = self.client.factory.create('mergeRule')
        merge_rule.insertOnNoMatch = 'TRUE'
        merge_rule.updateOnMatch = 'REPLACE_ALL'
        if isinstance(match_column, basestring):
            merge_rule.matchColumnName1 = match_column
        elif isinstance(match_column, list):
            if len(match_column) >= 1:
                merge_rule.matchColumnName1 = match_column[0]
            else:
                raise ValueError('Need to match on at least one column')
            if len(match_column) >= 2:
                merge_rule.matchColumnName2 = match_column[1]
            if len(match_column) >= 3:
                merge_rule.matchColumnName3 = match_column[2]
            if len(match_column) > 3:
                raise ValueError('Matching on too many columns: %s' %
                    str(match_column))
        # only use NONE or AND
        merge_rule.matchOperator = 'NONE'
        merge_rule.optinValue = 'I'
        merge_rule.optoutValue = 'O'
        merge_rule.defaultPermissionStatus = default_permission
        return merge_rule


    def _create_trigger_data(self, opt_data):
        ''' Takes a list of dictionaries and creates triggerData[] '''
        assert opt_data, 'Must pass in optional opt_data to create '\
            'trigger data.'
        keys = set()
        # Get the union of keys in each record.
        for datas in opt_data:
            keys |= set(datas.keys())
        keys = list(keys)
        if len(keys) == 0:
            keys = ['']
        trigger_datas = []
        for datas in opt_data:
            trigger_data = self.client.factory.create('TriggerData')
            trigger_data.optionalData = []
            for key in keys:
                opt = self.client.factory.create('OptionalData')
                opt.name = key
                opt.value = datas.get(key, '')
                trigger_data.optionalData += [opt]
            trigger_datas += [trigger_data]
        return trigger_datas


