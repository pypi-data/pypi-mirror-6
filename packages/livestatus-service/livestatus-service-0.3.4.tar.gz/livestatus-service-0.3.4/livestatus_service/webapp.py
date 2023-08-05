'''
The MIT License (MIT)

Copyright (c) 2013 ImmobilienScout24

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''


from __future__ import absolute_import
from flask import Flask, request, render_template
import logging
import traceback

from livestatus_service import __version__ as livestatus_version
from livestatus_service.dispatcher import perform_query, perform_command

'''
    The web application livestatus-service.
    Contains the routing information and defers handling to imported functions.
'''

LOGGER = logging.getLogger('livestatus.webapp')


application = Flask(__name__)


def render_application_template(template_name, **template_parameters):
    template_parameters['version'] = livestatus_version
    return render_template(template_name, **template_parameters)


@application.route('/')
def handle_index():
    return render_application_template('index.html', **locals())


@application.route('/query', methods=['GET'])
def handle_query():
    return validate_and_dispatch(request, perform_query)


@application.route('/cmd', methods=['GET', 'POST'])
def handle_command():
    return validate_and_dispatch(request, perform_command)


def dispatch_request(query, dispatch_function, **kwargs):
    result = dispatch_function(query, **kwargs)
    return '{0}\n'.format(result), 200


def validate_query(query):
    if not query:
        raise ValueError('The "q" parameter (query) is mandatory.')
    query = query.replace('\\n', '\n')
    if 'OutputFormat' in query:
        raise ValueError('The query parameter is not allowed to contain an "OutputFormat" directive.')
    return query


def validate_and_dispatch(request, dispatch_function):
    try:
        query = request.args.get('q') or request.form.get('q')
        query = validate_query(query)
        key = request.args.get('key')
        handler = request.args.get('handler') or request.form.get('handler')
        return dispatch_request(query, dispatch_function, key=key, handler=handler)
    except BaseException as exception:
        LOGGER.error(traceback.format_exc())
        return 'Error : %s' % exception, 200
