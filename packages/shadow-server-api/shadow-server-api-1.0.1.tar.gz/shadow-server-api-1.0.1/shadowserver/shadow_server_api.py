#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__version__ = '1.0.1'
__license__ = 'GPLv3'

import re
import ast
import json
import requests


class ShadowServerApi():
    def __init__(self):
        self.shadowserver_bintest = 'http://bin-test.shadowserver.org/api'
        self.shadowserver_av = 'http://innocuous.shadowserver.org/api/'

    def get_bintest(self, this_hash):
        """ Get Binary Whitelist Test Results

        This server provides a lookup mechanism to test an executable file
        against a list of known software applications.

        Information in this database has been collected from the following sources:

        NSRL : National Software Reference Library. Field descriptions can be found
        in the Data Formats of the NSRL Reference Data Set (RDS) Distribution paper.
        http://www.nsrl.nist.gov

        :param this_hash: Can be a md5 or sha1 hash.
        :return: result dictionary

        Example Output::
        {
            "response_code": 200,
            "results": {
                "os_mfg": "Microsoft Corporation",
                "fileversion": "5.1.2600.5512",
                "reference": "os_patches_all",
                "application_type": "exe",
                "filetimestamp": "04/14/2008 12:00:00",
                "sig_timestamp": "04/14/2008 02:07:47",
                "language_code": "1033",
                "source_version": "1.6",
                "dirname": "c:\\WINDOWS\\system32",
                "binary": "1",
                "source": "AppInfo",
                "product_version": "5.1.2600.5512",
                "mfg_name": "Microsoft Corporation",
                "filename": "notepad.exe",
                "os_version": "5.1",
                "sig_trustfile": "C:\\WINDOWS\\system32\\CatRoot\\{F750E6C3-38EE-11D1-85E5-00C04FC295EE}\\NT5.CAT",
                "filesize": "69120",
                "sha256": "865F34FE7BA81E9622DDBDFC511547D190367BBF3DAD21CEB6DA3EEC621044F5",
                "sha512": "CB7218CFEA8813AE8C7ACF6F7511AECBEB9D697986E0EB8538065BF9E3E9C6CED9C2927...<snip>",
                "product_name": "Microsoft Windows Operating System",
                "os_name": "Microsoft Windows XP Professional Service Pack 3 (build 2600)",
                "description": "Notepad",
                "trusted_signature": "1",
                "crc32": "877EA041",
                "bit": "32",
                "md5": "5E28284F9B5F9097640D58A73D38AD4C",
                "sha1": "7A90F8B051BC82CC9CADBCC9BA345CED02891A6C",
                "language": "English",
                "signer": "Microsoft Windows Component Publisher",
                "strongname_signed": "0"
            }
        }

        Example Output for a hash not found::
        {
            "response_code": 200,
            "results": "039ea049f6d0f36f55ec064b3b371c46 - not found."
        }
        """
        #: Validate Input
        hash_check = re.findall(r'(?i)(?<![a-zA-Z0-9])[a-fA-F0-9]{32}(?![a-zA-Z0-9])', this_hash)
        if len(this_hash) == 32 and len(hash_check) == 1:
            params = {'md5': this_hash}
        elif len(this_hash) == 40 and len(hash_check) == 1:
            params = {'sha1': this_hash}
        else:
            return dict(error='Malformed Input: needs to be a single md5 or sha1 hash.', response_code=400)

        try:
            response = requests.get(self.shadowserver_bintest, params=params)
        except Exception:
            return dict(error=Exception)

        if response.status_code == requests.codes.ok:
            if this_hash == response.content.strip('\n').strip():
                return dict(results='{} - not found.'.format(this_hash), response_code=response.status_code)
            elif '! invalid request' in response.content:
                return dict(error='invalid request', response_code=response.status_code)
            else:
                for line in response.content.split('\n'):
                    l = line.split(' ', 1)
                    if len(l) == 2:
                        try:
                            return dict(results=ast.literal_eval(l[1]), response_code=response.status_code)
                        except ValueError:
                            return dict(error='malformed string', response_code=response.status_code)
        else:
            print "Server Error Code: " + response.status_code
            return dict(response_code=response.status_code)

    def get_av(self, this_hash):
        """ Get AV Results

        :param this_hash:
        :return: result dictionary

        Example Output for Input Hash 039ea049f6d0f36f55ec064b3b371c46 ::
        {
            "sha1": "ada0f47d8a52d664a5548bf67aa4a28c1d7dbf15",
            "last_seen_date_utc": "2013-12-12 15:11:38",
            "av": {
                "DrWeb": "BackDoor.Kuluoz.4",
                "FSecure": "Suspicious:W32/Malware!Online",
                "Clam": "PUA.Win32.Packer.Upx-53",
                "Symantec": "Trojan.Fakeavlock",
                "TrendMicro": "TROJ_SPNR.11LC13",
                "Avast": "Win32:Malware-gen",
                "GData": "Trojan.GenericKD.1449455",
                "Kaspersky": "Trojan-Downloader.Win32.Dofoil.rmy",
                "BitDefender": "Trojan.GenericKD.1449455",
                "McAfee": "RDN/Downloader.a!og",
                "Eset": "Win32/Kryptik.BQYU",
                "Avira": "TR/Crypt.ZPACK.Gen8",
                "Sunbelt": "Trojan.Win32.Dofoil.qtz",
                "K7": "Trojan ( 004912141 )",
                "Fortinet": "W32/DOFOIL.LF!tr",
                "Microsoft": "TrojanDownloader:Win32/Kuluoz.D",
                "AVG": "Generic_r.DHD",
                "K7GW": "Trojan ( 004912141 )",
                "Emsisoft": "Trojan.GenericKD.1449455",
                "QuickHeal": "TrojanDownloader.Kuluoz.aob",
                "Comodo": "UnclassifiedMalware"
            },
            "file_type": "exe",
            "ssdeep": "",
            "first_seen_date_utc": "2013-12-12 15:11:38",
            "md5": "039ea049f6d0f36f55ec064b3b371c46"
        }

        Example Output for Input Hash 039ea049f6d0f36f55ec064b3b371c46 (notepad.exe)::
        {
            "sha1": "7a90f8b051bc82cc9cadbcc9ba345ced02891a6c",
            "last_seen_date_utc": "2009-07-24 02:09:53",
            "file_type": "exe",
            "response_code": 200,
            "av": {},
            "ssdeep": "1536:bwOnbNQKLjWDyy1o5I0foMJUEbooPRrKKReFX3:RNQKPWDyDI0fFJltZrpReFX3",
            "first_seen_date_utc": "2009-07-24 02:09:53",
            "md5": "5e28284f9b5f9097640d58a73d38ad4c"
        }

        Example Output for a hash not found::
        {
            "response_code": 200,
            "results": "039ea049f6d0f36f55ec064b3b371c4A - not found."
        }

        """
        #: Validate Input
        hash_check = re.findall(r'(?i)(?<![a-zA-Z0-9])[a-fA-F0-9]{32}(?![a-zA-Z0-9])', this_hash)
        if len(this_hash) == 32 or len(this_hash) == 40 and len(hash_check) == 1:
            params = {'query': this_hash}
        else:
            return dict(error='Malformed Input: needs to be a single md5 or sha1 hash.', response_code=400)

        try:
            response = requests.get(self.shadowserver_av, params=params)
        except Exception:
            return dict(error=Exception)
        if response.status_code == requests.codes.ok:
            if '! No match found' in response.content:
                return dict(results='{} - not found.'.format(this_hash), response_code=response.status_code)
            elif '! Whitelisted' in response.content:
                return dict(results=response.content.strip('\n'), response_code=response.status_code)
            elif '! invalid request' in response.content:
                return dict(error='invalid request', response_code=response.status_code)
            else:
                lines = response.content.splitlines()
                extracted_list = lines[0].replace('"', '').strip().split(',')
                md5, sha1, first_seen_date_utc, last_seen_date_utc, file_type, ssdeep = extracted_list
                return dict(md5=md5, sha1=sha1, first_seen_date_utc=first_seen_date_utc, ssdeep=ssdeep,
                            last_seen_date_utc=last_seen_date_utc, file_type=file_type, av=json.loads(lines[1]),
                            response_code=response.status_code)
        else:
            print "Server Error Code: " + response.status_code
            return dict(response_code=response.status_code)

    @property
    def list_av_engines(self):
        """ Get list of Anti-Virus Vendors

        :return: list - Returns a list of AV vendor names.

        Example Output::
        {
            "response_code": 200,
            "av": [
                "AVG7",
                "AntiVir",
                "Avast-Commercial",
                "BitDefender",
                "Clam",
                "DrWeb",
                "F-Prot6",
                "F-Secure",
                "Ikarus",
                "Kaspersky",
                "McAfee",
                "NOD32",
                "Panda",
                "QuickHeal",
                "Sophos",
                "TrendMicro",
                "VBA32",
                "Vexira",
                "VirusBuster"
            ]
        }
        """
        try:
            response = requests.get('http://innocuous.shadowserver.org/api/?avvendors')
        except Exception:
            return dict(error=Exception)
        if response.status_code == requests.codes.ok:
            lines = response.content.splitlines()
            return dict(av=lines[0].replace('"', '').strip().split(','), response_code=response.status_code)

    ## Extended API -----------------------------------------------------------------------------------------------
    #  Access to the extended API calls are controlled by IP/CIDR Whitelisting.
    #  To gain access please send an email to request_api <AT> shadowserver.org
    #  with an explanation of why you would like access.
    #
    #  We will need to know the following information:
    #   - IP/CIDR
    #   - Full Name
    #   - Phone Number
    #   - E-Mail address for contact
    #   - Company

    # TODO : Implement download_sample
    def download_sample(self, this_md5):
        params = {'download': this_md5}
        response = requests.get(self.shadowserver_av, params=params)
        if response.status_code == requests.codes.ok:
            pass

    # TODO : Implement get_av_results_from_hash
    def get_av_results_from_hash(self, this_md5):
        params = {'avresult': this_md5}
        response = requests.get(self.shadowserver_av, params=params)
        if response.status_code == requests.codes.ok:
            pass
    # TODO : Implement get_ssdeep_matches
    def get_ssdeep_matches(self, this_ssdeep):
        params = {'ssdeep': this_ssdeep}
        response = requests.get(self.shadowserver_av, params=params)
        if response.status_code == requests.codes.ok:
            pass