#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
# FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.
#

import sys
import time
import base64
import random
import json

from ast import literal_eval
from blazemeter.common import (call_url, encode_multipart)

# Initialize variables
base_url = server.get('url').strip('/')
contents = ''

# Make sure all the required paramaters are set
if not base_url.strip():
    print 'Input error!\n'
    print 'Reason: Server configuration url undefined\n'
    sys.exit(101)

if not keyId.strip():
    print 'Input error!\n'
    print 'Reason: Parameter keyId undefined\n'
    sys.exit(102)

if not secret.strip():
    print 'Input error!\n'
    print 'Reason: Parameter secret undefined\n'
    sys.exit(103)

if not test.strip():
    print 'Input error!\n'
    print 'Reason: Parameter test undefined\n'
    sys.exit(104)

if not filename.strip():
    print 'Input error!\n'
    print 'Reason: Parameter filename undefined\n'
    sys.exit(105)

if not testData:
    print 'Input error!\n'
    print 'Reason: Parameter testData undefined\n'
    sys.exit(106)

print 'BlazeMeter test data upload started\n'

# Write the data to a string
for r in testData:
    row = literal_eval(r)
    contents += ','.join(map(str, row)) + '\n'

# Encode multipart form data
files = {'file': {'filename': filename, 'content': contents}}
url_data, url_headers = encode_multipart({}, files)

# Add authentication headers
base64string = base64.encodestring('%s:%s' % (keyId, secret)).replace('\n', '')
url_headers['Authorization'] = 'Basic %s' % base64string

# Upload the test data
upload_url = '%s/tests/%s/files' % (base_url, test)
data = call_url('post', upload_url, url_data, url_headers)

if 'updated' in data.get('result') and data.get('result').get('updated') == True:
    print 'BlazeMeter file upload for test %s completed **successfully**\n' % test
    print '```'
    print json.dumps(data)
    print '```'
    sys.exit(0)    
        
print 'BlazeMeter upload for test %s **failed**\n' % test
print '```'
print json.dumps(data)
print '```'
sys.exit(1)