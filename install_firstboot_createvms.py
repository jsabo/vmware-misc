"""
Create VMware images on firstboot based on data in Cobbler
"""

import distutils.sysconfig
import utils
import sys

plib = distutils.sysconfig.get_python_lib()
mod_path="%s/cobbler" % plib
sys.path.insert(0, mod_path)

def register():
    # this pure python trigger acts as if it were a legacy shell-trigger, but is much faster.
    # the return of this method indicates the trigger type
    return "/var/lib/cobbler/triggers/install/firstboot/*"

def run(api,args,logger):
    # FIXME: make everything use the logger, no prints, use util.subprocess_call, etc

    objtype = args[0] # "system" or "profile"
    name    = args[1] # name of system or profile
    ip      = args[2] # ip or "?"

    if objtype == "system":
        target = api.find_system(name)
    else:
        target = api.find_profile(name)

    # collapse the object down to a rendered datastructure
    target = utils.blender(api, False, target)

    if target == {}:
        logger.info("unable to locate %s " % name)
        raise CX("failure looking up target")

    if target['ks_meta']['vms']:
        for vm in target['ks_meta']['vms'].split(','):
            try:
                arglist = ["/usr/local/bin/createvm",target['ip_address_vmnic1'],vm,target['server']]
                logger.info("creating virtual guest %s" % vm)
                rc = utils.subprocess_call(logger, arglist, shell=False)
            except Exception, reason:
                logger.error("unable to create %s: %s" % (name,reason))
            if rc != 0:
                raise CX("cobbler trigger failed: %(file)s returns ")

    return 0
