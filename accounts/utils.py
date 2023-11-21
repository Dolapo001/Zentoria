from rest_framework.response import Response


class ErrorCode:
    INVALID_CREDENTIALS = 'invalid_credentials'
    UNVERIFIED_USER = 'unverified_user'
    NON_EXISTENT = 'non_existent'


class RequestError(Exception):
    def __init__(self, err_code, err_msg, status_code):
        self.err_code = err_code
        self.err_msg = err_msg
        self.status_code = status_code


def custom_response(data, message, status_code, status):
    return Response({'data': data, 'message': message, 'status_code': status_code, 'status': status}, status=status_code)


class CustomResponse:
    @staticmethod
    def success(message, data=None, status_code=200):
        return custom_response(data, message, status_code, 'success')

    @staticmethod
    def error(data=None, message="Error", status_code=500):
        return custom_response(data, message, status_code, 'error')
