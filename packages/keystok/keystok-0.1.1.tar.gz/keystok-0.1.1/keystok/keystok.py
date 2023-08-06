import sys
import os
import argparse
import base64
import json
import time
# These imports require the pycrypto, pbkdf2, requests modules to be installed
import requests
from Crypto.Cipher import AES
from pbkdf2 import PBKDF2

# Shortcut for creating a KeystokClient with the specified options.
# The options parameter can be an access token or a dictionary with these keys:
# 'access_token': The access token to use (required)
# 'api_host': API server to use
# 'auth_host': Authentication server to use
# 'cache_dir': Cache directory to use
# 'verbose': Verbose mode if set to True

def connect(options):
    return KeystokClient(options)

class KeystokClient:
    def __init__(self, options=None):
        self.options = options or {}
        if isinstance(self.options, str):
            self.options = {
                'access_token': self.options
            }
        self.token = self.decode_access_token(self.options['access_token'])
        if not self.options.get('api_host', None):
            self.options['api_host'] = 'https://api.keystok.com'
        if not self.options['api_host'].startswith('http'):
            self.options['api_host'] = 'https://' + self.options['api_host']
        if not self.options.get('auth_host', None):
            self.options['auth_host'] = 'https://keystok.com/oauth/token'
        if not self.options['auth_host'].startswith('http'):
            self.options['auth_host'] = 'https://' + self.options['auth_host']
        if not self.options.get('cache_dir', None):
            self.options['cache_dir'] = os.path.join(os.path.expanduser('~'), '.keystok')
        if not self.options.get('verbose', None):
            self.options['verbose'] = False
        # Ensure cache directory exists
        try:
            os.mkdir(self.options['cache_dir'], 0o700)
        except OSError:
            pass

    def get_key(self, key_id):
        url = '%s/apps/%s/deploy/%s?access_token=%s' % (self.options['api_host'], self.token['id'], key_id, self.refresh_access_token(self.token))
        response = requests.get(url).json()
        return response

    def list_keys(self):
        url = '%s/apps/%s/keys?access_token=%s' % (self.options['api_host'], self.token['id'], self.refresh_access_token(self.token))
        response = requests.get(url).json()
        return response

    def cmd_ls(self):
        response = self.list_keys()
        if self.options['verbose']:
            # Show headers and descriptions
            print('KEY ID                         DESCRIPTION')
            print('------------------------------ -----------------------------------------------')
            for key in response:
                print('%-30s %s' % (key['id'], key.get('description', '')))
        else:
            # Show key ids only
            for key in response:
                print(key['id'])

    def cmd_get(self, key_id):
        response = self.get_key(key_id)
        print(self.decrypt_data(self.token, response[key_id]['key']))

    def decode_access_token(self, token):
        return json.loads(base64.b64decode(token.replace('-', '+').replace('_', '/')).decode('utf-8'))

    def refresh_access_token(self, token):
        # First see what we already have in the token
        access_token = token.get('at')
        refresh_token = token.get('rt')
        if access_token:
            # Already have an access token
            return access_token

        # Do we have an access token cached?
        try:
            cached_token = json.load(open('%s/access_token' % (self.options['cache_dir'])))
            if cached_token['expires_at'] > int(time.time()):
                return cached_token['access_token']
        except IOError:
            # Could not read it
            pass

        # Must refresh to get new access token
        data = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        })
        response = requests.post(REFRESH_TOKEN_URL, data).json()
        response['expires_at'] = int(time.time()) + response['expires_in']
        with open('%s/access_token' % (self.options['cache_dir']), 'w') as f:
            json.dump(response, f)
        return response['access_token']

    def make_decryption_key(self, password, keysize, salt, iterations):
        return PBKDF2(password, salt, iterations).read(keysize//8)

    def decrypt_data(self, token, data):
        if not data.startswith(':aes256:'):
            raise Exception('Unsupported encryption scheme')
        data = json.loads(base64.b64decode(data[8:]).decode('utf-8'))
        # First we need to make the actual encryption key
        decryption_key = self.make_decryption_key(token['dk'], data['ks'], base64.b64decode(data['salt']), data['iter'])
        iv = base64.b64decode(data['iv'])
        cipher_text = base64.b64decode(data['ct'])
        aes = AES.new(decryption_key, AES.MODE_CBC, iv)
        clear_text = aes.decrypt(cipher_text)
        if clear_text:
            padding = clear_text[-1]
            if isinstance(padding, str):
                padding = ord(padding)
            clear_text = clear_text[:0-padding]
        return clear_text.decode('utf-8')

def main():
    access_token = os.environ.get('KEYSTOK_ACCESS_TOKEN', '')
    cache_dir = os.environ.get('KEYSTOK_CACHE_DIR', '')
    parser = argparse.ArgumentParser(description='Keystok shell access')
    parser.add_argument('-a', '--access-token', type=str, help='Specify access token (overrides $KEYSTOK_ACCESS_TOKEN)')
    parser.add_argument('-c', '--cache-dir', type=str, help='Specify cache directory (overrides $KEYSTOK_CACHE_DIR, defaults to ~/.keystok)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show verbose output')
    parser.add_argument('command', choices=['ls', 'get'], help='Command to execute')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    # Access token is required
    if args.access_token:
        access_token = args.access_token
    if not access_token:
        sys.stderr.write('Access token is not configured. Please set KEYSTOK_ACCESS_TOKEN environment variable or use the -a option.\n');
        sys.exit(1)

    # Allow overriding cache dir
    if args.cache_dir:
        cache_dir = args.cache_dir

    # Execute the command
    client = KeystokClient({
        'access_token': access_token,
        'cache_dir': cache_dir,
        'verbose': args.verbose,
    })
    cmd = getattr(client, 'cmd_' + args.command)
    if not cmd:
        sys.stderr.write('Invalid command \'%s\'". Try -h for help.\n' % args.command)
        sys.exit(2)
    cmd(*args.args)

if __name__ == '__main__':
    main()
