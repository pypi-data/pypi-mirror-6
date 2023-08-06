#!/usr/bin/env python
import sys, os
import struct
from M2Crypto import RSA, Rand, X509
from suds.client import Client, WebFault


def get_client(pod):
    wsdl = ('https://ws%s'
        '.responsys.net/webservices/wsdl/ResponsysWS_Level1.wsdl' % pod)
    end = ('https://ws%s'
        '.responsys.net/webservices/services/ResponsysWSService' % pod)
    # Proxy here at Client(... proxy=)
    proxy = { 'https': '127.0.0.1:8080', 'http': '127.0.0.1:8080' }
    client = Client(
        wsdl,
        location=end,
        proxy= None,
    )
    client.set_options(timeout=5)
    return client


def authenticate(client, username, verbose=False):
    # Not going to authenticate the server. trust in SSL
    authResponse = client.service.authenticateServer(username, ['127']*8)
    token = client.factory.create('AuthSessionHeader')
    token.authSessionId = authResponse.authSessionId
    client.set_options(soapheaders=token)
    if verbose:
        print client.last_received()
    challenge = ''.join(
        [chr(int(x) % 256) for x in authResponse.serverChallenge])
    return challenge


def login_with_cert(client, username, key_path, server_cert_path,
    verbose=False):
    key = RSA.load_key(key_path, lambda x: None)
    server_pk = X509.load_cert(server_cert_path)
    challenge = authenticate(client, username)
    ctxt = key.private_encrypt(challenge, RSA.pkcs1_padding)
    ctxt_challenge = list(struct.unpack('<' + 'b'*len(ctxt), ctxt))
    response = client.service.loginWithCertificate(ctxt_challenge)
    token = client.factory.create('SessionHeader')
    token.sessionId = response.sessionId
    client.set_options(soapheaders=token)
    if verbose:
        print client.last_sent()
        print client.last_received()


def load_config(pod):
    config_path = os.path.join(os.getenv('HOME'), 
        '.interact_creds.py')
    assert os.path.isfile(config_path), 'No credentials found.'
    config_d = {}
    with open(config_path) as config_f:
        exec(config_f, config_d)
    key_path = config_d['credentials'][pod]['keypath']
    server_cert_path = config_d['credentials']['server_cert_path']   
    return key_path, server_cert_path 


def catch_webfault(client, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except WebFault as wf:
        e = getattr(wf.fault.detail, wf.fault.faultstring)
        print client.last_sent()
        print('[%s] %s: %s' % (
            wf.fault.faultstring, str(e.exceptionCode), e.exceptionMessage))
        sys.exit(1)


if __name__ == '__main__':
    pod = sys.argv[1]
    username = sys.argv[2]
    client = get_client(pod)
    key_path, server_cert_path = load_config(pod)
    catch_webfault(client, login_with_cert, client, username, key_path,
        server_cert_path)
    catch_webfault(client, client.service.logout)


