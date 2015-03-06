__author__ = 'fer'


from sweeper.cloud.common import Resource
from sweeper.cloud.common import generate_random_password


def create_resource(name):
    res = Resource(name, '{0}.cloudapp.net', generate_random_password())

    return res