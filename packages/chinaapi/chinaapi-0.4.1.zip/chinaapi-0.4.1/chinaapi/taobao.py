# coding=utf-8
from .utils.clients import ApiClientBase, Method
from .utils.exceptions import ApiError, ApiResponseError
from .utils import jsonDict
from datetime import datetime
import hmac


VALUE_TO_STR = {
    type(datetime.now()): lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
    type(u'a'): lambda v: v.encode('utf-8'),
    type(0.1): lambda v: "%.2f" % v,
    type(True): lambda v: str(v).lower(),
}

DEFAULT_VALUE_TO_STR = lambda x: str(x)


class ApiClient(ApiClientBase):
    def prepare_url(self, segments, queries):
        if segments[0] != 'taobao':
            segments.insert(0, 'taobao')
        queries['method'] = '.'.join(segments)
        return 'http://gw.api.taobao.com/router/rest'

    def prepare_method(self, segments):
        """
        淘宝接口全部使用POST提交
        """
        return Method.POST

    def sign(self, values):
        """
        Return encoded data and files
        """
        data, files = {}, {}
        args = {'app_key': self.app.key, 'sign_method': 'hmac', 'format': 'json', 'v': '2.0',
                'timestamp': datetime.now()}

        for k, v in values.items() + args.items():
            kk = k.replace('__', '.')
            if hasattr(v, 'read'):
                files[kk] = v
            elif v is not None:
                data[kk] = VALUE_TO_STR.get(type(v), DEFAULT_VALUE_TO_STR)(v)

        args_str = "".join(["%s%s" % (k, data[k]) for k in sorted(data.keys())])
        sign = hmac.new(self.app.secret)
        sign.update(args_str)
        data['sign'] = sign.hexdigest().upper()
        return data, files

    def prepare_body(self, queries):
        if not self.token.is_expires:
            queries['session'] = self.client.access_token
        return self.sign(queries)

    def pre_parse_response(self, response):
        try:
            return super(ApiClient, self).parse_response(response)
        except ApiResponseError:
            try:
                text = response.text.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
                return jsonDict.loads(text)
            except ValueError, e:
                raise ApiResponseError(response, 15, 'json decode error', 'ism.json-decode-error',
                                       "json-error: %s || %s" % (str(e), response.text))

    def parse_response(self, response):
        r = self.pre_parse_response(response)
        keys = r.keys()
        if keys:
            key = keys[0]
            if 'error_response' in keys:
                error = r.error_response
                raise ApiResponseError(response, error.get('code', ''), error.get('msg', ''), error.get('sub_code', ''),
                                       error.get('sub_msg', ''))
            return r[key]
        return r


