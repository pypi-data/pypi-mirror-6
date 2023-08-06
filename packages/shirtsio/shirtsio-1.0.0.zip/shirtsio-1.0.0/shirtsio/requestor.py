import ast
import json
import platform
import textwrap
import requests
from shirtsio.exception import APIConnectionError, APIError, InvalidRequestError, AuthenticationError
from version import VERSION

api_base = 'https://www.shirts.io/api/v1/'
api_version = None


class APIRequestor(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_headers(self):
        ua = {
            'bindings_version': VERSION,
            'lang': 'python',
            'publisher': 'shirts.io',
            'httplib': 'requests',
        }

        for attr, func in [['lang_version', platform.python_version],
                           ['platform', platform.platform],
                           ['uname', lambda: ' '.join(platform.uname())]]:
            try:
                val = func()
            except Exception, e:
                val = "!! %s" % e
            ua[attr] = val

        headers = {
            'X-Shirtsio-Client-User-Agent': json.dumps(ua),
            'User-Agent': 'Shirtsio/v1 PythonBindings/%s' % VERSION,
            'Authorization': 'Bearer %s' % self.api_key
        }

        return headers

    @classmethod
    def api_url(cls, url=''):
        return '%s%s' % (api_base, url)

    def request(self, url, params, method='get', files=None):
        headers = self.get_headers()
        response = None
        try:
            try:
                if method == 'get':
                    response = requests.get(url, headers=headers, params=params)
                elif method == 'post':
                    response = requests.post(url, headers=headers, data=params, files=files)
            except TypeError, e:
                raise TypeError(
                    'Warning: It looks like your installed version of the "requests" library is not compatible '
                    'with Shirtsio\'s usage thereof. (HINT: The most likely cause is '
                    'that your "requests" library is out of date. '
                    'You can fix that by running "pip install -U requests".) The underlying error was: %s' % (
                        e, ))

            content = response.content
            status_code = response.status_code

            return self.interpret_response(content, status_code)

        except ValueError:
            print "request error:", response.text
            # raise Exception(err)
        except Exception as e:
            self.handle_requests_error(e)

    def interpret_response(self, rbody, rcode):
        try:
            resp = json.loads(rbody.decode('utf-8'))
            if type(resp) == unicode:
                resp = ast.literal_eval(resp)

        except Exception:
            raise APIError("Invalid response body from API: %s (HTTP response code was %d)" % (rbody, rcode), rbody,
                           rcode)
        if not (200 <= rcode < 300):
            self.handle_api_error(rbody, rcode, resp)
        return resp["result"]

    def handle_api_error(self, rbody, rcode, resp):
        try:
            error = resp['error']
        except (KeyError, TypeError):
            raise APIError("Invalid response object from API: %r (HTTP response code was %d)" % (rbody, rcode), rbody,
                           rcode, resp)

        if rcode in [400, 404]:
            raise InvalidRequestError(error, rbody, rcode, resp)
        elif rcode == 401:
            raise AuthenticationError(error, rbody, rcode, resp)
        else:
            raise APIError(error, rbody, rcode, resp)

    def handle_requests_error(self, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = "Unexpected error communicating with Shirtsio.  " \
                  "If this problem persists, let us know at support@shirts.io."
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = "Unexpected error communicating with Shirtsio.  " \
                  "It looks like there's probably a configuration issue locally.  " \
                  "If this problem persists, let us know at support@shirts.io."
            err = "A %s was raised" % (type(e).__name__, )
            if str(e):
                err += " with error message %s" % (str(e), )
            else:
                err += " with no error message"
        msg = textwrap.fill(msg) + "\n\n(Network error: " + err + ")"
        raise APIConnectionError(msg)