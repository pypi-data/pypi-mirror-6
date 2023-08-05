# use termcolor if it's available,
# but don't strictly require it
try:
    from termcolor import colored
except ImportError:
    def colored(message, *args, **kwargs):
        return message

# normal imports
from copy import copy
from datetime import datetime
import json
import SocketServer
import sys
import traceback


class Handler(SocketServer.BaseRequestHandler):
    class BadRequest(Exception):
        def __str__(self):
            return 'Bad Request: %s' % super(BadRequest, self).__str__()
    
    def handle(self):
        """Accept JSON requests, and handle them appropriately."""

        # set up dummy variables for action and request so
        # they're guaranteed to be set in exception cases (e.g. if an
        # exception is raised extremely early in the process)
        action = ''
        request = ''
    
        try:
            # accept data from the client (until the client sends a shutdown)
            data = ''
            chunk = self.request.recv(2048)
            while chunk:
                data += chunk
                chunk = self.request.recv(2048)

            # unserialize the request
            try:
                request = json.loads(data)
            except ValueError:
                raise self.BadRequest, 'Invalid JSON.'
    
            # what is the action I am supposed to take?
            if '_action' not in request:
                raise self.BadRequest, 'No action requested.'
            action = request.pop('_action')
            if not hasattr(self, 'action_%s' % action):
                raise self.BadRequest, 'Unknown action: %s' % action
    
            # convert the request keys to str (from unicode)
            # to get around a Python incompatibility with unicode kwargs
            kwargs = {}
            for key, value in request.iteritems():
                kwargs[str(key)] = value
    
            # take the action
            response = getattr(self, 'action_%s' % action)(**kwargs) or {}
            
            # make sure a status code is present; if none is given,
            # assume ok
            if 'status' not in response:
                response['status'] = 'ok'
    
        except Exception, ex:
            # sanity check: don't stop KeyboardInterrupt
            if type(ex) == KeyboardInterrupt:
                raise
            
            # create a response payload for the error case
            response = {
                'code': getattr(ex, 'code', None),
                'reason': str(ex),
                'status': 'error',
                'traceback': ''.join(traceback.format_exception(*sys.exc_info())),
            }

        # get a JSON version of the response
        response_json = json.dumps(response)

        # understand an abbreviated response for the output to stderr
        response_json_short = response_json
        if 'data' in response and len(response['data']) > 1:
            short_response = copy(response)
            short_response['data'] = [response['data'][0], '%d more...' % (len(response['data']) - 1)]
            response_json_short = json.dumps(short_response)

        # output the header to stderr
        header = '[%s %s] %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.client_address[0], action.replace('_', ' ').upper())
        self._output(header, status=response['status'], color='white')

        # output the request body to stderr (if it exists)
        request_json = None
        if len(request):
            request_json = json.dumps(request)

            # understand an abbreviated request (for cleaner output)
            request_json_short = request_json
            if 'updates' in request and len(request['updates']) > 1:
                short_request = copy(request)
                short_request['updates'] = [request['updates'][0], '%d more...' % (len(request['updates']) - 1)]
                request_json_short = json.dumps(short_request)
    
            # print the abbreviated request to stderr
            self._output('>>> %s' % request_json_short, status=response['status'], color='white')

        # output the response to stderr
        output_color = 'red'
        if response['status'] == 'empty':
            output_color = 'blue'
        if response['status'] == 'warning':
            output_color = 'yellow'
        if response['status'] == 'ok':
            output_color = 'green'
        self._output('<<< %s\n' % response_json_short, status=response['status'], color=output_color)

        # return the final response
        self.request.sendall(response_json)
        self.request.close()

    def action_ping(self):
        """Return back a success message with no data. A test method."""
        return {
            'version': self.version,
        }

    def _output(self, message, status='ok', color='white'):
        # send the message to the appropriate log
        if status in ('ok', 'empty'):
            self.request_log.info(message)
        elif status == 'warning':
            self.error_log.warning(message)
        else:
            self.error_log.error(message)

        # if output to screen is set, then do that too
        if self.output_to_screen:
            sys.stderr.write(colored('%s\n' % message, color, attrs=['bold']))