#########################
#Credentials to be used
#########################
CREDENTIALS = {
    'EC2': {
        'api_key': "AKIAJ4CJHJDWUMIQCIHA",
        'api_secret': "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"
    },
    'Rackspace': {
        'username': "unwebme",
        'api_key': "853e73d90b5da2a19b75fbd084e043b4"
    },
    'BareMetal': {
        'hostname': "",
        'user': "",
        'key': {
            'name': "",
            'private': ""
        }
    },
    'Openstack': {
        'username': "admin",
        'password': "mist",
        'auth_url': "http://37.58.77.91:5000",
        'tenant': "admin"
    },
    'Softlayer': {
        'api_key': "SL282402",
        'api_secret': "1a11556d004daba636db734ad27070d304699b33f79a0cb628c6423f292fb417"
    },
    'Nephoscale': {
        'username': "mistiotest",
        'password': "n3ph0t3stmy455"
    },
    'Linode': {
        'username': "unwebme",
        'api_key': "0HRvfSdwUKlnM8Ds1Mtmt2Ysdt6Fo2T97dJDWCp5o4UwJsPrxsr8d8HQGsL87cgY"
    },
    'HPCloud': {
        'username': "mistio",
        'password': "@mistiohpcl0ud",
        'tenant': "mistio-test"
    }
}

#####################
#Credentials for mist.io to test io-core connectivity
#####################
MISTCREDS = {
    'username': "commixon@gmail.com",
    'password': "lida1234"
}

####################
#They'll be used to add random Machine names and keys
####################
TESTNAMES = {
    "machine_name": "TESTMACHINE",
    "image_machine": "IMAGEMACHINE",
    "key":"TESTKEY"
}
