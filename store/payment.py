import uuid
import requests
from rest_framework.response import Response
from secret_keys import FLUTTERWAVE_SECRET_KEY


def initiate_payment(amount, email, redirect_url):
    base_url = "https://api.flutterwave.com/v3/payments"
    headers = {
        'Authorization': f'Bearer {FLUTTERWAVE_SECRET_KEY}',
    }

    data = {
        'tx_ref': str(uuid.uuid4()),
        'amount': str(amount),
        'currency': 'NGN',
        'redirect_url': redirect_url,
        'meta': {'consumer_id': 23, 'consumer_mac': '92a3-912ba-1192a'},
        'customer': {
            'email': email,
            'phonenumber': '081029093894',
            'name': 'Ladoke Akintola',
        },
        "customizations": {
            "title": "Pied Piper Payments",
            "logo": "https://www.piedpiper.com/app/themes/joystick-v27/images/logo.png"
        }
    }
    try:
        response = requests.post(base_url, headers=headers, json=data)

        if response.status_code == 200:
            response_data = response.json()
            return Response(response_data)
        else:
            print(f"The payment didn't go through. Status code: {response.status_code}")
            return Response({"error": f"The payment didn't go through. Status code: {response.status_code}"}, status=500)
    except requests.exceptions.RequestException as err:
        print(f"The payment didn't go through. Error: {err}")
        return Response({"error": str(err)}, status=500)
