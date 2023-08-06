"""
	Redid CLI tools entry point.
"""
import sys, os, yaml, argparse, json, mimetypes, urllib

from common import log
import common

verbose = False
config = None
	
def cmd_setup( args ):
	""" Create/Update the configuration file """
	config = common.load_config( args )
	if config == None:
		config = {}
	if 'access' not in config:
		config['access'] = {}
		
	config['access']['account'] = raw_input( "Redid account: " )
	config['access']['user'] = raw_input( "Redid user name: " )
	config['access']['password'] = raw_input( "Redid password: " )
	
	yaml.safe_dump( config, stream = file(args.config,'w'), encoding='utf-8', allow_unicode=True,
		default_flow_style = False )
	log( "Configuration <{}> updated.".format( args.config ) )

	
def cmd_show_config( args ):
	return handle_object_response( args, { 'data': config } )
	
	
def cmd_check_auth( args ):
	r = api_request( 'GET', 'check-auth' )
	return handle_object_response( args, r )

	
def cmd_get_profile( args ):
	r = api_request( 'GET', 'profile/' + args.profile )
	if r == None:
		sys.exit(1)
	return handle_object_response( args, r )
	
	
def cmd_put_profile( args ):
	profile = args.profile
	if profile == None:
		profile = os.path.splitext( os.path.basename( args.load ) )[0]
		
	data = load_data( args.load )
	r = api_request( 'PUT', 'profile/' + profile, json_data = data )
	return handle_object_response( args, r )
	
def cmd_delete_profile( args ):
	r = api_request( 'DELETE', 'profile/' + args.profile )
	return handle_object_response( args, r )

	
def cmd_get_profile_signature( args ):
	r = api_request( 'GET', 'profile-signature/' + args.profile )
	return handle_object_response( args, r )
	
	
def cmd_list_profiles( args ):
	profiles = []
	r = api_request( 'GET', 'profile-list' )
	if r == None:
		return False
	profiles = profiles + r['data']

	while 'next' in r:
		r = api_request( 'GET', 'profile-list', query_string = { 'next': r['next'] } )
		if r == None:
			return False
		profiles = profiles + r['data']
	
	if args.full:
		mapped = { p['name']: p for p in profiles }
		handle_data( args, mapped )
	else:
		names = [ p['name'] for p in profiles ]
		handle_data( args, names )
	return True
	
def cmd_list_resources( args ):
	query = {}
	if args.sha256 != None:
		query['sha256'] = args.sha256
	if args.name_prefix != None:
		query['name_prefix'] = args.name_prefix
		
	resources = []
	r = api_request( 'GET', 'resource-list', query_string = query )
	if r == None:
		return False
	resources = resources + r['data']

	while 'next' in r:
		query['next'] = r['next']
		r = api_request( 'GET', 'resource-list', query_string = query )
		if r == None:
			return False
		resources = resources + r['data']
		
	if args.full:
		mapped = { (r['name'] if 'name' in r else r['id']): r for r in resources  }
		handle_data( args, mapped )
	else:
		names = sorted( [ (r['name'] if 'name' in r else r['id']) for r in resources ] )
		handle_data( args, names )
	
	return True
	
	
def cmd_get_resource_record( args ):
	r = api_request( 'GET', 'resource-record/' + args.path )
	return handle_object_response( args, r )
	
	
def cmd_delete_resource( args ):
	r = api_request( 'DELETE', 'resource/' + args.path )
	return handle_object_response( args, r )
	
	
def cmd_get_resource( args ):
	r = api_request( 'GET', 'resource/' + args.path )
	return handle_binary_response( args, r )
	
	
def cmd_upload_resource( args ):
	if args.content_type == None:
		args.content_type, enc = mimetypes.guess_type( args.local_file, strict = False )

	query = {}
	if args.resource_type != None:
		query['resource_type'] = args.resource_type
	if args.signed_only:
		query['signed_only'] = 'True'
	if args.cache_ttl != None:
		query['cache_ttl'] = args.cache_ttl
	if args.expires != None:
		query['expires'] = args.expires
	
	headers = {}
	if args.content_type != None:	
		headers['Content-Type'] = args.content_type

	if args.path != None:	
		method = 'PUT'
		url = 'resource/' + args.path
	else:
		method = 'POST'
		url = 'resource'
	
	with open( args.local_file, 'rb' ) as fp:
		r = api_request( method, url, query_string = query, data = fp.read(), headers = headers )
	return handle_object_response( args, r )
	
	
def cmd_get_resource_url( args ):
	query = {
		'type_ext': args.type_ext,
		'profile': args.profile,
	}
	
	if args.signed:
		query['signed'] = 'True'
	if args.expires != None:
		query['expires'] = args.expires
	if args.domain != None:
		query['domain'] = args.domain
	if args.http:
		query['proto'] = 'http'
	if args.https:
		query['proto'] = 'https'
	
	if len( args.query_args ) > 0:
		qs = ''
		for p in args.query_args:
			s = p.split('=',1)
			if len(qs) > 0:
				qs += '&'

			qs += urllib.quote( s[0] )
			if len(s) > 1:
				qs += '='
				qs += urllib.quote( s[1] )
		query['query_string'] = qs
		
	
	r = api_request( 'GET', 'resource-url/' + args.path, query_string = query )
	return handle_object_response( args, r )
	

def main():
	opts = argparse.ArgumentParser()
	common.add_config_args( opts )
	opts.add_argument( "--verbose", help = "show verbose output", action='store_const', const = True )
	opts.add_argument( "--save", help = "save the command result to this file instead of displaying",
		nargs = "?" )
	sub = opts.add_subparsers( help = 'command help', title = "Commands", dest = 'command' )
	
	def add_local( name, help,
		with_path = False ):
		o = sub.add_parser( name, help = help )
		o.set_defaults( func = globals()['cmd_' + name.replace( '-', '_' )] )
		if with_path:
			o.add_argument( 'path', help = 'resource name or id' )
		return o
		
	add_local( 'setup', "configure Redid CLI tools" )

	add_local( 'show-config', "dump the Redid CLI configuration" )
	
	add_local( 'check-auth', "check Redid access/authorization" )
	
	
	# Profile commands
	o = add_local( 'get-profile', "get a profile by name" )
	o.add_argument( "profile" )
		
	o = add_local( 'put-profile', 'create/update a profile' )
	o.add_argument( 'load', help = 'filename of the profile to upload' )
	o.add_argument( 'profile', help = 'name of profile, if not specified basename of file is used',
		nargs = '?' )
		
	o = add_local( 'delete-profile', 'delete a profile' )
	o.add_argument( 'profile', help = 'name of the profile to delete' )
	
	o = add_local( 'get-profile-signature', 'generate access signature for signed URL' )
	o.add_argument( 'profile', help = 'name of the profile for signed access' )
	
	o = add_local( 'list-profiles', 'get a listing of the profiles' )
	o.add_argument( '--full', help = 'output the complete profile, not just the name', 
		action = 'store_const', const = True )
	
	
	# Resource commands
	o = add_local( 'list-resources', 'get a listing of resources' )
	o.add_argument( '--sha256', help = 'matching the given hash (hex encoded)' )
	o.add_argument( '--name-prefix', help = 'starting with this name prefix' )
	o.add_argument( '--full', help = 'output the resource record, not just the name', 
		action = 'store_const', const = True )
	
	o = add_local( 'get-resource-record', 'get the resource record', with_path = True )
	
	o = add_local( 'delete-resource', 'delete the resource', with_path = True )
	
	o = add_local( 'get-resource', 'get the binary data for the resource', with_path = True )
	
	o = add_local( 'upload-resource', 'upload a resource' )
	o.add_argument( 'local_file', metavar = 'local-file',  help = 'name of local file to upload' )
	o.add_argument( 'path', help = 'resource name or id, if not specified then a unique ID is chosen', 
		nargs = '?' )
	o.add_argument( '--content-type', help = 'specify a content-type, otherwise guess based on filename' )
	o.add_argument( '--resource-type', help = 'force a resource type "raw" or "image" ' )
	o.add_argument( '--signed-only', help = 'resource can only be accessed via signed URLs',
		action='store_const', const = True )
	o.add_argument( '--cache-ttl', help = 'limit on the time this resource can be cached' )
	o.add_argument( '--expires', help = 'resource expires on this datetime' )
	
	o = add_local( 'get-resource-url', 'Get a client url to a resource. This does not validate the request,'
		+ ' thus if the parameters are wrong the resulting URL may not work.', 
		with_path = True )
	o.add_argument( '--type-ext', help = 'filename extension' )
	o.add_argument( '--profile', help = 'using this profile' )
	o.add_argument( '--signed', help = 'a signed URL', action = 'store_const', const = True )
	o.add_argument( '--expires', help = 'expiration for signed URL' )
	o.add_argument( '--domain', help = 'using this domain (default is based on account settings)' )
	o.add_argument( '--http', help = 'force HTTP', action = 'store_const', const = True )
	o.add_argument( '--https', help = 'force HTTPS', action = 'store_const', const = True )
	o.add_argument( "query_args", metavar = 'query-args', nargs = '*',
		help = 'additional query-string parameters for the URL, Name=Value or Name' )
	
	# args parsing
	args = opts.parse_args()
	global verbose
	verbose = args.verbose
	
	if args.command == 'setup':
		args.func( args )
	else:
		global config
		config = common.load_config( args )
		if config == None:
			log( "Unable to load configuration. Please run 'redid setup' " )
			sys.exit(1)
		if not args.func( args ):
			sys.exit(2)

		
def api_request( *args, **kwargs ):
	return common.api_request( *args, config = config, verbose = verbose, **kwargs )

	
def handle_object_response( args, data ):
	""" Common handling of object responses. Either display or write to the provided file. """
	if data == None:
		return False
	handle_data( args, data['data'] )
	return True

def handle_binary_response( args, data ):
	if data == None:
		return False
	handle_data( args, data, binary = True )
	return True
	
def handle_data( args, data, binary = False ):
	if args.save != None:
		save_data( data, args.save, binary = binary )
	else:
		common.show_data( data, binary = binary )

	
def save_data( data, filename, binary = False ):
	""" Save response data to a file. """
	if binary:
		with open( filename, 'wb' ) as fp:
			fp.write( data )

	elif filename.endswith( '.yaml' ):
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
