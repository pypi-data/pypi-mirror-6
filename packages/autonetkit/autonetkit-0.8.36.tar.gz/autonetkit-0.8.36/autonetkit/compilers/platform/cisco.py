import itertools
import os
from datetime import datetime

import autonetkit
import autonetkit.config
import autonetkit.log as log
import autonetkit.plugins.naming as naming
from autonetkit.ank import sn_preflen_to_network
from autonetkit.ank_utils import call_log
from autonetkit.compilers.device.cisco import (IosBaseCompiler,
                                               IosClassicCompiler,
                                               IosXrCompiler, NxOsCompiler,
                                               StarOsCompiler)
from autonetkit.compilers.platform.platform_base import PlatformCompiler
from autonetkit.nidb import config_stanza


class CiscoCompiler(PlatformCompiler):
    """Platform compiler for Cisco"""

    @staticmethod
    def numeric_to_interface_label_ios(x):
        """Starts at GigabitEthernet0/1 """
        x = x + 1
        return "GigabitEthernet0/%s" % x

    @staticmethod
    def numeric_to_interface_label_ra(x):
        """Starts at Gi0/1
        #TODO: check"""
        x = x + 1
        return "GigabitEthernet%s" % x

    @staticmethod
    def numeric_to_interface_label_nxos(x):
        return "Ethernet2/%s" % (x+1)

    @staticmethod
    def numeric_to_interface_label_ios_xr(x):
        return "GigabitEthernet0/0/0/%s" % x

    @staticmethod
    def numeric_to_interface_label_star_os(x):
        return "ethernet 1/%s" % (x + 10)

    @staticmethod
    def numeric_to_interface_label_linux(x):
        return "eth%s" % x

    @staticmethod
    def loopback_interface_ids():
        for x in itertools.count(100): # start at 100 for secondary
            prefix = IosBaseCompiler.lo_interface_prefix
            yield "%s%s" % (prefix, x)

    @staticmethod
    def interface_ids_ios():
        #TODO: make this skip if in list of allocated ie [interface.name for interface in node]
        for x in itertools.count(0):
            yield "GigabitEthernet0/%s" % x

    @staticmethod
    def interface_ids_csr1000v():
        #TODO: make this skip if in list of allocated ie [interface.name for interface in node]
        for x in itertools.count(0):
            yield "GigabitEthernet%s" % x

    @staticmethod
    def interface_ids_nxos():
        for x in itertools.count(0):
            yield "Ethernet2/%s" % x

    @staticmethod
    def interface_ids_ios_xr():
        for x in itertools.count(0):
            yield "GigabitEthernet0/0/0/%s" % x

    @staticmethod
    def numeric_interface_ids():
        """#TODO: later skip interfaces already taken"""
        for x in itertools.count(0):
            yield x

    @call_log
    def compile(self):
        self.copy_across_ip_addresses()
        self.compile_devices()
        self.assign_management_interfaces()

    def _parameters(self):
        g_phy = self.anm['phy']
        settings = autonetkit.config.settings
        to_memory = settings['Compiler']['Cisco']['to memory']
        use_mgmt_interfaces = g_phy.data.mgmt_interfaces_enabled


        now = datetime.now()
        if settings['Compiler']['Cisco']['timestamp']:
            timestamp = now.strftime("%Y%m%d_%H%M%S_%f")
            dst_folder = os.path.join("rendered", self.host, timestamp, "cisco")
        else:
            dst_folder = os.path.join("rendered", self.host, "cisco")

        #TODO: use a namedtuple
        return to_memory, use_mgmt_interfaces, dst_folder

    @call_log
    def compile_devices(self):
        g_phy = self.anm['phy']

        to_memory, use_mgmt_interfaces, dst_folder = self._parameters()
        if use_mgmt_interfaces:
            log.info("Allocating VIRL management interfaces")
        else:
            log.info("Not allocating VIRL management interfaces")
#TODO: need to copy across the interface name from edge to the interface

# TODO: merge common router code, so end up with three loops: routers, ios
# routers, ios_xr routers

    #TODO: Split out each device compiler into own function

    #TODO: look for unused code paths here - especially for interface allocation

        # store autonetkit_cisco version
        log.info("Generating device configurations")
        from pkg_resources import get_distribution

        for phy_node in g_phy.l3devices(host=self.host):
            loopback_ids = self.loopback_interface_ids()
            # allocate loopbacks to routes (same for all ios variants)
            nidb_node = self.nidb.node(phy_node)
            nidb_node.add_stanza("render")
            nidb_node.indices = phy_node.indices

            for interface in nidb_node.loopback_interfaces:
                if interface != nidb_node.loopback_zero:
                    interface.id = loopback_ids.next()

            # numeric ids
            numeric_int_ids = self.numeric_interface_ids()
            for interface in nidb_node.physical_interfaces:
                phy_numeric_id = phy_node.interface(interface).numeric_id
                if phy_numeric_id is None:
                    #TODO: remove numeric ID code
                    interface.numeric_id = numeric_int_ids.next()
                else:
                    interface.numeric_id = int(phy_numeric_id)

                phy_specified_id = phy_node.interface(interface).specified_id
                if phy_specified_id is not None:
                    interface.id = phy_specified_id

        #from autonetkit.compilers.device.ubuntu import UbuntuCompiler
        from autonetkit_cisco.compilers.device.ubuntu import UbuntuCompiler

        ubuntu_compiler = UbuntuCompiler(self.nidb, self.anm)
        for phy_node in g_phy.servers(host=self.host):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.add_stanza("render")
            nidb_node.add_stanza("ip")

            #TODO: look at server syntax also, same as for routers
            for interface in nidb_node.physical_interfaces:
                phy_specified_id = phy_node.interface(interface).specified_id
                if phy_specified_id is not None:
                    interface.id = phy_specified_id

                #interface.id = self.numeric_to_interface_label_linux(interface.numeric_id)
                #print "numeric", interface.numeric_id, interface.id
                nidb_node.ip.use_ipv4 = phy_node.use_ipv4
                nidb_node.ip.use_ipv6 = phy_node.use_ipv6

                #TODO: clean up interface handling
            numeric_int_ids = self.numeric_interface_ids()
            for interface in nidb_node.physical_interfaces:
                phy_int = phy_node.interface(interface)
                phy_numeric_id = phy_node.interface(interface).numeric_id
                if phy_numeric_id is None:
                    #TODO: remove numeric ID code
                    interface.numeric_id = numeric_int_ids.next()
                else:
                    interface.numeric_id = int(phy_numeric_id)

                phy_specified_id = phy_node.interface(interface).specified_id
                if phy_specified_id is not None:
                    interface.id = phy_specified_id

                #TODO: make this part of the base device compiler, which server/router inherits

            if use_mgmt_interfaces: # not these are physical interfaces; configure after previous config steps
                mgmt_int = nidb_node.add_interface(management = True, description = "eth0")
                mgmt_int_id = "eth0"
                mgmt_int.id = mgmt_int_id

                    # render route config
            nidb_node = self.nidb.node(phy_node)
            ubuntu_compiler.compile(nidb_node)

            if not phy_node.dont_configure_static_routing:
                nidb_node.render.template = os.path.join("templates", "linux", "static_route.mako")
                if to_memory:
                    nidb_node.render.to_memory = True
                else:
                    nidb_node.render.dst_folder = dst_folder
                    nidb_node.render.dst_file = "%s.conf" % naming.network_hostname(
                        phy_node)


        #TODO: refactor out common logic

        ios_compiler = IosClassicCompiler(self.nidb, self.anm)
        host_routers = g_phy.routers(host=self.host)
        ios_nodes = (n for n in host_routers if n.syntax in ("ios", "ios_xe"))
        for phy_node in ios_nodes:
            nidb_node = self.nidb.node(phy_node)
            nidb_node.add_stanza("render")
            nidb_node.render.template = os.path.join("templates","ios.mako")
            if to_memory:
                nidb_node.render.to_memory = True
            else:
                nidb_node.render.dst_folder = dst_folder
                nidb_node.render.dst_file = "%s.conf" % naming.network_hostname(
                    phy_node)

            #TODO: write function that assigns interface number excluding those already taken

            # Assign interfaces
            if phy_node.device_subtype == "IOSv":
                int_ids = self.interface_ids_ios()
                numeric_to_interface_label = self.numeric_to_interface_label_ios
            elif phy_node.device_subtype == "CSR1000v":
                int_ids = self.interface_ids_csr1000v()
                numeric_to_interface_label = self.numeric_to_interface_label_ra
            else:
                # default if no subtype specified
                #TODO: need to set default in the load module
                log.warning("Unexpected subtype %s for %s" % (phy_node.device_subtype, phy_node))
                int_ids = self.interface_ids_ios()
                numeric_to_interface_label = self.numeric_to_interface_label_ios

            if use_mgmt_interfaces:
                if phy_node.device_subtype == "IOSv":
                    #TODO: make these configured in the internal config file
                    # for platform/device_subtype keying
                    mgmt_int_id = "GigabitEthernet0/0"
                if phy_node.device_subtype == "CSR1000v":
                    mgmt_int_id = "GigabitEthernet1"

            for interface in nidb_node.physical_interfaces:
                #TODO: use this code block once for all routers
                if not interface.id:
                    interface.id = numeric_to_interface_label(interface.numeric_id)

            ios_compiler.compile(nidb_node)
            if use_mgmt_interfaces:
                mgmt_int = nidb_node.add_interface(management = True)
                mgmt_int.id = mgmt_int_id

        try:
            from autonetkit_cisco.compilers.device.cisco import IosXrCompiler
            ios_xr_compiler = IosXrCompiler(self.nidb, self.anm)
        except ImportError:
            ios_xr_compiler = IosXrCompiler(self.nidb, self.anm)

        for phy_node in g_phy.routers(host=self.host, syntax='ios_xr'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.add_stanza("render")
            nidb_node.render.template = os.path.join("templates","ios_xr","router.conf.mako")
            if to_memory:
                nidb_node.render.to_memory = True
            else:
                nidb_node.render.dst_folder = dst_folder
                nidb_node.render.dst_file = "%s.conf" % naming.network_hostname(
                    phy_node)

            # Assign interfaces
            int_ids = self.interface_ids_ios_xr()
            for interface in nidb_node.physical_interfaces:
                if not interface.id:
                    interface.id = self.numeric_to_interface_label_ios_xr(interface.numeric_id)

            ios_xr_compiler.compile(nidb_node)

            if use_mgmt_interfaces:
                mgmt_int_id = "mgmteth0/0/CPU0/0"
                mgmt_int = nidb_node.add_interface(management = True)
                mgmt_int.id = mgmt_int_id

        nxos_compiler = NxOsCompiler(self.nidb, self.anm)
        for phy_node in g_phy.routers(host=self.host, syntax='nx_os'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.add_stanza("render")
            nidb_node.render.template = os.path.join("templates","nx_os.mako")
            if to_memory:
                nidb_node.render.to_memory = True
            else:
                nidb_node.render.dst_folder = dst_folder
                nidb_node.render.dst_file = "%s.conf" % naming.network_hostname(
                    phy_node)

            # Assign interfaces
            int_ids = self.interface_ids_nxos()
            for interface in nidb_node.physical_interfaces:
                if not interface.id:
                    interface.id = self.numeric_to_interface_label_nxos(interface.numeric_id)

            nidb_node.supported_features = config_stanza(mpls_te = False, mpls_oam = False, vrf = False)

            nxos_compiler.compile(nidb_node)
            #TODO: make this work other way around

            if use_mgmt_interfaces:
                mgmt_int_id = "mgmt0"
                mgmt_int = nidb_node.add_interface(management = True)
                mgmt_int.id = mgmt_int_id

        staros_compiler = StarOsCompiler(self.nidb, self.anm)
        for phy_node in g_phy.routers(host=self.host, syntax='StarOS'):
            nidb_node = self.nidb.node(phy_node)
            nidb_node.add_stanza("render")
            nidb_node.render.template = os.path.join("templates","staros.mako")
            if to_memory:
                nidb_node.render.to_memory = True
            else:
                nidb_node.render.dst_folder = dst_folder
                nidb_node.render.dst_file = "%s.conf" % naming.network_hostname(
                    phy_node)

            # Assign interfaces
            int_ids = self.interface_ids_nxos()
            for interface in nidb_node.physical_interfaces:
                if not interface.id:
                    interface.id = self.numeric_to_interface_label_star_os(interface.numeric_id)

            staros_compiler.compile(nidb_node)
            #TODO: make this work other way around

            if use_mgmt_interfaces:
                mgmt_int_id = "ethernet 1/1"
                mgmt_int = nidb_node.add_interface(management = True)
                mgmt_int.id = mgmt_int_id


    def assign_management_interfaces(self):
        g_phy = self.anm['phy']
        use_mgmt_interfaces = g_phy.data.mgmt_interfaces_enabled
        if not use_mgmt_interfaces:
            return
        lab_topology = self.nidb.topology[self.host]
        oob_management_ips = {}

        hosts_to_allocate = sorted(self.nidb.l3devices(host=self.host))
        dhcp_subtypes = {"vios"}
        dhcp_hosts = [h for h in hosts_to_allocate if h.device_subtype in dhcp_subtypes]

        for nidb_node in hosts_to_allocate:
            for interface in nidb_node.physical_interfaces:
                if interface.management:
                    interface.description = "OOB Management"
                    interface.physical = True
                    interface.mgmt = True
                    interface.comment = "Configured on launch"
                    if nidb_node.ip.use_ipv4:
                        interface.use_ipv4 = False # want a "no ip address" stanza
                    if nidb_node.use_cdp:
                        interface.use_cdp = True # ensure CDP activated
                    if nidb_node in dhcp_hosts:
                        interface.use_dhcp = True
