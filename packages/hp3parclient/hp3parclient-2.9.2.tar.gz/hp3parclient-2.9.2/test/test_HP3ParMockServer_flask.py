#from flask import Flask, request, abort, make_response, session, escape
from flask import *
import pprint
import json, os, random, string
import argparse
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

parser = argparse.ArgumentParser()
parser.add_argument("-debug", help="Turn on http debugging", 
                    default=False, action="store_true")
parser.add_argument("-user", help="User name")
parser.add_argument("-password", help="User password")
parser.add_argument("-port", help="Port to listen on", type=int, default=5000)
args = parser.parse_args()
user_name = args.user
user_pass = args.password
debugRequests = False
if "debug" in args and args.debug == True:
    debugRequests = True

#__all__ = ['make_json_app']

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for x in range(size))

def make_json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        pprint.pprint(ex)
        pprint.pprint(ex.code)
        #response = jsonify(message=str(ex))
        response = jsonify(ex)
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(import_name, **kwargs)
    #app.debug = True
    app.secret_key = id_generator(24)
    

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

app = make_json_app(__name__)

session_key = id_generator(24)

def debugRequest(request):
    if debugRequests:
        print "\n"
        pprint.pprint(request)
        pprint.pprint(request.headers)
        pprint.pprint(request.data)


def throw_error(http_code, error_code=None, desc=None, debug1=None, debug2=None):
    if error_code:
        info = {'code': error_code, 'desc': desc}
        if debug1:
            info['debug1'] = debug1
        if debug2:
            info['debug2'] = debug2
        abort(Response(json.dumps(info), status=http_code))
    else:
        abort(http_code)

@app.route('/')
def index():
    debugRequest(request)
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    abort(401)

@app.route('/api/v1/throwerror')
def errtest():
    debugRequest(request)
    throw_error(405, 'ERR_TEST', 'testing throwing an error', 
                'debug1 message', 'debug2 message')


@app.errorhandler(404)
def not_found(error):
    debugRequest(request)
    return Response("%s has not been implemented" % request.path, status=501)


@app.route('/api/v1/credentials', methods=['GET', 'POST'])
def credentials():
    debugRequest(request)

    if request.method == 'GET':
        return 'GET credentials called'

    elif request.method == 'POST':
	data = json.loads(request.data)

        if data['user'] == user_name and data['password'] == user_pass:
            #do something good here
            try:
                resp = make_response(json.dumps({'key':session_key}), 201)
                resp.headers['Location'] = '/api/v1/credentials/%s' % session_key
                session['username'] = data['user']
                session['password'] = data['password']
                session['session_key'] = session_key
                return resp
            except Exception as ex:
                pprint.pprint(ex)

        else:
            #authentication failed!
            throw_error(401, "HTTP_AUTH_FAIL", "Username and or Password was incorrect")


@app.route('/api/v1/credentials/<session_key>', methods=['DELETE'])
def logout_credentials(session_key):
    debugRequest(request)
    session.clear()
    return 'DELETE credentials called'


#### CPG ####

@app.route('/api/v1/cpgs', methods=['POST'])
def create_cpgs():
    debugRequest(request)
    data = json.loads(request.data)
        
    valid_keys = {'name':None, 'growthIncrementMB':None, 'growthLimitMB':None, 
                  'usedLDWarningAlertMB':None, 'domain':None, 'LDLayout':None}

    valid_LDLayout_keys = {'RAIDType':None, 'setSize':None, 'HA':None, 
                           'chuckletPosRef':None, 'diskPatterns':None} 

    for key in data.keys():
        if key not in valid_keys.keys():
           throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % key)
        elif 'LDLayout' in data.keys():
           layout = data ['LDLayout']
           for subkey in layout.keys():
               if subkey not in valid_LDLayout_keys:
                   throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % subkey) 

    if data['domain'] == 'BAD_DOMAIN': 
        throw_error(404, 'NON_EXISTENT_DOMAIN', "Non-existing domain specified.")     
    
    for cpg in cpgs['members'] :
        if data['name'] == cpg['name'] :
            throw_error(409, 'EXISTENT_CPG', "CPG '%s' already exist." % data['name'])
    
    cpgs['members'].append(data)
    cpgs['total'] = cpgs['total'] +1
 
    return  make_response("", 200)

@app.route('/api/v1/cpgs', methods=['GET'])
def get_cpgs():
    debugRequest(request)
    
    #should get it from global cpgs 
    resp = make_response(json.dumps(cpgs), 200)
    return resp

@app.route('/api/v1/cpgs/<cpg_name>', methods=['GET'])
def get_cpg(cpg_name):
    debugRequest(request)
    
    for cpg in cpgs['members']:
        if cpg['name'] == cpg_name:
            resp = make_response(json.dumps(cpg), 200)
            return resp
        
    throw_error(404, 'NON_EXISTENT_CPG', "CPG '%s' doesn't exist" % cpg_name)

@app.route('/api/v1/cpgs/<cpg_name>', methods=['DELETE'])
def delete_cpg(cpg_name):
    debugRequest(request)
    
    for cpg in cpgs['members']:
        if cpg['name'] == cpg_name:
            cpgs['members'].remove(cpg)
            return make_response("", 200)            

    throw_error(404, 'NON_EXISTENT_CPG', "CPG '%s' doesn't exist" % cpg_name)


#### Host ####

@app.route('/api/v1/hosts', methods=['POST'])
def create_hosts():
    debugRequest(request)  
    data = json.loads(request.data)

    valid_members = ['FCWWNs', 'descriptors', 'domain', 'iSCSINames', 'id','name']

    for member_key in data.keys() :
        if member_key not in valid_members :
            throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % member_key)

    if data['name'] is None:
        throw_error(400,'INV_INPUT_MISSING_REQUIRED', 'Name not specified.')

    elif len(data['name']) > 31:
        throw_error(400, 'INV_INPUT_EXCEEDS_LENGTH', 'Host name is too long.')

    elif 'domain' in data and len(data['domain']) > 31:
        throw_error(400, 'INV_INPUT_EXCEEDS_LENGTH', 'Domain name is too long.')

    elif 'domain' in data and data['domain'] == '':
        throw_error(400,'INV_INPUT_EMPTY_STR',
                    'Input string (for domain, iSCSI etc.) is empty.')        

    charset = {'!', '@', '#', '$', '%', '&', '^'}
    for char in charset:
        if char in data['name']:
            throw_error(400, 'INV_INPUT_ILLEGAL_CHAR',
                        'Error parsing host-name or domain-name')

        elif 'domain' in data and char in data['domain']:
            throw_error(400, 'INV_INPUT_ILLEGAL_CHAR',
                        'Error parsing host-name or domain-name')

    if 'FCWWNs' in data.keys():
        if 'iSCSINames' in data.keys():
            throw_error(400, 'INV_INPUT_PARAM_CONFLICT',
                        'FCWWNS and iSCSINames are both specified.')

    if 'FCWWNs' in data.keys():
        fc = data['FCWWNs']
        for wwn in fc :
            if len(wwn.replace(':','')) <> 16 : 
                throw_error(400, 'INV_INPUT_WRONG_TYPE',
                            'Length of WWN is not 16.')

    if 'FCWWNs' in data:
        for host in hosts ['members']:
            if 'FCWWNs' in host:
                for fc_path in data['FCWWNs']:
                    if fc_path in host['FCWWNs']:
                        throw_error(409, 'EXISTENT_PATH', 'WWN already claimed by other host.')

    if 'iSCSINames' in data:
        for host in hosts:
            if 'iSCSINames' in host:
                for iqn in data['iSCSINames']:
                    if iqn in host['iSCSINames']:
                        throw_error(409, 'EXISTENT_PATH', 'iSCSI name already claimed by other host.')

    for host in hosts['members'] :
        if data['name'] == host['name'] :
            throw_error(409, 'EXISTENT_HOST', "HOST '%s' already exist." % data['name'])

    hosts['members'].append(data)
    hosts['total'] = hosts['total'] +1

    resp = make_response("", 201)
    return resp

@app.route('/api/v1/hosts/<host_name>', methods=['PUT'])
def modify_host(host_name):
    debugRequest(request)  
    data = json.loads(request.data)

    if host_name == 'None':
        throw_error (404, 'INV_INPUT', 'Missing host name.')

    if 'FCWWNs' in data.keys():
        if 'iSCSINames' in data.keys():
            throw_error(400, 'INV_INPUT_PARAM_CONFLICT',
                        'FCWWNS and iSCSINames are both specified.')
        elif 'pathOperation' not in data.keys():
            throw_error(400, 'INV_INPUT_ONE_REQUIRED',
                        'pathOperation is missing and WWN is specified.')

    if 'iSCSINames' in data.keys():
        if 'pathOperation' not in data.keys():
            throw_error(400, 'INV_INPUT_ONE_REQUIRED',
                        'pathOperation is missing and iSCSI Name is specified.')

    if 'newName' in data.keys():
        charset = {'!', '@', '#', '$', '%', '&', '^'}
        for char in charset:
            if char in data['newName']:
                throw_error(400, 'INV_INPUT_ILLEGAL_CHAR',
                            'Error parsing host-name or domain-name')
        if len(data['newName']) > 32:
            throw_error(400, 'INV_INPUT_EXCEEDS_LENGTH',
                        'New host name is too long.')
        for host in hosts['members']:
            if host['name'] == data['newName']:
                throw_error(409, 'EXISTENT_HOST',
                            'New host name is already used.')

    if 'pathOperation' in data.keys():
        if 'iSCSINames' in data.keys():
            for host in hosts['members']:
                if host['name'] == host_name:
                    if data['pathOperation'] == 1:
                        for host in hosts['members']:
                            if 'iSCSINames' in host.keys():
                                for path in data['iSCSINames']:
                                    for h_paths in host['iSCSINames']:
                                        if path == h_paths:
                                            throw_error(409, 'EXISTENT_PATH',
                                                        'iSCSI name is already claimed by other host.')
                        for path in data['iSCSINames']:
                            host['iSCSINames'].append(path)
                        resp = make_response(json.dumps(host), 200)
                        return resp
                    elif data['pathOperation'] == 2:
                        for path in data['iSCSINames']:
                            for h_paths in host['iSCSINames']:
                                if path == h_paths:
                                    host['iSCSINames'].remove(h_paths)
                                    resp = make_response(json.dumps(host), 200)
                                    return resp
                            throw_error(404, 'NON_EXISTENT_PATH',
                                        'Removing a non-existent path.')
                    else:
                        throw_error(400, 'INV_INPUT_BAD_ENUM_VALUE',
                                    'pathOperation: Invalid enum value.')
            throw_error(404, 'NON_EXISTENT_HOST',
                        'Host to be modified does not exist.')
        elif 'FCWWNs' in data.keys():
            for host in hosts['members']:
                if host['name'] == host_name:
                    if data['pathOperation'] == 1:
                        for host in hosts['members']:
                            if 'FCWWNs' in host.keys():
                                for path in data['FCWWNs']:
                                    for h_paths in host['FCWWNs']:
                                        if path == h_paths:
                                            throw_error(409, 'EXISTENT_PATH',
                                                        'WWN is already claimed by other host.')
                        for path in data['FCWWNs']:
                            host['FCWWNs'].append(path)
                        resp = make_response(json.dumps(host), 200)
                        return resp
                    elif data['pathOperation'] == 2:
                        for path in data['FCWWNs']:
                            for h_paths in host['FCWWNs']:
                                if path == h_paths:
                                    host['FCWWNs'].remove(h_paths)
                                    resp = make_response(json.dumps(host), 200)
                                    return resp
                            throw_error(404, 'NON_EXISTENT_PATH',
                                        'Removing a non-existent path.')
                    else:
                        throw_error(400, 'INV_INPUT_BAD_ENUM_VALUE',
                                    'pathOperation: Invalid enum value.')
            throw_error(404, 'NON_EXISTENT_HOST',
                        'Host to be modified does not exist.')
        else:
            throw_error(400, 'INV_INPUT_ONE_REQUIRED',
                        'pathOperation specified and no WWNs or iSCSNames specified.')

    for host in hosts['members']:
        if host['name'] == host_name:
            for member_key in data.keys() :
                if member_key == 'newName':
                    host['name'] = data['newName']
                else:
                    host[member_key] = data[member_key]            
            resp = make_response(json.dumps(host), 200)
            return resp

    throw_error(404, 'NON_EXISTENT_HOST',
                'Host to be modified does not exist.')

@app.route('/api/v1/hosts/<host_name>', methods=['DELETE'])
def delete_host(host_name):
    debugRequest(request)

    for host in hosts['members']:
        if host['name'] == host_name:
            hosts['members'].remove(host)
            return make_response("", 200)    

    throw_error(404, 'NON_EXISTENT_HOST', "The host '%s' doesn't exist" % host_name)

@app.route('/api/v1/hosts', methods=['GET'])
def get_hosts():
    debugRequest(request)
    resp = make_response(json.dumps(hosts), 200)
    return resp

@app.route('/api/v1/hosts/<host_name>', methods=['GET'])
def get_host(host_name):
    debugRequest(request)
    charset = {'!', '@', '#', '$', '%', '&', '^'}
    for char in charset:
        if char in host_name:
            throw_error(400, 'INV_INPUT_ILLEGAL_CHAR',
                        'Host name contains invalid character.')

    if host_name == 'InvalidURI':
        throw_error(400, 'INV_INPUT', 'Invalid URI Syntax.') 

    for host in hosts['members']:
        if host['name'] == host_name:
            
            if 'iSCSINames' in host.keys():
                iscsi_paths = []
                for path in host['iSCSINames']:
                    iscsi_paths.append({'name': path})
                host['iSCSIPaths'] = iscsi_paths

            elif 'FCWWNs' in host.keys():
                fc_paths = []
                for path in host['FCWWNs']:
                    fc_paths.append({'wwn': path.replace(':', '')})
                host['FCPaths'] = fc_paths

            resp = make_response(json.dumps(host), 200)
            return resp

    throw_error(404, 'NON_EXISTENT_HOST', "Host '%s' doesn't exist" % host_name)

#### Port ####

@app.route('/api/v1/ports', methods=['GET'])
def get_ports():
    debugRequest(request)
    resp = make_response(json.dumps(ports), 200)
    return resp

#### VLUN ####

@app.route('/api/v1/vluns', methods=['POST'])
def create_vluns():
    debugRequest(request)
    data = json.loads(request.data)

    valid_keys = {'volumeName':None, 'lun':0, 'hostname':None, 'portPos':None,
                  'noVcn': False, 'overrideLowerPriority':False}

    valid_port_keys = {'node':1, 'slot':1, 'cardPort':0}

    ## do some fake errors here depending on data
    for key in data.keys():
        if key not in valid_keys.keys():
            throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % key) 
        elif 'portPos' in data.keys():
            portP = data ['portPos']
            for subkey in portP.keys():
                if subkey not in valid_port_keys:
                    throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % subkey)

    if 'lun' in data:
        if data['lun'] > 16384:
            throw_error(400, 'TOO_LARGE', 'LUN is greater than 16384.')
    else:
        throw_error(400, 'INV_INPUT', 'Missing LUN.')

    if 'volumeName' not in data:
        throw_error(400, 'INV_INPUT_MISSING_REQUIRED', 'Missing volumeName.')
    else:
        for volume in volumes['members']:
            if volume['name'] == data['volumeName']:
                vluns['members'].append(data)
                resp = make_response(json.dumps(vluns), 201)
                resp.headers['location'] = '/api/v1/vluns/'
                return resp
        throw_error(404, 'NON_EXISTENT_VOL', 'Specified volume does not exist.')

@app.route('/api/v1/vluns/<vlun_str>', methods=['DELETE'])
def delete_vluns(vlun_str):
    #<vlun_str> is like volumeName,lun,host,node:slot:port
    debugRequest(request)

    params = vlun_str.split(',')
    for vlun in vluns['members']:
        if vlun['volumeName'] == params[0] and vlun['lun'] == int(params[1]):
            if len(params) == 4:
                if str(params[2]) != vlun['hostname']:
                    throw_error(404, 'NON_EXISTENT_HOST', "The host '%s' doesn't exist" % params[2])

                print vlun['portPos']
                port = getPort(vlun['portPos'])
                if not port == params[3]:
                    throw_error(400, 'INV_INPUT_PORT_SPECIFICATION', "Specified port is invalid %s" % params[3])

            elif len(params) == 3:
                if ':' in params[2]:
                    port = getPort(vlun['portPos'])
                    if not port == params[2]:
                        throw_error(400, 'INV_INPUT_PORT_SPECIFICATION', "Specified port is invalid %s" % params[2])

                else:
                    if str(params[2]) != vlun['hostname']:
                        throw_error(404, 'NON_EXISTENT_HOST', "The host '%s' doesn't exist" % params[2])

            vluns['members'].remove(vlun)
            return make_response(json.dumps(params), 200)

    throw_error(404, 'NON_EXISTENT_VLUN', "The volume '%s' doesn't exist" % vluns)

def getPort(portPos):
    port = "%s:%s:%s" % (portPos['node'], portPos['slot'], portPos['cardPort'])
    print port
    return port

@app.route('/api/v1/vluns', methods=['GET'])
def get_vluns():
    debugRequest(request)
    resp = make_response(json.dumps(vluns), 200)
    return resp


#### VOLUMES & SNAPSHOTS ####

@app.route('/api/v1/volumes/<volume_name>', methods=['POST'])
def create_snapshot(volume_name):
    debugRequest(request)
    data = json.loads(request.data)

    valid_keys = {'action': None, 'parameters': None}
    valid_parm_keys = {'name':None, 'id':None, 'comment': None,
                       'readOnly':None, 'expirationHours': None,
                       'retentionHours':None}

    ## do some fake errors here depending on data
    for key in data.keys():
        if key not in valid_keys.keys():
            throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % key)
        elif 'parameters' in data.keys():
            parm = data ['parameters']
            for subkey in parm.keys():
                if subkey not in valid_parm_keys:
                    throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % subkey)

    for volume in volumes['members']:
        if volume['name'] == volume_name:
            volumes['members'].append({'name': data['parameters'].get('name')})
            resp = make_response(json.dumps(volume), 200)
            return resp

    throw_error(404, 'NON_EXISTENT_VOL', "volume doesn't exist")

@app.route('/api/v1/volumes', methods=['POST'])
def create_volumes():
    debugRequest(request)
    data = json.loads(request.data)

    valid_keys = {'name':None, 'cpg':None, 'sizeMiB':None, 'id':None,
                  'comment':None, 'policies':None, 'snapCPG':None,
                  'ssSpcAllocWarningPct': None, 'ssSpcAllocLimitPct': None,
                  'tpvv':None, 'usrSpcAllocWarningPct':None,
                  'usrSpcAllocLimitPct': None, 'isCopy':None,
                  'copyOfName':None, 'copyRO':None, 'expirationHours': None,
                  'retentionHours':None}

    for key in data.keys():
        if key not in valid_keys.keys():
            throw_error(400, 'INV_INPUT', "Invalid Parameter '%s'" % key)

    if 'name' in data.keys():
        for vol in volumes['members']:
            if vol['name'] == data['name']:
                throw_error(409, 'EXISTENT_VOL',
                            'The volume already exists.')
        if len(data['name']) > 31:
            throw_error(400, 'INV_INPUT_EXCEEDS_LENGTH', 'Invalid Input: String length exceeds limit : Name')
    else:
        throw_error(400, 'INV_INPUT',
                    'No volume name provided.')

    if 'sizeMiB' in data.keys():
        if data['sizeMiB'] < 256:
            throw_error(400, 'TOO_SMALL',
                        'Minimum volume size is 256 MiB')
        elif data['sizeMiB'] > 16777216:
            throw_error(400, 'TOO_LARGE',
                        'Volume size is above architectural limit : 16TiB')

    if 'id' in data.keys():
        for vol in volumes['members']:
            if vol['id'] == data['id']:
                throw_error(409, 'EXISTENT_ID', 'Specified volume ID already exists.')

    volumes['members'].append(data)
    return  make_response("", 200)

@app.route('/api/v1/volumes/<volume_name>', methods=['DELETE'])
def delete_volumes(volume_name):
    debugRequest(request)

    for volume in volumes['members']:
        if volume['name'] == volume_name:
            volumes['members'].remove(volume)
            return make_response("", 200)

    throw_error(404, 'NON_EXISTENT_VOL', "The volume '%s' does not exists." % volume_name)

@app.route('/api/v1/volumes', methods=['GET'])
def get_volumes():
    debugRequest(request)
    resp = make_response(json.dumps(volumes), 200)
    return resp

@app.route('/api/v1/volumes/<volume_name>', methods=['GET'])
def get_volume(volume_name):
    debugRequest(request)

    charset = {'!', '@', '#', '$', '%', '&', '^'}
    for char in charset:
        if char in volume_name:
            throw_error(400, 'INV_INPUT_ILLEGAL_CHAR',
                        'Invalid character for volume name.')

    for volume in volumes['members']:
        if volume['name'] == volume_name:
            resp = make_response(json.dumps(volume), 200)
            return resp

    throw_error(404, 'NON_EXISTENT_VOL', "volume doesn't exist")

@app.route('/api', methods=['GET'])
def get_version():
    debugRequest(request)
    version = {'major': 1,
               'minor': 2,
               'build': 30102422}
    resp = make_response(json.dumps(version), 200)
    return resp

if __name__ == "__main__":

    #fake 2 CPGs
    global cpgs
    cpgs = {'members':
           [{'SAGrowth': {'LDLayout': {'diskPatterns': [{'diskType': 1}]},
                         'incrementMiB': 8192},
            'SAUsage': {'rawTotalMiB': 24576,
                         'rawUsedMiB': 768,
                         'totalMiB': 8192,
                         'usedMiB': 256},
            'SDGrowth': {'LDLayout': {'diskPatterns': [{'diskType': 1}]},
                         'incrementMiB': 16384,
                         'limitMiB': 256000,
                         'warningMiB': 204800},
            'SDUsage': {'rawTotalMiB': 32768,
                        'rawUsedMiB': 2048,
                        'totalMiB': 16384,
                        'usedMiB': 1024},
            'UsrUsage': {'rawTotalMiB': 239616,
                         'rawUsedMiB': 229376,
                         'totalMiB': 119808,
                         'usedMiB': 114688},
            'additionalStates': [],
            'degradedStates': [],
            'domain': 'UNIT_TEST',
            'failedStates': [],
            'id': 0,
            'name': 'UnitTestCPG',
            'numFPVVs': 12,
            'numTPVVs': 0,
            'state': 1,
            'uuid': 'f9b018cc-7cb6-4358-a0bf-93243f853d96'},
           {'SAGrowth': {'LDLayout': {'diskPatterns': [{'diskType': 1}]},
                          'incrementMiB': 8192},
             'SAUsage': {'rawTotalMiB': 24576,
                         'rawUsedMiB': 768,
                         'totalMiB': 8192,
                         'usedMiB': 256},
             'SDGrowth': {'LDLayout': {'diskPatterns': [{'diskType': 1}]},
                          'incrementMiB': 16384,
                          'limitMiB': 256000,
                          'warningMiB': 204800},
             'SDUsage': {'rawTotalMiB': 32768,
                         'rawUsedMiB': 2048,
                         'totalMiB': 16384,
                         'usedMiB': 1024},
             'UsrUsage': {'rawTotalMiB': 239616,
                          'rawUsedMiB': 229376,
                          'totalMiB': 119808,
                          'usedMiB': 114688},
             'additionalStates': [],
             'degradedStates': [],
             'domain': 'UNIT_TEST',
             'failedStates': [],
             'id': 0,
             'name': 'UnitTestCPG2',
             'numFPVVs': 12,
             'numTPVVs': 0,
             'state': 1,
             'uuid': 'f9b018cc-7cb6-4358-a0bf-93243f853d97'}],
      'total': 2}

    #fake  volumes
    global volumes
    volumes = {'members':
               [{'additionalStates': [],
                 'adminSpace': {'freeMiB': 0,
                                'rawReservedMiB': 384,
                                'reservedMiB': 128,
                                'usedMiB': 128},
                 'baseId': 1,
                 'copyType': 1,
                 'creationTime8601': u'2012-09-24T15:12:13-07:00',
                 'creationTimeSec': 1348524733,
                 'degradedStates': [],
                 'domain': 'UNIT_TEST',
                 'failedStates': [],
                 'id': 91,
                 'name': 'UnitTestVolume',
                 'policies': {'caching': True,
                              'oneHost': False,
                              'staleSS': True,
                              'system': False,
                              'zeroDetect': False},
                 'provisioningType': 1,
                 'readOnly': False,
                 'sizeMiB': 102400,
                 'snapCPG': 'UnitTestCPG',
                 'snapshotSpace': {'freeMiB': 0,
                                   'rawReservedMiB': 1024,
                                   'reservedMiB': 512,
                                   'usedMiB': 512},
                 'ssSpcAllocLimitPct': 0,
                 'ssSpcAllocWarningPct': 95,
                 'state': 1,
                 'userCPG': 'UnitTestCPG',
                 'userSpace': {'freeMiB': 0,
                               'rawReservedMiB': 204800,
                                'reservedMiB': 102400,
                 'usedMiB': 102400},
                 'usrSpcAllocLimitPct': 0,
                 'usrSpcAllocWarningPct': 0,
                 'uuid': '8bc9394e-f87a-4c1a-8777-11cba75af94c',
                 'wwn': '50002AC00001383D'},
                {'additionalStates': [],
                 'adminSpace': {'freeMiB': 0,
                                'rawReservedMiB': 384,
                                'reservedMiB': 128,
                                'usedMiB': 128},
                 'baseId': 41,
                 'comment': 'test volume',
                 'copyType': 1,
                 'creationTime8601': '2012-09-27T14:11:56-07:00',
                 'creationTimeSec': 1348780316,
                 'degradedStates': [],
                 'domain': 'UNIT_TEST',
                 'failedStates': [],
                 'id': 92,
                 'name': 'UnitTestVolume2',
                 'policies': {'caching': True,
                              'oneHost': False,
                              'staleSS': True,
                              'system': False,
                              'zeroDetect': False},
                 'provisioningType': 1,
                 'readOnly': False,
                 'sizeMiB': 10240,
                 'snapCPG': 'UnitTestCPG',
                 'snapshotSpace': {'freeMiB': 0,
                                   'rawReservedMiB': 1024,
                                   'reservedMiB': 512,
                                   'usedMiB': 512},
                 'ssSpcAllocLimitPct': 0,
                 'ssSpcAllocWarningPct': 0,
                 'state': 1,
                 'userCPG': 'UnitTestCPG',
                 'userSpace': {'freeMiB': 0,
                               'rawReservedMiB': 20480,
                               'reservedMiB': 10240,
                               'usedMiB': 10240},
                 'usrSpcAllocLimitPct': 0,
                 'usrSpcAllocWarningPct': 0,
                 'uuid': '6d5542b2-f06a-4788-879e-853ad0a3be42',
                 'wwn': '50002AC00029383D'}],
              'total': 26}

    #fake ports
    global ports
    ports = {'members':
             [{'linkState': 4,
               'mode': 2,
               'nodeWwn': None,
               'portPos': {'cardPort': 1, 'node': 1, 'slot': 7},
               'portWwn': '2C27D75375D5',
               'protocol': 2,
               'type': 7},
              {'linkState': 4,
               'mode': 2,
               'nodeWwn': None,
               'portPos': {'cardPort': 2, 'node': 2, 'slot': 8},
               'portWwn': '2C27D75375D6',
               'protocol': 2,
               'type': 7},
              {'linkState': 4,
               'mode': 2,
               'nodeWwn': None,
               'portPos': {'cardPort': 3, 'node': 3, 'slot': 5},
               'portWwn': '2C27D75375D7',
               'protocol': 1,
               'type': 7},
              {'linkState': 4,
               'mode': 2,
               'nodeWwn': None,
               'portPos': {'cardPort': 4, 'node': 4, 'slot': 6},
               'portWwn': '2C27D75375D8',
               'protocol': 1,
               'type': 7}],
            'total': 4}

    #fake hosts
    global hosts
    hosts = {'members':
             [{'FCWWNs': [],
               'descriptors': None,
               'domain': 'UNIT_TEST',
               'iSCSINames': [{'driverVersion': '1.0',
                               'firmwareVersion': '1.0',
                               'hostSpeed': 100,
                               'ipAddr': '10.10.221.59',
                               'model': 'TestModel',
                               'name': 'iqnTestName',
                               'portPos': {'cardPort': 1, 'node': 1,
                                           'slot': 8},
                               'vendor': 'HP'}],
               'id': 11,
               'name': 'UnitTestHost'},
              {'FCWWNs': [],
               'descriptors': None,
               'domain': 'UNIT_TEST',
               'iSCSINames': [{'driverVersion': '1.0',
                               'firmwareVersion': '1.0',
                               'hostSpeed': 100,
                               'ipAddr': '10.10.221.58',
                               'model': 'TestMode2',
                               'name': 'iqnTestName2',
                               'portPos': {'cardPort': 1, 'node': 1,
                                           'slot': 8},
                               'vendor': 'HP'}],
               'id': 12,
               'name': 'UnitTestHost2'}],
            'total': 2}     

    #fake create vluns
    global vluns
    vluns = {'members':
             [{'active': True,
               'failedPathInterval': 0,
               'failedPathPol': 1,
               'hostname': 'UnitTestHost',
               'lun': 31,
               'multipathing': 1,
               'portPos': {'cardPort': 1, 'node': 1, 'slot': 2},
               'remoteName': '100010604B0174F1',
               'type': 4,
               'volumeName': 'UnitTestVolume',
               'volumeWWN': '50002AC00001383D'}, 
              {'active': False,
               'failedPathInterval': 0,
               'failedPathPol': 1,
               'hostname': 'UnitTestHost2',
               'lun': 32,
               'multipathing': 1,
               'portPos': {'cardPort': 2, 'node': 2, 'slot': 3},
               'type': 3,
               'volumeName': 'UnitTestVolume2',
               'volumeWWN': '50002AC00029383D'}],
            'total': 2}

    app.run(port=args.port, debug=debugRequests)