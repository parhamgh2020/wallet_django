"""
- RESPONSE_WEIGHT: A list of tuples, where each tuple contains a mock response
  and a weight indicating the probability that the response is returned. This
  constant

- request_third_party_deposit: Sends a POST request to a third-party service
  to make a deposit, and returns the response. In production, the request is
  sent to a real service using the requests library. In testing mode, a mock
  response is returned based on a predefined list of possible responses.
"""

from random import choices

import requests
from django.conf import settings

RESPONSE_WEIGHT = [
    ({'data': 'success', 'status': 200}, 0.9),
    ({'data': 'failed', 'status': 503}, 0.033),
    ({'data': 'failed', 'status': 400}, 0.033),
    ({}, 0.033),
]


def request_third_party_deposit():
    if settings.TEST_DEBUG_MODE:
        responses, weights = list(zip(*RESPONSE_WEIGHT))
        response = choices(responses, weights=weights).pop()
        return response
    try:
        return requests.post("http://localhost:8010/").json()
    except Exception as err:
        return {'data': str(err), 'status': 500}
