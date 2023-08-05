from urlparse import urlparse

from s3 import S3Storage
from cloudfiles import CloudfilesStorage

available_services = {
    's3': S3Storage,
    # Cloudfiles currently disabled, it's just not production ready yet.
    # 'cf': CloudfilesStorage
}


def luggage(url, credentials=()):
    """
    Creates a handle to the cloud storage denoted by the URL.

    The following URL formats are supported:

    * Amazon S3: s3://[region]/bucket/ with credentials=(access_key, secret_key)
    * Cloudfiles: cf://region/container/ with credentials=(username, key)
    """
    parsed_url = urlparse(url)

    try:
        service = available_services[parsed_url.scheme]
        return service(parsed_url, credentials)
    except KeyError:
        raise ValueError('Unsupported service {}'.format(parsed_url.scheme))


def get_available_schemes():
    return available_services.keys()