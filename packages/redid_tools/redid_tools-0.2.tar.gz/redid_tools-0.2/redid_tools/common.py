"""
	Common handling in CLI tools
"""
from __future__ import print_function

import os, yaml, base64, requests, sys, json, urllib, mimetypes

api_endpoint = 'https://api.redid.net'

# Extra mappings for special Redid formats/missing ones
redid_type_map = {
	'.webp': 'image/webp',
	'.9.png': 'image/x-redid-9patch',
	'.gradient.yaml': 'image/x-redid-gradient',
}
def guess_mime_type( filename ):
	""" 
		Guess a content-type for the given filename 
		
		@return: ( content-type, extension )
	"""
	for k,v in redid_type_map.iteritems():
		if filename.endswith( k ):
			return ( v, k )
			
	base, ext = os.path.splitext( filename )
	ct, enc = mimetypes.guess_type( filename, strict = False )
	if ct == None:
		ct = 'application/octet-stream'
	return ( ct, ext )
	
def log( *args ):
	""" Do not use "print" to output log/trace/verbose info as it will interfere with the stdout. """
	print( *args, file = sys.stderr )

	
def add_config_args( opts ):
	""" Add common configuration arguments to ArgumentParster """
	opts.add_argument( "--config", help = "use this configuration file", 
		default= os.environ.get( 'REDID_CONFIG_FILE', "~/.redid.yaml" ) )
	
def load_config( args ):
	args.config = os.path.expanduser( args.config )
	path = args.config
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
		log( "Missing access settings in configuration <{}>".format( path ) )
		return None
		
	return data

def escape_cli( string ):
	return "\"" + string.replace( "\"", "\\\"" ) + "\""

def api_request( method, path, json_data = None, data = None, query_string = None, headers = None,
	config = None, verbose = False, show_curl = False, data_file = None ):
	"""
		Issue a request to the API server for the account.
	"""
	# allow config to override (for local testing)
	endpoint = config.get( 'api_endpoint', api_endpoint )
	
	path = "/{}/{}".format( config['access']['account'], path )
	
	if headers == None:
		headers = {}
		
	if json_data != None:
		assert data == None
		data = json.dumps( json_data )
		headers['Content-Type'] = 'application/json'
		
	if data_file != None:
		with open( data_file, 'rb') as fp:
			data = fp.read()

	if verbose:
		log( '{} {} {}'.format( method, endpoint + path, str(query_string) ) )
		
	if show_curl:
		if query_string != None:
			qs = "&".join( [ urllib.quote(k) + ('=' + urllib.quote(v) if v != None else '')
				for k,v in query_string.iteritems() 
			] )
			if len(qs):
				qs = '?' + qs
		else:
			qs = ''
			
		cmd = "curl -X {method} {url} --user {user} {headers}".format(
			method = method,
			url = escape_cli(endpoint + path + qs ),
			user = escape_cli( config['access']['user'] + ':' + config['access']['password'] ),
			headers = " ".join( [ '-H ' + escape_cli('{}: {}'.format( k, v )) for k, v in headers.iteritems() ] ),
		) 
		if data_file != None:
			cmd += " --data-binary {}".format( escape_cli( '@' + data_file ) )
		elif data != None:
			cmd += " --data {}".format( escape_cli(data) )
		log( cmd )
			
	headers['Authorization'] = 'Basic ' + base64.b64encode( "{}:{}".format(
		config['access']['user'], config['access']['password'] ) )
	resp = requests.request( method, endpoint + path, headers = headers, data = data,
		params = query_string )
	
	jdata = None
	if resp.headers.get( 'Content-Type', None ) == 'application/json':
		jdata = resp.json()
		
	if resp.status_code != 200:
		log( "Failed with HTTP status {}".format( resp.status_code ) )
		if jdata != None:
			show_data( jdata )
		return None

	if jdata != None:
		return jdata
	return resp.content

	
def show_data( data, binary = False ):
	""" Display data on stdout."""
	if binary:
		sys.stdout.write( data )
	else:
		print( yaml.safe_dump( data, allow_unicode=True, default_flow_style = False ) )
	