import json

from sys import argv, exit
from fabric.operations import prompt

def set_kvp(key):
	value = prompt("%s (default: %s): " % (key[0], "[none]" if key[1] is None else str(key[1])))
	if len(value) == 0 or type(value) not type(key[1]):
		return None

	return value

def dbb_client_setup(client_name):
	default_keys = []

	if client_name == "dropbox":
		default_keys = [
			("app_key", None),
			("app_secret", None)
		]

	config = {}
	for key in default_keys:
		config[key[0]] = get_kvp(key)

	return config

def dbb_client_verify(client_name, config):
	if client_name == "dropbox":
		import dropbox

		try:
			client = dropbox.client.DropboxOAuth2FlowNoRedirect(config['app_key'], config['app_secret'])

			print "VERIFYING DROPBOX!"
			print "Visit this url in a browser: %s." % client.start()
			print "You will be shown an authorization code."

			access_token, user_id = client.finish(prompt("dropbox auth code: "))

			config['access_token'] = access_token
			config['user_id'] = user_id
		except Exception as e:
			raise Exception("error verifying dropbox client:\n(%s) %s" % (type(e), e))


	return config

def dbb_setup(with_args=None):
	print "setting up..."
	
	config = {}

	if with_args is not None and len(with_args) == 1:
		try:
			with open(with_args[0], 'rb') as c:
				config = json.loads(c.read())
		except Exception as e:
			print "no real conf, using default: %e" % e

	default_keys = [
		('api_port', 8081),
		('num_processes', 5), 
		('api_client', "dropbox"), 
		('video_root', None)
	]

	for key in default_keys:
		if key[0] not in config.keys() or type(config[key[0]]) not type(key[1]):
			config[key[0]] = get_kvp(key)

	if config['api_client'] not in config.keys():
		config[config['api_client']] = dbb_client_setup(config['api_client'])

	try:
		config[config['api_client']].update(
			dbb_client_verify(config['api_client'], config[config['api_client']]))
	except Exception as e:
		print e
		return False

	BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
	
	config['log_file'] = os.path.join(BASE_DIR, ".monitor", "log.txt")
	config['pid_file'] = os.path.join(BASE_DIR, ".monitor", "pid.txt")
	config['asset_dir'] = os.path.join(BASE_DIR, "web")
	
	config['tornado_opts'] = {
		'static_path' : config['asset_dir'],
		'debug' : True,
		'xsrf_cookies' : True
	}

	from fabric.api import settings, local
	with settings(warn_only=True):
		local("mkdir %s" % os.path.join(BASE_DIR, ".monitor"))

	with open(os.path.join(BASE_DIR, ".config"), 'wb+') as c:
		c.write(json.dumps(config))

	return True

if __name__ == "__main__":
	try:
		if dbb_setup(with_args=argv[1:]):
			exit(0)
	except Exception as e:
		print e

	exit(-1)