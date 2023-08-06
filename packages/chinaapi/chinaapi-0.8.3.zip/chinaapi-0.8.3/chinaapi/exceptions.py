# coding=utf-8
class ApiError(IOError):
    """API异常。"""

    def __init__(self, url, code, message, sub_code='', sub_message=''):
        self.url = url
        self.code = code
        self.message = message
        self.sub_code = sub_code
        self.sub_message = sub_message
        super(ApiError, self).__init__(code, message)

    def __str__(self):
        if self.sub_code or self.sub_message:
            return u'[{0}]: {1}, [{2}]: {3}, request: {4}'.format(str(self.code), self.message, str(self.sub_code),
                                                                  self.sub_message, self.url)
        return u'[{0}]: {1}, request: {2}'.format(str(self.code), self.message, self.url)


class ApiResponseError(ApiError):
    """响应结果中包含的异常。"""

    def __init__(self, response, code, message, sub_code='', sub_message=''):
        self.response = response
        super(ApiResponseError, self).__init__(self.get_url(), code, message, sub_code, sub_message)

    def get_url(self):
        request = self.response.request
        if 'multipart/form-data' not in request.headers.get('Content-Type', '') and request.body:
            return u'{0}?{1}'.format(self.response.url, self.response.request.body)
        return self.response.url


class ApiResponseValueError(ApiResponseError, ValueError):
    """解析响应结果时抛出的异常。"""

    def __init__(self, response, value_error):
        super(ApiResponseValueError, self).__init__(response, response.status_code,
                                                    response.text if response.text else str(value_error))


class InvalidApi(ApiError, ValueError):
    """无效的API。"""

    def __init__(self, url, code=0, message='Invalid Api!'):
        super(InvalidApi, self).__init__(url, code, message)


class NotExistApi(ApiResponseError, ValueError):
    """该API不存在。"""

    def __init__(self, response, code=0, message='Request Api not found!'):
        if response.text:
            message = response.text
        if not code:
            code = response.status_code
        super(NotExistApi, self).__init__(response, code, message)


class MutexApiParameters(ApiError, ValueError):
    """同时存在两个或两个以上互相排斥的参数"""

    def __init__(self, key_list):
        super(MutexApiParameters, self).__init__('', '', u'{0}参数只能选择其一'.format(','.join(key_list)))


class OAuth2Error(ApiError):
    """OAuth2异常。"""

    def __init__(self, url, code, message):
        super(OAuth2Error, self).__init__(url, code, message)


class MissingRedirectUri(OAuth2Error, ValueError):
    """缺少 redirect_uri。"""

    def __init__(self, url):
        super(MissingRedirectUri, self).__init__(url, 'OAuth2 request', 'Parameter absent: redirect_uri')