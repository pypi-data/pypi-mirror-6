"""
	Redid CLI tools entry point.
"""
import sys, os, yaml, argparse, requests, base64, json

# TODO: Switch to HTTPS once setup
api_endpoint = 'http://api.redid.net'
verbose = False
config = None

def load_config( path ):
	if not os.path.exists( path ):
		return None
			
	data = yaml.load( file( path, 'r' ) )
	if 'access' not in data:
		data['access'] = {}

	# Environment overrides
	account = os.environ.get( 'REDID_ACCOUNT', None )
	user = os.environ.get( 'REDID_USER', None )
	password = os.environ.get( 'REDID_PASSWORD', None )

	if account != None:
		data['access']['account'] = account
	if user != None:
		data['access']['user'] = user
	if password != None:
		data['access']['password'] = password

	if data['access']['account'] == None or \
		data['access']['user'] == None or \
		data['access']['password'] == None:
		print( "Missing access settings in configuration <{}>".format( path ) )
		return None
		
	return data

	
def cmd_setup( args ):
	""" Create/Update the configuration file """
	config = load_config( args.config )
	if config == None:
		config = {}
	if 'access' not in config:
		config['access'] = {}
		
	config['access']['account'] = raw_input( "Redid account: " )
	config['access']['user'] = raw_input( "Redid user name: " )
	config['access']['password'] = raw_input( "Redid password: " )
	
	yaml.safe_dump( config, stream = file(args.config,'w'), encoding='utf-8', allow_unicode=True,
		default_flow_style = False )
	print( "Configuration <{}> updated.".format( args.config ) )

	
def cmd_show_config( args ):
	show_data( config )
	
	
def cmd_check_auth( args ):
	r = api_request( 'GET', 'check-auth' )
	show_data( r )

	
def cmd_get_profile( args ):
	r = api_request( 'GET', 'profile/' + args.profile )
	if r == None:
		sys.exit(1)
	if args.save != None:
		save_data( r['data'], args.save )
	else:
		show_data( r['data'] )
	
	
def cmd_put_profile( args ):
	profile = args.profile
	if profile == None:
		profile = os.path.splitext( os.path.basename( args.load ) )[0]
		
	data = load_data( args.load )
	api_request( 'PUT', 'profile/' + profile, json_data = data )
	
	
def cmd_delete_profile( args ):
	api_request( 'DELETE', 'profile/' + args.profile )

	
def main():
	opts = argparse.ArgumentParser()
	opts.add_argument( "--config", help = "use this configuration file", default="~/.redid.yaml" )
	opts.add_argument( "--verbose", help = "show verbose output", action='store_const', const = True )
	sub = opts.add_subparsers( help = 'command help', title = "Commands", dest = 'command' )
	
	def add_local( name, help ):
		o = sub.add_parser( name, help = help )
		o.set_defaults( func = globals()['cmd_' + name.replace( '-', '_' )] )
		return o
		
	add_local( 'setup', "configure Redid CLI tools" )

	add_local( 'show-config', "dump the Redid CLI configuration" )
	
	add_local( 'check-auth', "check Redid access/authorization" )
	
	o = add_local( 'get-profile', "get a profile by name" )
	o.add_argument( "profile" )
	o.add_argument( "save", help = "save the the profile to this file instead of displaying",
		nargs = "?" )
		
	o = add_local( 'put-profile', 'create/update a profile' )
	o.add_argument( 'load', help = 'filename of the profile to upload' )
	o.add_argument( 'profile', help = 'name of profile, if not specified basename of file is used',
		nargs = '?' )
		
	o = add_local( 'delete-profile', 'delete a profile' )
	o.add_argument( 'profile', help = 'name of the profile to delete' )
	
	args = opts.parse_args()
	global verbose
	verbose = args.verbose
	args.config = os.path.expanduser( args.config )
	
	if args.command == 'setup':
		args.func( args )
	else:
		global config
		config = load_config( args.config )
		if config == None:
			print( "Unable to load configuration. Please run 'redid setup' " )
			sys.exit(1)
		args.func( args )

		
def api_request( method, path, json_data = None ):
	"""
		Issue a request to the API server for the account.
	"""
	path = "/{}/{}".format( config['access']['account'], path )
	
	headers = {}
	headers['Authorization'] = 'Basic ' + base64.b64encode( "{}:{}".format(
		config['access']['user'], config['access']['password'] ) )
		
	data = None
	if json_data != None:
		data = json.dumps( json_data )
		headers['Content-Type'] = 'application/json'

	if verbose:
		print( '{} {}'.format( method, api_endpoint + path ) )
	resp = requests.request( method, api_endpoint + path, headers = headers, data = data )
	
	jdata = None
	if resp.headers['Content-Type'] == 'application/json':
		jdata = resp.json()
		
	if resp.status_code != 200:
		print( "Failed with HTTP status {}".format( resp.status_code ) )
		if jdata != None:
			print( "Status: {}".format( jdata['status'] ) )
		return None

	if jdata != None:
		return jdata
	return resp.data
	
def show_data( data ):
	print( yaml.safe_dump( data, allow_unicode=True, default_flow_style = False ) )

def save_data( data, filename ):
	if filename.endswith( '.yaml' ):
		yaml.safe_dump( data, stream = file(filename,'w'), allow_unicode=True, 
			default_flow_style = False, indent = 4 )
	elif filename.endswith( '.json' ):
		json.dump( data, file( filename,'w'), indent = 4 )
	else:
		raise Exception( "unknown-file-type: " + filename )
		
def load_data( filename ):
	if filename.endswith( '.yaml' ):
		return yaml.load( file( filename, 'r' ) )
	elif filename.endswith( '.json' ):
		return json.load( file( filename, 'r' ) )
	else:
		raise Exception( "unknown-file-type: " + filename )
