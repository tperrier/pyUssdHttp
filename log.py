# system imports
import os.path
import sys

# set this to False to ignore logging
log = True


base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)

logpath = os.path.join(base_dir, 'logs')

def save_log(session_id, log):
	if log:
		with open(os.path.join(log, str(session_id)+'.log'), 'w') as logfile:
			logfile.write('this is the log for session {}'.format(session_id))