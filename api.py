def start_daemon(log_file, pid_file):
	print "starting daemon"

def stop_daemon(pid_file, with_ports=None):
	print "stopping daemon"

	if with_ports is not None:
		if type(with_ports) in [str, unicode, int]:
			with_ports = [with_ports]


class DropBlockbusterAPI(object):
	def __init__(self):
		print "API STARTED"

		if api_client is None:
			api_client = "dropbox"

	def get_videos(self):
		print "getting videos"
