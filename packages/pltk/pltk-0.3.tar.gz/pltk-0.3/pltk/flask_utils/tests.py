"""Test helpers."""
import unittest

from pltk.flask_utils.view import json_dumps


class TestCase(unittest.TestCase):
    """Base test class."""

    def __init__(self, *args, **kwargs):
        super(TestCase, self).__init__(*args, **kwargs)

        self.app_initialized = False
        self.app = None
        self.redis = None
        self.context = None

    def init_app(self, app, redis=None):
        """Initialize the app."""
        self.app_initialized = True
        self.app = app
        self.redis = redis
        self.context = app.test_request_context()

    def setUp(self):
        """Setup the test database and create the structure."""

        if not self.app_initialized:
            raise Exception('Flask app must be inited before calling setUp!')
        self.context.push()
        self.headers = [('Accept', ' application/json')]

    def tearDown(self):
        """Drop all the changes made to the test database."""

        try:
            self.context.pop()
        except:
            pass  # stop bugging

        #remove any config stored in redis
        if self.redis:
            self.redis.erase_config()

    def post(self, url, data=None, auth=False, headers=None):
        """Perform a POST method to the eelogic test server."""
        if data is None:
            data = {}

        client = self.app.test_client()
        response = client.post(url, data=json_dumps(data), content_type='application/json',
                               headers=headers or self.headers)
        return response

    def get(self, url, auth=False, headers=None):
        """Perform a GET method to the eelogic test server."""

        client = self.app.test_client()
        response = client.get(url, content_type='application/json',
                              headers=headers or self.headers)
        return response

    def assert_response(self, response, code):
        """Check the response status code."""
        self.assertTrue(response.status_code == code)
