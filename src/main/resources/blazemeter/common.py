#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#
import mimetypes
import random
import string
import sys
import json
from xlrelease.HttpRequest import HttpRequest
import org.slf4j.LoggerFactory as LoggerFactory

logger = LoggerFactory.getLogger("Blazemeter")

_BOUNDARY_CHARS = string.digits + string.ascii_letters

# Encode multipart form data to upload files via POST
def encode_multipart(fields, files, boundary=None):
    r"""Encode dict of form fields and dict of files as multipart/form-data.
    Return tuple of (body_string, headers_dict). Each value in files is a dict
    with required keys 'filename' and 'content', and optional 'mimetype' (if
    not specified, tries to guess mime type or uses 'application/octet-stream').

    >>> body, headers = encode_multipart({'FIELD': 'VALUE'},
    ...                                  {'FILE': {'filename': 'F.TXT', 'content': 'CONTENT'}},
    ...                                  boundary='BOUNDARY')
    >>> print('\n'.join(repr(l) for l in body.split('\r\n')))
    '--BOUNDARY'
    'Content-Disposition: form-data; name="FIELD"'
    ''
    'VALUE'
    '--BOUNDARY'
    'Content-Disposition: form-data; name="FILE"; filename="F.TXT"'
    'Content-Type: text/plain'
    ''
    'CONTENT'
    '--BOUNDARY--'
    ''
    >>> print(sorted(headers.items()))
    [('Content-Length', '193'), ('Content-Type', 'multipart/form-data; boundary=BOUNDARY')]
    >>> len(body)
    193
    """
    def escape_quote(s):
        return s.replace('"', '\\"')

    if boundary is None:
        boundary = ''.join(random.choice(_BOUNDARY_CHARS) for i in range(30))
    lines = []

    for name, value in fields.items():
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"'.format(escape_quote(name)),
            '',
            str(value),
        ))

    for name, value in files.items():
        filename = value['filename']
        if 'mimetype' in value:
            mimetype = value['mimetype']
        else:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(
                    escape_quote(name), escape_quote(filename)),
            'Content-Type: {0}'.format(mimetype),
            '',
            value['content'],
        ))

    lines.extend((
        '--{0}--'.format(boundary),
        '',
    ))
    body = '\r\n'.join(lines)

    headers = {
        'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary),
        'Content-Length': str(len(body)),
    }

    return (body, headers)

# Call URL with proper error handling
def call_url(verb, data, baseUrl, testUrl, keyId, keySecret, serverProxyHost, serverProxyPort, serverProxyUsername, serverProxyPassword ):
    r"""A convenience definition to call a URL with the necessary headers
    and payload. No need to worry about how to POST multipart/form-data
    or how to handle certain error exceptions. The return value is either 
    the respopnse body or error reason code.
    """

    params = {
        'url': baseUrl,
        'username': keyId,
        'password': keySecret,
        'proxyHost': serverProxyHost,
        'proxyPort': serverProxyPort,
        'proxyUsername': serverProxyUsername,
        'proxyPassword': serverProxyPassword
    }

    try:
        if verb == 'post':
            response = HttpRequest(params).post(testUrl, json.dumps(data), contentType='application/json')
        elif verb == 'put':
            response = HttpRequest(params).put(testUrl, json.dumps(data), contentType='application/json')
        elif verb == 'patch':
            response = HttpRequest(params).patch(testUrl, json.dumps(data), contentType='application/json')
        elif verb == 'delete':
            response = HttpRequest(params).delete(testUrl, json.dumps(data), contentType='application/json')
        elif verb == 'get':
            response = HttpRequest(params).get(testUrl, contentType='application/json')
        else:
            logger.error("FATAL: HTTP verb error! Only POST, PUT, PATCH, DELETE and GET verbs supported.")
            sys.exit(201)

        output = json.loads(response.getResponse())

    # Catch all exceptions
    except Exception as error:
        logger.error("FATAL: Error! %s" % error)
        raise Exception(
            "Failed to connect to Blazemeter Server."
        )
        sys.exit(205)

    return output