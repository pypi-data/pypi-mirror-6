from __init__ import UAParser, UA
uas = UAParser("/Users/ojarva/src/ua-detection-python/uaparser")
test = ['SonyEricssonK750i/R1L Browser/SEMC-Browser/4.2 Profile/MIDP-2.0 Configuration/CLDC-1.1',
        'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-GB; rv:1.8.1.18) Gecko/20081029 Firefox/2.0.0.18',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_5; en-us) AppleWebKit/525.26.2 (KHTML, like Gecko) Version/3.2 Safari/525.26.12',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows XP 5.1) Lobo/0.98.4',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; )',
        'Opera/9.80 (Windows NT 5.1; U; cs) Presto/2.2.15 Version/10.00',
        'boxee (alpha/Darwin 8.7.1 i386 - 0.9.11.5591)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; CSM-NEWUSER; GTB6; byond_4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 1.1.4322; .NET CLR 3.0.04506.648; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; InfoPath.1)',
        'Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36',
]


for item in test:
    res = UA(uas, item)
    print res.parse()
#    print "---%s: %s @ %s" % (res['type'],res['ua_name'],res['os_name'])
