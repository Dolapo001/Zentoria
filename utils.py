def custom_response(data, message, status_code, status_text=None):
    response_data = {
        "status_code": status_code,
        "message": message,
        "data": data,
    }

    if status_text is not None:
        response_data["status"] = status_text