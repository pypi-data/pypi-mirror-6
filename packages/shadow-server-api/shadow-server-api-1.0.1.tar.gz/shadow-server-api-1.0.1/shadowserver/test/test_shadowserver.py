#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Josh Maine'
__version__ = '1.0.1'
__license__ = 'GPLv3'

import json
from unittest import TestCase
from shadowserver.shadow_server_api import ShadowServerApi


class InitTests(TestCase):
    def test_list_av_engines(self):
        myteam = ShadowServerApi()

        try:
            print 'Get list of Anti-Virus Vendors'
            print json.dumps(myteam.list_av_engines, sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_get_av_hash_not_found(self):
        myteam = ShadowServerApi()

        try:
            print 'Get AV Results for NOT FOUND {}'.format('039ea049f6d0f36f55ec064b3b371c4A')
            print json.dumps(myteam.get_av('039ea049f6d0f36f55ec064b3b371c4A'), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_get_av_hash_found(self):
        myteam = ShadowServerApi()

        try:
            print 'Get AV Results for FOUND {}'.format('039ea049f6d0f36f55ec064b3b371c46')
            print json.dumps(myteam.get_av('039ea049f6d0f36f55ec064b3b371c46'), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_get_av_hash_clean(self):
        myteam = ShadowServerApi()

        try:
            print 'Get AV Results for {}'.format('5e28284f9b5f9097640d58a73d38ad4c')
            print json.dumps(myteam.get_av('5e28284f9b5f9097640d58a73d38ad4c'), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_get_av_bad_input(self):
        myteam = ShadowServerApi()

        try:
            print 'Get AV Results for {}'.format('Not a hash')
            print json.dumps(myteam.get_av('Not a hash'), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_get_bintest_not_found(self):
        myteam = ShadowServerApi()

        try:
            print 'Get Binary Whitelist Test Results for NOT FOUND {}'.format('039ea049f6d0f36f55ec064b3b371c4A')
            print json.dumps(myteam.get_bintest('039ea049f6d0f36f55ec064b3b371c4A'), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_get_bintest_found(self):
        myteam = ShadowServerApi()

        try:
            print 'Get Binary Whitelist Test Results for {}'.format('5e28284f9b5f9097640d58a73d38ad4c')
            print json.dumps(myteam.get_bintest('5e28284f9b5f9097640d58a73d38ad4c'), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)

    def test_get_bintest_bad_input(self):
        myteam = ShadowServerApi()

        try:
            print 'Get Binary Whitelist Test Results for {}'.format('Not a hash')
            print json.dumps(myteam.get_bintest('Not a hash'), sort_keys=False, indent=4)
        except Exception as e:
            self.fail(e)