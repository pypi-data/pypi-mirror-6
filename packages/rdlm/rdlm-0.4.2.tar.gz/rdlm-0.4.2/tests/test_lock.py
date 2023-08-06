#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tornado.testing
from rdlm.main import get_app as rdlm_get_app
from rdlm.main import get_ioloop as rdlm_get_ioloop
import json
import tornado.ioloop
import tornado.gen
import time

TEST_MULTIPLE_WAITERS1 = 0
TEST_MULTIPLE_WAITERS2 = 0


class LockTestCase(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        return rdlm_get_app()

    # compatibility with python 2.6
    def assertIn(self, str1, str2):
        self.assertTrue(str1 in str2)

    def get_new_ioloop(self):
        return rdlm_get_ioloop()

    def tearDown(self):
        req = tornado.httpclient.HTTPRequest(self.get_url("/resources"), method='DELETE')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        super(LockTestCase, self).tearDown()

    def test_not_acquired_lock_bad_json(self):
        tmp = {"wait": 5, "lifetime": 10, "title": "test case"}
        raw_body = json.dumps(tmp)[0:10]
        req = tornado.httpclient.HTTPRequest(self.get_url('/locks/resource1'), method='POST',
                                             body=raw_body)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 400)

    def test_not_acquired_lock_empty_body(self):
        raw_body = ""
        req = tornado.httpclient.HTTPRequest(self.get_url('/locks/resource1'), method='POST',
                                             body=raw_body)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 400)

    def test_not_acquired_lock_missing_field(self):
        tmp = {"wait": 5, "lifetime": 10}
        raw_body = json.dumps(tmp)
        req = tornado.httpclient.HTTPRequest(self.get_url('/locks/resource1'), method='POST',
                                             body=raw_body)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 400)

    def _acquire_lock(self, resource, wait, lifetime, title, callback=None):
        tmp = {"wait": wait, "lifetime": lifetime, "title": title}
        raw_body = json.dumps(tmp)
        req = tornado.httpclient.HTTPRequest(self.get_url('/locks/%s' % resource),
                                             method='POST', body=raw_body)
        if not(callback):
            self.http_client.fetch(req, self.stop)
            response = self.wait()
            self.assertEqual(response.code, 201)
            location = response.headers['Location']
            self.assertTrue(location.startswith('http://'))
            self.assertIn('/%s/' % resource, location)
            return location
        else:
            self.http_client.fetch(req, callback)

    def _delete_lock(self, lock_url):
        req = tornado.httpclient.HTTPRequest(lock_url, method='DELETE')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)

    def test_acquire_lock(self):
        self._acquire_lock("resource1", 5, 60, "test case")

    def test_delete_existing_lock(self):
        location = self._acquire_lock("resource1", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(location, method='DELETE')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)

    def test_delete_non_existing_lock(self):
        location = self._acquire_lock("resource1", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(location, method='DELETE')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)
        location2 = location.replace('/resource1/', '/resource2/')
        req = tornado.httpclient.HTTPRequest(location2, method='DELETE')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)

    def test_get_existing_lock(self):
        location = self._acquire_lock("resource1", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(location, method='GET')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/hal+json')
        tmp = json.loads(response.body.decode('utf-8'))
        self.assertEqual(tmp['title'], "test case")
        self.assertEqual(tmp['wait'], 5)
        self.assertEqual(tmp['lifetime'], 60)

    def test_get_not_existing_lock(self):
        location = self._acquire_lock("resource1", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(location, method='DELETE')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 204)
        req = tornado.httpclient.HTTPRequest(location, method='GET')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)

    def test_expired_lock(self):
        location1 = self._acquire_lock("resource1", 5, 1, "test case")
        location2 = self._acquire_lock("resource1", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(location1, method='GET')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)
        req = tornado.httpclient.HTTPRequest(location2, method='GET')
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)

    def test_wait_timeout_lock(self):
        self._acquire_lock("resource1", 5, 60, "test case")
        tmp = {"wait": 1, "lifetime": 60, "title": "test case"}
        raw_body = json.dumps(tmp)
        req = tornado.httpclient.HTTPRequest(self.get_url('/locks/%s' % "resource1"),
                                             method='POST', body=raw_body)
        self.http_client.fetch(req, self.stop)
        response = self.wait()
        self.assertEqual(response.code, 408)

    def _test_multiple_waiters_callback2(self, r):
        global TEST_MULTIPLE_WAITERS1  # pylint: disable-msg=W0603
        TEST_MULTIPLE_WAITERS1 = TEST_MULTIPLE_WAITERS1 + 1
        self.assertEqual(r.code, 204)
        if TEST_MULTIPLE_WAITERS1 == 4:
            self.stop()

    def _test_multiple_waiters_callback4(self, r):
        global TEST_MULTIPLE_WAITERS2  # pylint: disable-msg=W0603
        TEST_MULTIPLE_WAITERS2 = TEST_MULTIPLE_WAITERS2 + 1
        self.assertEqual(r.code, 204)
        if TEST_MULTIPLE_WAITERS2 == 4:
            self.stop()

    def _test_multiple_waiters_callback1(self, r):
        self.assertEqual(r.code, 201)
        lock_url = r.headers['Location']
        req = tornado.httpclient.HTTPRequest(lock_url, method='DELETE')
        self.http_client.fetch(req, callback=self._test_multiple_waiters_callback2)

    def _test_multiple_waiters_callback3(self, r):
        self.assertEqual(r.code, 201)
        lock_url = r.headers['Location']
        req = tornado.httpclient.HTTPRequest(lock_url, method='DELETE')
        self.http_client.fetch(req, callback=self._test_multiple_waiters_callback4)

    def test_multiple_waiters1(self):
        self._acquire_lock("resource10", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback1)
        self._acquire_lock("resource20", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback1)
        self._acquire_lock("resource30", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback1)
        self._acquire_lock("resource40", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback1)
        self.wait()

    def test_multiple_waiters2(self):
        self._acquire_lock("resource1", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback3)
        self._acquire_lock("resource1", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback3)
        self._acquire_lock("resource1", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback3)
        self._acquire_lock("resource1", 10, 60, "test case",
                           callback=self._test_multiple_waiters_callback3)
        self.wait()

    def _test_delete_all_callback1(self, r):
        self.assertEqual(r.code, 409)
        self.stop()

    def _test_delete_all_callback2(self):
        req = tornado.httpclient.HTTPRequest(self.get_url("/resources"), method='DELETE')
        self.http_client.fetch(req, self._test_delete_all_callback3)

    def _test_delete_all_callback3(self, response):
        self.assertEqual(response.code, 204)
        self.stop()

    def test_delete_all(self):
        location1 = self._acquire_lock("resource1", 5, 60, "test case")
        location3 = self._acquire_lock("resource2", 5, 60, "test case")
        self._acquire_lock("resource1", 5, 60, "test case",
                           callback=self._test_delete_all_callback1)
        tornado.ioloop.IOLoop.instance().add_timeout(time.time() + 2,
                                                     self._test_delete_all_callback2)
        self.wait()
        self.wait()
        for location in [location1, location3]:
            req2 = tornado.httpclient.HTTPRequest(location, method='GET')
            self.http_client.fetch(req2, self.stop)
            response2 = self.wait()
            self.assertEqual(response2.code, 404)

    def test_delete_resource(self):
        location1 = self._acquire_lock("resource1", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(self.get_url("/resources/resource2"), method='DELETE')
        self.http_client.fetch(req, self.stop)
        r = self.wait()
        self.assertEqual(r.code, 404)
        req2 = tornado.httpclient.HTTPRequest(location1, method='GET')
        self.http_client.fetch(req2, self.stop)
        response2 = self.wait()
        self.assertEqual(response2.code, 200)
        req = tornado.httpclient.HTTPRequest(self.get_url("/resources/resource1"), method='DELETE')
        self.http_client.fetch(req, self.stop)
        r = self.wait()
        self.assertEqual(r.code, 204)
        req2 = tornado.httpclient.HTTPRequest(location1, method='GET')
        self.http_client.fetch(req2, self.stop)
        response2 = self.wait()
        self.assertEqual(response2.code, 404)

    def test_get_resource(self):
        self._acquire_lock("resource1", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(self.get_url("/resources/resource2"), method='GET')
        self.http_client.fetch(req, self.stop)
        r = self.wait()
        self.assertEqual(r.code, 200)
        req = tornado.httpclient.HTTPRequest(self.get_url("/resources/resource1"), method='GET')
        self.http_client.fetch(req, self.stop)
        r = self.wait()
        self.assertEqual(r.code, 200)

    def test_get_resources(self):
        self._acquire_lock("resource1", 5, 60, "test case")
        self._acquire_lock("resource2", 5, 60, "test case")
        req = tornado.httpclient.HTTPRequest(self.get_url("/resources"), method='GET')
        self.http_client.fetch(req, self.stop)
        r = self.wait()
        self.assertEqual(r.code, 200)
