from saml2 import config, extension_elements_to_elements
from saml2 import saml
from saml2 import md
from saml2.attribute_converter import ac_factory
from saml2.mdstore import MetadataStore
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
import xmldsig
import xmlenc

from pathutils import full_path

sec_config = config.Config()
#sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])

ONTS = {
    saml.NAMESPACE: saml,
    mdui.NAMESPACE: mdui,
    mdattr.NAMESPACE: mdattr,
    dri.NAMESPACE: dri,
    ui.NAMESPACE: ui,
    idpdisc.NAMESPACE: idpdisc,
    md.NAMESPACE: md,
    xmldsig.NAMESPACE: xmldsig,
    xmlenc.NAMESPACE: xmlenc
}

ATTRCONV = ac_factory(full_path("attributemaps"))
R_AND_S = 'http://id.incommon.org/category/research-and-scholarship'


def test_ent_cat():
    mds = MetadataStore(ONTS.values(), ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp({"mdfile": [full_path("incommon.md")]})

    assigned = []
    print "Assigned"
    # Find all that are assigned R&S
    for ent in mds.keys():
        res = mds.entity_categories(ent)
        if R_AND_S in res:
            assigned.append(ent)

    assert len(assigned) > 0

    supports = []
    print "Supports"
    for ent in mds.keys():
        # Find which entity categories NN supports
        res = mds.supported_entity_categories(ent)
        # Does NN support entity category C
        if R_AND_S in res:
            supports.append(ent)

    assert len(supports) > 0


if __name__ == "__main__":
    test_ent_cat()