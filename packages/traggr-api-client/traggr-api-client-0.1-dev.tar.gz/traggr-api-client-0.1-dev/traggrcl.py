__author__ = 'vyakoviv'


# TODO: more =P


import os
import json
import requests


REQUIRED_RESULT_KEYS = ('component', 'suite', 'test_id')


class TRAggrAPIClient(object):

    def __init__(self, host, port, context=None):

        self.scheme = 'http'
        self.host = host
        self.port = port
        self.context = context or '/'

    def _compile_url(self, path):

        url_path = os.path.join(self.context, path.lstrip('/'))
        return '%s://%s:%s%s' % (self.scheme, self.host, self.port, url_path)

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

        import pdb; pdb.set_trace()

        response = requests.post(url, data=json.dumps(results), headers=headers)

        # TODO: Validate response.
        # print response
        return response


if __name__ == '__main__':

    host = 'localhost'
    port = 5001

    project = 'proj'
    sprint = '2014-04'

    client = TRAggrAPIClient(host=host,
                             port=port,
                             context='/')

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
