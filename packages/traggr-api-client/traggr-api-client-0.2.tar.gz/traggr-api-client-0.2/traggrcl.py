__author__ = 'vyakoviv'


# TODO: more =P


import os
import json
import requests


REQUIRED_RESULT_KEYS = ('component', 'suite', 'test_id')


class TRAggrAPIClient(object):

    def __init__(self, url):

        self.base_url = url

    def _compile_url(self, path):

        return '%s/%s' % (self.base_url.rstrip('/'), path.lstrip('/'))

    def ping(self):

        path = '/ping'
        url = self._compile_url(path)
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception('API does not respond.')

    def post_results(self, project,
                           sprint,
                           results):

        headers = {'Content-Type': 'text/json'}

        # Validate results.
        for result in results:
            for required_key in REQUIRED_RESULT_KEYS:
                if required_key not in result:
                    raise Exception('Result record %s does not contain a required key "%s"' % (record, required_key))
        # TODO: More validation.

        path = '/results/%s/%s' % (project, sprint)
        url = self._compile_url(path)

        response = requests.post(url, data=json.dumps(results), headers=headers)

        if response.status_code != 200:
            raise Exception('Failed to post results. Code: %s. Text: %s' %
                            (response.status_code, response.text))


if __name__ == '__main__':

    url = 'http://localhost:5001'

    project = 'proj'
    sprint = '2014-04'

    client = TRAggrAPIClient(url=url)
    client.ping()

    results = [{'component': 'API',
                'suite': 'Functions',
                'test_id': 'A-1',
                'other_attributes': {'title': 'Test for login',
                                     'description': 'Some more description',
                                     'types': ['Functional']},
                'result_attributes': {'result': 'passed',
                                      'error': 'Exception'}}]

    client.post_results(project=project,
                        sprint=sprint,
                        results=results)


# EOF
