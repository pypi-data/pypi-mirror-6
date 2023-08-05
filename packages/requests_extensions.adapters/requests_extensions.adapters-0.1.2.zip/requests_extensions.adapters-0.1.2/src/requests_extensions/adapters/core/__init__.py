from requests.adapters import BaseAdapter, HTTPAdapter
from requests.compat import urlparse

class Helper(object):

    @classmethod
    def get_subclasses(helper_class, in_class):
        """ Get all of the subclasses of in_class (recursively) """

        subclasses = in_class.__subclasses__()
        for subclass in list(subclasses):
            subclasses.extend(helper_class.get_subclasses(subclass))
        return subclasses

class BaseAdapterExtension(BaseAdapter):
    """ A base class for the Adapter Extensions """

    SUPPORTED_SCHEMES = []

    @classmethod
    def supports_request(cls, request):
        """ Determines if this adapter extension is expected this 'type' of request.

            Returns True if the request.url scheme is supported by this extension.
            Otherwise returns False.

            An AdapterExtension should consider overriding this
            to perform more advanced logic
        """

        # Parse the request URL
        parsed_url = urlparse(request.url)

        # Determine the request scheme
        scheme = parsed_url.scheme

        # Check the scheme is supported
        if scheme in cls.SUPPORTED_SCHEMES:
            return True
        else:
            return False

class HTTPAdapterExtensionWrapper(HTTPAdapter, BaseAdapterExtension):
    """ A wrapper for the requests.HTTPAdapter class.

        Adds the SUPPORTED_SCHEMES information to the HTTPAdapter,
        making it compatible with the extension framework logic.
    """

    SUPPORTED_SCHEMES = ['http', 'https']

class FAdapterExtension(object):
    """ A Factory for selecting the appropriate AdapterExtension for a given
        request.
    """

    @classmethod
    def get_adapter_extension_class(cls, request):
        """ Returns the appropraite AdapterExtension to handle the request.

            If no AdapterExtension supports the request, None is returned.
        """

        # Iterate over the adapters that subclass BaseAdapterExtension
        for adapter_extension_cls in Helper.get_subclasses(BaseAdapterExtension):

            # If the adapter supports the request, return the adapter class
            if adapter_extension_cls.supports_request(request):
                return adapter_extension_cls

        return None
