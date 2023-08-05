
from openid.extensions.draft import pape2 as pape
from openid.message import *
from openid.server import server

import unittest

class PapeRequestTestCase(unittest.TestCase):
    def setUp(self):
        self.req = pape.Request()

    def test_construct(self):
        self.assertEqual([], self.req.preferred_auth_policies)
        self.assertEqual(None, self.req.max_auth_age)
        self.assertEqual('pape', self.req.ns_alias)

        req2 = pape.Request([pape.AUTH_MULTI_FACTOR], 1000)
        self.assertEqual([pape.AUTH_MULTI_FACTOR], req2.preferred_auth_policies)
        self.assertEqual(1000, req2.max_auth_age)

    def test_add_policy_uri(self):
        self.assertEqual([], self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.assertEqual([pape.AUTH_MULTI_FACTOR], self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.assertEqual([pape.AUTH_MULTI_FACTOR], self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_PHISHING_RESISTANT)
        self.assertEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT],
                             self.req.preferred_auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.assertEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT],
                             self.req.preferred_auth_policies)

    def test_getExtensionArgs(self):
        self.assertEqual({'preferred_auth_policies': ''}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://uri')
        self.assertEqual({'preferred_auth_policies': 'http://uri'}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://zig')
        self.assertEqual({'preferred_auth_policies': 'http://uri http://zig'}, self.req.getExtensionArgs())
        self.req.max_auth_age = 789
        self.assertEqual({'preferred_auth_policies': 'http://uri http://zig', 'max_auth_age': '789'}, self.req.getExtensionArgs())

    def test_parseExtensionArgs(self):
        args = {'preferred_auth_policies': 'http://foo http://bar',
                'max_auth_age': '9'}
        self.req.parseExtensionArgs(args)
        self.assertEqual(9, self.req.max_auth_age)
        self.assertEqual(['http://foo','http://bar'], self.req.preferred_auth_policies)

    def test_parseExtensionArgs_empty(self):
        self.req.parseExtensionArgs({})
        self.assertEqual(None, self.req.max_auth_age)
        self.assertEqual([], self.req.preferred_auth_policies)

    def test_fromOpenIDRequest(self):
        openid_req_msg = Message.fromOpenIDArgs({
          'mode': 'checkid_setup',
          'ns': OPENID2_NS,
          'ns.pape': pape.ns_uri,
          'pape.preferred_auth_policies': ' '.join([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT]),
          'pape.max_auth_age': '5476'
          })
        oid_req = server.OpenIDRequest()
        oid_req.message = openid_req_msg
        req = pape.Request.fromOpenIDRequest(oid_req)
        self.assertEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], req.preferred_auth_policies)
        self.assertEqual(5476, req.max_auth_age)

    def test_fromOpenIDRequest_no_pape(self):
        message = Message()
        openid_req = server.OpenIDRequest()
        openid_req.message = message
        pape_req = pape.Request.fromOpenIDRequest(openid_req)
        assert(pape_req is None)

    def test_preferred_types(self):
        self.req.addPolicyURI(pape.AUTH_PHISHING_RESISTANT)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        pt = self.req.preferredTypes([pape.AUTH_MULTI_FACTOR,
                                      pape.AUTH_MULTI_FACTOR_PHYSICAL])
        self.assertEqual([pape.AUTH_MULTI_FACTOR], pt)

class DummySuccessResponse:
    def __init__(self, message, signed_stuff):
        self.message = message
        self.signed_stuff = signed_stuff

    def getSignedNS(self, ns_uri):
        return self.signed_stuff

class PapeResponseTestCase(unittest.TestCase):
    def setUp(self):
        self.req = pape.Response()

    def test_construct(self):
        self.assertEqual([], self.req.auth_policies)
        self.assertEqual(None, self.req.auth_time)
        self.assertEqual('pape', self.req.ns_alias)
        self.assertEqual(None, self.req.nist_auth_level)

        req2 = pape.Response([pape.AUTH_MULTI_FACTOR], "2004-12-11T10:30:44Z", 3)
        self.assertEqual([pape.AUTH_MULTI_FACTOR], req2.auth_policies)
        self.assertEqual("2004-12-11T10:30:44Z", req2.auth_time)
        self.assertEqual(3, req2.nist_auth_level)

    def test_add_policy_uri(self):
        self.assertEqual([], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.assertEqual([pape.AUTH_MULTI_FACTOR], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.assertEqual([pape.AUTH_MULTI_FACTOR], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_PHISHING_RESISTANT)
        self.assertEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], self.req.auth_policies)
        self.req.addPolicyURI(pape.AUTH_MULTI_FACTOR)
        self.assertEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], self.req.auth_policies)

    def test_getExtensionArgs(self):
        self.assertEqual({'auth_policies': 'none'}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://uri')
        self.assertEqual({'auth_policies': 'http://uri'}, self.req.getExtensionArgs())
        self.req.addPolicyURI('http://zig')
        self.assertEqual({'auth_policies': 'http://uri http://zig'}, self.req.getExtensionArgs())
        self.req.auth_time = "1776-07-04T14:43:12Z"
        self.assertEqual({'auth_policies': 'http://uri http://zig', 'auth_time': "1776-07-04T14:43:12Z"}, self.req.getExtensionArgs())
        self.req.nist_auth_level = 3
        self.assertEqual({'auth_policies': 'http://uri http://zig', 'auth_time': "1776-07-04T14:43:12Z", 'nist_auth_level': '3'}, self.req.getExtensionArgs())

    def test_getExtensionArgs_error_auth_age(self):
        self.req.auth_time = "long ago"
        self.assertRaises(ValueError, self.req.getExtensionArgs)

    def test_getExtensionArgs_error_nist_auth_level(self):
        self.req.nist_auth_level = "high as a kite"
        self.assertRaises(ValueError, self.req.getExtensionArgs)
        self.req.nist_auth_level = 5
        self.assertRaises(ValueError, self.req.getExtensionArgs)
        self.req.nist_auth_level = -1
        self.assertRaises(ValueError, self.req.getExtensionArgs)

    def test_parseExtensionArgs(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_time': '1970-01-01T00:00:00Z'}
        self.req.parseExtensionArgs(args)
        self.assertEqual('1970-01-01T00:00:00Z', self.req.auth_time)
        self.assertEqual(['http://foo','http://bar'], self.req.auth_policies)

    def test_parseExtensionArgs_empty(self):
        self.req.parseExtensionArgs({})
        self.assertEqual(None, self.req.auth_time)
        self.assertEqual([], self.req.auth_policies)
      
    def test_parseExtensionArgs_strict_bogus1(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_time': 'yesterday'}
        self.assertRaises(ValueError, self.req.parseExtensionArgs,
                              args, True)

    def test_parseExtensionArgs_strict_bogus2(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_time': '1970-01-01T00:00:00Z',
                'nist_auth_level': 'some'}
        self.assertRaises(ValueError, self.req.parseExtensionArgs,
                              args, True)
      
    def test_parseExtensionArgs_strict_good(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_time': '1970-01-01T00:00:00Z',
                'nist_auth_level': '0'}
        self.req.parseExtensionArgs(args, True)
        self.assertEqual(['http://foo','http://bar'], self.req.auth_policies)
        self.assertEqual('1970-01-01T00:00:00Z', self.req.auth_time)
        self.assertEqual(0, self.req.nist_auth_level)

    def test_parseExtensionArgs_nostrict_bogus(self):
        args = {'auth_policies': 'http://foo http://bar',
                'auth_time': 'when the cows come home',
                'nist_auth_level': 'some'}
        self.req.parseExtensionArgs(args)
        self.assertEqual(['http://foo','http://bar'], self.req.auth_policies)
        self.assertEqual(None, self.req.auth_time)
        self.assertEqual(None, self.req.nist_auth_level)

    def test_fromSuccessResponse(self):
        openid_req_msg = Message.fromOpenIDArgs({
          'mode': 'id_res',
          'ns': OPENID2_NS,
          'ns.pape': pape.ns_uri,
          'pape.auth_policies': ' '.join([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT]),
          'pape.auth_time': '1970-01-01T00:00:00Z'
          })
        signed_stuff = {
          'auth_policies': ' '.join([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT]),
          'auth_time': '1970-01-01T00:00:00Z'
        }
        oid_req = DummySuccessResponse(openid_req_msg, signed_stuff)
        req = pape.Response.fromSuccessResponse(oid_req)
        self.assertEqual([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT], req.auth_policies)
        self.assertEqual('1970-01-01T00:00:00Z', req.auth_time)

    def test_fromSuccessResponseNoSignedArgs(self):
        openid_req_msg = Message.fromOpenIDArgs({
          'mode': 'id_res',
          'ns': OPENID2_NS,
          'ns.pape': pape.ns_uri,
          'pape.auth_policies': ' '.join([pape.AUTH_MULTI_FACTOR, pape.AUTH_PHISHING_RESISTANT]),
          'pape.auth_time': '1970-01-01T00:00:00Z'
          })

        signed_stuff = {}

        class NoSigningDummyResponse(DummySuccessResponse):
            def getSignedNS(self, ns_uri):
                return None

        oid_req = NoSigningDummyResponse(openid_req_msg, signed_stuff)
        resp = pape.Response.fromSuccessResponse(oid_req)
        self.assertTrue(resp is None)
