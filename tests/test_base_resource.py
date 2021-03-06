# -*- coding: utf-8 -*-
from __future__ import with_statement
import six
if six.PY3:
    import unittest
else:
    import unittest2 as unittest

from mock import Mock
from nose.tools import assert_equal, assert_true, assert_is_none
from twilio.rest.resources import Resource
from twilio.rest.resources import ListResource
from twilio.rest.resources import InstanceResource
from six import advance_iterator

base_uri = "https://api.twilio.com/2010-04-01"
account_sid = "AC123"
auth = (account_sid, "token")


def test_resource_init():
    r = Resource(base_uri, auth)
    uri = "%s/%s" % (base_uri, r.name)

    assert_equal(r.base_uri, base_uri)
    assert_equal(r.auth, auth)
    assert_equal(r.uri, uri)


def test_equivalence():
    p = ListResource(base_uri, auth)
    r1 = p.load_instance({"sid": "AC123"})
    r2 = p.load_instance({"sid": "AC123"})
    assert_equal(r1, r2)


class ListResourceTest(unittest.TestCase):

    def setUp(self):
        self.r = ListResource(base_uri, auth)

    def testListResourceInit(self):
        uri = "%s/%s" % (base_uri, self.r.name)
        self.assertEquals(self.r.uri, uri)

    def testKeyValueLower(self):
        self.assertEquals(self.r.key, self.r.name.lower())

    def testIterNoKey(self):
        self.r.request = Mock()
        self.r.request.return_value = Mock(), {}

        with self.assertRaises(StopIteration):
            advance_iterator(self.r.iter())

    def testRequest(self):
        self.r.request = Mock()
        self.r.request.return_value = Mock(), {self.r.key: [{'sid': 'foo'}]}
        advance_iterator(self.r.iter())
        self.r.request.assert_called_with("GET", "https://api.twilio.com/2010-04-01/Resources", params={})

    def testIterOneItem(self):
        self.r.request = Mock()
        self.r.request.return_value = Mock(), {self.r.key: [{'sid': 'foo'}]}

        items = self.r.iter()
        advance_iterator(items)

        with self.assertRaises(StopIteration):
            advance_iterator(items)

    def testIterNoNextPage(self):
        self.r.request = Mock()
        self.r.request.return_value = Mock(), {self.r.key: []}

        with self.assertRaises(StopIteration):
            advance_iterator(self.r.iter())

    def testKeyValue(self):
        self.r.key = "Hey"
        self.assertEquals(self.r.key, "Hey")

    def testInstanceLoading(self):
        instance = self.r.load_instance({"sid": "foo"})

        self.assertIsInstance(instance, InstanceResource)
        self.assertEquals(instance.sid, "foo")


class testInstanceResourceInit(unittest.TestCase):

    def setUp(self):
        self.parent = ListResource(base_uri, auth)
        self.r = InstanceResource(self.parent, "123")
        self.uri = "%s/%s" % (self.parent.uri, "123")

    def testInit(self):
        self.assertEquals(self.r.uri, self.uri)

    def testLoad(self):
        self.r.load({"hey": "you"})
        self.assertEquals(self.r.hey, "you")

    def testLoadWithUri(self):
        self.r.load({"hey": "you", "uri": "foobar"})
        self.assertEquals(self.r.hey, "you")
        self.assertEquals(self.r.uri, self.uri)

    def testLoadDateCreated(self):
        self.r.load({"date_created": "Sat, 29 Sep 2012 12:47:54 +0000",
                     "uri": "foobar"})
        try:
            assert_true(hasattr(self.r.date_created, "day"))
            assert_equal(self.r.date_created.day, 29)
        except AttributeError:
            pass

    def testLoadNullDate(self):
        self.r.load({"date_created": None, "uri": "foobar"})
        assert self.r.date_created is None

    def testLoadWithFrom(self):
        self.r.load({"from": "foo"})
        self.assertEquals(self.r.from_, "foo")

    def testLoadSubresources(self):
        m = Mock()
        self.r.subresources = [m]
        self.r.load_subresources()
        m.assert_called_with(self.r.uri, self.r.auth)
