"""
	Common handling in CLI tools
"""
from __future__ import print_function

import os, yaml, base64, requests, sys

api_endpoint = 'https://api.redid.net'

def log( *args ):
	""" Do not use "print" to output log/trace/verbose info as it will interfere with the stdout. """
	print( *args, file = sys.stderr )

	
def add_config_args( opts ):
	""" Add common configuration arguments to ArgumentParster """
	opts.add_argument( "--config", help = "use this configuration file", default="~/.redid.yaml" )
	
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

	
def api_request( method, path, json_data = None, data = None, query_string = None, headers = None,
	config = None, verbose = False ):
	"""
		Issue a request to the API server for the account.
	"""
	path = "/{}/{}".format( config['access']['account'], path )
	
	if headers == None:
		headers = {}
	headers['Authorization'] = 'Basic ' + base64.b64encode( "{}:{}".format(
		config['access']['user'], config['access']['password'] ) )
		
	if json_data != None:
		assert data == None
		data = json.dumps( json_data )
		headers['Content-Type'] = 'application/json'

	if verbose:
		log( '{} {} {}'.format( method, api_endpoint + path, str(query_string) ) )
	resp = requests.request( method, api_endpoint + path, headers = headers, data = data,
		params = query_string )
	
	jdata = None
	if resp.headers['Content-Type'] == 'application/json':
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
	