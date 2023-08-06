# -*- coding: iso-8859-15 -*-
"""ReadOnly FunkLoad test

$Id: $
"""
import unittest

from funkload import FunkLoadTestCase


class Readonly(FunkLoadTestCase.FunkLoadTestCase):
    """Read only load test scenario

    This test use a configuration file Readonly.conf.
    """

    def setUp(self):
        """Setting up test."""
        self.logd("setUp")
        self.server_url = self.conf_get('main', 'url')
        # XXX here you can setup the credential access like this
        # credential_host = self.conf_get('credential', 'host')
        # credential_port = self.conf_getInt('credential', 'port')
        # self.login, self.password = xmlrpc_get_credential(credential_host,
        #                                                   credential_port,
        # XXX replace with a valid group
        #                                                   'members')

    def test_ReadOnly(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------

        self.get(server_url + "/coreloadtests",
            description="Get /coreloadtests")

        self.get(server_url + "/coreloadtests/Members",
            description="Get /coreloadtests/Members")

        self.get(server_url + "/coreloadtests/contact-info",
            description="Get /coreloadtests/contact-info")

        self.get(server_url + "/coreloadtests/folder_listing",
            description="Get coreloadtests/folder_listing")

        self.get(server_url + "/coreloadtests/sitemap",
            description="Get coreloadtests/sitemap")

        self.get(server_url + "/coreloadtests/search?Type=Page",
            description="Get /coreloadtests/search?Type=Page")

        # end of test -----------------------------------------------

    def tearDown(self):
        """Setting up test."""
        self.logd("tearDown.\n")

def test_suite():
    return unittest.makeSuite(Readonly)

additional_tests = test_suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
