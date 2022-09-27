import json

import responses
from django.conf import settings
import os
import pytest

@pytest.fixture
def response_ok():
    dirname = os.path.dirname(__file__)
    resp_file_name = os.path.join(dirname, 'responses/ok.json')
    with open(resp_file_name) as resp_file:
        response_ok = json.loads(resp_file.read())
        yield response_ok



class TestViews():

    @responses.activate
    def test_get_controller_page(self, client, db, response_ok):
        """/ (GET) returns html page with sensors data."""
        controller_url = settings.SMART_HOME_API_URL
        headers = {'Authorization': 'Bearer {}'.format(settings.SMART_HOME_ACCESS_TOKEN)}
        responses.add(responses.GET, controller_url,
                      json=response_ok, status=200, headers=headers)

        response = client.get('/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/html; charset=utf-8'
        document = response.content.decode('utf-8')

        for sensor in response_ok['data']:
            assert sensor['name'] in document
        assert '</form>' in document

