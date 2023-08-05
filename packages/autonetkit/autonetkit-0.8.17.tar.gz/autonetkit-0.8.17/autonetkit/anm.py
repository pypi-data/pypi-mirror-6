#!/usr/bin/python
# -*- coding: utf-8 -*-
import functools
import itertools
import pprint
import string
import time
from functools import total_ordering

import autonetkit.log as log
import networkx as nx
from autonetkit.ank_utils import unwrap_edges, unwrap_nodes

try:
    import cPickle as pickle
except ImportError:
    import pickle

import logging


#TODO: rename duplicate use of logger var in log setup
class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return '[%s]: %s' % (self.extra['item'], msg), kwargs

class AutoNetkitException(Exception):

    pass


class OverlayNotFound(AutoNetkitException):

    def __init__(self, errors):
        self.Errors = errors

    def __str__(self):
        return 'Overlay %s not found' % self.Errors

# TODO: rename to OverlayInterface

class overlay_interface(object):

    def __init__(
        self,
        anm,
        overlay_id,
        node_id,
        interface_id,
    ):
        object.__setattr__(self, 'anm', anm)
        object.__setattr__(self, 'overlay_id', overlay_id)
        object.__setattr__(self, 'node_id', node_id)
        object.__setattr__(self, 'interface_id', interface_id)
        logger = logging.getLogger("ANK")
        logstring = "Node: %s" % str(self)
        logger = CustomAdapter(logger, {'item': logstring})
        object.__setattr__(self, 'log', logger)

    def __key(self):
        """Note: key doesn't include overlay_id to allow fast cross-layer comparisons"""

        # based on http://stackoverflow.com/q/2909106

        return (self.interface_id, self.node_id)

    def __hash__(self):
        """"""

        return hash(self.__key())

    def __repr__(self):
        description = self.description or self.interface_id
        return '(%s, %s)' % (description, self.node)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __nonzero__(self):

        # TODO: work out why description and type being set/copied to each
        # overlay

        try:
            interface = self._interface
        except KeyError:
            return False

        return len(interface) > 0  # if interface data set

    def __lt__(self, other):

        # TODO: check how is comparing the nodes

        return (self.node, self.interface_id) < (other.node,
                                                 other.interface_id)

    @property
    def is_bound(self):
        """Returns if this interface is bound to an edge on this layer"""

        return len(self.edges()) > 0

    def __str__(self):
        return self.__repr__()

    @property
    def _graph(self):
        """Return graph the node belongs to"""

        return self.anm.overlay_nx_graphs[self.overlay_id]

    @property
    def _node(self):
        """Return graph data the node belongs to"""

        return self._graph.node[self.node_id]

    @property
    def _interface(self):
        """Return data dict for the interface"""

        try:
            return self._node['_interfaces'][self.interface_id]
        except KeyError:
            log.warning('Unable to find interface %s in %s'
                        % (self.interface_id, self.node))
            return None

    @property
    def phy(self):

        # check overlay requested exists

        if self.overlay_id == 'phy':
            return self
        return overlay_interface(self.anm, 'phy', self.node_id,
                                 self.interface_id)

    def __getitem__(self, overlay_id):
        """Returns corresponding interface in specified overlay"""

        if not self.anm.has_overlay(overlay_id):
            log.warning('Trying to access interface %s for non-existent overlay %s'
                        % (self, overlay_id))
            return None

        if not self.node_id in self.anm.overlay_nx_graphs[overlay_id]:
            log.debug('Trying to access interface %s for non-existent node %s in overlay %s'
                      % (self, self.node_id, self.overlay_id))
            return None

        try:
            return overlay_interface(self.anm, overlay_id,
                                     self.node_id, self.interface_id)
        except KeyError:
            return

    @property
    def is_loopback(self):
        """"""

        return self.type == 'loopback' or self.phy.type == 'loopback'

    @property
    def is_physical(self):
        """"""

        return self.type == 'physical' or self.phy.type == 'physical'

    @property
    def description(self):
        """"""

        retval = self._interface.get('description')
        if retval:
            return retval

        if self.overlay_id != 'phy':  # prevent recursion
            self.phy._interface.get('description')

    @property
    def is_loopback_zero(self):
        return self.interface_id == 0 and self.is_loopback

    @property
    def type(self):
        """"""

# TODO: make 0 correctly access interface 0 -> copying problem
# TODO: this needs a bugfix rather than the below hard-coded workaround

        if self.interface_id == 0:
            return 'loopback'

        if self.overlay_id == 'input':
            return object.__getattr__(self, 'type')
        elif self.overlay_id != 'phy':

                                        # prevent recursion

            return self.phy._interface.get('type')

        retval = self._interface.get('type')
        if retval:
            return retval

    @property
    def node(self):
        """Returns parent node of this interface"""

        return OverlayNode(self.anm, self.overlay_id, self.node_id)

    def dump(self):
        return str(self._interface.items())

    def __getattr__(self, key):
        """Returns interface property"""

        try:
            return self._interface.get(key)
        except KeyError:
            return

    def get(self, key):
        """For consistency, node.get(key) is neater
        than getattr(interface, key)"""

        return getattr(self, key)

    def __setattr__(self, key, val):
        """Sets interface property"""

        try:
            self._interface[key] = val
        except KeyError, e:
            log.warning(e)

            # self.set(key, val)

    def set(self, key, val):
        """For consistency, node.set(key, value) is neater
        than setattr(interface, key, value)"""

        return self.__setattr__(key, val)

    def edges(self):
        """Returns all edges from node that have this interface ID
        This is the convention for binding an edge to an interface"""

        # edges have _interfaces stored as a dict of {node_id: interface_id, }

        valid_edges = [e for e in self.node.edges() if self.node_id
                       in e._interfaces and e._interfaces[self.node_id]
                       == self.interface_id]
        return list(valid_edges)

    def neighbors(self):
        """Returns interfaces on nodes that are linked to this interface
        Can get nodes using [i.node for i in interface.neighbors()]
        """

        edges = self.edges()
        return [e.dst_int for e in edges]


@total_ordering
class OverlayNode(object):

    """OverlayNode"""

    def __init__(
        self,
        anm,
        overlay_id,
        node_id,
    ):

# Set using this method to bypass __setattr__

        object.__setattr__(self, 'anm', anm)
        object.__setattr__(self, 'overlay_id', overlay_id)
# should be able to use _graph from here as anm and overlay_id are defined
        object.__setattr__(self, 'node_id', node_id)
        logger = logging.getLogger("ANK")
        logstring = "Node: %s" % str(self)
        logger = CustomAdapter(logger, {'item': logstring})
        object.__setattr__(self, 'log', logger)

    def __hash__(self):
        """"""

        return hash(self.node_id)

    def __nonzero__(self):
        """Allows for checking if node exists"""

        return self.node_id in self._graph

    def __iter__(self):
        """Shortcut to iterate over the physical interfaces of this node"""

        return self.interfaces(type='physical')

    def __eq__(self, other):
        """"""

        try:
            return self.node_id == other.node_id
        except AttributeError:
            return self.node_id == other  # eg compare Node to label

    def __ne__(self, other):
            return not self.__eq__(other)

    @property
    def loopback_zero(self):
        """"""

        return (i for i in self.interfaces('is_loopback_zero')).next()

    @property
    def physical_interfaces(self):
        """"""

        return self.interfaces(type='physical')

    @property
    def loopback_interfaces(self):
        """"""

        return self.interfaces(type='loopback')

    def __lt__(self, other):
        """"""

# want [r1, r2, ..., r11, r12, ..., r21, r22] not [r1, r11, r12, r2, r21, r22]
# so need to look at numeric part

        self_node_id = self.node_id
        other_node_id = other.node_id
        try:
            self_node_string = [x for x in self.node_id if x
                                not in string.digits]
            other_node_string = [x for x in self.node_id if x
                                 not in string.digits]
        except TypeError:

            # e.g. non-iterable type, such as an int node_id

            pass
        else:
            if self_node_string == other_node_string:
                self_node_id = """""".join([x for x in self.node_id
                                            if x in string.digits])
                other_node_id = """""".join([x for x in other.node_id
                                             if x in string.digits])
                try:
                    self_node_id = int(self_node_id)
                except ValueError:
                    pass  # not a number
                try:
                    other_node_id = int(other_node_id)
                except ValueError:
                    pass  # not a number

        return (self.asn, self_node_id) < (other.asn, other_node_id)

    @property
    def _next_int_id(self):
        """"""

# returns next free interface ID

        for int_id in itertools.count(1):  # start at 1 as 0 is loopback
            if int_id not in self._interfaces:
                return int_id

    # TODO: interface function access needs to be cleaned up

    def _add_interface(
        self,
        description=None,
        type='physical',
        *args,
        **kwargs
    ):
        """"""

        data = dict(kwargs)

        if self.overlay_id != 'phy' and self.phy:
            next_id = self.phy._next_int_id
            self.phy._interfaces[next_id] = {'type': type,
                                             'description': description}

            # TODO: fix this workaround for not returning description from phy
            # graph

            data['description'] = description
        else:
            next_id = self._next_int_id
            data['type'] = type  # store type on node
            data['description'] = description

        self._interfaces[next_id] = data
        return next_id

    def add_loopback(self, *args, **kwargs):
        '''Public function to add a loopback interface'''

        interface_id = self._add_interface(type='loopback', *args,
                                           **kwargs)
        return overlay_interface(self.anm, self.overlay_id,
                                 self.node_id, interface_id)

    def add_interface(self, *args, **kwargs):
        """Public function to add interface"""

        interface_id = self._add_interface(*args, **kwargs)
        return overlay_interface(self.anm, self.overlay_id,
                                 self.node_id, interface_id)

    def interfaces(self, *args, **kwargs):
        """Public function to view interfaces"""

        def filter_func(interface):
            """Filter based on args and kwargs"""

            return all(getattr(interface, key) for key in args) \
                and all(getattr(interface, key) == val for (key,
                        val) in kwargs.items())

        all_interfaces = iter(overlay_interface(self.anm,
                              self.overlay_id, self.node_id,
                              interface_id) for interface_id in
                              self._interface_ids)

        retval = (i for i in all_interfaces if filter_func(i))
        return retval

    def interface(self, key):
        """Returns interface based on interface id"""

        try:
            if key.interface_id in self._interface_ids:
                return overlay_interface(self.anm, self.overlay_id,
                                         self.node_id, key.interface_id)
        except AttributeError:

            # try with key as id

            try:
                if key in self._interface_ids:
                    return overlay_interface(self.anm, self.overlay_id,
                                             self.node_id, key)
            except AttributeError:

                # no match for either

                log.warning('Unable to find interface %s in %s '
                            % (key, self))
                return None

    @property
    def _interface_ids(self):
        """Returns interface ids for this node"""

        if self.overlay_id != 'phy' and self.phy:

            # graph isn't physical, and node exists in physical graph -> use
            # the interface mappings from phy

            return self.phy._graph.node[self.node_id]['_interfaces'
                                                      ].keys()
        else:
            try:
                return self._graph.node[self.node_id]['_interfaces']
            except KeyError:
                self.log.debug('No interfaces initialised')
                return []

    @property
    def _interfaces(self):
        """Returns underlying interface dict"""

        try:
            return self._graph.node[self.node_id]['_interfaces']
        except KeyError:
            self.log.debug('No interfaces initialised for')
            return []

    @property
    def _graph(self):
        """Return graph the node belongs to"""

        return self.anm.overlay_nx_graphs[self.overlay_id]

    @property
    def is_router(self):
        """Either from this graph or the physical graph"""

        return self.device_type == 'router' or self.phy.device_type \
            == 'router'

    @property
    def is_switch(self):
        """Returns if device is a switch"""

        return self.device_type == 'switch' or self.phy.device_type \
            == 'switch'

    @property
    def is_server(self):
        """Returns if device is a server"""

        return self.device_type == 'server' or self.phy.device_type \
            == 'server'

    @property
    def is_l3device(self):
        """Layer 3 devices: router, server, cloud, host
        ie not switch
        """

        return self.is_router or self.is_server

    def __getitem__(self, key):
        """Get item key"""

        return OverlayNode(self.anm, key, self.node_id)

    @property
    def asn(self):
        """Returns ASN of this node"""

        try:
            return self._graph.node[self.node_id]['asn']  # not in this graph
        except KeyError:

            # try from phy

            try:
                return self.anm.overlay_nx_graphs['phy'
                                                  ].node[self.node_id]['asn']
            except KeyError:
                if self.node_id not in self.anm.overlay_nx_graphs['phy'
                                                                  ]:
                    message = \
                        'Node id %s not found in physical overlay' \
                        % self.node_id
                    if self.overlay_id == 'input':

                        # don't warn, most likely node not copied across

                        log.debug(message)
                    else:
                        log.warning(message)
                    return

    @asn.setter
    def asn(self, value):

        # TODO: double check this logic

        try:
            self.anm.overlay_nx_graphs['phy'].node[self.node_id]['asn'
                                                                 ] = value
        except KeyError:

            # set ASN directly on the node, eg for collision domains

            self._graph.node[self.node_id]['asn'] = value

    @property
    def id(self):
        """Returns node id"""

        return self.node_id

    @property
    def _overlay(self):
        """Access overlay graph for this node"""

        return OverlayGraph(self.anm, self.overlay_id)

    def degree(self):
        """Returns degree of node"""

        return self._graph.degree(self.node_id)

    def neighbors(self, *args, **kwargs):
        """Returns neighbors of node"""

        neighs = self._overlay.neighbors(self)
        return self._overlay.filter(neighs, *args, **kwargs)

    def neighbor_interfaces(self, *args, **kwargs):

        # TODO: implement filtering for args and kwargs

        if len(args) or len(kwargs):
            log.warning('Attribute-based filtering not currently supported for neighbor_interfaces'
                        )

        return iter(edge.dst_int for edge in self.edges())

    @property
    def label(self):
        """Returns node label (mapped from ANM)"""

        return self.__repr__()

    @property
    def phy(self):
        """Shortcut back to physical OverlayNode
        Same as node.overlay.phy
        ie node.phy.x is same as node.overlay.phy.x
        """

# refer back to the physical node, to access attributes such as name

        return OverlayNode(self.anm, 'phy', self.node_id)

    def dump(self):
        """Dump attributes of this node"""

        data = dict(self._graph.node[self.node_id])
        del data['_interfaces']
        return str(data)

    def edges(self, *args, **kwargs):
        """Edges to/from this node"""

        return list(self._overlay.edges(self, *args, **kwargs))

    def __str__(self):
        return str(self.__repr__())

    def __repr__(self):
        """Try label if set in overlay, otherwise from physical,
        otherwise node id"""

        try:
            return self.anm.node_label(self)
        except KeyError:
            try:
                return self._graph.node[self.node_id]['label']
            except KeyError:
                return self.node_id  # node not in physical graph

    def __getattr__(self, key):
        """Returns node property
        This is useful for accesing attributes passed through from graphml"""

        try:
            node_data = self._graph.node[self.node_id]
        except KeyError:
            #TODO: only carry out this logic if "Strict mode"
            if key == "device_type":
                #TODO: tidy accessors so this doesn't occur, and remove the suppress
                pass # supress
                return
            self.log.debug("Cannot access %s: node not present in %s"
                %(key, self.overlay_id))
            return
        else:
            try:
                result = node_data[key]
                return result
            except KeyError:
                if key == "device_type":
                    #TODO: tidy accessors so this doesn't occur, and remove the suppress
                    pass # supress
                    return

                # from http://stackoverflow.com/q/2654113
                self.log.debug("Accessing unset attribute %s in %s" % (key, self.overlay_id))
                #import inspect
                #caller = ", ".join(reversed([elem[3] for elem in inspect.stack()[1:-4]]))
                #self.log.debug("Caller: %s" % caller)
                return

    def get(self, key):
        """For consistency, node.get(key) is neater than getattr(node, key)"""

        return getattr(self, key)

    def __setattr__(self, key, val):
        """Sets node property
        This is useful for accesing attributes passed through from graphml"""

        # TODO: look at mapping the object __dict__ straight to the graph.node[self.node_id]
        # TODO: fix wrt using @x.setter won't work due to following:
        # as per
        # http://docs.python.org/2/reference/datamodel.html#customizing-attribute-access

        # TODO: fix workaround for asn

        if key == 'asn':
            object.__setattr__(self, 'asn', val)  # calls @asn.setter

        try:
            self._graph.node[self.node_id][key] = val
        except KeyError:
            self._graph.add_node(self.node_id)
            self.set(key, val)

    def set(self, key, val):
        """For consistency, node.set(key, value) is neater
        than setattr(node, key, value)"""

        return self.__setattr__(key, val)


@total_ordering
class OverlayEdge(object):

    """API to access link in network"""

    def __init__(
        self,
        anm,
        overlay_id,
        src_id,
        dst_id,
    ):

# Set using this method to bypass __setattr__

        object.__setattr__(self, 'anm', anm)
        object.__setattr__(self, 'overlay_id', overlay_id)
        object.__setattr__(self, 'src_id', src_id)
        object.__setattr__(self, 'dst_id', dst_id)
        logger = logging.getLogger("ANK")
        logstring = "Interface: %s" % str(self)
        logger = CustomAdapter(logger, {'item': logstring})
        object.__setattr__(self, 'log', logger)

    def __key(self):
        """Note: key doesn't include overlay_id to allow fast cross-layer comparisons"""

        # based on http://stackoverflow.com/q/2909106

        return (self.src_id, self.dst_id)

    def __hash__(self):
        """"""

        return hash(self.__key())

    def __eq__(self, other):
        """"""

        try:
            return (self.src_id, self.dst_id) == (other.src_id,
                                                  other.dst_id)
        except AttributeError:
            return self.node_id == other

    def __repr__(self):
        """String of node"""

        return '%s: (%s, %s)' % (self.overlay_id, self.src, self.dst)

    def __getitem__(self, key):
        """"""

        overlay = OverlayGraph(self.anm, key)
        return overlay.edge(self)

    def __lt__(self, other):
        """"""

        return (self.src.node_id, self.dst.node_id) \
            < (other.src.node_id, other.dst.node_id)

    @property
    def src(self):
        """Source node of edge"""

        return OverlayNode(self.anm, self.overlay_id, self.src_id)

    @property
    def dst(self):
        """Destination node of edge"""

        return OverlayNode(self.anm, self.overlay_id, self.dst_id)

    def apply_to_interfaces(self, attribute):
        val = self.__getattr__(attribute)
        self.src_int.__setattr__(attribute, val)
        self.dst_int.__setattr__(attribute, val)

    @property
    def src_int(self):
        """Interface bound to source node of edge"""

        src_int_id = self._interfaces[self.src_id]
        return overlay_interface(self.anm, self.overlay_id,
                                 self.src_id, src_int_id)

    @property
    def dst_int(self):
        """Interface bound to destination node of edge"""

        dst_int_id = self._interfaces[self.dst_id]
        return overlay_interface(self.anm, self.overlay_id,
                                 self.dst_id, dst_int_id)

    def attr_equal(self, *args):
        """Return edges which both src and dst have attributes equal"""

        return all(getattr(self.src, key) == getattr(self.dst, key)
                   for key in args)

    def attr_both(self, *args):
        """Return edges which both src and dst have attributes set"""

        return all(getattr(self.src, key) and getattr(self.dst, key)
                   for key in args)

    def attr_any(self, *args):
        """Return edges which either src and dst have attributes set"""

        return all(getattr(self.src, key) or getattr(self.dst, key)
                   for key in args)

    def dump(self):
        return str(self._graph[self.src_id][self.dst_id])

    def __nonzero__(self):
        """Allows for checking if edge exists
        """

        return self._graph.has_edge(self.src_id, self.dst_id)

    def bind_interface(self, node, interface):
        """Bind this edge to specified index"""

        self._interfaces[node.id] = interface

    def interfaces(self):

        # TODO: warn if interface doesn't exist on node

        return iter(overlay_interface(self.anm, self.overlay_id,
                    node_id, interface_id) for (node_id,
                    interface_id) in self._interfaces.items())

    @property
    def _graph(self):
        """Return graph the node belongs to"""

        return self.anm.overlay_nx_graphs[self.overlay_id]

    def get(self, key):
        """For consistency, edge.get(key) is neater than getattr(edge, key)"""

        return self.__getattr__(key)

    def set(self, key, val):
        """For consistency, edge.set(key, value) is neater than
        setattr(edge, key, value)"""

        return self.__setattr__(key, val)

    def __getattr__(self, key):
        """Returns edge property"""

        return self._graph[self.src_id][self.dst_id].get(key)

    def __setattr__(self, key, val):
        """Sets edge property"""

        self._graph[self.src_id][self.dst_id][key] = val


class OverlayGraphData(object):

    """API to access link in network"""

    def __init__(self, anm, overlay_id):

# Set using this method to bypass __setattr__

        object.__setattr__(self, 'anm', anm)
        object.__setattr__(self, 'overlay_id', overlay_id)

    def __repr__(self):
        """"""

        return 'Data for (%s, %s)' % (self.anm, self.overlay_id)

    def dump(self):
        """"""

        print str(self._graph.graph)

    @property
    def _graph(self):

        # access underlying graph for this OverlayNode

        return self.anm.overlay_nx_graphs[self.overlay_id]

    def __getattr__(self, key):
        return self._graph.graph.get(key)

    def __setattr__(self, key, val):
        self._graph.graph[key] = val

    def __getitem__(self, key):
        """"""

        return self._graph.graph.get(key)

    def __setitem__(self, key, val):
        """"""

        self._graph.graph[key] = val


class OverlayBase(object):

    '''Base class for overlays - overlay graphs, subgraphs, projections, etc'''

    def __init__(self, anm, overlay_id):
        """"""

        if overlay_id not in anm.overlay_nx_graphs:
            raise OverlayNotFound(overlay_id)
            #TODO: return False instead?
        self._anm = anm
        self._overlay_id = overlay_id
        logger = logging.getLogger("ANK")
        logstring = "Overlay: %s" % str(overlay_id)
        logger = CustomAdapter(logger, {'item': logstring})
        object.__setattr__(self, 'log', logger)

    def __repr__(self):
        """"""

        return self._overlay_id

    @property
    def data(self):
        """Returns data stored on this overlay graph"""

        return OverlayGraphData(self._anm, self._overlay_id)

    def __contains__(self, n):
        """"""

        try:
            return n.node_id in self._graph
        except AttributeError:

            # try with node_id as a string

            return n in self._graph

    def interface(self, interface):
        """"""

        return overlay_interface(self._anm, self._overlay_id,
                                 interface.node_id,
                                 interface.interface_id)

    def edge(self, edge_to_find, dst_to_find=None):
        '''returns edge in this graph with same src and dst'''

        if isinstance(edge_to_find, OverlayEdge):
            src_id = edge_to_find.src
            dst_id = edge_to_find.dst

            # TODO: add MultiGraph support in terms of key here

            for (src, dst) in self._graph.edges_iter(src_id):
                if dst == dst_id:
                    return OverlayEdge(self._anm, self._overlay_id,
                                       src, dst)

        # TODO: tidy this logic up

        try:
            src = edge_to_find
            dst = dst_to_find
            src.lower()
            dst.lower()
            if self._graph.has_edge(src, dst):
                return OverlayEdge(self._anm, self._overlay_id, src,
                                   dst)
        except AttributeError:
            pass  # not strings
        except TypeError:
            pass

        try:
            if dst_to_find:
                src_id = edge_to_find.node_id
                search_id = dst_to_find.node_id
            else:
                log.warning("Searching by edge_id has been deprecated")
        except AttributeError:
            src_id = None
            search_id = edge_to_find

        for (src, dst) in self._graph.edges_iter(src_id):
            try:
                if (src, dst) == (src_id, search_id):

                    # searching by nodes

                    return OverlayEdge(self._anm, self._overlay_id,
                                       src, dst)
            except KeyError:
                pass  #

    def __getitem__(self, key):
        """"""

        return self.node(key)

    def node(self, key):
        """Returns node based on name
        This is currently O(N). Could use a lookup table"""

        try:
            if key.node_id in self._graph:
                return OverlayNode(self._anm, self._overlay_id,
                                   key.node_id)
        except AttributeError:

            # doesn't have node_id, likely a label string, search based on this
            # label

            for node in self:
                if str(node) == key:
                    return node
            log.warning('Unable to find node %s in %s ' % (key, self))
            return None

    def degree(self, node):
        """"""

        return node.degree()

    def neighbors(self, node):
        return iter(OverlayNode(self._anm, self._overlay_id, node)
                    for node in self._graph.neighbors(node.node_id))

    def overlay(self, key):
        """Get to other overlay graphs in functions"""

        return OverlayGraph(self._anm, key)

    @property
    def name(self):
        """"""

        return self.__repr__()

    def __nonzero__(self):
        return self.anm.has_overlay(self._overlay_id)

    def node_label(self, node):
        """"""

        return repr(OverlayNode(self._anm, self._overlay_id, node))

    def dump(self):
        """"""

        self._anm.dump_graph(self)

    def has_edge(self, edge):
        """Tests if edge in graph"""

        return self._graph.has_edge(edge.src, edge.dst)

    def __iter__(self):
        """"""

        return iter(OverlayNode(self._anm, self._overlay_id, node)
                    for node in self._graph)

    def __len__(self):
        """"""

        return len(self._graph)

    def nodes(self, *args, **kwargs):
        """"""

        result = self.__iter__()
        if len(args) or len(kwargs):
            result = self.filter(result, *args, **kwargs)
        return list(result)

    def routers(self, *args, **kwargs):
        """Shortcut for nodes(), sets device_type to be router"""

        kwargs['device_type'] = 'router'
        return self.nodes(*args, **kwargs)

    def device(self, key):
        """To access programatically"""

        return OverlayNode(self._anm, self._overlay_id, key)

    def groupby(self, attribute, nodes=None):
        """Returns a dictionary sorted by attribute

        >>> G_in.groupby("asn")
        {u'1': [r1, r2, r3, sw1], u'2': [r4]}
        """

        result = {}

        if not nodes:
            data = self.nodes()
        else:
            data = nodes
        data = sorted(data, key=lambda x: x.get(attribute))
        for (key, grouping) in itertools.groupby(data, key=lambda x:
                                                 x.get(attribute)):
            result[key] = list(grouping)

        return result

    def filter(
        self,
        nbunch=None,
        *args,
        **kwargs
    ):
        """"""

        if not nbunch:
            nbunch = self.nodes()

        def filter_func(node):
            """Filter based on args and kwargs"""

            return all(getattr(node, key) for key in args) \
                and all(getattr(node, key) == val for (key, val) in
                        kwargs.items())

        return (n for n in nbunch if filter_func(n))

    def edges(
        self,
        src_nbunch=None,
        dst_nbunch=None,
        *args,
        **kwargs
    ):
        """"""

# nbunch may be single node

        if src_nbunch:
            try:
                src_nbunch = src_nbunch.node_id
            except AttributeError:
                src_nbunch = (n.node_id for n in src_nbunch)

                              # only store the id in overlay

        def filter_func(edge):
            """Filter based on args and kwargs"""

            return all(getattr(edge, key) for key in args) \
                and all(getattr(edge, key) == val for (key, val) in
                        kwargs.items())

        valid_edges = ((src, dst) for (src, dst) in
                       self._graph.edges_iter(src_nbunch))
        if dst_nbunch:
            try:
                dst_nbunch = dst_nbunch.node_id
                dst_nbunch = set([dst_nbunch])
            except AttributeError:

                                 # faster membership test than other sequences

                dst_nbunch = (n.node_id for n in dst_nbunch)

                              # only store the id in OverlayEdge

                # faster membership test than other sequences
                dst_nbunch = set(dst_nbunch)

            valid_edges = ((src, dst) for (src, dst) in valid_edges
                           if dst in dst_nbunch)

        if len(args) or len(kwargs):
            all_edges = iter(OverlayEdge(self._anm, self._overlay_id,
                             src, dst) for (src, dst) in valid_edges)
            result = (edge for edge in all_edges if filter_func(edge))
        else:
            result = (OverlayEdge(self._anm, self._overlay_id, src,
                                  dst) for (src, dst) in valid_edges)
        return list(result)


class OverlaySubgraph(OverlayBase):

    """OverlaySubgraph"""

    def __init__(
        self,
        anm,
        overlay_id,
        graph,
        name=None,
    ):
        """"""

        super(OverlaySubgraph, self).__init__(anm, overlay_id)
        self._graph = graph
        self._subgraph_name = name

    def __repr__(self):
        return self._subgraph_name or 'subgraph'


class OverlayGraph(OverlayBase):

    """API to interact with an overlay graph in ANM"""

    @property
    def anm(self):
        """Returns anm for this overlay"""

        return self._anm

    @property
    def _graph(self):
        """Access underlying graph for this OverlayNode"""

        return self._anm.overlay_nx_graphs[self._overlay_id]

    def _replace_graph(self, graph):
        """"""

        self._anm.overlay_nx_graphs[self._overlay_id] = graph

    # these work similar to their nx counterparts: just need to strip the
    # node_id

    def add_nodes_from(
        self,
        nbunch,
        retain=None,
        update=False,
        **kwargs
    ):
        """Update won't append data (which could clobber) if node exists"""
        nbunch = list(nbunch)  # listify in case consumed in try/except

        if not retain:
            retain = []
        try:
            retain.lower()
            retain = [retain]  # was a string, put into list
        except AttributeError:
            pass  # already a list

        if not update:

# filter out existing nodes

            nbunch = (n for n in nbunch if n not in self._graph)

        nbunch = list(nbunch)
        node_ids = list(nbunch)  # before appending retain data

        if len(retain):
            add_nodes = []
            for node in nbunch:
                data = dict((key, node.get(key)) for key in retain)
                add_nodes.append((node.node_id, data))
            nbunch = add_nodes
        else:
            try:
                # only store the id in overlay
                nbunch = [n.node_id for n in nbunch]
            except AttributeError:
                pass  # use nbunch directly as the node IDs

        self._graph.add_nodes_from(nbunch, **kwargs)
        for node in self._graph.nodes():
            node_data = self._graph.node[node]
            if "label" not in node_data:
                node_data["label"] = str(node)  # use node id

        self._init_interfaces(node_ids)

    def add_node(
        self,
        node,
        retain=None,
        **kwargs
    ):
        """Adds node to overlay"""

        if not retain:
            retain = []
        try:
            retain.lower()
            retain = [retain]  # was a string, put into list
        except AttributeError:
            pass  # already a list

        try:
            node_id = node.id
        except AttributeError:
            node_id = node  # use the string node id

        data = {}
        if len(retain):
            data = dict((key, node.get(key)) for key in retain)
            kwargs.update(data)  # also use the retained data
        self._graph.add_node(node_id, kwargs)
        self._init_interfaces([node_id])

    def _init_interfaces(self, nbunch=None):
        """Initialises interfaces"""
        # TODO: this needs a major refactor!

        # store the original bunch to check if going input->phy
        if nbunch is not None:
            nbunch = list(nbunch)  # listify generators

        original_nbunch = {}

        if nbunch is None:
            nbunch = [n for n in self._graph.nodes()]

        try:
            previous = list(nbunch)
            nbunch = list(unwrap_nodes(nbunch))
        except AttributeError:
            pass  # don't need to unwrap
        else:
            # record a dict of the new nbunch to the original
            for index, element in enumerate(nbunch):
                previous_element = previous[index]
                if previous_element is not None:
                    original_nbunch[element] = previous[index]

        phy_graph = self._anm.overlay_nx_graphs['phy']

        initialised_nodes = []
        for node in nbunch:
            try:
                phy_interfaces = phy_graph.node[node]['_interfaces']
                interface_data = {'description': None,
                                  'type': 'physical'}

                # need to do dict() to copy, otherwise all point to same memory
                # location -> clobber

                data = dict((key, dict(interface_data)) for key in
                            phy_interfaces)
                self._graph.node[node]['_interfaces'] = data
            except KeyError:
                # TODO: split this off into seperate function
                # test if adding from input graph
                # Note: this has to be done on a node-by-node basis
                # as ANK allows adding nodes from multiple graphs at once
                # TODO: warn if adding from multiple overlays at onc
                if self._overlay_id == "phy" and len(original_nbunch):
                        # see if adding from input->phy,
                        # overlay nodes were provided as input
                        original_node = original_nbunch[node]
                        if original_node.overlay_id == "input":
                            # are doing input->phy
                            # copy the
                            original_interfaces = original_node.get(
                                "_interfaces")
                            if original_interfaces is not None:
                                # Initialise with the keys
                                int_data = {k: {"description": v.get("description"), "type": v.get("type")}
                                            for k, v in original_interfaces.items()}
                                self._graph.node[node][
                                    '_interfaces'] = int_data

                else:
                    # no counterpart in physical graph, initialise
                    # Can't do node log becaue node doesn't exist yet
                    self._graph.node[node]['_interfaces'] = \
                        {0: {'description': 'loopback', 'type': 'loopback'}}
                    initialised_nodes.append(node)

        if len(initialised_nodes):
            initialised_nodes = [OverlayNode(self.anm, self._overlay_id, n) for n in initialised_nodes]
            initialised_nodes = sorted([str(n) for n in initialised_nodes])
            self.log.debug("Initialised interfaces for %s" % ", ".join(initialised_nodes))

    def allocate_interfaces(self):
        """allocates edges to interfaces"""

        if self._overlay_id in ('input', 'phy'):
            if all(len(node['input']._interfaces) > 0 for node in self) \
                and all(len(edge['input']._interfaces) > 0 for edge in
                        self.edges()):
                input_interfaces_allocated = True
            else:
                log.info('Automatically assigning input interfaces')
                input_interfaces_allocated = False

        if self._overlay_id == 'input':

            # only return if allocated here

            if input_interfaces_allocated:
                return   # already allocated

        # int_counter = (n for n in itertools.count() if n not in

        if self._overlay_id == 'phy':

            # check if nodes added

            nodes = list(self)
            edges = list(self.edges())
            if len(nodes) and len(edges):

                # allocate called once physical graph populated

                if input_interfaces_allocated:
                    for node in self:
                        input_interfaces = node['input']._interfaces
                        if len(input_interfaces):
                            node._interfaces = input_interfaces

                    for edge in self.edges():
                        edge._interfaces = edge['input']._interfaces
                        input_interfaces = edge['input']._interfaces
                        if len(input_interfaces):
                            edge._interfaces = input_interfaces
                    return

        self._init_interfaces()

        ebunch = sorted(self.edges())

        for edge in ebunch:
            src = edge.src
            dst = edge.dst
            dst = edge.dst
            src_int_id = src._add_interface('%s to %s' % (src.label,
                                                          dst.label))
            dst_int_id = dst._add_interface('%s to %s' % (dst.label,
                                                          src.label))
            edge._interfaces = {}
            edge._interfaces[src.id] = src_int_id
            edge._interfaces[dst.id] = dst_int_id

    def __delitem__(self, key):
        """Alias for remove_node. Allows
        >>> del overlay[node]
        """

        self.remove_node(key)

    def remove_node(self, node):
        """Removes a node from the overlay"""

        try:
            node_id = node.node_id
        except AttributeError:
            node_id = node
        self._graph.remove_node(node_id)

    def add_edge(
        self,
        src,
        dst,
        retain=None,
        **kwargs
    ):
        """Adds an edge to the overlay"""

        if not retain:
            retain = []
        try:
            retain.lower()
            retain = [retain]  # was a string, put into list
        except AttributeError:
            pass  # already a list
        self.add_edges_from([(src, dst)], retain, **kwargs)

    def remove_edges_from(self, ebunch):
        """Removes set of edges from ebunch"""

        try:
            ebunch = unwrap_edges(ebunch)
        except AttributeError:
            pass  # don't need to unwrap
        self._graph.remove_edges_from(ebunch)

    def add_edges(self, *args, **kwargs):
        """Adds a set of edges. Alias for add_edges_from"""

        self.add_edges_from(args, kwargs)

    def add_edges_from(
        self,
        ebunch,
        bidirectional=False,
        retain=None,
        **kwargs
    ):
        """Add edges. Unlike NetworkX, can only add an edge if both
        src and dst in graph already.
        If they are not, then they will not be added (silently ignored)

        Bidirectional will add edge in both directions. Useful if going
        from an undirected graph to a
        directed, eg G_in to G_bgp
        """

        if not retain:
            retain = []
        try:
            retain.lower()
            retain = [retain]  # was a string, put into list
        except AttributeError:
            pass  # already a list

        retain.append('_interfaces')
        try:
            if len(retain):
                add_edges = []
                for edge in ebunch:
                    data = dict((key, edge.get(key)) for key in retain)
                    add_edges.append((edge.src.node_id,
                                      edge.dst.node_id, data))
                ebunch = add_edges
            else:
                ebunch = [(e.src.node_id, e.dst.node_id, {}) for e in
                          ebunch]
        except AttributeError:
            ebunch_out = []
            for (src, dst) in ebunch:

                # TODO: check this works across nodes, etc

                if isinstance(src, overlay_interface) \
                    and isinstance(dst, overlay_interface):
                    _interfaces = {src.node_id: src.interface_id,
                                   dst.node_id: dst.interface_id}
                    ebunch_out.append((src.node_id, dst.node_id,
                                       {'_interfaces': _interfaces}))
                else:
                    try:
                        src_id = src.node_id
                    except AttributeError:
                        src_id = src  # use directly
                    try:
                        dst_id = dst.node_id
                    except AttributeError:
                        dst_id = dst  # use directly
                    ebunch_out.append((src_id, dst_id, {'_interfaces': {}}))

            ebunch = ebunch_out

        ebunch = [(src, dst, data) for (src, dst, data) in ebunch
                  if src in self._graph and dst in self._graph]
        if bidirectional:
            ebunch += [(dst, src, data) for (src, dst, data) in ebunch
                       if src in self._graph and dst in self._graph]

        self._graph.add_edges_from(ebunch, **kwargs)

    def update(self, nbunch=None, **kwargs):
        """Sets property defined in kwargs to all nodes in nbunch"""

        if nbunch is None:
            nbunch = self.nodes()

        if nbunch in self:
            nbunch = [nbunch]  # single node in the list for iteration

        # if the node is in the underlying networkx graph, then map to an overlay node
        nbunch = [self.node(n) if n in self._graph else n for n in nbunch]
        for node in nbunch:
            for (key, value) in kwargs.items():
                node.set(key, value)

    def update_edges(self, ebunch=None, **kwargs):
        """Sets property defined in kwargs to all edges in ebunch"""
        # TODO: also allow (src_id, dst_id) and single overlay edge

        if not ebunch:
            ebunch = self.edges()
        for edge in ebunch:
            for (key, value) in kwargs.items():
                edge.set(key, value)

    def subgraph(self, nbunch, name=None):
        """"""

        nbunch = (n.node_id for n in nbunch)  # only store the id in overlay
        return OverlaySubgraph(self._anm, self._overlay_id,
                               self._graph.subgraph(nbunch), name)


class AbstractNetworkModel(object):

    """"""

    def __init__(self):
        """"""

        self._overlays = {}
        self.add_overlay('phy')
        self.add_overlay('graphics')

        self.label_seperator = '_'
        self.label_attrs = ['label']
        self._build_node_label()
        self.timestamp = time.strftime('%Y%m%d_%H%M%S',
                                       time.localtime())

    def __repr__(self):
        """"""

        return 'ANM %s' % self.timestamp

    @property
    def overlay_nx_graphs(self):
        """"""

        return self._overlays

    def has_overlay(self, overlay_id):
        """"""

        return overlay_id in self._overlays

    def dump(self):
        import autonetkit.ank_json as ank_json
        data = ank_json.jsonify_anm(self)

        # data = data.replace("\\n", "\n")
        # data = data.replace('\\"', '\"')

        return data

    def save(self):
        """"""

        # TODO: take optional filename as parameter

        import autonetkit.ank_json as ank_json
        import os
        import gzip
        archive_dir = os.path.join('versions', 'anm')
        if not os.path.isdir(archive_dir):
            os.makedirs(archive_dir)

        data = ank_json.jsonify_anm(self)
        json_file = 'anm_%s.json.gz' % self.timestamp
        json_path = os.path.join(archive_dir, json_file)
        log.debug('Saving to %s' % json_path)
        with gzip.open(json_path, 'wb') as json_fh:
            json_fh.write(data)

    def restore_latest(self, directory=None):
        """Restores latest saved ANM"""

        import os
        import glob
        if not directory:
            directory = os.path.join('versions', 'anm')

        glob_dir = os.path.join(directory, '*.json.gz')
        pickle_files = glob.glob(glob_dir)
        pickle_files = sorted(pickle_files)
        try:
            latest_file = pickle_files[-1]
        except IndexError:

# No files loaded

            log.warning('No previous ANM saved. Please compile new ANM')
            return
        self.restore(latest_file)

    def restore(self, pickle_file):
        """"""

        import json
        import gzip
        import autonetkit.ank_json as ank_json
        log.debug('Restoring %s' % pickle_file)
        with gzip.open(pickle_file, 'r') as fh:
            data = json.load(fh)
            for (overlay_id, graph_data) in data.items():

                self._overlays[overlay_id] = \
                    ank_json.ank_json_loads(graph_data)

        ank_json.rebind_interfaces(self)

    @property
    def _phy(self):
        """"""

        return OverlayGraph(self, 'phy')

    def initialise_graph(self, graph):
        """Sets input graph. Converts to undirected.
        Initialises graphics overlay."""

        # TODO: check why this isn't used in build_network

        graph = nx.Graph(graph)
        g_graphics = self['graphics']
        g_in = self.add_overlay('input', graph=graph, directed=False)
        g_graphics.add_nodes_from(g_in, retain=[
            'x',
            'y',
            'device_type',
            'device_subtype',
            'pop',
            'label',
            'asn',
        ])
        return g_in

    def add_overlay(
        self,
        name,
        nodes=None,
        graph=None,
        directed=False,
        multi_edge=False,
        retain=None,
    ):
        """Adds overlay graph of name name"""

        if graph:
            if not directed and graph.is_directed():
                log.info('Converting graph %s to undirected' % name)
                graph = nx.Graph(graph)
        elif directed:

            if multi_edge:
                graph = nx.MultiDiGraph()
            else:
                graph = nx.DiGraph()
        else:
            if multi_edge:
                graph = nx.MultiGraph()
            else:
                graph = nx.Graph()

        self._overlays[name] = graph
        overlay = OverlayGraph(self, name)
        overlay.allocate_interfaces()
        if nodes:
            retain = retain or []  # default is an empty list
            overlay.add_nodes_from(nodes, retain)

        return overlay

    def overlays(self):
        """"""

        return self._overlays.keys()

    def devices(self, *args, **kwargs):
        """"""

        return self._phy.filter(*args, **kwargs)

    def __getitem__(self, key):
        """"""

        return OverlayGraph(self, key)

    def node_label(self, node):
        """Returns node label from physical graph"""

        return self.default_node_label(node)

    def _build_node_label(self):
        """"""

        def custom_label(node):
            return self.label_seperator.join(str(self._overlays['phy'
                                                                ].node[node.node_id].get(val)) for val in
                                             self.label_attrs if self._overlays['phy'
                                                                                ].node[node.node_id].get(val) is not None)

        self.node_label = custom_label

    def set_node_label(self, seperator, label_attrs):
        """"""

        try:
            label_attrs.lower()
            label_attrs = [label_attrs]  # was a string, put into list
        except AttributeError:
            pass  # already a list

        self.label_seperator = seperator
        self.label_attrs = label_attrs

    def dump_graph(self, graph):
        """"""

        print '----Graph %s----' % graph
        print 'Graph'
        print self.dump_graph_data(graph)
        print 'Nodes'
        print self.dump_nodes(graph)
        print 'Edges'
        print self.dump_edges(graph)

    @staticmethod
    def dump_graph_data(graph):
        """"""

        debug_data = dict((key, val) for (key, val) in
                          sorted(graph._graph.graph.items()))
        return pprint.pformat(debug_data)

    @staticmethod
    def dump_nodes(graph):
        """"""

        debug_data = dict((graph.node_label(node), data) for (node,
                          data) in graph._graph.nodes(data=True))
        return pprint.pformat(debug_data)

    @staticmethod
    def dump_edges(graph):
        """"""

        debug_data = dict(((graph.node_label(src),
                          graph.node_label(dst)), data) for (src, dst,
                          data) in graph._graph.edges(data=True))
        return pprint.pformat(debug_data)
