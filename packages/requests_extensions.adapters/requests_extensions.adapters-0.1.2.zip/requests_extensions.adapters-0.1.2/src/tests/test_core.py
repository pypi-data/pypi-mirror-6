import unittest
from requests import Request
from requests_extensions.adapters.core import HTTPAdapterExtensionWrapper, FAdapterExtension

class TestFAdapterExtension(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_http_request_returns_http_adapter_extension(self):
        req = Request('GET', 'https://example.com')
        cls = FAdapterExtension.get_adapter_extension_class(req)
        self.assertEqual(cls, HTTPAdapterExtensionWrapper)

    def test_https_request_returns_http_adapter_extension(self):
        req = Request('GET', 'http://example.com')
        cls = FAdapterExtension.get_adapter_extension_class(req)
        self.assertEqual(cls, HTTPAdapterExtensionWrapper)

    def test_unexpected_scheme_returns_none(self):
        req = Request('GET', 'unexpected://example.com')
        cls = FAdapterExtension.get_adapter_extension_class(req)
        self.assertEqual(cls, None)

    def test_file_scheme_returns_none(self):
        req = Request('GET', 'file://example.com')
        cls = FAdapterExtension.get_adapter_extension_class(req)
        self.assertEqual(cls, None)

    def test_http_adapter_extension_supports_http_and_https(self):
        self.assertEqual(HTTPAdapterExtensionWrapper.SUPPORTED_SCHEMES, ['http', 'https'])
