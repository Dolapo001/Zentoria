from rest_framework.response import Response


def custom_response(data, message, status_code, status_text=None, tokens=None):
    status_code = int(status_code)

    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
    }

    if status_text is not None:
        response_data["status"] = status_text

    if tokens is not None:
        response_data["tokens"] = tokens

    return Response(response_data, status=status_code)
