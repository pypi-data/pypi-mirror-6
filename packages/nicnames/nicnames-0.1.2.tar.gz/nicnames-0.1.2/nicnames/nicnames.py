__author__ = 'Stephan Solomonidis'
# TODO: Add support for all strings, including foreign characters
import socket
import bleach
from tld_data import tld_regexpr
from utilities import (
    str_to_date,
    DOMAIN_REGEX
)

def DNS_Lookup(domain):
    """
    Accepts a fully qualified domain name. Undertakes no validation. Supports IPv4 and IPv6.
    If a TCP connection can be made, returns a list of tuples containing the Nameservers that could be reached.
    Otherwise, returns False.

    >>> DNS_Lookup('python.org')
    [(2, 1, 6, '', ('82.94.164.162', 0)), (30, 1, 6, '', ('2001:888:2000:d::a2', 0, 0, 0))]
    >>> DNS_Lookup('github.com')
    [(2, 1, 6, '', ('192.30.252.129', 0))]
    >>> DNS_Lookup('ouyegrouyqbouygouytbwrt.com')
    False
    """
    try:
        return socket.getaddrinfo(domain, None, 0, socket.SOCK_STREAM)
    except socket.gaierror:
        return False

def validate_domain(fqdn):
    """
    Asserts that the domain name is fully qualified, with a valid TLD, label(s) lasting between 3 and 63 characters,
    optional protocol, and optional 'www' prefix. Does not allow subdomains or subfolders in the URL string.

    Returns a dictionary representing the named groups from the regex.

    >>> validate_domain('http://www.google.com')
    {'protocol': 'http://', 'www': 'www', 'fqdn': 'google.com', 'first_name': 'google', 'tld': 'com'}
    """
    fqdn = bleach.clean(fqdn)
    m = DOMAIN_REGEX.match(fqdn)
    if m is None:
        raise InvalidDomain("You have not entered a valid domain.")
    return m.groupdict()

def whois(fqdn, tld=None):
    """
    Accepts a fully-qualified domain name (i.e. 'google.com'), and preferably also the TLD as a separate argument.
    Returns whois_record as string. 'google.com' will work as the sole argument, but function is slightly faster if
    you pass the TLD explicitly as well: whois('google.com', 'com')

    Queries to Verisign for .com and .net lookups are prepended with the following string: "domain ", to avoid returning
    lots of whois spam.
    """
    if tld is None:
        # Don't rely on this for validation. If validation is important, do it beforehand, and pass the 'fqdn'
        # and 'tld' arguments from the result into this function.
        tld = validate_domain(fqdn)['tld']
    whois_server = tld_regexpr[tld]['whois_server']
    prefix = "domain " if tld == "com" or tld == "net" else ""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((whois_server, 43))
        s.send(b'{0}{1}\r\n'.format(prefix, fqdn))
    except:
        raise ConnectionError("Couldn't connect to {0} (the whois server for {1})".format(whois_server, tld))
    whois_record = b''
    while True:
        try:
            d = s.recv(4096)
            whois_record += d
        except:
            raise ConnectionError("Couldn't connect to {0} (the whois server for {1})".format(whois_server, tld))
        if not d:
            break
    return whois_record


class Domain():
    """
    A record of an existing domain (i.e. unavailable to purchase).
    """
    __is_available = None

    def __init__(self, fqdn, parse_record=True):
        try:
            kwargs = validate_domain(fqdn)
            self.fqdn = kwargs['fqdn']
            self.tld = kwargs['tld']
            for key in kwargs:
                setattr(self, key, kwargs[key])
        except InvalidDomain:
            raise ValueError("{0} is not a valid domain name - no record available".format(fqdn))

        # Fetch and optionally parse the whois record
        if not self.is_available:
            self.whois_record = whois(self.fqdn, self.tld)
        else:
            self.whois_record = None
        if parse_record and self.whois_record is not None:
            self._parse_whois_record()

    def _parse_whois_record(self):
        """
        Parse the raw whois record and assign metadata to instance attributes
        """
        data = tld_regexpr[self.tld]
        for k, v in data.items():
            if k == 'availability_flag':
                self.is_available=True if v in self.whois_record else False
                continue
            if k == "whois_server" or v is None:
                setattr(self, k, v)
                continue

            m = v.search(self.whois_record)
            if m is not None:
                if k == "creation_date" or k == "expiration_date" or k == "updated_date":
                    setattr(self, k, str_to_date(m.group(1), self.tld))
                else:
                    setattr(self, k, m.group(1))

    @property
    def is_available(self):
        if self.__is_available is not None:
            return self.__is_available
        self.is_available = True if DNS_Lookup(self.fqdn) else False
        return self.__is_available

    @is_available.setter
    def is_available(self, boolean_value):
        self.__is_available = boolean_value

    @property
    def whois(self):
        if self.is_available():
            return None
        try:
            if self.whois_record is None:
                self.whois_record = whois(self.fqdn, self.tld)
        except AttributeError:
            self.whois_record = whois(self.fqdn, self.tld)
        return self.whois_record

    @whois.setter
    def whois(self, whois_record):
        self.whois_record = whois_record

class InvalidDomain(Exception):
    pass

class ConnectionError(Exception):
    pass