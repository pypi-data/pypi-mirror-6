import logging
import requests

_LOG = logging.getLogger(__name__)
# requests logs a line every time a new connection is established
logging.getLogger("requests").setLevel(logging.ERROR)

class ApiClient(object):
  """Ease making calls to AgileZen API."""

  def __init__(self, api_key):
    """
    Args:
      api_key: the AgileZen api key
    """
    self._api_key = api_key

  def get(self, resource_path, headers={}):
    """Issue a HTTP GET request with the specified resource path and headers.

    Args:
      resource_path: path to the resource which will receive the request
      headers: additional headers
    Raises:
      requests.HTTPError if we couldn't get the resource
    """
    url = self._get_url(resource_path)
    headers = self._get_headers(headers)
    return self._get(url, headers)

  def _get(self, url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    _LOG.debug("'GET' request issued to '%s' [%s s]", url, response.elapsed.total_seconds())
    return response.json()

  def _get_url(self, resource_path):
    """Return the full URL to an API resource

    Args:
      resource_path: path to the resource from the API root
    """
    return "https://agilezen.com/api/v1/%s" % resource_path

  def _get_headers(self, headers):
    """Return the given headers update with headers required by the API.

    Args:
      headers: headers provided by the user
    """
    headers.update({
      "Accept": "application/json",
      "Content-type": "application/json",
      "X-Zen-ApiKey": self._api_key
    })
    return headers
