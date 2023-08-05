__author__ = 'Stephan Solomonidis'

import re

# TODO: co.jp

tld_regexpr = {
    'gs': { 'whois_server': 'whois.nic.gs'},
    'gr': { 'whois_server': 'whois.ripe.net'},
    'ge': { 'whois_server': 'whois.ripe.net'},
    'gb': { 'whois_server': 'whois.ripe.net'},
    'edu': { 'whois_server': 'whois.educause.net'},
    'gm': { 'whois_server': 'whois.ripe.net'},
    'gl': { 'whois_server': 'whois.nic.gl'},
    'tz': { 'whois_server': 'whois.tznic.or.tz'},
    'tv': { 'whois_server': 'whois.nic.tv'},
    'tw': { 'whois_server': 'whois.twnic.net.tw'},
    'tr': { 'whois_server': 'whois.nic.tr'},
    # The .tp domain was the precursor to .tl, both being of East Timor.
    # .tp is now deprecated and new registrations have not been possible since 2005
    #'tp': { 'whois_server': 'whois.domains.tl'},
    'tn': { 'whois_server': 'whois.ripe.net'},
    'to': { 'whois_server': 'whois.tonic.to'},
    'tl': { 'whois_server': 'whois.nic.tl'},
    'tm': { 'whois_server': 'whois.nic.tm'},
    'tj': { 'whois_server': 'whois.nic.tj'},
    'tk': { 'whois_server': 'whois.nic.tk'},
    'th': { 'whois_server': 'whois.thnic.net'},
    'tf': { 'whois_server': 'whois.nic.tf'},
    'tc': { 'whois_server': 'whois.adamsnames.tc'},
    'cn.com': { 'whois_server': 'whois.centralnic.com'},
    'coop': { 'whois_server': 'whois.nic.coop'},
    'dk': { 'whois_server': 'whois.dk-hostmaster.dk'},
    'de': {
        'domain_name':				re.compile(r'\ndomain:\s*(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Creation Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'\nChanged:\s?(.+)'),

        'name_servers':				re.compile(r'Nserver:\s*(.+)'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.denic.de',
        'availability_flag':        ''
    },
    'dz': { 'whois_server': 'whois.nic.dz'},
    'uk.net': { 'whois_server': 'whois.centralnic.com'},
    'eu.com': { 'whois_server': 'whois.centralnic.com'},
    'gov': { 'whois_server': 'whois.nic.gov'},
    'uy.com': { 'whois_server': 'whois.centralnic.com'},
    'se.net': { 'whois_server': 'whois.centralnic.com'},
    'tel': { 'whois_server': 'whois.nic.tel'},
    'asia': { 'whois_server': 'whois.nic.asia'},
    'net': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Creation Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.verisign-grs.com',
        'availability_flag':        'No match'
    },
    'jobs': {'whois_server': 'jobswhois.verisign-grs.com'},
    'jp': {
        'domain_name':				re.compile(r'\[Domain Name\]\s?(.+)'),
        'registrar':				None,
        'registrant':				re.compile(r'\[Registrant\]\s?(.+)'),

        'creation_date':			re.compile(r'\[Created on\]\s?(.+)'),
        'expiration_date':			re.compile(r'\[Expires on\]\s?(.+)'),
        'updated_date':				re.compile(r'\[Last Updated\]\s?(.+)'),

        'name_servers':				re.compile(r'\[Name Server\]\s*(.+)'),
        'status':					re.compile(r'\[Status\]\s?(.+)'),
        'whois_server':             'whois.jprs.jp',
        'availability_flag':        ''
        },
    'ws': { 'whois_server': 'whois.website.ws'},
    'je': { 'whois_server': 'whois.je'},
    'com': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Creation Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.verisign-grs.com',
        'availability_flag':        'No match'
        },
    'ck': { 'whois_server': 'whois.nic.ck'},
    'ch': { 'whois_server': 'whois.nic.ch'},
    'co': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Sponsoring Registrar:\s?(.+)'),
        'registrant':				re.compile(r'Registrant Organization:\s?(.+)'),

        'creation_date':			re.compile(r'Domain Registration Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Domain Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Domain Last Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.nic.co',
        'availability_flag':        ""
    },
    'cn': { 'whois_server': 'whois.cnnic.net.cn'},
    'cl': { 'whois_server': 'whois.nic.cl'},
    'cc': { 'whois_server': 'whois.nic.cc'},
    'ca': { 'whois_server': 'whois.cira.ca'},
    'cd': { 'whois_server': 'whois.nic.cd'},
    'cz': {
        'domain_name':				re.compile(r'Domain:\s?(.+)'),
        'registrar':				re.compile(r'registrar:\s?(.+)'),
        'registrant':				re.compile(r'registrar:\s?(.+)'),

        'creation_date':			re.compile(r'registered:\s?(.+)'),
        'expiration_date':			re.compile(r'expire:\s?(.+)'),
        'updated_date':				re.compile(r'changed:\s?(.+)'),

        'name_servers':				re.compile(r'nserver:\s*(.+) '),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.nic.cz',
        'availability_flag':        None
    },
    'cy': { 'whois_server': 'whois.ripe.net'},
    'cx': { 'whois_server': 'whois.nic.cx'},
    'pr': { 'whois_server': 'whois.nic.pr'},
    'pw': { 'whois_server': 'whois.nic.pw'},
    'pt': { 'whois_server': 'whois.dns.pt'},
    'pl': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				re.compile(r'Registrant:\n\s*(.+)'),

        'creation_date':			re.compile(r'\ncreated:\s*(.+)\n'),
        'expiration_date':			re.compile(r'Renewal date:\s*(.+)'),
        'updated_date':				re.compile(r'\nlast modified:\s*(.+)\n'),

        'name_servers':				re.compile(r'\nnameservers:\s*(.+)\n\s*(.+)\n'),
        'status':					re.compile(r'\nStatus:\n\s*(.+)'),
        'whois_server':             'whois.dns.pl',
        'availability_flag':        ''
    },
    'aero': { 'whois_server': 'whois.aero'},
    'br.com': { 'whois_server': 'whois.centralnic.com'},
    'me': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Sponsoring Registrar:\s?(.+)'),
        'registrant':				re.compile(r'Registrant Organization:\s?(.+)'),

        'creation_date':			re.compile(r'Domain Create Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Domain Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Domain Last Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Nameservers:\s?(.+)'),
        'status':					re.compile(r'Domain Status:\s?(.+)'),
        'whois_server':             'whois.nic.me',
        'availability_flag':        None
    },
    'md': { 'whois_server': 'whois.nic.md'},
    'ma': { 'whois_server': 'whois.iam.net.ma'},
    'mc': { 'whois_server': 'whois.ripe.net'},
    'mk': { 'whois_server': 'whois.ripe.net'},
    'cat': { 'whois_server': 'whois.cat'},
    'mu': { 'whois_server': 'whois.nic.mu'},
    'mt': { 'whois_server': 'whois.ripe.net'},
    'ms': { 'whois_server': 'whois.nic.ms'},
    'my': { 'whois_server': 'whois.mynic.net.my'},
    'mx': { 'whois_server': 'whois.nic.mx'},
    'hu.com': { 'whois_server': 'whois.centralnic.com'},
    'va': { 'whois_server': 'whois.ripe.net'},
    'vc': { 'whois_server': 'whois2.afilias-grs.net'},
    've': { 'whois_server': 'whois.nic.ve'},
    'no.com': { 'whois_server': 'whois.centralnic.com'},
    'vg': { 'whois_server': 'whois.adamsnames.tc'},
    'iq': { 'whois_server': 'vrx.net'},
    'is': { 'whois_server': 'whois.isnic.is'},
    'ir': { 'whois_server': 'whois.nic.ir'},
    'it': {
        'domain_name':				re.compile(r'Domain:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s*Organization:\s*(.+)'),
        'registrant':				re.compile(r'Registrant:\s?Name:\s?(.+)'),

        'creation_date':			re.compile(r'Created:\s?(.+)'),
        'expiration_date':			re.compile(r'Expire Date:\s?(.+)'),
        'updated_date':				re.compile(r'Last Update:\s?(.+)'),

        'name_servers':				re.compile(r'Nameservers:\s?(.+)\s?(.+)\s?(.+)\s?(.+)'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.nic.it',
        'availability_flag':        None
    },
    'dm': { 'whois_server': 'whois.nic.cx'},
    'il': { 'whois_server': 'whois.isoc.org.il'},
    'io': { 'whois_server': 'whois.nic.io'},
    'in': { 'whois_server': 'whois.inregistry.net'},
    'ie': { 'whois_server': 'whois.domainregistry.ie'},
    'travel': { 'whois_server': 'whois.nic.travel'},
    'fr': {
        'domain_name':				re.compile(r'domain:\s?(.+)'),
        'registrar':				re.compile(r'registrar:\s*(.+)'),
        'registrant':				re.compile(r'contact:\s?(.+)'),

        'creation_date':			re.compile(r'created:\s?(.+)'),
        'expiration_date':			None,
        'updated_date':				re.compile(r'last-update:\s?(.+)'),

        'name_servers':				re.compile(r'nserver:\s*(.+)'),
        'status':					re.compile(r'status:\s?(.+)'),
        'whois_server':             'whois.nic.fr',
        'availability_flag':        None
    },
    'fi': { 'whois_server': 'whois.ficora.fi'},
    'fo': { 'whois_server': 'whois.nic.fo'},
    'mobi': { 'whois_server': 'whois.dotmobiregistry.net'},
    'su': { 'whois_server': 'whois.tcinet.ru'},
    'st': { 'whois_server': 'whois.nic.st'},
    'sk': { 'whois_server': 'whois.sk-nic.sk'},
    'si': { 'whois_server': 'whois.arnes.si'},
    'sh': { 'whois_server': 'whois.nic.sh'},
    'so': { 'whois_server': 'whois.nic.so'},
    'sm': { 'whois_server': 'whois.nic.sm'},
    'sc': {'whois_server': 'whois2.afilias-grs.net'},
    'sb': { 'whois_server': 'whois.nic.net.sb'},
    'sa': { 'whois_server': 'saudinic.net.sa'},
    'uk.com': { 'whois_server': 'whois.centralnic.com'},
    'sg': { 'whois_server': 'whois.nic.net.sg'},
    'se': {'whois_server': 'whois.nic-se.se'},
    'org.uk': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				re.compile(r'Registrant:\n\s*(.+)'),


        'creation_date':			re.compile(r'Registered on:\s*(.+)'),
        'expiration_date':			re.compile(r'Renewal date:\s*(.+)'),
        'updated_date':				re.compile(r'Last updated:\s*(.+)'),

        'name_servers':				re.compile(r'Name Servers:\s*(.+)\s*'),
        'status':					re.compile(r'Registration status:\n\s*(.+)'),
        'whois_server':             'whois.nic.uk',
        'availability_flag':        'No match'
    },
    'la': {'whois_server': 'whois2.afilias-grs.net'},
    'li': { 'whois_server': 'whois.nic.li'},
    'lv': {
        'domain_name':				re.compile(r'\ndomain:\s*(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Registered:\s*(.+)\n'),
        'expiration_date':			re.compile(r'\npaid-till:\s*(.+)'),
        'updated_date':				re.compile(r'Changed:\s*(.+)\n'),

        'name_servers':				re.compile(r'\nnserver:\s*(.+)'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.nic.lv',
        'availability_flag':        ''
    },
    'lt': { 'whois_server': 'whois.domreg.lt'},
    'lu': { 'whois_server': 'whois.restena.lu'},
    'gb.net': { 'whois_server': 'whois.centralnic.com'},
    'ly': { 'whois_server': 'whois.lydomains.com'},
    'biz': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Sponsoring Registrar:\s?(.+)'),
        'registrant':				re.compile(r'Registrant Organization:\s?(.+)'),

        'creation_date':			re.compile(r'Domain Registration Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Domain Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Domain Last Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					None,
        'whois_server':             'whois.neulevel.biz',
        'availability_flag':        "Not found"
    },
    'za.com': { 'whois_server': 'whois.centralnic.com'},
    'yu': { 'whois_server': 'whois.ripe.net'},
    'name': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Creation Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					re.compile(r'Domain Status:\s?(.+)'),
        'whois_server':             'whois.nic.name',
        'availability_flag':        "No match"
    },
    'co.uk': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				re.compile(r'Registrant:\n\s*(.+)'),

        'creation_date':			re.compile(r'Registered on:\s*(.+)'),
        'expiration_date':			re.compile(r'Renewal date:\s*(.+)'),
        'updated_date':				re.compile(r'Last updated:\s*(.+)'),

        'name_servers':				re.compile(r'Name Servers:\s*(.+)\s*'),
        'status':					re.compile(r'Registration status:\n\s*(.+)'),
        'whois_server':             'whois.nic.uk',
        'availability_flag':        'No match'
    },
    'ee': { 'whois_server': 'whois.tld.ee'},
    'eg': { 'whois_server': 'whois.ripe.net'},
    'eu': {
        'domain_name':				re.compile(r'\ndomain:\s*(.+)'),
        'registrar':				re.compile(r'Name:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Creation Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.eu',
        'availability_flag':        "Status:\tAVAILABLE"
    },
    'es': { 'whois_server': 'whois.ripe.net'},
    'ru': {
        'domain_name':				re.compile(r'\ndomain:\s*(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'\ncreated:\s*(.+)'),
        'expiration_date':			re.compile(r'\npaid-till:\s*(.+)'),
        'updated_date':				re.compile(r'Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'\nnserver:\s*(.+)'),
        'status':					re.compile(r'\nstate:\s*(.+)'),
        'whois_server':             'whois.tcinet.ru',
        'availability_flag':        ''
    },
    'gb.com': { 'whois_server': 'whois.centralnic.com'},
    'ro': { 'whois_server': 'whois.rotld.ro'},
    'be': {
        'domain_name':				re.compile(r'\nDomain:\s*(.+)'),
        'registrar':				re.compile(r'Company Name:\n?(.+)'),
        'registrant':				re.compile(r'Registrant:\n\s*(.+)'),

        'creation_date':			re.compile(r'Registered:\s*(.+)\n'),
        'expiration_date':			re.compile(r'Renewal date:\s*(.+)'),
        'updated_date':				re.compile(r'\nlast modified:\s*(.+)\n'),

        'name_servers':				re.compile(r'\nnameservers:\s*(.+)\n\s*(.+)\n'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.dns.be',
        'availability_flag':        None
    },
    'bg': { 'whois_server': 'whois.register.bg'},
    'ba': { 'whois_server': 'whois.ripe.net'},
    'bi': { 'whois_server': 'whois.nic.bi'},
    'bj': { 'whois_server': 'www.nic.bj'},
    'bt': { 'whois_server': 'whois.netnames.net'},
    'br': { 'whois_server': 'whois.nic.br'},
    'org': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'\nCreated On:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'\nLast Updated On:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s?(.+)\s*'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.pir.org',
        'availability_flag':        "NOT FOUND"
    },
    'by': { 'whois_server': 'whois.ripe.net'},
    'bz': { 'whois_server': 'whois.belizenic.bz'},
    'co.nl': { 'whois_server': 'whois.co.nl'},
    'gov.uk': { 'whois_server': 'whois.ja.net'},
    'us.com': { 'whois_server': 'whois.centralnic.com'},
    'qc.com': { 'whois_server': 'whois.centralnic.com'},
    'hr': { 'whois_server': 'whois.ripe.net'},
    'hu': { 'whois_server': 'whois.nic.hu'},
    'hk': { 'whois_server': 'whois.hknic.net.hk'},
    'hn': {'whois_server': 'whois2.afilias-grs.net'},
    'hm': { 'whois_server': 'whois.registry.hm'},
    'info': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Sponsoring Registrar:\s?(.+)'),
        'registrant':				re.compile(r'Registrant Organization:\s?(.+)'),

        'creation_date':			re.compile(r'Created On:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Last Updated On:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.afilias.info',
        'availability_flag':        "NOT FOUND"
    },
    'uy': { 'whois_server': 'nic.uy'},
    'uz': { 'whois_server': 'whois.cctld.uz'},
    'us': {
        'domain_name':				re.compile(r'Domain Name:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Creation Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'Updated Date:\s?(.+)'),

        'name_servers':				re.compile(r'Name Server:\s*(.+)\s*'),
        'status':					re.compile(r'Domain Status:\s?(.+)'),
        'whois_server':             'whois.nic.us',
        'availability_flag':        ""
    },
    'uk': { 'whois_server': 'whois.nic.uk'},
    'ua': { 'whois_server': 'whois.ua'},
    'ac': { 'whois_server': 'whois.nic.ac'},
    'ae': { 'whois_server': 'whois.aeda.net.ae'},
    'ag': { 'whois_server': 'whois.nic.ag'},
    'af': { 'whois_server': 'whois.nic.af'},
    'int': { 'whois_server': 'whois.isi.edu'},
    'pro': { 'whois_server': 'whois.registrypro.pro'},
    'am': { 'whois_server': 'whois.amnic.net'},
    'al': { 'whois_server': 'whois.ripe.net'},
    'as': { 'whois_server': 'whois.nic.as'},
    'au': { 'whois_server': 'whois.aunic.net'},
    'at': {
        'domain_name':				re.compile(r'domain:\s?(.+)'),
        'registrar':				re.compile(r'Registrar:\s?(.+)'),
        'registrant':				None,

        'creation_date':			re.compile(r'Creation Date:\s?(.+)'),
        'expiration_date':			re.compile(r'Expiration Date:\s?(.+)'),
        'updated_date':				re.compile(r'changed:\s?(.+)'),

        'name_servers':				re.compile(r'nserver:\s*(.+)'),
        'status':					re.compile(r'Status:\s?(.+)'),
        'whois_server':             'whois.nic.at',
        'availability_flag':        ''
    },
    'ax': { 'whois_server': 'whois.ax'},
    'az': { 'whois_server': 'whois.ripe.net'},
    'nl': {'whois_server': 'whois.domain-registry.nl'},
    'mil': { 'whois_server': 'whois.nic.mil'},
    'no': { 'whois_server': 'whois.norid.no'},
    'nf': { 'whois_server': 'whois.nic.cx'},
    'ng': { 'whois_server': 'whois.nic.net.ng'},
    'nz': {
        'domain_name':				re.compile(r'domain_name:\s?(.+)'),
        'registrar':				re.compile(r'registrar_name:\s?(.+)'),
        'registrant':				re.compile(r'registrant_contact_name:\s?(.+)'),

        'creation_date':			re.compile(r'domain_dateregistered:\s?(.+)'),
        'expiration_date':			re.compile(r'domain_datebilleduntil:\s?(.+)'),
        'updated_date':				re.compile(r'domain_datelastmodified:\s?(.+)'),

        'name_servers':				re.compile(r'ns_name_[0-9]{2}:\s?(.+)'),
        'status':					re.compile(r'query_status:\s?(.+)'),
        'whois_server':             'whois.srs.net.nz',
        'availability_flag':        None
    },
    'nu': { 'whois_server': 'whois.nic.nu'},
    'xxx': { 'whois_server': 'whois.nic.xxx'},
    'se.com': { 'whois_server': 'whois.centralnic.com'},
    'sa.com': { 'whois_server': 'whois.centralnic.com'},
    'kg': { 'whois_server': 'whois.domain.kg'},
    'ke': { 'whois_server': 'whois.kenic.or.ke'},
    'kr': { 'whois_server': 'whois.nic.or.kr',}
    }