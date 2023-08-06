from cubicweb.web import uicfg

def setup_ui(vreg):
    _afs = uicfg.autoform_section
    _afs.tag_attribute(('SecurityProfile', 'dn'), 'main', 'hidden')
    _pvs = uicfg.primaryview_section
    _pvs.tag_attribute(('SecurityProfile', 'dn'), 'hidden')

def registration_callback(vreg):
    setup_ui(vreg)
