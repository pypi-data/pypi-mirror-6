# coding=utf-8
from chinaapi.utils.open import ClientBase, Method, OAuth2Base, Token
from chinaapi.utils.exceptions import ApiResponseError


class Client(ClientBase):
    #写入接口
    _post_methods = ['put', 'share', 'remove', 'upload']

    def __init__(self, app):
        super(Client, self).__init__(app)

    def _prepare_url(self, segments, queries):
        return 'https://api.renren.com/v2/{0}'.format('/'.join(segments))

    def _prepare_method(self, segments):
        if segments[-1].lower() in self._post_methods:
            return Method.POST
        return Method.GET

    def _prepare_queries(self, queries):
        if not self.token.is_expires:
            queries['access_token'] = self.token.access_token

    def _prepare_body(self, queries):
        files = self._isolated_files(queries, ['file'])
        return queries, files

    def _parse_response(self, response):
        r = super(Client, self)._parse_response(response)
        if 'error' in r and 'code' in r.error:
            raise ApiResponseError(response, r.error.get('code', ''), r.error.get('message', ''))
        return r


class OAuth2(OAuth2Base):
    def __init__(self, app):
        super(OAuth2, self).__init__(app, 'https://graph.renren.com/oauth/')

    def _get_access_token_url(self):
        return self._url + 'token'

    def _parse_token(self, response):
        data = super(OAuth2, self)._parse_token(response)
        access_token = data.get('access_token', None)
        user = data.get('user', None)
        uid = user.get('id', None) if user is not None else None
        refresh_token = data.get('refresh_token', None)
        expires_in = data.get('expires_in', None)

        token = Token(access_token, refresh_token=refresh_token, uid=uid)
        token.expires_in = expires_in
        return token

    def _parse_response(self, response):
        r = super(OAuth2, self)._parse_response(response)
        if 'error_code' in r:
            raise ApiResponseError(response, r.error_code, r.get('error_description', r.get('error', '')))
        return r


