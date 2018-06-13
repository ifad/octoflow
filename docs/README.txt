############
## Setup: ##
############

- create a folder readable and writable by the user that will be used from Octoflow, in a path of choice
- copy inside this folder:
  - the templates folder
  - the octoflow.yaml global configuration file (or generate one yourself but put in this directory)
- inside the same directory create the following folders:
  - confs
  - collector, inside the confs folder
  - exporters, inside the confs folder

Here there is an example of the needed folder structure

			/etc/octoflow/
			├── confs
			│   ├── collectors
			│   │   ├── collector_02.conf
			│   │   └── collector_02.conf
			│   ├── exporters
			│   │   ├── exporter_01.conf
			│   │   ├── exporter_02.conf
			│   │   └── exporter_03.conf
			│   └── supervisor.conf
			├── octoflow.yaml
			└── templates
			    ├── collector.j2
			    ├── exporter.j2
			    └── supervisord.j2 


############
## Usage: ##
############

* Server:
  - After octoflow configuration is generated (or modified as needed), is possible to start the server via the script octoflow_server.py ( python2 octoflow_server.py --config_file /path/to/octoflow.yaml/file/is )

* Client:
  - After octoflow configuration is generated (or modified as needed), is possible to start the server via the script octoflow_client.py ( python2 octoflow_client.py --config_file /path/to/octoflow.yaml/file/is --action_to_perform <TARGET> )
