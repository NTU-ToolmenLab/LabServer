#!/usr/bin/env python
# -*- coding: utf-8 -*-
from saml2 import BINDING_HTTP_REDIRECT, BINDING_URI
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_SOAP
from saml2.saml import NAME_FORMAT_URI
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import NAMEID_FORMAT_PERSISTENT
import os.path
import saml2.xmldsig as ds

try:
    from saml2.sigver import get_xmlsec_binary
except ImportError:
    get_xmlsec_binary = None

if get_xmlsec_binary:
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin"])
else:
    xmlsec_path = '/usr/bin/xmlsec1'

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def full_path(local_file):
    return os.path.join(BASEDIR, local_file)

HOST = '0.0.0.0'
PORT = 8088

# for traefik
HTTPS = False
BASE = "https://%s:%s" % (HOST, PORT)

# HTTPS cert information
SERVER_CERT = "pki/host.cert"
SERVER_KEY = "pki/host.key"
CERT_CHAIN = "pki/host.chain"
SIGN_ALG = None
DIGEST_ALG = None
#SIGN_ALG = ds.SIG_RSA_SHA512
#DIGEST_ALG = ds.DIGEST_SHA512


CONFIG = {
    "entityid": "myEntityID",
    "description": "My pyIDP",
    "valid_for": 168,
    "service": {
        "aa": {
            "endpoints": {
                "attribute_service": [
                    ("%s/attr" % BASE, BINDING_SOAP)
                ]
            },
            #"name_id_format": [NAMEID_FORMAT_TRANSIENT,
            #                   NAMEID_FORMAT_PERSISTENT]
        },
        "aq": {
            "endpoints": {
                "authn_query_service": [
                    ("%s/aqs" % BASE, BINDING_SOAP)
                ]
            },
        },
        "idp": {
            "name": "My pyIDP",
            "endpoints": {
                "single_sign_on_service": [
                    ("%s/sso/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/sso/post" % BASE, BINDING_HTTP_POST),
                    ("%s/sso/art" % BASE, BINDING_HTTP_ARTIFACT),
                    ("%s/sso/ecp" % BASE, BINDING_SOAP)
                ],
                "single_logout_service": [
                    ("%s/slo/soap" % BASE, BINDING_SOAP),
                    ("%s/slo/post" % BASE, BINDING_HTTP_POST),
                    ("%s/slo/redirect" % BASE, BINDING_HTTP_REDIRECT)
                ],
                "artifact_resolve_service": [
                    ("%s/ars" % BASE, BINDING_SOAP)
                ],
                "assertion_id_request_service": [
                    ("%s/airs" % BASE, BINDING_URI)
                ],
                "manage_name_id_service": [
                    ("%s/mni/soap" % BASE, BINDING_SOAP),
                    ("%s/mni/post" % BASE, BINDING_HTTP_POST),
                    ("%s/mni/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/mni/art" % BASE, BINDING_HTTP_ARTIFACT)
                ],
                "name_id_mapping_service": [
                    ("%s/nim" % BASE, BINDING_SOAP),
                ],
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes": 1},
                    "attribute_restrictions": None, # means all I have
                    #"name_form": NAME_FORMAT_URI,
                },
            },
            "subject_data": "./idp.subject",
            #"name_id_format": [NAMEID_FORMAT_TRANSIENT,
            #                   NAMEID_FORMAT_PERSISTENT]
        },
    },
    "debug": 1,
    "key_file": full_path(SERVER_KEY),
    "cert_file": full_path(SERVER_CERT),
    "metadata": {
        "remote": [{
            "url": "https://my.domain.ntu.edu.tw:443/apps/user_saml/saml/metadata",
            "cert":"pki/mycert.pem"
        }],
        "local":["metadata_tzf.xml"]
    },
    # This database holds the map between a subject's local identifier and
    # the identifier returned to a SP
    "xmlsec_binary": xmlsec_path,
    #"attribute_map_dir": "../attributemaps",
    "logger": {
        "rotating": {
            "filename": "idp.log",
            "maxBytes": 500000,
            "backupCount": 5,
        },
        "loglevel": "debug",
    }
}

# Authentication contexts

    #(r'verify?(.*)$', do_verify),

CAS_SERVER = "https://cas.umu.se"
CAS_VERIFY = "%s/verify_cas" % BASE
PWD_VERIFY = "%s/verify_pwd" % BASE

AUTHORIZATION = {
    "CAS" : {"ACR": "CAS", "WEIGHT": 1, "URL": CAS_VERIFY},
    "UserPassword" : {"ACR": "PASSWORD", "WEIGHT": 2, "URL": PWD_VERIFY}
}
