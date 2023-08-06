import requests

from kirrupt_tv.errors import APIError

API_URL = 'https://kirrupt.com/tv/api/'


class Client(object):

    """Base API client."""

    def __init__(self, url=None, version=None):
        self.url = url
        self.version = version

    def _make_request(self, request, url, **kwargs):
        "Makes HTTP request to the server."

        response = request('%s%s' % (API_URL, url), **kwargs)
        if response.headers.get('content-type') == 'application/json':
            try:
                return response.json()
            except (TypeError, ValueError):
                return response.text
        else:
            return APIError('Not JSON response!')

    def _request(self, method, url, **kwargs):
        "Handles errors."
        request = getattr(requests, method, None)
        if not callable(request):
            raise APIError('Invalid method %s' % method)

        if method == 'get' and 'data' in kwargs:
            kwargs['params'] = kwargs['data']

        return self._make_request(request, url, **kwargs)

    def watched_episodes_changes_for_user(
            self, since=None, watched_episodes=None):
        data = {}

        if since:
            data['since'] = since

        if watched_episodes:
            data['watched_episodes'] = watched_episodes

        return self._request(
            'post', 'watched-episodes-changes-for-user', data=data)

    def episodes_changes_for_user(self, since=None):
        data = {}

        if since:
            data['since'] = since

        return self._request('post', 'episodes-changes-for-user', data=data)

    def trending(self):
        return self._request('get', 'trending')


class BasicAuthClient(Client):

    """API client that uses a username and password."""

    def __init__(self, username=None, password=None, **kwargs):
        if username is not None and password is not None:
            self.username = username
            self.password = password
        else:
            raise APIError('Please provide a username and password.')

    def _make_request(self, *args, **kwargs):
        kwargs['auth'] = (self.username, self.password)
        return super(BasicAuthClient, self)._make_request(*args, **kwargs)
