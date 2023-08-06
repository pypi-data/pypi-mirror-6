import base64
import json
import unittest

from libsaas import port
from libsaas.executors import test_executor
from libsaas.services import mixpanel


class MixpanelTestCase(unittest.TestCase):

    def setUp(self):
        self.executor = test_executor.use()
        self.executor.set_response(b'1', 200, {})

        self.service = mixpanel.Mixpanel('my-token', 'api-key', 'api-secret')

    def serialize(self, data):
        return base64.b64encode(json.dumps(data).encode('utf-8'))

    def expect(self, uri, params_expected=None, subdomain=None, b64params=()):
        if not subdomain:
            domain = 'mixpanel.com'
        else:
            domain = '{0}.mixpanel.com'.format(subdomain)

        if subdomain != 'api':
            uri = 'api/2.0/{0}'.format(uri)

        self.assertEqual(self.executor.request.uri,
                         'http://{0}/{1}'.format(domain, uri))
        if not params_expected:
            return

        params_used = self.executor.request.params.copy()

        if 'api_key' in params_used:
            params_expected['api_key'] = 'api-key'

        params_used.pop('sig', None)
        params_used.pop('expire', None)

        for name in b64params:
            decoded = base64.b64decode(params_used[name])
            params_used[name] = json.loads(port.to_u(decoded))

        self.assertEqual(params_used, params_expected)

    def test_track(self):
        ret = self.service.track('login', {'user': 'foo', 'important': True,
                                           'widgets': ['foo', 'bar']}, ip=True)
        data = self.serialize({'event': 'login',
                               'properties': {'token': 'my-token',
                                              'user': 'foo',
                                              'important': True,
                                              'widgets': ['foo', 'bar']}})
        self.expect('track/', {'data': data, 'ip': '1', 'test': '0'}, 'api')
        self.assertTrue(ret)

        ret = self.service.track('logout', test=True)
        data = {'event': 'logout', 'properties': {'token': 'my-token'}}
        self.expect('track/', {'data': data, 'ip': '0', 'test': '1'}, 'api',
                    b64params=('data', ))
        self.assertTrue(ret)

    def test_engage(self):
        ret = self.service.engage(42, {"$set": {"$first_name": "John",
                                                "$last_name": "Smith"}})
        data = {'$token': 'my-token', '$distinct_id': 42,
                "$set": {"$first_name": "John", "$last_name": "Smith"}}

        self.expect('engage/', {'data': data}, 'api', b64params=('data', ))
        self.assertTrue(ret)

    def test_track_failure(self):
        self.executor.set_response(b'0', 200, {})

        ret = self.service.track('ev')
        self.assertFalse(ret)

    def test_events(self):
        self.service.events().get(['login', 'logout'], 'general', 'day', 10)
        self.expect('events/', {'event': json.dumps(['login', 'logout']),
                                'type': 'general', 'unit': 'day',
                                'interval': 10})

        self.service.events().top('general', limit=10)
        self.expect('events/top/', {'type': 'general', 'limit': 10})

        self.service.events().names('general')
        self.expect('events/names/', {'type': 'general'})

    def test_properties(self):
        self.service.properties().get('login', 'plan', 'unique', 'day', 7,
                                      values=['standard', 'premium'])

        self.expect('events/properties/',
                    {'event': 'login', 'name': 'plan', 'type': 'unique',
                     'unit': 'day', 'interval': 7,
                     'values': json.dumps(['standard', 'premium'])})

        self.service.properties().top('login')
        self.expect('events/properties/top/', {'event': 'login'})

        self.service.properties().values('login', 'plan', bucket='10')
        self.expect('events/properties/values/',
                    {'event': 'login', 'name': 'plan', 'bucket': '10'})

    def test_funnels(self):
        self.service.funnels().get(10, '2012-01-01', length=5)
        self.expect('funnels/', {'funnel_id': 10, 'from_date': '2012-01-01',
                                  'length': 5})

        self.service.funnels().list()
        self.expect('funnels/list/', {})

    def test_segmentation(self):
        self.service.segmentation().get('login', '2011-01-01',
                                        '2012-01-01', type='unique')
        self.expect('segmentation/',
                    {'event': 'login', 'from_date': '2011-01-01',
                     'to_date': '2012-01-01', 'type': 'unique'})

        self.service.segmentation().numeric('login', '2011-01-01',
                                            '2012-01-01', on='true', buckets=3)
        self.expect('segmentation/numeric/',
                    {'event': 'login', 'from_date': '2011-01-01',
                     'to_date': '2012-01-01', 'on': 'true', 'buckets': 3})

        on = 'properties["succeeded"] - property["failed"]'
        self.service.segmentation().sum('buy', '2011-01-01', '2012-01-01', on)
        self.expect('segmentation/sum/',
                    {'event': 'buy', 'from_date': '2011-01-01',
                     'to_date': '2012-01-01', 'on': on})

        on = 'property["amount"]'
        self.service.segmentation().average('pay', '2011-01-01',
                                            '2012-01-01', on, 'day')
        self.expect('segmentation/average/',
                    {'event': 'pay', 'from_date': '2011-01-01',
                     'to_date': '2012-01-01', 'on': on, 'unit': 'day'})

        inner = 'property["amount"]'
        outer = 'property["succeeded"]'
        self.service.segmentation().multiseg('pay', 'general', '2011-01-01',
                                            '2012-01-01', inner, outer, 25, 'day')
        self.expect('segmentation/multiseg/',
                    {'event': 'pay', 'type': 'general', 'from_date': '2011-01-01',
                     'to_date': '2012-01-01', 'inner': inner, 'outer': outer, 'limit': 25, 'unit': 'day'})

    def test_retention(self):
        self.service.retention().get('2011-01-01', '2012-01-01',
                                     born_event='login', limit=10)
        self.expect('retention/',
                    {'from_date': '2011-01-01', 'to_date': '2012-01-01',
                     'born_event': 'login', 'limit': 10})

    def test_export(self):
        self.executor.set_response(b'{"foo": "bar"}\n{"baz": "quuz"}', 200, {})
        res = self.service.export('2011-01-01', '2012-01-01',
                                  ['login', 'logout'])
        self.expect('export/',
                    {'from_date': '2011-01-01', 'to_date': '2012-01-01',
                     'event': json.dumps(['login', 'logout'])}, 'data')

        self.assertEqual(res, [{'foo': 'bar'}, {'baz': 'quuz'}])

    def test_no_key(self):
        self.service = mixpanel.Mixpanel('my-token')

        # tracking is allowed without setting the api key and api secret
        self.service.track('login')
        data = {'event': 'login', 'properties': {'token': 'my-token'}}
        self.expect('track/', {'data': data, 'ip': '0', 'test': '0'}, 'api',
                    b64params=('data', ))

        # but data export methods fail
        exc = mixpanel.InsufficientSettings
        self.assertRaises(exc, self.service.funnels().list)
        self.assertRaises(exc, self.service.export,
                          '2011-01-01', '2012-01-01', ['login', 'logout'])

    def test_unicode(self):
        # return the lambda Unicode character
        self.executor.set_response(b'{"lambda": "\xce\xbb"}', 200, {})
        # and send a capital lambda in the request
        self.service.export('2011-01-01', '2012-01-01', [b'\xce\x9b'])

        self.expect('export/',
                    {'from_date': '2011-01-01', 'to_date': '2012-01-01',
                     'event': r'["\u039b"]'}, 'data')

        # try a unicode event name
        self.executor.set_response(b'1', 200, {})
        self.service.track(b'\xce\xbb'.decode('utf-8'))
        data = {'event': b'\xce\xbb'.decode('utf-8'), 'properties': {'token': 'my-token'}}
        self.expect('track/', {'data': data, 'ip': '0', 'test': '0'}, 'api',
                    b64params=('data', ))
