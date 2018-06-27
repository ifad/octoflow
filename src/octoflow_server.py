from libs.octoflow_config import OctoflowConfigHandler
import os
import argparse

# CMDline arguments parsing
parser = argparse.ArgumentParser(description='Octoflow server')
parser.add_argument('--config_file', help='Octoflow YAML configuration file.', default='/etc/octoflow/octoflow.yaml', dest='config_file', required=False)
args = parser.parse_args()

# Initialize configurations
conf = OctoflowConfigHandler()

if conf.read(str(args.config_file)) is not True:
	quit()
else:
  if conf.write() is not True:
  	quit()
  else:
    # Exec supervisord in foreground
    os.system("supervisord -c "+conf.supervisor_conf_path)
