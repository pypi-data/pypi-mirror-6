import requests
import json
import time
from datetime import timedelta

from . import errors

API_VERSION = 'v1'
API_URL = 'https://api.evercam.io/%s' % API_VERSION
basic_auth = None


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
        global API_URL
        url = "%s%s" % (API_URL, target)
        headers = {'Connection': 'close', 'Content-Type': 'application/json'}
        if method == 'GET':
            try:
                r = requests.get(url, params=param, headers=headers)
                if r.status_code == 404:
                    raise errors.NotFound()
                content = {'data': r.json(), 'code': r.status_code}
            except requests.HTTPError as e:
                    content = {'data': e.reason, 'code': r.response.status_code}
            return content

        elif method == 'POST':
            try:
                r = requests.post(url, data=json.dumps(param), headers=headers, auth=basic_auth)
                if r.status_code == 404:
                    raise errors.NotFound()
                if r.status_code == 401:
                    raise errors.AuthenticationRequired()
                content = {'data': r.json(), 'code': r.status_code}
            except requests.HTTPError as e:
                    content = {'data': e.reason, 'code': r.response.status_code}
            return content


class Camera(EvercamObject):
    url = '/cameras'

    def __init__(self, data=None, **params):
        super(Camera, self).__init__(data)
        self.endpoint = None
        self.lastendpointcheck = 0

    @staticmethod
    def create(param=None):
        response = EvercamObject.make_req(Camera.url, 'POST', param)
        if response['code'] == 201:
            return Camera(response['data']['cameras'][0])
        elif response['code'] == 400:
            raise errors.BadRequest(response['data']['message'])
        else:
            return []

    @staticmethod
    def by_user(uid):
        cameras = []
        response = EvercamObject.make_req('%s/%s%s' % (User.url, uid, Camera.url), 'GET')
        if response['code'] == 200:
            for s in response['data']['cameras']:
                cameras.append(Camera(s))
        elif response['code'] == 400:
            raise errors.NotFound('Username %s not found' % uid)
        return cameras

    @staticmethod
    def by_id(sid):
        response = EvercamObject.make_req('%s/%s' % (Camera.url, sid), 'GET')
        if response['code'] == 200:
            return Camera(response['data']['cameras'][0])
        elif response['code'] == 400:
            raise errors.NotFound('Camera %s not found' % sid)
        else:
            return []

    def select_endpoint(self):
        # Check for fastest endpoint every minute
        current = int(time.time())
        if current - self.lastendpointcheck > 60000:
            self.lastendpointcheck = current
        else:
            return
        fastest = timedelta(seconds=100)
        for e in self.endpoints:
            url = e + self.snapshots['jpg']
            r = requests.get(url)
            if r.status_code == 401:
                r = requests.get(url, auth=(self.auth['basic']['username'], self.auth['basic']['password']))
            if r.status_code == 200:
                restime = r.elapsed
                if restime < fastest:
                    fastest = restime
                    self.endpoint = e

    def get_snapshot(self):
        self.select_endpoint()
        if self.endpoint is None:
            raise errors.NoActiveEndpoint()
        url = self.endpoint + self.snapshots['jpg']
        return requests.get(url, auth=(self.auth['basic']['username'], self.auth['basic']['password']), stream=True)


class User(EvercamObject):
    url = '/users'

    @staticmethod
    def create(param=None):
        """Create user.
        Args:
            - ``param``: New user parameters: forename, lastname, email, username, country

        Returns:
            - A User object

        Raises:
            - A :class:`evercam.UsernameAlreadyExists` when received HTTP status of
            400: Bad request when username already exists

        """
        response = EvercamObject.make_req(User.url, 'POST', param)
        if response['code'] == 201:
            return User(response['data']['users'][0])
        elif response['code'] == 400:
            raise errors.UsernameAlreadyExists('Username %s already exists' % param['username'])
        else:
            return []

    def cameras(self):
        return Camera.by_user(self.id)


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

    def model(self, mid):
        response = EvercamObject.make_req("/models/%s/%s" % (self.id, mid), 'GET')
        if response['code'] == 200:
            return Model(response['data']['models'][0])
        else:
            raise errors.NotFound('Model %s not found for vendor %s' % (mid, self.id))


class Model(EvercamObject):

    @staticmethod
    def all(extra=''):
        """Returns list of all IP camera vendors along with any MAC address prefixes they are known to use and the list
         of model names we currently hold configuration information about on Evercam.
        Returns:
            - A list containing the Vendor objects
        """
        vendors = []
        response = EvercamObject.make_req("/models%s" % extra, 'GET')
        if response['code'] == 200:
            for v in response['data']['vendors']:
                vendors.append(Vendor(v))
        return vendors

    @staticmethod
    def by_vendor(vid):
        """Returns Vendor containing list of models.
        Args:
            - ``vid``: Vendor id

        Returns:
            - Vendor object
        """
        response = EvercamObject.make_req("/models/%s" % vid, 'GET')
        if response['code'] == 200:
            return Vendor(response['data']['vendors'][0])
        else:
            raise errors.NotFound('Vendor %s not found' % vid)

