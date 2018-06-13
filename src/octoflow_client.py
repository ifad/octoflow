from libs.octoflow_config import OctoflowConfigHandler
import os
import argparse

# CMDline argument parsing
parser = argparse.ArgumentParser(description='Octoflow client')
parser.add_argument('--config_file', help='Octoflow YAML configuration file.', default='/etc/octoflow/octoflow.yaml', dest='config_file', required=False)

group = parser.add_mutually_exclusive_group()
group.add_argument('--start', help='Start a single process (by process name), a group (by group name) or "all" for every process.', dest='start')
group.add_argument('--stop', help='Stop a single process (by process name), a group (by group name) or "all" for every process.', dest='stop')
group.add_argument('--status', help='Query Status for a single process (by process name), a group (by group name) or "all" for every process.', dest='status')
group.add_argument('--restart', help='Restart a single process (by process name), a group (by group name) or "all" for every process.', dest='restart')
group.add_argument('--reload', help='Reload Octoflow instances configurations: THIS WILL RESTART THE INSTANCES WITH THE NEW CONFIGURATIONS.', action='store_true')
group.add_argument('--reread', help='Reread Octoflow instances configurations. THIS WILL NOT RESTART THE INSTANCES WITH THE NEW CONFIGURATIONS.', action='store_true')
group.add_argument('--shutdown', help='Shutdown Octoflow and all processes instances', action='store_true')

args = parser.parse_args()

# Initialize configurations
conf = OctoflowConfigHandler()
if conf.read(str(args.config_file)) is not True:
  quit()
else:
  # Exec specific action based on arguments passed in the CMDline
  if args.start:
    os.system("supervisorctl -c "+conf.supervisor_conf_path+" start "+args.start)
  elif args.stop:
    os.system("supervisorctl -c "+conf.supervisor_conf_path+" stop "+args.stop)
  elif args.status:
    os.system("supervisorctl -c "+conf.supervisor_conf_path+" status "+args.status)
  elif args.restart:
    os.system("supervisorctl -c "+conf.supervisor_conf_path+" restart "+args.restart)
  elif args.shutdown == True:
    os.system("supervisorctl -c "+conf.supervisor_conf_path+" shutdown")
  elif args.reread == True:
    if conf.read(str(args.config_file)) is not True:
      quit()
    else:
      if conf.write() is not True:
        quit()
      else:
        os.system("supervisorctl -c "+conf.supervisor_conf_path+" reread")
  elif args.reload == True:
    if conf.read(str(args.config_file)) is not True:
      quit()
    else:
      if conf.write() is not True:
        quit()
      else:
        os.system("supervisorctl -c "+conf.supervisor_conf_path+" reload")
  else:
    pass