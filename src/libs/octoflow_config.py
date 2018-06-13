import yaml
from jinja2 import Template, Environment, FileSystemLoader
import logging


class OctoflowConfigHandler(object):
  """
  Object representing the configuration
  """
  def __init__(self):
    """
    Initialize configuration handler object

    :param no params.
    :return: returns nothing.
    """
    self.general_conf = None
    self.supervisor_conf = None
    self.nprobe_conf = None
    self.exporters_conf = None
    self.collectors_conf = None

    self.base_confs_path = None
    self.supervisor_conf_path = None
    self.exporters_confs_path = None
    self.collectors_confs_path = None
    self.templates_path = None

    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(__name__)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #handler.setFormatter(formatter)
    #self.logger.addHandler(handler)

  def __generate_conf_file(self, config_data, template):
    """
    Generate configuration files

    :param config_data: dictionary containing all the configurations.
    :param template: template of the wanted configuration to update/deploy
    :return: returns templated configuration.
    """
    env = Environment(loader = FileSystemLoader(self.templates_path), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(str(template))

    config_data['autostart_instances'] = self.supervisor_conf['autostart_instances']
    config_data['autorestart_instances'] = self.supervisor_conf['autorestart_instances']
    config_data['startretries_instances'] = self.supervisor_conf['startretries_instances']
    config_data['nprobe_bin_path'] = self.nprobe_conf['bin_path']

    #Render the template with data and save the output
    conf = template.render(config_data)
    return conf

  def __write_conf_file(self, data, dest):
    """
    Write config files

    :param data:.
    :param dest:.
    :return: returns nothing.
    """
    try:
      with open(dest, "w") as f:
        f.write(data)
        return True
    except IOError as e:
      self.logger.critical("Configuration file not accessible from the user")
      return False

  def __clean_conf(self, confs_path):
    """
    Clean config files

    :param confs_path:.
    :return: returns a boolean representing the success or failure (True/False) of the operation.
    """
    if os.path.isfile(str(confs_path)):
      os.remove(str(confs_path))
      return True
    elif os.path.isdir(str(confs_path)):
      filelist = [ f for f in os.listdir(confs_path) ]
      for f in filelist:
        os.remove(os.path.join(mydir, f))
      return True
    else:
      return False

  def __search_exporter(self, id, list):
    for item in list:
      if item['id'] == id:
        return item['listen_host'],item['listen_port']

  def check_env(self):
    """
    Check environment configuration for the correct operations of octoflow

    :param conf_path: path to octoflow.yaml (main configuration file).
    :return: returns a boolean value: True if configuration is OK, False otherwise.
    """
    self.logger.debug(self.general_conf)

  def check_config(self, conf):
    """
    Checks Octoflow configuration.

    :param conf:  adictionary containing parsed YAML from octoflow.yaml.
    :return: returns a boolean value: True if configuration is OK, False otherwise.
    """
    collectors = conf['collectors']
    exporters = conf['exporters']

    mux_to = set([])
    exporters_to = set([])

    # Populate sets
    for collector in collectors:
      mux_to.update(collector['mux_to'])
    for exporter in exporters:
      exporters_to.add(exporter['id'])

    # If difference between sets is 0, then we have a correct amount of nprobe instances referenced
    if len(mux_to - exporters_to) == 0:
      return True
    # Else fail configuration check
    else:
      return False

  def read(self, conf_file_path):
    """
    Read configurations from specified file and save in dict

    :param conf_file_path: path to main configuration file, octoflow.yaml.
    :return: returns a boolean value (True or False) representing the success or failure of main configuration (octoflow.yaml) read.
    """
    self.logger.debug("Opening configuration file")
    try:
      with open(conf_file_path) as c:
        try:
          self.logger.debug("Parsing octoflow.yaml configuration file")
          conf_dict = yaml.load(c)
        except yaml.YAMLError as e:
          self.logger.critical("Octoflow configuration not correct or YAML syntax not valid")
          return False

        if self.check_config(conf_dict) == True:
          self.logger.debug("Save configuration in object attributes")
          self.general_conf = conf_dict['general']
          self.supervisor_conf = conf_dict['supervisor']
          self.nprobe_conf = conf_dict['nprobe']
          self.collectors_conf = conf_dict['collectors']
          self.exporters_conf = conf_dict['exporters']

          self.logger.debug("Generate configurations paths")
          self.base_confs_path = str(self.general_conf['base_confs_path'])
          self.supervisor_conf_path = str(self.base_confs_path+'/supervisor.conf')
          self.exporters_confs_path = str(self.base_confs_path+'/exporters/')
          self.collectors_confs_path = str(self.base_confs_path+'/collectors/')

          self.logger.debug("Generate templates paths")
          self.templates_path = str(self.general_conf['base_templates_path'])
          return True
        else:
          return False
    except IOError as e:
      self.logger.critical("Configuration file not accessible from the user")
      return False

  def write(self):
    """
    Write configurations to specified directory and update object properties.
    """
    instance_conf = self.__generate_conf_file(self.supervisor_conf, 'supervisord.j2')
    if self.__write_conf_file(instance_conf, str(self.supervisor_conf_path)) is not True:
      return False

    for item in self.exporters_conf:
      instance_conf = self.__generate_conf_file(item, 'exporter.j2')
      if self.__write_conf_file(instance_conf, str(self.exporters_confs_path+str(item['id']+'.conf'))) is not True:
        return False

    for item in self.collectors_conf:
      item['mux_to2'] = []
      for item2 in item['mux_to']:
        host, port = self.__search_exporter(item2, self.exporters_conf)
        asd = 'udp://' + str(host)+':'+str(port)
        item['mux_to2'].append(asd)
      instance_conf = self.__generate_conf_file(item, 'collector.j2')
      if self.__write_conf_file(instance_conf, str(self.collectors_confs_path+str(item['id']+'.conf'))) is not True:
        return False

    return True

  def clean(self):
    """
    Clean configurations.
    """
    self.__clean_exporters_confs()
    self.__clean_collectors_confs()
    self.__clean_supervisor_conf()

  '''
  def refresh(self, conf_file_path):
    """
    Refresh configurations from specified file.

    :param conf_file: path to octoflow.yaml (main configuration file).
    :return: returns a success message in case the file exists and can be read. A failure message otherwise.
    """
    if self.check_env() == True:
      if self.read(conf_file_path) == True:
        if self.clean() == True:
          if self.write() == True:
            return True
          else:
            print("Error in Write sequence.")
            return False
        else:
          print("Error in Clean sequence.")
          return False
      else:
        print("Error in Read sequence.")
        return False
    else:
      print("Error in Environment Check sequence.")
      return False
  '''