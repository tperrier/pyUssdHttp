# system imports
import os.path
import sys
import collections

# set this to False to ignore logging
write_to_log = True

LogNode = collections.namedtuple("LogNode", ['time_from_start', 'current_screen', 'input'])

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)

logpath = os.path.join(base_dir, 'logs')

def save_log(session_id, created, phone_number, log):
	if write_to_log:
		with open(os.path.join(logpath, str(session_id)+'.log'), 'w') as logfile:
			logfile.write('session ID: {} from {} created {}\n'.format(session_id, phone_number, created))

			for node in log:
				logfile.write('T:{}, {}, {}\n'.format(*node))

if __name__ == '__main__':
	pass