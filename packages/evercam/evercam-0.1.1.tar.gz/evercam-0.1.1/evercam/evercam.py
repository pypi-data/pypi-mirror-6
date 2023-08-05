import json
import requests

from . import errors

API_VERSION = 'v1'
API_URL = 'http://api.evercam.io/%s' % API_VERSION


class EvercamClient(object):

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

    def basic_auth(self):
        pass


class EvercamObject(dict):

    def __init__(self, data=None, **params):
        super(EvercamObject, self).__init__()
        if data:
            for k, v in data.items():
                super(EvercamObject, self).__setitem__(k, v)
                self.__setattr__(k, v)

    @classmethod
    def retrieve(cls, oid, **params):
        instance = cls({'id': oid}, **params)
        instance.refresh()
        return instance

    def refresh(self):
        self.make_req(self.instance_url(), 'GET')
        return self

    @classmethod
    def class_name(cls):
        return str(cls.__name__.lower())

    @classmethod
    def class_url(cls):
        cls_name = cls.class_name()
        return "%ss" % (cls_name,)

    def instance_url(self):
        oid = self.get('id')
        base = self.class_url()
        return "/%s/%s" % (base, oid)

    @staticmethod
    def make_req(target, method, param=None):
        url = "%s%s" % (API_URL, target)

        if method == 'GET':
            try:
                headers = {'Connection': 'close'}
                r = requests.get(url, params=param, headers=headers)
                if r.status_code == 404:
                    raise errors.NotFound()
                content = {'data': r.json(), 'code': r.status_code}
            except requests.HTTPError as e:
                    content = {'data': e.reason, 'code': r.response.status_code}
            return content

        elif method == 'POST':
            try:
                headers = {'Connection': 'close'}
                r = requests.post(url, params=param, headers=headers)
                if r.status_code == 404:
                    raise errors.NotFound()
                content = {'data': r.json(), 'code': r.status_code}
            except requests.HTTPError as e:
                    content = {'data': e.reason, 'code': r.response.status_code}
            return content


class User(EvercamObject):

    @staticmethod
    def create_user(param=None):
        """Create user.
        Args:
            - ``param``: New user parameters: forename, lastname, email, username, country

        Returns:
            - A User object

        Raises:
            - A :class:`evercam.UsernameAlreadyExists` when received HTTP status of
            400: Bad request when username already exists

        """
        response = EvercamObject.make_req("/users", 'POST', param)
        if response['code'] == 201:
            return User(response['data']['users'][0])
        elif response['code'] == 400:
            raise errors.UsernameAlreadyExists('Username %s already exists' % param['username'])
        else:
            return []


class Vendor(EvercamObject):

    @staticmethod
    def all(extra=''):
        """Returns list of all vendors.
        Returns:
            - A list containing the Vendor objects
        """
        vendors = []
        response = EvercamObject.make_req("/vendors%s" % extra, 'GET')
        if response['code'] == 200:
            for v in response['data']['vendors']:
                vendors.append(Vendor(v))
        return vendors

    @staticmethod
    def by_mac(mac):
        """Returns list of vendors which use MAC address starting with ``mac``.
        Args:
            - ``mac``: MAC address (first three octects or all six)

        Returns:
            - A list containing the Vendor objects
        """
        return Vendor.all("/%s" % mac)


class Snapshot(EvercamObject):

    @staticmethod
    def get_snapshots(stream):
        """Returns all data required to connect to the stream device, authenticate where nessessary, and retrieve images
         in whatever formats are currently available.
        Args:
            - ``stream``: Stream name

        Returns:
            - Sanpshot object
        """
        response = EvercamObject.make_req("/streams/%s/snapshots/new" % stream, 'GET')
        if response['code'] == 200:
            return Snapshot(response['data'])
        else:
            return []
