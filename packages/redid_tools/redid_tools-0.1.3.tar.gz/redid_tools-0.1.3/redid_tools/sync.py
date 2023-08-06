"""
	Synchronize a Redid resource directory with a local directory.
"""
import argparse, sys, os, mimetypes, yaml, hashlib

from shelljob import fs

import common

config = None
verbose = False

def main():
	opts = argparse.ArgumentParser()
	common.add_config_args( opts )
	opts.add_argument( "--verbose", help = "show verbose output", action='store_const', const = True )
	opts.add_argument( 'local_dir', metavar = 'local-directory', 
		help = 'The local directory of files to put on Redid' )
	opts.add_argument( 'redid_dir', metavar = 'remote-directory', 
		help = 'Where to store the files on Redid, this becomes the prefix' )

	args = opts.parse_args()
	global config, verbose
	verbose = args.verbose
	config = common.load_config( args )
	
	if config == None:
		common.log( "Missing a configuration, please run 'redid setup'" )
		sys.exit(1)
	
	if not args.redid_dir.endswith( '/' ):
		common.log( "The redid-directory is expected to end in a /" )
		sys.exit(1)
	
	redid_config = load_redid_config( args.local_dir )
		
	local = get_local_files( redid_config, args.local_dir )
	#common.show_data( local )
	
	current = get_current_resources( args.redid_dir )
	if current == False:
		common.log( "Failed to obtain current resource listing" )
		sys.exit(1)
	#common.show_data( current )
		
	sync_files( redid_config, args.redid_dir, local, current )
	
	delete_missing_files( redid_config, current )
	
def load_redid_config( base_location ):
	"""
		Options for synchroniization can be stored in the <.redid.yaml> file in the root of
		the synchronized directory.
	"""
	redid_cfg_file = base_location + '/.redid.yaml'
	if os.path.exists( redid_cfg_file ):
		redid_config = yaml.load( file( redid_cfg_file, 'r' ) )
	else:
		redid_config = {}
		
	if not 'ext_map' in redid_config:
		redid_config['ext_map'] = {}
		
	return redid_config
	
def get_current_resources( prefix ):
	"""
		Get a listing of the current resources in the target directory.
	"""
	common.log( "Getting current resource listing" )
	query = {
		'name_prefix': prefix,
	}
	
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

	mapped = { (r['name'] if 'name' in r else r['id']): r for r in resources  }
	common.log( "Found {} remote resources".format( len( mapped ) ) )
	return mapped
	
	
def api_request( *args, **kwargs ):
	return common.api_request( *args, config = config, **kwargs )
	
	
def get_local_files( redid_config, where ):
	"""
		Create the listing of local files which are to be synchronized. This also creates the name
		of the resource and determines it's content-type.
	"""
	if not where.endswith('/'):
		where += '/'
		
	files = {}
	for lp in fs.find( where, include_dirs = False, not_name_regex = '\..*', relative = True ):
		ct, base = get_file_type( redid_config, lp )
		
		if base in files:
			common.log( "Error: {} is duplicated locally, only one will be uploaded".format( base ) )
			continue
			
		files[base] = {
			'path': where + lp,
			'type': ct,
		}

	common.log( "Found {} local resources".format( len(files) ) )
	return files
	

# Extra mappings for special Redid formats
redid_type_map = {
	'.9.png': 'image/x-redid-9patch',
	'.gradient.yaml': 'image/x-redid-gradient',
}

def get_file_type( redid_config, filename ):
	"""
		Determine the type of the file, and it's basename (less extensions)
	"""
	# specific wildcard match from config
	for k, v in redid_config['ext_map'].iteritems():
		if filename.endswith( k ):
			return v, filename[:-len(k)]
			
	for k, v in redid_type_map.iteritems():
		if filename.endswith( k ):
			return v, filename[:-len(k)]

	base, ext = os.path.splitext( filename )
	ct, enc = mimetypes.guess_type( filename, strict = False )
	if ct != None:
		return ct, base
		
	return 'application/octet-stream', base
	
def sync_files( redid_config, target, local, current ):
	"""
		Do the file synchronization of any modified file.
	"""
	skip = 0
	update = 0
	create = 0
	
	for name, spec in local.iteritems():
		with open( spec['path'], 'rb' ) as fp:
			blob = fp.read()
			
		# check if binary resource is the same
		rname = target + name
		if rname in current:
			# Track all those that exist locally
			current[rname]['_local_found'] = True
			
			sha256 = hashlib.sha256(blob).hexdigest()
			if current[rname]['sha256'] == sha256:
				if verbose:
					common.log( "Skipping {}, same hash".format( name ) )
				skip += 1
				continue
			update +=1
		else:
			create += 1
				
		headers = {
			'Content-Type': spec['type']
		}
		common.log( "Uploading {}".format( name ) )
		api_request( 'PUT', 'resource/' + rname, data = blob, headers = headers )
		
	common.log( "{} not modified, {} updated, {} new resources".format( skip, update, create ) )
		
def delete_missing_files( redid_config, current ):
	"""
		Remove remote files which have not been found locally.
	"""
	is_delete = redid_config.get( 'remote_delete_missing', False)
	deleted = 0
	if is_delete:
		common.log( "Deleting missing resources" )
		
	for k, v in current.iteritems():
		if '_local_found' in v:
			continue
			
		deleted += 1
		
		if is_delete:
			if verbose:
				common.log( "Deleting resource: " + k )
			api_request( 'DELETE', 'resource/' + k )
		else:
			if verbose:
				common.log( "Remote resource not found locally: " + k )
		
	if is_delete:
		common.log( "Deleted {} remote resources".format( deleted ) )
	else:
		common.log( "{} redundant remote sources".format( deleted ) )
		