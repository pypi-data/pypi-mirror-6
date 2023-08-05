"""Tests for drest.exc."""

import os
import unittest
from nose.tools import eq_, raises
import drest
from drest.testing import MOCKAPI

api = drest.api.API(MOCKAPI)

class ExceptionTestCase(unittest.TestCase):
    @raises(drest.exc.dRestError)
    def test_error(self):
        try:
            raise drest.exc.dRestError('Error Msg')
        except drest.exc.dRestError as e:
            e.__repr__()
            eq_(e.msg, 'Error Msg')
            eq_(e.__str__(), str(e.msg))
            raise

    @raises(drest.exc.dRestInterfaceError)
    def test_interface_error(self):
        try:
            raise drest.exc.dRestInterfaceError('Error Msg')
        except drest.exc.dRestInterfaceError as e:
            e.__repr__()
            eq_(e.msg, 'Error Msg')
            eq_(e.__str__(), str(e.msg))
            raise

    @raises(drest.exc.dRestRequestError)
    def test_request_error(self):
        try:
            api = drest.api.API(MOCKAPI)
            response = api.make_request('GET', '/')
            raise drest.exc.dRestRequestError('Error Msg', response)
        except drest.exc.dRestRequestError as e:
            e.__repr__()
            eq_(e.msg, 'Error Msg')
            eq_(e.__str__(), str(e.msg))
            raise
        
    @raises(drest.exc.dRestResourceError)
    def test_resource_error(self):
        try:
            raise drest.exc.dRestResourceError('Error Msg')
        except drest.exc.dRestResourceError as e:
            e.__repr__()
            eq_(e.msg, 'Error Msg')
            eq_(e.__str__(), str(e.msg))
            raise
        
    @raises(drest.exc.dRestAPIError)
    def test_api_error(self):
        try:
            raise drest.exc.dRestAPIError('Error Msg')
        except drest.exc.dRestAPIError as e:
            e.__repr__()
            eq_(e.msg, 'Error Msg')
            eq_(e.__str__(), str(e.msg))
            raise