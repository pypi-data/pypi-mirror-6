import unittest
import imghdr

from . import evercam

evercam.API_URL = 'http://proxy.evercam.io:3000/v1'
evercam.basic_auth = ('joeyb', '12345')


class TestVendors(unittest.TestCase):
    def test_vendors(self):
        vendors = evercam.Vendor.all()
        self.assertIsInstance(vendors, list)
        self.assertIsInstance(vendors[0], evercam.Vendor)

    def test_vendors_mac(self):
        vendors = evercam.Vendor.by_mac('00:73:57')
        self.assertIsInstance(vendors, list)
        self.assertEqual(len(vendors), 1)
        self.assertEqual(vendors[0]['id'], 'testid')
        self.assertEqual('00:73:57' in vendors[0]['known_macs'], True)

        with self.assertRaises(evercam.errors.NotFound) as e:
            evercam.Vendor.by_mac('GG:GG:GG')


class TestModels(unittest.TestCase):
    def test_models(self):
        vendors = evercam.Model.all()
        self.assertIsInstance(vendors, list)
        self.assertIsInstance(vendors[0], evercam.Vendor)
        self.assertEqual('models' in vendors[0], True)

    def test_models_vendor(self):
        vendor = evercam.Model.by_vendor('testid')
        self.assertIsInstance(vendor, evercam.Vendor)
        self.assertEqual(vendor.id, 'testid')
        self.assertEqual('00:73:57' in vendor.known_macs, True)
        self.assertEqual('YCW005' in vendor.models, True)

        with self.assertRaises(evercam.errors.NotFound) as e:
            evercam.Model.by_vendor('nonExistentId')

    def test_models_vendor_model(self):
        model = evercam.Model.by_vendor('testid').model('YCW005')
        self.assertIsInstance(model, evercam.Model)
        self.assertEqual('defaults' in model, True)
        self.assertEqual('YCW005', model.name)
        self.assertEqual('testid', model.vendor)

        with self.assertRaises(evercam.errors.NotFound) as e:
            evercam.Model.by_vendor('nonExistentId').model('YCW005')


class TestUsers(unittest.TestCase):
    def test_create(self):
        user = evercam.User.create({'forename': 'Joe', 'lastname': 'Bloggs', 'email': 'joe.bloggs@example.org',
                                    'username': 'joeyb', 'country': 'us'})
        self.assertIsInstance(user, evercam.User)
        self.assertEqual(user.id, 'joeyb')
        self.assertEqual(user.forename, 'Joe')
        self.assertEqual(user.lastname, 'Bloggs')
        self.assertEqual(user.email, 'joe.bloggs@example.org')
        self.assertEqual(user.country, 'us')

        cameras = user.cameras()
        self.assertIsInstance(cameras, list)
        self.assertIsInstance(cameras[0], evercam.Camera)

        with self.assertRaises(evercam.errors.UsernameAlreadyExists) as e:
            evercam.User.create({'forename': 'Joe', 'lastname': 'Bloggs', 'email': 'joe.bloggs@example.org',
                                 'username': 'fail', 'country': 'us'})


class TestCameras(unittest.TestCase):
    def test_create(self):
        camera = evercam.Camera.create({'id': 'testcamera', 'endpoints': ['http://127.0.0.1:8080'],
                                       'is_public': True, "snapshots": {'jpg': '/onvif/snapshot'},
                                       'auth': {'basic': {'username': 'user1', 'password': 'abcde'}}})
        self.assertIsInstance(camera, evercam.Camera)
        self.assertEqual(camera.id, 'testcamera')
        self.assertEqual(camera.is_public, True)

        with self.assertRaises(evercam.errors.BadRequest) as e:
            evercam.Camera.create({'id': 'fail', 'endpoints': ['http://127.0.0.1:8080'],
                                  'is_public': True, "snapshots": {'jpg': '/onvif/snapshot'},
                                  'auth': {'basic': {'username': 'user1', 'password': 'abcde'}}})

    def test_byuser(self):
        cameras = evercam.Camera.by_user('joeyb')
        self.assertIsInstance(cameras, list)
        self.assertIsInstance(cameras[0], evercam.Camera)

    def test_byid(self):
        camera = evercam.Camera.by_id('testcamera')
        self.assertIsInstance(camera, evercam.Camera)
        self.assertEqual(camera.id, 'testcamera')
        self.assertEqual(camera.is_public, True)

        # Test snapshots
        jpg = camera.get_snapshot()
        self.assertEqual(imghdr.what(None, jpg.content), 'jpeg')


if __name__ == '__main__':
    unittest.main()