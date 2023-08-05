import re


PREFIX = 'http://confine-project.eu/rel/'

# API types
SERVER_PREFIX = PREFIX + 'server/'
CONTROLLER_PREFIX = PREFIX + 'controller/'
NODE_PREFIX = PREFIX + 'node/'
SYSTEM_PREFIX = PREFIX + 'system/'

# Server API
SERVER_BASE = SERVER_PREFIX + 'base'
SERVER_SERVER = SERVER_PREFIX + 'server'
SERVER_NODES = SERVER_PREFIX + 'node-list'
SERVER_NODE_BASE = SERVER_PREFIX + 'node-base'
SERVER_GATEWAYS = SERVER_PREFIX + 'gateway-list'
SERVER_HOSTS = SERVER_PREFIX + 'host-list'
SERVER_USERS = SERVER_PREFIX + 'user-list'
SERVER_GROUPS = SERVER_PREFIX + 'group-list'
SERVER_SLIVERS = SERVER_PREFIX + 'sliver-list'
SERVER_TEMPLATES = SERVER_PREFIX + 'template-list'
SERVER_ISLANDS = SERVER_PREFIX + 'island-list'
SERVER_SLICES = SERVER_PREFIX + 'slice-list'
SERVER_REBOOT = SERVER_PREFIX + 'do-reboot'
SERVER_UPDATE = SERVER_PREFIX + 'do-update'

# Node API
NODE_SOURCE = NODE_PREFIX + 'source'
NODE_BASE = NODE_PREFIX + 'base'
NODE_NODE = NODE_PREFIX + 'node'
NODE_SLIVERS = NODE_PREFIX + 'sliver-list'
NODE_TEMPLATES = NODE_PREFIX + 'template-list'

# System API
SYSTEM_PULL = SYSTEM_PREFIX + 'do-pull'

# Controller API
CONTROLLER_GET_AUTH_TOKEN = CONTROLLER_PREFIX + 'do-get-auth-token'
CONTROLLER_CHANGE_PASSWORD = CONTROLLER_PREFIX + 'do-change-password'
CONTROLLER_FIRMWARE = CONTROLLER_PREFIX + 'firmware'
CONTROLLER_VM = CONTROLLER_PREFIX + 'vm'
CONTROLLER_UPLOAD_EXP_DATA = CONTROLLER_PREFIX + 'do-upload-exp-data'
CONTROLLER_UPLOAD_OVERLAY = CONTROLLER_PREFIX + 'do-upload-overlay'
CONTROLLER_REQUEST_API_CERT = CONTROLLER_PREFIX + 'do-request-api-cert'


# Utility methods and data structures
relations = dict((var,value) for var,value in dict(locals()).iteritems() if var.isupper())
reverse_map = dict((value,var) for var,value in relations.iteritems())

def get(name, type=None, cls=None):
    regex = r"[^'.]*_"
    if type is not None:
        regex = r"%s_"% type.upper()
    if cls is not None:
        raise NotImplementedError('cls attribute lookup not implemented')
    regex += "%s'" % name.upper().replace('-', '_')
    matches = re.findall(regex, str(relations.keys()))
    if len(matches) == 1:
        var_name = matches[0][:-1]
        return relations[var_name]
    elif len(matches) < 1:
        raise KeyError("relation for '%s' not found" % name)
    else:
        raise KeyError("found multiple matches for '%s'" % name)

# TODO better naming than name and type
def reverse(relation):
    """ given a relation returns the associated type, class and name """
    name = reverse_map[relation]
    name = name.lower()
    parts = name.split('_')
    type = parts.pop(0)
    name = '_'.join(parts)
    return type, name
