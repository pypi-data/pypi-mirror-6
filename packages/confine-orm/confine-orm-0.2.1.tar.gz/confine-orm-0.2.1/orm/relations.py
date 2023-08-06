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


def get_name(relation):
    if relation.startswith(PREFIX):
        family, name = relation.replace(PREFIX, '').split('/')
        name = name.replace('-', '_')
        if name.startswith('do_'):
            name = name.replace('do_', '')
        elif name.endswith('_list'):
            name = name.replace('_list', 's')
        return name
    else:
        msg = "Suport for non '%s' relations is not implemented"
        raise NotImplementedError(msg % PREFIX)
