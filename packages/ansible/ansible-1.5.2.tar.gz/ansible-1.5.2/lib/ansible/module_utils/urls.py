# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Michael DeHaan <michael.dehaan@gmail.com>, 2012-2013
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

try:
    import urllib
    HAS_URLLIB = True
except:
    HAS_URLLIB = False

try:
    import urllib2
    HAS_URLLIB2 = True
except:
    HAS_URLLIB2 = False

try:
    import urlparse
    HAS_URLPARSE = True
except:
    HAS_URLPARSE = False

try:
    import ssl
    HAS_SSL=True
except:
    HAS_SSL=False


class RequestWithMethod(urllib2.Request):
    '''
    Workaround for using DELETE/PUT/etc with urllib2
    Originally contained in library/net_infrastructure/dnsmadeeasy
    '''

    def __init__(self, url, method, data=None, headers={}):
        self._method = method
        urllib2.Request.__init__(self, url, data, headers)

    def get_method(self):
        if self._method:
            return self._method
        else:
            return urllib2.Request.get_method(self)


class SSLValidationHandler(urllib2.BaseHandler):
    '''
    A custom handler class for SSL validation.

    Based on:
    http://stackoverflow.com/questions/1087227/validate-ssl-certificates-with-python
    http://techknack.net/python-urllib2-handlers/
    '''

    def __init__(self, module, hostname, port, ca_cert=None):
        self.module = module
        self.hostname = hostname
        self.port = port
        self.ca_cert = ca_cert

    def get_ca_cert(self):
        # tries to find a valid CA cert in one of the
        # standard locations for the current distribution

        if self.ca_cert and os.path.exists(self.ca_cert):
            # the user provided a custom CA cert (ie. one they
            # uploaded themselves), so use it
            return self.ca_cert

        ca_cert = None
        platform = get_platform()
        distribution = get_distribution()
        if platform == 'Linux':
            if distribution in ('Fedora',):
                ca_cert = '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem'
            elif distribution in ('RHEL','CentOS','ScientificLinux'):
                ca_cert = '/etc/pki/tls/certs/ca-bundle.crt'
            elif distribution in ('Ubuntu','Debian'):
                ca_cert = '/usr/share/ca-certificates/cacert.org/cacert.org.crt'
        elif platform == 'FreeBSD':
            ca_cert = '/usr/local/share/certs/ca-root.crt'
        elif platform == 'OpenBSD':
            ca_cert = '/etc/ssl/cert.pem'
        elif platform == 'NetBSD':
            ca_cert = '/etc/openssl/certs/ca-cert.pem'
        elif platform == 'SunOS':
            # FIXME?
            pass
        elif platform == 'AIX':
            # FIXME?
            pass

        if ca_cert and os.path.exists(ca_cert):
            return ca_cert
        elif os.path.exists('/etc/ansible/ca-cert.pem'):
            # fall back to a user-deployed cert in a standard
            # location if the OS platform one is not available
            return '/etc/ansible/ca-cert.pem'
        else:
            # CA cert isn't available, no validation
            return None

    def http_request(self, req):
        try:
            server_cert = ssl.get_server_certificate((self.hostname, self.port), ca_certs=self.get_ca_cert())
        except ssl.SSLError:
            self.module.fail_json(msg='failed to validate the SSL certificate for %s:%s. You can use validate_certs=no, however this is unsafe and not recommended' % (self.hostname, self.port))
        return req

    https_request = http_request


def url_argument_spec():
    '''
    Creates an argument spec that can be used with any module
    that will be requesting content via urllib/urllib2
    '''
    return dict(
        url = dict(),
        force = dict(default='no', aliases=['thirsty'], type='bool'),
        http_agent = dict(default='ansible-httpget'),
        use_proxy = dict(default='yes', type='bool'),
        validate_certs = dict(default='yes', type='bool'),
    )


def fetch_url(module, url, data=None, headers=None, method=None, 
              use_proxy=False, validate_certs=True, force=False, last_mod_time=None, timeout=10):
    '''
    Fetches a file from an HTTP/FTP server using urllib2
    '''

    if not HAS_URLLIB:
        module.fail_json(msg='urllib is not installed')
    if not HAS_URLLIB2:
        module.fail_json(msg='urllib2 is not installed')
    elif not HAS_URLPARSE:
        module.fail_json(msg='urlparse is not installed')

    r = None
    handlers = []
    info = dict(url=url)

    parsed = urlparse.urlparse(url)
    if parsed[0] == 'https':
        if not HAS_SSL and validate_certs:
            module.fail_json(msg='SSL validation is not available in your version of python. You can use validate_certs=no, however this is unsafe and not recommended')
        elif validate_certs:
            # do the cert validation
            netloc = parsed[1]
            if '@' in netloc:
                netloc = netloc.split('@', 1)[1]
            if ':' in netloc:
                hostname, port = netloc.split(':', 1)
            else:
                hostname = netloc
                port = 443
            # create the SSL validation handler and
            # add it to the list of handlers
            ssl_handler = SSLValidationHandler(module, hostname, port)
            handlers.append(ssl_handler)

    if '@' in parsed[1]:
        credentials, netloc = parsed[1].split('@', 1)
        if ':' in credentials:
            username, password = credentials.split(':', 1)
        else:
            username = credentials
            password = ''
        parsed = list(parsed)
        parsed[1] = netloc

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        passman.add_password(None, netloc, username, password)
        # because we have put None at the start it will always
        # use this username/password combination for  urls
        # for which `theurl` is a super-url

        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        # create the AuthHandler
        handlers.append(authhandler)

        #reconstruct url without credentials
        url = urlparse.urlunparse(parsed)

    if not use_proxy:
        proxyhandler = urllib2.ProxyHandler({})
        handlers.append(proxyhandler)

    opener = urllib2.build_opener(*handlers)
    urllib2.install_opener(opener)

    if method:
        if method.upper() not in ('OPTIONS','GET','HEAD','POST','PUT','DELETE','TRACE','CONNECT'):
            module.fail_json(msg='invalid HTTP request method; %s' % method.upper())
        request = RequestWithMethod(url, method.upper(), data)
    else:
        request = urllib2.Request(url, data)

    # add the custom agent header, to help prevent issues 
    # with sites that block the default urllib agent string 
    request.add_header('User-agent', module.params.get('http_agent'))

    # if we're ok with getting a 304, set the timestamp in the 
    # header, otherwise make sure we don't get a cached copy
    if last_mod_time and not force:
        tstamp = last_mod_time.strftime('%a, %d %b %Y %H:%M:%S +0000')
        request.add_header('If-Modified-Since', tstamp)
    else:
        request.add_header('cache-control', 'no-cache')

    # user defined headers now, which may override things we've set above
    if headers:
        if not isinstance(headers, dict):
            module.fail_json("headers provided to fetch_url() must be a dict")
        for header in headers:
            request.add_header(header, headers[header])

    try:
        if sys.version_info < (2,6,0):
            # urlopen in python prior to 2.6.0 did not
            # have a timeout parameter
            r = urllib2.urlopen(request, None)
        else:
            r = urllib2.urlopen(request, None, timeout)
        info.update(r.info())
        info['url'] = r.geturl()  # The URL goes in too, because of redirects.
        info.update(dict(msg="OK (%s bytes)" % r.headers.get('Content-Length', 'unknown'), status=200))
    except urllib2.HTTPError, e:
        info.update(dict(msg=str(e), status=e.code))
    except urllib2.URLError, e:
        code = int(getattr(e, 'code', -1))
        info.update(dict(msg="Request failed: %s" % str(e), status=code))

    return r, info

