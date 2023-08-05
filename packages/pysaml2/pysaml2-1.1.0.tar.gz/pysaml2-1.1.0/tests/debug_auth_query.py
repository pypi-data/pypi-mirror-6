from urlparse import urlparse
from urlparse import parse_qs
from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_POST
from saml2.saml import AuthnContextClassRef
from saml2.saml import AUTHN_PASSWORD
from saml2.saml import Subject
from saml2.saml import NameID
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.samlp import RequestedAuthnContext, AuthnQuery, AuthnRequest, \
    NameIDPolicy
from saml2.server import Server
from saml2.client import Saml2Client

__author__ = 'rolandh'

TAG1 = "name=\"SAMLRequest\" value="

def get_msg(hinfo, binding):
    if binding == BINDING_SOAP:
        xmlstr = hinfo["data"]
    elif binding == BINDING_HTTP_POST:
        _inp = hinfo["data"][3]
        i = _inp.find(TAG1)
        i += len(TAG1) + 1
        j = _inp.find('"', i)
        xmlstr = _inp[i:j]
    else: # BINDING_HTTP_REDIRECT
        parts = urlparse(hinfo["headers"][0][1])
        xmlstr = parse_qs(parts.query)["SAMLRequest"][0]

    return xmlstr

# ------------------------------------------------------------------------

sp = Saml2Client(config_file="servera_conf")
idp = Server(config_file="idp_all_conf")

relay_state = "FOO"
# -- dummy request ---
orig_req = AuthnRequest(issuer=sp._issuer(),
                        name_id_policy=NameIDPolicy(allow_create="true",
                                                    format=NAMEID_FORMAT_TRANSIENT))

# == Create an AuthnRequest response

name_id = idp.ident.transient_nameid(sp.config.entityid, "id12")
binding, destination = idp.pick_binding("assertion_consumer_service",
                                        entity_id=sp.config.entityid)
resp = idp.create_authn_response({"eduPersonEntitlement": "Short stop",
                                  "surName": "Jeter",
                                  "givenName": "Derek",
                                  "mail": "derek.jeter@nyy.mlb.com",
                                  "title": "The man"},
                                 "id-123456789",
                                 destination,
                                 sp.config.entityid,
                                 name_id=name_id,
                                 authn=(AUTHN_PASSWORD,
                                        "http://www.example.com/login"))

hinfo = idp.apply_binding(binding, "%s" % resp, destination, relay_state)

# ------- @SP ----------

xmlstr = get_msg(hinfo, binding)
aresp = sp.parse_authn_request_response(xmlstr, binding,
                                        {resp.in_response_to :"/"})

binding, destination = sp.pick_binding("authn_query_service",
                                       entity_id=idp.config.entityid)

authn_context = [RequestedAuthnContext(
                            authn_context_class_ref=AuthnContextClassRef(
                                text=AUTHN_PASSWORD))]

subject = aresp.assertion.subject

aq = sp.create_authn_query(subject, destination, authn_context)

print aq

assert isinstance(aq, AuthnQuery)
binding = BINDING_SOAP

hinfo = sp.apply_binding(binding, "%s" % aq, destination, "state2")

# -------- @IDP ----------

xmlstr = get_msg(hinfo, binding)

pm = idp.parse_authn_query(xmlstr, binding)

msg = pm.message
assert msg.id == aq.id


p_res = idp.create_authn_query_response(msg.subject, msg.session_index,
                                        msg.requested_authn_context)

print p_res

hinfo = idp.apply_binding(binding, "%s" % p_res, "", "state2", "SAMLResponse")

# ------- @SP ----------

xmlstr = get_msg(hinfo, binding)

final = sp.parse_authn_query_response(xmlstr, binding)

print final

