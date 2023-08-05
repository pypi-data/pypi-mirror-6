__author__ = 'Stephan Solomonidis'

import datetime
import re
import sys

# TODO: Add support for foreign characters

PYTHON_VERSION = sys.version_info[0]

DOMAIN_REGEX = re.compile(r"""
        ^                                       # match from the start of the string
        (?P<protocol>https?://)?                # protocol (optional)

        (?P<www>www\.)?                         # this is also unnecessary, but users may include it

        (?P<fqdn>

        (?P<first_name>[^_\W]{1}[a-z0-9\-]{1,61}?[^_\W]{1}) # a single 'label', within length parameters

        ((\.(?P<last_name>[^_\W]{1}[a-z0-9\-]{1,61}?[^_\W]{1})
            )(?=\.name))?    # optional 'surname' if matching a '.name' domain

        \.                                      # this is the dot that comes before the TLD

        (?P<tld>gs|gr|ge|gb|edu|gm|gl|tz|tv|tw|tr|tp|tn|to|tl|tm|tj|tk|th|tf|tc|cn\.com|coop|dk|de|dz|
        uk\.net|eu\.com|gov|uy\.com|se\.net|tel|asia|net|jobs|jp|ws|je|com|ck|ch|co|cn|cl|cc|ca|cd|cz|
        cy|cx|pr|pw|pt|pl|xxx|br\.com|me|md|ma|mc|mk|cat|mu|mt|ms|my|mx|hu\.com|va|vc|ve|no\.com|vg|iq|
        is|ir|it|dm|il|io|in|ie|travel|fr|fi|fo|mobi|su|st|sk|si|sh|so|sm|sc|sb|sa|uk\.com|sg|se|org\.uk|
        la|li|lv|lt|lu|gb\.net|ly|biz|za\.com|yu|name|co\.uk|ee|eg|eu|es|ru|gb\.com|ro|be|bg|ba|bi|bj|bt|
        br|org|by|bz|co\.nl|gov\.uk|us\.com|qc\.com|hr|hu|hk|hn|hm|info|uy|uz|us|uk|ua|ac|ae|ag|af|int|pro|
        am|al|as|au|at|ax|az|nl|mil|no|nf|ng|nz|nu|aero|se\.com|sa\.com|kg|ke|kr)

        # matches only those approved TLDs

        )                                       # and so concludes the fqdn group

        (?P<port>:\d{1,5})?                     # port number (optional)

        $""",
    re.IGNORECASE|re.VERBOSE
)

# http://docs.python.org/library/datetime.html#strftime-strptime-behavior
DATE_FORMATS = [
    '%d-%b-%Y',						# 02-jan-2000
    '%d.%m.%Y',						# 02.02.2000
    '%d/%m/%Y',						# 01/06/2011
    '%Y-%m-%d',						# 2000-01-02
    '%Y.%m.%d',						# 2000.01.02
    '%Y/%m/%d',						# 2005/05/30

    '%Y.%m.%d %H:%M:%S',			# 2002.09.19 13:00:00
    '%Y%m%d %H:%M:%S',			    # 20110908 14:44:51
    '%Y-%m-%d %H:%M:%S',		    # 2011-09-08 14:44:51
    '%d.%m.%Y  %H:%M:%S',			# 19.09.2002 13:00:00
    '%d-%b-%Y %H:%M:%S %Z',			# 24-Jul-2009 13:20:03 UTC
    '%Y/%m/%d %H:%M:%S (%z)',		# 2011/06/01 01:05:01 (+0900)
    '%Y/%m/%d %H:%M:%S',			# 2011/06/01 01:05:01
    '%a %b %d %H:%M:%S %Z %Y',		# Tue Jun 21 23:59:59 GMT 2011
    '%a %b %d %Y',					# Tue Dec 12 2000
    '%Y-%m-%dT%H:%M:%S',			# 2007-01-26T19:10:31
    '%Y-%m-%dT%H:%M:%SZ',			# 2007-01-26T19:10:31Z
    '%Y-%m-%dT%H:%M:%S%z',			# 2011-03-30T19:36:27+0200
    '%Y-%m-%dT%H:%M:%S.%f%z',		# 2011-09-08T14:44:51.622265+03:00
    '%Y-%m-%dt%H:%M:%S.%f',			# 2011-09-08t14:44:51.622265
]

def str_to_date(s, tld):
    s = s.strip().lower()
    if not s or s == 'not defined': return

    s = s.replace('(jst)', '(+0900)')
    s = re.sub('(\+[0-9]{2}):([0-9]{2})', '\\1\\2', s)

    if PYTHON_VERSION < 3: return str_to_date_py2(s, tld)

    for format in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(s, format)
        except ValueError:
            pass

    raise ValueError("Unknown date format: '{0}' for tld {1}".format(s, tld))

def str_to_date_py2(s, tld):
    tmp = re.findall('\+([0-9]{2})00', s)
    if tmp: tz = int(tmp[0])
    else: tz = 0

    for format in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(s, format) + datetime.timedelta(hours=tz)
        except ValueError:
            pass

    raise ValueError("Unknown date format: '{0}' for tld {1}".format(s, tld))