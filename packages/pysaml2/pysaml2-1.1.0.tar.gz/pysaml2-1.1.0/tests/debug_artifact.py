from urlparse import parse_qs
from urlparse import urlparse
from saml2.saml import AUTHN_PASSWORD
from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_ARTIFACT
from saml2.client import Saml2Client

from saml2.s_utils import sid
from saml2.server import Server
from saml2.soap import parse_soap_enveloped_saml_artifact_response

__author__ = 'rolandh'

TAG1 = "name=\"SAMLRequest\" value="

def get_msg(hinfo, binding, response=False):
    if binding == BINDING_SOAP:
        msg = hinfo["data"]
    elif binding == BINDING_HTTP_POST:
        _inp = hinfo["data"][3]
        i = _inp.find(TAG1)
        i += len(TAG1) + 1
        j = _inp.find('"', i)
        msg = _inp[i:j]
    elif binding == BINDING_HTTP_ARTIFACT:
        # either by POST or by redirect
        if hinfo["data"]:
            _inp = hinfo["data"][3]
            i = _inp.find(TAG1)
            i += len(TAG1) + 1
            j = _inp.find('"', i)
            msg = _inp[i:j]
        else:
            parts = urlparse(hinfo["url"])
            msg = parse_qs(parts.query)["SAMLart"][0]
    else: # BINDING_HTTP_REDIRECT
        parts = urlparse(hinfo["headers"][0][1])
        msg = parse_qs(parts.query)["SAMLRequest"][0]

    return msg

SP = 'urn:mace:example.com:saml:roland:sp'
sp = Saml2Client(config_file="servera_conf")
idp = Server(config_file="idp_all_conf")

# original request

binding, destination = sp.pick_binding("single_sign_on_service",
                                       entity_id=idp.config.entityid)
relay_state = "RS0"
req = sp.create_authn_request(destination, id="id1")

artifact = sp.use_artifact(req, 1)

binding, destination = sp.pick_binding("single_sign_on_service",
                                       [BINDING_HTTP_ARTIFACT],
                                       entity_id=idp.config.entityid)

hinfo = sp.apply_binding(binding, "%s" % artifact, destination, relay_state)

# ========== @IDP ============

artifact2 = get_msg(hinfo, binding)

assert artifact == artifact2

# The IDP now wants to replace the artifact with the real request

destination = idp.artifact2destination(artifact2, "spsso")

msg = idp.create_artifact_resolve(artifact2, destination, sid())

hinfo = idp.use_soap(msg, destination, None, False)

# ======== @SP ==========

msg = get_msg(hinfo, BINDING_SOAP)

ar = sp.parse_artifact_resolve(msg)

assert ar.artifact.text == artifact

# The SP picks the request out of the repository with the artifact as the key
oreq = sp.artifact[ar.artifact.text]
# Should be the same as req above

# Returns the information over the existing SOAP connection so
# no transport information needed

msg = sp.create_artifact_response(ar, ar.artifact.text)
hinfo = sp.use_soap(msg, destination)

# ========== @IDP ============

msg = get_msg(hinfo, BINDING_SOAP)

# The IDP untangles the request from the artifact resolve response
spreq = idp.parse_artifact_resolve_response(msg)

# should be the same as req above

assert spreq.id == req.id

# That was one way, the Request from the SP
# ---------------------------------------------#
# Now for the other, the response from the IDP

name_id = idp.ident.transient_nameid(sp.config.entityid, "derek")

resp_args = idp.response_args(spreq, [BINDING_HTTP_POST])

response = idp.create_authn_response({"eduPersonEntitlement": "Short stop",
                                      "surName": "Jeter", "givenName": "Derek",
                                      "mail": "derek.jeter@nyy.mlb.com",
                                      "title": "The man"},
                                     name_id=name_id,
                                     authn=(AUTHN_PASSWORD,
                                            "http://www.example.com/login"),
                                     **resp_args)

print response

# with the response in hand create an artifact

artifact = idp.use_artifact(response, 1)

binding, destination = sp.pick_binding("single_sign_on_service",
                                       [BINDING_HTTP_ARTIFACT],
                                       entity_id=idp.config.entityid)

hinfo = sp.apply_binding(binding, "%s" % artifact, destination, relay_state,
                         response=True)

# ========== SP =========

artifact3 = get_msg(hinfo, binding)

assert artifact == artifact3

destination = sp.artifact2destination(artifact3, "idpsso")

# Got an artifact want to replace it with the real message
msg = sp.create_artifact_resolve(artifact3, destination, sid())

print msg

hinfo = sp.use_soap(msg, destination, None, False)

# ======== IDP ==========

msg = get_msg(hinfo, BINDING_SOAP)

ar = idp.parse_artifact_resolve(msg)

print ar

assert ar.artifact.text == artifact3

# The IDP retrieves the response from the database using the artifact as the key
oreq = idp.artifact[ar.artifact.text]

binding, destination = idp.pick_binding("artifact_resolution_service",
                                        entity_id=sp.config.entityid)

resp = idp.create_artifact_response(ar, ar.artifact.text)
hinfo = idp.use_soap(resp, destination)

# ========== SP ============

msg = get_msg(hinfo, BINDING_SOAP)
sp_resp = sp.parse_artifact_resolve_response(msg)

assert sp_resp.id == response.id
