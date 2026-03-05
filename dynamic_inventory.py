'''
Example Ansible inventory generated from libvirt domain metadata.
'''

from xml.dom import minidom
import libvirt

from ansible.plugins.inventory import BaseInventoryPlugin

class InventoryModule(BaseInventoryPlugin):
    '''Demo inventory plugin'''
    NAME = 'petardo.ansible.inventory.libvirt'

    def verify_file(self, path):
        ''' return true/false if this is possibly a valid file for this plugin to consume '''
        valid = False
        with open('/tmp/blah', 'a', encoding='utf8') as f:
            f.write('running\n')
        print('verify_file', path)
        if super().verify_file(path):
            # base class verifies that file exists and is readable by current user
            if path.endswith(('libvirt.yml')):
                valid = True
        return valid

def get_domain_role(domain):
    '''Return role for libvirt domain `domain`.'''
    state, _reason = domain.state()
    if state != libvirt.VIR_DOMAIN_RUNNING:
        return None

    try:
        # FIXME: even though we catch the exception this prints to stderr.
        # How can we avoid doing that?
        meta = domain.metadata(libvirt.VIR_DOMAIN_METADATA_ELEMENT, 'http://xml.petardo.dk')
    except libvirt.libvirtError as ex:
        errcode, _, _errmsg, *_rest = libvirt.virGetLastError()
        if errcode == libvirt.VIR_ERR_NO_DOMAIN_METADATA:
            return None
        raise ex

    doc = minidom.parseString(meta)

    for elem in doc.getElementsByTagName('meta'):
        role = elem.getAttribute('role')
        if len(role) < 1:
            continue
        return role

with open('/tmp/blah', 'a', encoding='utf8') as f:
    f.write('loaded\n')

if __name__ == '__main__':
    conn = libvirt.open("qemu:///system")
    domains = conn.listAllDomains()

    for domain in domains:
        role = get_domain_role(domain)
        if role:
            print(domain.name(), role)

