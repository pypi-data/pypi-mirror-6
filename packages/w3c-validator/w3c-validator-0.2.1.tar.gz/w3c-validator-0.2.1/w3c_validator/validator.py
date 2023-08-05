import requests


class Validator(object):
    VALIDATOR_URL = 'http://validator.w3.org/check'
    DEFAULT_OUTPUT = 'json'

    def _validate_get(self, params, headers=None):
        uri = self.VALIDATOR_URL
        if 'output' not in params:
            params['output'] = self.DEFAULT_OUTPUT

        resp = requests.get(uri, params=params, headers=headers)
        self._process_response(resp)

    def _validate_post(self, params, headers=None, files=None):
        uri = self.VALIDATOR_URL
        if 'output' not in params:
            params['output'] = self.DEFAULT_OUTPUT

        try:
            resp = requests.post(uri, data=params, files=files, headers=headers, timeout=1)
        except requests.exceptions.Timeout:
            resp = None
        self._process_response(resp)

    def _process_response(self, resp):
        self.errors = []
        self.warnings = []
        if resp is None:
            self.type = 'html'
            self.content = '<p>Request to {} took longer than 1 second.<p>'.format(self.VALIDATOR_URL)
            self.error_count = 0
            self.warning_count = 0
            self.status = 'Timeout'
            return

        if 'json' in resp.headers['content-type']:
            self.type = 'json'
            self.content = resp.json()

            for message in self.content.get('messages', []):
                if 'lastLine' in message:
                    i = message['lastLine']
                    if hasattr(self, 'source') and len(self.source) > i-1:
                        message['src'] = self.source[i-1]
                if message['type'] == u'error':
                    self.errors.append(message)
                else:
                    self.warnings.append(message)
        else:
            self.type = 'html'
            self.content = resp.content

        self.error_count = int(resp.headers.get('x-w3c-validator-errors', '0'))
        self.warning_count = int(resp.headers.get('x-w3c-validator-warnings', '0'))
        self.status = resp.headers.get('x-w3c-validator-status', 'Invalid')

    def validate(self, uri):
        params = dict(uri=uri)
        return self._validate_get(params)

    def validate_file(self, file):
        return self._validate_post(dict(), files=dict(uploaded_file=(file)))

    def validate_source(self, source):
        self.source = source.split("\n")
        self._validate_post(dict(), files=dict(uploaded_file=('source.html', source, 'text/html')))

