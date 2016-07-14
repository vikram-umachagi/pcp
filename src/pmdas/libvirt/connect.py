#!/usr/bin/env python
#
# Copyright (C) 2016 Marko Myllynen <myllynen@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import os
import pwd
import sys
import libvirt

from pcp.pmapi import pmContext as PCP

conffile = PCP.pmGetConfig('PCP_PMDAS_DIR')
conffile += '/libvirt/libvirt.conf'

user = 'root'
uri = 'qemu:///system'

config = ConfigParser.SafeConfigParser()
config.read(conffile)
if config.has_section('pmda'):
    for opt in config.options('pmda'):
        if opt == 'user':
            user = config.get('pmda', opt)
        elif opt == 'uri':
            uri = config.get('pmda', opt)
        else:
            sys.stderr.write("Invalid directive '%s' in %s.\n" % (opt, conffile))
            sys.exit(1)

if len(sys.argv) > 1 and (sys.argv[1] == '-c' or sys.argv[1] == '--config'):
    sys.stdout.write("user=%s\nuri=%s\n" % (user, uri))
    sys.exit(0)

try:
    uid = pwd.getpwnam(user).pw_uid
    os.setuid(uid)
except:
    sys.stderr.write("Failed to switch as user %s, try sudo perhaps?\n" % user)
    sys.exit(1)

try:
    conn = libvirt.openReadOnly(uri)
    doms = conn.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_ACTIVE)
except:
    sys.stdout.write("Connection as %s to %s failed!\n" % (user, uri))
    sys.exit(1)

sys.stdout.write("Connection as %s to %s ok.\n" % (user, uri))
