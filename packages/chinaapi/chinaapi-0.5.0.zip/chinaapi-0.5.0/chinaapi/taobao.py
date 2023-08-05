# coding=utf-8
import base64
import hmac
from hashlib import md5
from datetime import datetime
from urllib import unquote
from furl import furl
from .utils.api import Client, Parser, OAuth
from .utils.exceptions import ApiResponseError, ApiError


VALUE_TO_STR = {
    type(datetime.now()): lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
    type(u'a'): lambda v: v.encode('utf-8'),
    type(0.1): lambda v: "%.2f" % v,
    type(True): lambda v: str(v).lower(),
}

DEFAULT_VALUE_TO_STR = lambda x: str(x)

RETRY_SUB_CODES = {'isp.top-remote-unknown-error', 'isp.top-remote-connection-timeout',
                   'isp.remote-connection-error', 'mz.emptybody',
                   'isp.top-remote-service-unavailable', 'isp.top-remote-connection-timeout-tmall',
                   'isp.item-update-service-error:GENERIC_FAILURE',
                   'isp.item-update-service-error:IC_SYSTEM_NOT_READY_TRY_AGAIN_LATER',
                   'ism.json-decode-error', 'ism.demo-error'}


def to_message(data):
    return ''.join(["%s%s" % (k, v) for k, v in sorted(data.iteritems())])


def sign(data, app_secret):
    message = to_message(data)
    h = hmac.new(app_secret)
    h.update(message)
    return h.hexdigest().upper()


class ApiParser(Parser):
    # def pre_parse_response(self, response):
    #     try:
    #         return super(ApiParser, self).parse(response)
    #     except ApiResponseError:
    #         try:
    #             text = response.text.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
    #             return jsonDict.loads(text)
    #         except ValueError, e:
    #             raise ApiResponseError(response, 15, 'json decode error', 'ism.json-decode-error',
    #                                    "json-error: %s || %s" % (str(e), response.text))

    def parse_response(self, response):
        r = super(ApiParser, self).parse_response(response)
        keys = r.keys()
        if keys:
            key = keys[0]
            if 'error_response' in keys:
                error = r.error_response
                raise ApiResponseError(response, error.get('code', ''), error.get('msg', ''),
                                       error.get('sub_code', ''), error.get('sub_msg', ''))
            return r[key]


class ApiClient(Client, ApiParser):
    def __init__(self, app, retry_count=3):
        super(ApiClient, self).__init__(app)
        self._retry_count = retry_count

    @property
    def session(self):
        return self.token.access_token

    def _prepare_url(self, segments, queries):
        if segments[0] != 'taobao':
            segments.insert(0, 'taobao')
        queries['method'] = '.'.join(segments)
        return 'http://gw.api.taobao.com/router/rest'

    def _prepare_queries(self, queries):
        if not self.token.is_expires:
            queries['session'] = self.session
        queries.update({'app_key': self.app.key, 'sign_method': 'hmac', 'format': 'json', 'v': '2.0',
                        'timestamp': datetime.now()})

    def _prepare_body(self, queries):
        """
        Return encoded data and files
        """
        data, files = {}, {}
        for k, v in queries.items():
            kk = k.replace('__', '.')
            if hasattr(v, 'read'):
                files[kk] = v
            elif v is not None:
                data[kk] = VALUE_TO_STR.get(type(v), DEFAULT_VALUE_TO_STR)(v)
        data['sign'] = sign(data, self.app.secret)
        return data, files

    def request(self, segments, **queries):
        url = self._prepare_url(segments, queries)
        self._prepare_queries(queries)
        data, files = self._prepare_body(queries)
        for count in xrange(self._retry_count, 0, -1):
            try:
                response = self._session.post(url, data=data, files=files)
                return self.parse_response(response)
            except ApiError, e:
                if e.sub_message in RETRY_SUB_CODES and count > 1:
                    for f in files.values():
                        f.seek(0)
                    continue
                raise e


class ApiOAuth(OAuth, ApiParser):
    def __init__(self, app):
        super(ApiOAuth, self).__init__(app, 'http://container.open.taobao.com/container')

    def authorize(self):
        args = dict(appkey=self.app.key, encode='utf-8')
        return furl(self.url).set(args=args).url

    def refresh_token(self, refresh_token, top_session):
        # TODO:返回 system error ! 需要更新sign的算法
        params = dict(appkey=self.app.key, refresh_token=refresh_token, sessionkey=top_session)
        message = ''.join(["%s%s" % (k, v) for k, v in sorted(params.iteritems())]) + self.app.secret
        params['sign'] = md5(message).hexdigest().upper()
        response = self._session.get(self.url + '/refresh', params=params)
        return self.parse_response(response)

    def validate_sign(self, top_parameters, top_sign, top_session):
        """  验证签名是否正确（用于淘宝帐号授权）（已测试成功，不要更改）
        """
        top_sign = unquote(top_sign)
        top_parameters = unquote(top_parameters)
        sign = base64.b64encode(md5(self.app.key + top_parameters + top_session + self.app.secret).digest())
        return top_sign == sign

    def decode_parameters(self, top_parameters):
        """  将top_parameters字符串解码并转换为字典，（已测试成功，不要更改）
        """
        parameters = base64.decodestring(unquote(top_parameters))
        return self.parse_query_string(parameters)
