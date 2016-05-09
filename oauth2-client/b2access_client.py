from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth, prepare_request
from flask_oauthlib.utils import to_bytes

from base64 import b64encode
import os
import uuid

import ssl
from OpenSSL import crypto

try:
    import urllib2 as http
except ImportError:
    from urllib import request as http

import sys

if len(sys.argv) < 3:
    sys.stderr.write('Usage: python b2access_client.py <key> <secret>\n')
    sys.exit(1)
consumer_key=sys.argv[1]
consumer_secret=sys.argv[2]


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

b2access = oauth.remote_app(
    'b2access',
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    base_url='https://unity.eudat-aai.fz-juelich.de:8443/oauth2/',
    request_token_params={'scope': 'USER_PROFILE GENERATE_USER_CERTIFICATE'},
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://unity.eudat-aai.fz-juelich.de:8443/oauth2/token',
    authorize_url='https://unity.eudat-aai.fz-juelich.de:8443/oauth2-as/oauth2-authz'
)

b2accessCA = oauth.remote_app(
    'b2accessCA',
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    base_url='https://unity.eudat-aai.fz-juelich.de:8445/',
    request_token_params={'scope': 'USER_PROFILE GENERATE_USER_CERTIFICATE'},
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://unity.eudat-aai.fz-juelich.de:8443/oauth2/token',
    authorize_url='https://unity.eudat-aai.fz-juelich.de:8443/oauth2-as/oauth2-authz'
)


def generate_csr_and_key():
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 1024)
    req = crypto.X509Req()
    req.get_subject().CN = 'TestUser'
    req.set_pubkey(key)
    req.sign(key, "sha1")
    return key, req


def write_key_and_cert(key, cert):
    tempfile = "/tmp/%s" % uuid.uuid4()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    with os.fdopen(os.open(tempfile, flags, 0o600), 'w') as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        f.write(cert)
    return tempfile


def encode_csr(req):
    enc = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    data = {'certificate_request': enc}
    return data


@app.route('/')
def index():
    if 'b2access_token' in session:
        return 'Logged in. <a href="%s">Log out</a>' % url_for('logout')
    else:
        return 'Not logged in. <a href="%s">Log in</a>' % url_for('login')

@app.route('/userinfo')
def userinfo():
    if 'b2access_token' in session:
        print(session['b2access_token'])
        print(b2access.get('tokeninfo').data)
        me = b2access.get('userinfo')
        return jsonify(me.data)
    return redirect(url_for('login'))


def http_request_no_verify_host(uri, headers=None, data=None, method=None):
    uri, headers, data, method = prepare_request(uri, headers, data, method)
    req = http.Request(uri, headers=headers, data=data)
    req.get_method = lambda: method.upper()
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        resp = http.urlopen(req, context=ctx)
        content = resp.read()
        resp.close()
        return resp, content
    except http.HTTPError as resp:
        content = resp.read()
        resp.close()
        return resp, content


@app.route('/cert')
def get_certificate():
    if 'b2access_token' in session:
        key, req = generate_csr_and_key()
        b2accessCA.http_request = http_request_no_verify_host
        response = b2accessCA.post('ca/o/delegateduser',
                                   data=encode_csr(req),
                                   headers={'Accept-Encoding': 'identity'})
        if response.status != 200:
            print('HTTP response status: %s' % response.status)
            return '{"response": %s}' % response.status
            
        # write proxy certificate to a random file name
        proxyfile = write_key_and_cert(key, response.data)
        print('Wrote certificate to %s' % proxyfile)
        return '{"response" : "OK"}'
    
    session['origin'] = 'get_certificate'
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return b2access.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('b2access_token', None)
    return redirect(url_for('index'))


def decorate_http_request(remote):
    """ Decorate the OAuth call to access token endpoint to inject the Authorization header"""
    old_http_request = remote.http_request
    def new_http_request(uri, headers=None, data=None, method=None):
        if not headers:
            headers = {}
        if not headers.get("Authorization"):
            client_id = remote.consumer_key
            client_secret = remote.consumer_secret
            userpass = b64encode("%s:%s" % (client_id, client_secret)).decode("ascii")
            headers.update({ 'Authorization' : 'Basic %s' %  (userpass,) })
        return old_http_request(uri, headers=headers, data=data, method=method)
    remote.http_request = new_http_request


@app.route('/authorized')
def authorized():
    decorate_http_request(b2access)
    resp = b2access.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    access_token = resp['access_token']
    session['b2access_token'] = (access_token, '')
    if 'origin' in session:
        origin = session['origin']
        session.pop('origin', None)
        # redirect to where the request came from
        return redirect(url_for(origin))
    me = b2access.get('userinfo')
    # print(b2access.get('tokeninfo'))
    # print(me.data)
    return jsonify(me.data)


@b2access.tokengetter
@b2accessCA.tokengetter
def get_b2access_oauth_token():
    return session.get('b2access_token')


if __name__ == '__main__':
    app.run()