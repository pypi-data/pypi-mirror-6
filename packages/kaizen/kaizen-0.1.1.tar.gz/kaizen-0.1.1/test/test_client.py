import json
import requests
import responses
import unittest

from kaizen.client import ApiClient


class ApiClientTest(unittest.TestCase):

  def setUp(self):
    self._client = ApiClient("fake_api_key")

  @responses.activate
  def test_get_success(self):
    items = {"items": [1, 2]}
    responses.add(responses.GET, "https://agilezen.com/api/v1/fake_url",
                  body=json.dumps(items), status=200, content_type="application/json")
    self.assertEquals(self._client.get("fake_url"), items)

  @responses.activate
  def test_get_raises(self):
    responses.add(responses.GET, "https://agilezen.com/api/v1/fake_url",
                  status=404, content_type='application/json')
    self.assertRaises(requests.HTTPError, self._client.get, "fake_url")

if __name__ == "__main__":
  unittest.main()
