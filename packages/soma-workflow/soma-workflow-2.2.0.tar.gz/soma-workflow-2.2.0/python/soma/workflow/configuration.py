# -*- coding: utf-8 -*-
'''
@author: Soizic Laguitton
@organization: U{IFR 49<http://www.ifr49.org>}
@license: U{CeCILL version 2<http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>}
'''

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import os
import sys
import socket
import ConfigParser

from soma.workflow.errors import ConfigurationError
import soma.workflow.observer as observer


#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

LIGHT_MODE = 'light'
REMOTE_MODE = 'remote'
LOCAL_MODE = 'local'
MODES = [LIGHT_MODE,
         REMOTE_MODE,
         LOCAL_MODE]

LOCAL_SCHEDULER = 'local_basic'
DRMAA_SCHEDULER = 'drmaa'
SCHEDULER_TYPES = [LOCAL_SCHEDULER,
                   DRMAA_SCHEDULER]

# configuration variables ------------------------------------------------------

'''
CFG => Mandatory items
OCFG => Optional
'''
CFG_CLUSTER_ADDRESS = 'CLUSTER_ADDRESS'
CFG_SUBMITTING_MACHINES = 'SUBMITTING_MACHINES'
OCFG_DRMAA_IMPLEMENTATION = 'DRMAA_IMPLEMENTATION'


#OCFG_QUEUES is a list of queue name separated by white spaces.
#ex: "queue1 queue2"
OCFG_QUEUES = 'QUEUES'

OCFG_LOGIN = 'LOGIN'

#OCFG_MAX_JOB_IN_QUEUE allow to specify a maximum number of job N which can be
#in the queue for one user. The engine won't submit more than N job at once. The 
#also wait for the job to leave the queue before submitting new jobs.
#syntax: "{default_queue_max_nb_jobs} queue1{max_nb_jobs1} queue2{max_nb_job2}"
OCFG_MAX_JOB_IN_QUEUE = 'MAX_JOB_IN_QUEUE' 

#database server
CFG_DATABASE_FILE = 'DATABASE_FILE'
CFG_TRANSFERED_FILES_DIR = 'TRANSFERED_FILES_DIR'
CFG_SERVER_NAME = 'SERVER_NAME'
CFG_NAME_SERVER_HOST ='NAME_SERVER_HOST'

OCFG_SERVER_LOG_FILE = 'SERVER_LOG_FILE'
OCFG_SERVER_LOG_LEVEL = 'SERVER_LOG_LEVEL'
OCFG_SERVER_LOG_FORMAT = 'SERVER_LOG_FORMAT'

#Engine
OCFG_ENGINE_LOG_DIR = 'ENGINE_LOG_DIR'
OCFG_ENGINE_LOG_LEVEL = 'ENGINE_LOG_LEVEL'
OCFG_ENGINE_LOG_FORMAT = 'ENGINE_LOG_FORMAT'

#Shared resource path translation files 
#specify the translation files (if any) associated to a namespace
#eg. translation_files = brainvisa{/home/toto/.brainvisa/translation.sjtr} namespace2{path/translation1.sjtr} namespace2{path/translation2.sjtr}
OCFG_PATH_TRANSLATION_FILES = 'PATH_TRANSLATION_FILES' 

# Soma-workflow light mode.
# Define this item to use soma-workflow in the light mode.
# This mode doesn't require a database server to run. It can not be used on
# remote computing resource. The client application can not be closed before the
# workflows and jobs are done. 
OCFG_LIGHT_MODE = 'LIGHT_MODE'

# Parallel job configuration :
# DRMAA attributes used in parallel job submission (their value depends on the cluster and DRMS) 
OCFG_PARALLEL_COMMAND = "drmaa_native_specification"
OCFG_PARALLEL_JOB_CATEGORY = "drmaa_job_category"
PARALLEL_DRMAA_ATTRIBUTES = [OCFG_PARALLEL_COMMAND, OCFG_PARALLEL_JOB_CATEGORY]
# kinds of parallel jobs (items can be added by administrator)
OCFG_PARALLEL_PC_MPI="MPI"
OCFG_PARALLEL_PC_OPEN_MP="OpenMP"
PARALLEL_CONFIGURATIONS = [OCFG_PARALLEL_PC_MPI, OCFG_PARALLEL_PC_OPEN_MP]
# parallel job environment variables for the execution machine (items can be added by administrators) 
OCFG_PARALLEL_ENV_MPI_BIN = 'PARALLEL_ENV_MPI_BIN'
OCFG_PARALLEL_ENV_NODE_FILE = 'PARALLEL_ENV_NODE_FILE'
PARALLEL_JOB_ENV = [OCFG_PARALLEL_ENV_MPI_BIN, OCFG_PARALLEL_ENV_NODE_FILE]


# local sheduler configuration -------------------------------------------------

OCFG_SCDL_CPU_NB = "CPU_NB"
OCFG_SCDL_INTERVAL = "SCHEDULER_INTERVAL"



#-------------------------------------------------------------------------------
# Classes and functions
#-------------------------------------------------------------------------------

class Configuration(observer.Observable):
  
  # path of the configuration file
  _config_path = None

  # config parser object
  _config_parser = None

  _resource_id = None

  _mode = None

  _scheduler_type = None

  _database_file = None

  _transfered_file_dir = None

  _submitting_machines = None

  _cluster_address = None

  _name_server_host = None

  _server_name = None

  _queue_limits = None

  _queues = None

  _drmaa_implementation = None

  _login = None

  parallel_job_config = None

  path_translation = None

  QUEUE_LIMITS_CHANGED = 0

  def __init__(self,
               resource_id,
               mode,
               scheduler_type,
               database_file,
               transfered_file_dir,
               submitting_machines=None,
               cluster_address=None,
               name_server_host=None,
               server_name=None,
               queues=None,
               queue_limits=None,
               drmaa_implementation=None,
               login=None
               ):
    '''
    * resource_id *string*
      Identifier of the computing resource.

    * mode *string* 
      A mode among the existing modes defined in configuration.MODES
      
    * scheduler_type *string*
      A scheduler type among the existing schedulers defined in SCHEDULER_TYPES

    * database_file *string*
      Path of the database_file.

    * transfered_file_dir *string*
      Path of the directory where the transfered files are copied. Mandatory 
      in every mode (even local or light), the directory must exist.

    * submitting_machines *list of string*
      List of submitting machines. Mandatory in the REMOTE_MODE for the remote
      ssh connection.

    * cluster_address *string*
      Address of the cluster. Mandatory in the REMOTE_MODE for the remote
      ssh connection.

    * name_server_host *string*
      Machine where the pyro name server can be found. Mandatory in the 
      REMOTE_MODE to connect to the database_server.

    * server_name *string*
      Name of the database server regitered on the Pyro name server. Mandatory 
      in the REMOTE_MODE to connect to the database_server.
  
    * queues *list of string*
      List of the available queues. This item is only used in the GUI to make 
      easier the selection of the queue when submitting a workflow.

    * queue_limits *dictionary: string -> int*
      Maximum number of job in each queue (dictionary: queue name -> limit). 
      If a queue does not appear here, soma-workflow considers that there is 
      no limitation. 

    * drmaa_implementation *string*
      Set this item to "PBS" if you use FedStage PBS DRMAA 1.0 implementation, 
      otherwise it does not has to be set. 

    
    '''

    super(Configuration, self).__init__()

    self._config_path = None
    self._config_parser = None
    self._resource_id = resource_id
    self._mode = mode
    self._scheduler_type = scheduler_type
    self._database_file = database_file
    self._transfered_file_dir = transfered_file_dir
    self._submitting_machines = submitting_machines
    self._cluster_address = cluster_address
    self._name_server_host = name_server_host
    self._server_name = server_name
    self._login = login
    if queues == None:
      self._queues = []
    else:
      self._queues = queues
    if queue_limits == None:
      self._queue_limits = {}
    else:
      self._queue_limits = queue_limits
    self._drmaa_implementation = drmaa_implementation
    self.parallel_job_config = None
    self.path_translation = None


  @staticmethod
  def get_home_dir():
    # if python version > 2.5 expanduser should be ok
    homedir = os.getenv( 'HOME' )
    if not homedir:
      homedir = ''
      if sys.platform[:3] == 'win':
        homedir = os.getenv( 'USERPROFILE' )
        if not homedir:
          homedir = os.getenv( 'HOMEPATH' )
          if not homedir:
            homedir = '\\'
          drive = os.getenv( 'HOMEDRIVE' )
          if not drive:
            drive = os.getenv( 'SystemDrive' )
            if not drive:
              drive = os.getenv( 'SystemRoot' )
              if not drive:
                drive = os.getenv( 'windir' )
              if drive and len( drive ) >= 2:
                drive = drive[ :2 ]
              else:
                drive = ''
          homedir = drive + homedir
    return homedir


  @classmethod
  def load_from_file(cls,
                     resource_id=None, 
                     config_file_path=None):

    if config_file_path:
      config_path = config_file_path
    else:
      config_path = Configuration.search_config_path()

    config = None
    home_dir = Configuration.get_home_dir() 

    if resource_id == None or resource_id == socket.gethostname() :
      
      #scheduler local on the local machine
      resource_id = socket.gethostname()
      mode = LIGHT_MODE
      scheduler_type = LOCAL_SCHEDULER
      database_file = os.path.join(home_dir, ".soma-workflow/soma_workflow.db")
      transfered_file_dir = os.path.join(home_dir, ".soma-workflow/transfered_files")
      
      config = cls(resource_id=resource_id,
                   mode=mode,
                   scheduler_type=scheduler_type,
                   database_file=database_file,
                   transfered_file_dir=transfered_file_dir)

      if config_path != None:
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_path)
        if config_parser.has_section(resource_id):
          config._config_parser = config_parser
          config._config_path = config_path

      if not os.path.isdir(os.path.join(home_dir, ".soma-workflow")):
        os.mkdir(os.path.join(home_dir, ".soma-workflow"))
      if not os.path.isdir(transfered_file_dir):
        os.mkdir(transfered_file_dir)

      return config

    else:
      scheduler_type = DRMAA_SCHEDULER

      if config_path == None:
        raise ConfigurationError("A configuration file is required to connect " 
                                 "to " + repr(resource_id) + ": the soma-workflow "
                                 "configuration file could not be found.")
      config_parser = ConfigParser.ConfigParser()
      config_parser.read(config_path)
      if not config_parser.has_section(resource_id):
        raise ConfigurationError("Can not find section " + resource_id + " "
                                "in configuration file: " + config_path)

      config = cls(resource_id=resource_id,
                   mode=None,
                   scheduler_type=scheduler_type,
                   database_file=None,
                   transfered_file_dir=None)
      config._config_parser = config_parser
      config._config_path = config_path

      return config


  def get_scheduler_type(self):
    return self._scheduler_type

  def get_submitting_machines(self):
    if self._config_parser == None or self._submitting_machines: 
      return self._submitting_machines

    if not self._config_parser.has_option(self._resource_id,
                                          CFG_SUBMITTING_MACHINES):
      raise ConfigurationError("Can not find the configuration item %s for the "
                               "resource %s, in the configuration file %s." %
                               (CFG_SUBMITTING_MACHINES,
                                self._resource_id,
                                self._config_path))
    self._submitting_machines = self._config_parser.get(self._resource_id, 
                                         CFG_SUBMITTING_MACHINES).split()
    return self._submitting_machines


  @staticmethod
  def search_config_path():
    '''
    returns the path of the soma workflow configuration file
    '''

    home_dir = Configuration.get_home_dir() 

    config_path = os.getenv('SOMA_WORKFLOW_CONFIG')
    if not config_path or not os.path.isfile(config_path):
      config_path = os.path.join(home_dir, ".soma-workflow.cfg")
    if not config_path or not os.path.isfile(config_path):
      config_path = os.path.dirname(__file__)
      config_path = os.path.join(config_path, "etc/soma-workflow.cfg")
    if not config_path or not os.path.isfile(config_path):
      config_path = "/etc/soma-workflow.cfg"
    if not config_path or not os.path.isfile(config_path):
      config_path = None

    return config_path


  @staticmethod
  def get_configured_resources(config_file_path=None):
    '''
    returns the list of resouce ids
    '''
    resource_ids = []
    if config_file_path == None:
      return [socket.gethostname()]
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(config_file_path)
    for r_id in config_parser.sections():
      resource_ids.append(r_id)
    local_resource_id = socket.gethostname()
    if not local_resource_id in resource_ids:
      resource_ids.append(local_resource_id)
    return resource_ids


  @staticmethod
  def get_logins(config_file_path=None):
    '''
    returns the dictionary resouce_id -> login
    '''
    resource_ids = []
    if config_file_path == None:
      return { socket.gethostname(): None }
    config_parser = ConfigParser.ConfigParser()
    config_parser.read(config_file_path)
    logins = {}
    for r_id in config_parser.sections():
      resource_ids.append(r_id)
      if config_parser.has_option(r_id, OCFG_LOGIN):
        logins[r_id] = config_parser.get(r_id, OCFG_LOGIN)
      else:
        logins[r_id] = None
    logins[socket.gethostname()] = None
    return logins

  def get_mode(self):
    '''
    Return the application mode: 'local', 'remote' or 'light'
    '''
    if self._mode:
      return self._mode

    if self._config_parser.has_option(self._resource_id, OCFG_LIGHT_MODE):
      self._mode = LIGHT_MODE
      return self._mode
    
    if not self._submitting_machines:
      self._submitting_machines = self.get_submitting_machines()
   
    hostname = socket.gethostname()
    mode = REMOTE_MODE
    for machine in self._submitting_machines:
      if hostname == machine: 
        mode = LOCAL_MODE
    self._mode = mode 
    return mode
    

  def get_cluster_address(self):
    if self._config_parser == None or self._cluster_address:
      return self._cluster_address
    
    if not self._config_parser.has_option(self._resource_id, CFG_CLUSTER_ADDRESS):
      raise ConfigurationError("Can not find the configuration item %s for the "
                               "resource %s, in the configuration file %s." %
                               (CFG_CLUSTER_ADDRESS,
                                self._resource_id,
                                self._config_path))
    self._cluster_address= self._config_parser.get(self._resource_id, 
                                                   CFG_CLUSTER_ADDRESS)
    return self._cluster_address


  def get_database_file(self):
    if self._database_file:
      return self._database_file

    if not self._config_parser.has_option(self._resource_id, CFG_DATABASE_FILE):
      raise ConfigurationError("Can not find the configuration item %s " 
                                "for the resource %s, in the configuration " "file %s." %
                                (CFG_DATABASE_FILE,
                                  self._resource_id,
                                  self._config_path))
    self._database_file = self._config_parser.get(self._resource_id, 
                                                  CFG_DATABASE_FILE)
    return self._database_file


  def get_transfered_file_dir(self):
    if self._transfered_file_dir:
      return self._transfered_file_dir

    if not self._config_parser.has_option(self._resource_id, 
                                          CFG_TRANSFERED_FILES_DIR):
      raise ConfigurationError("Can not find the configuration item %s " 
                                "for the resource %s, in the configuration " "file %s." %
                                (CFG_TRANSFERED_FILES_DIR,
                                  self._resource_id,
                                  self._config_path))
    self._transfered_file_dir = self._config_parser.get(self._resource_id, 
                                                      CFG_TRANSFERED_FILES_DIR)
    return self._transfered_file_dir


  def get_parallel_job_config(self):
    if self._config_parser == None or self.parallel_job_config != None:
      return self.parallel_job_config
    
    self.parallel_job_config = {}
    for parallel_config_info in PARALLEL_DRMAA_ATTRIBUTES + \
                                PARALLEL_JOB_ENV + \
                                PARALLEL_CONFIGURATIONS:
      if self._config_parser.has_option(self._resource_id, parallel_config_info):
        self.parallel_job_config[parallel_config_info] = self._config_parser.get(self._resource_id, parallel_config_info)

    return self.parallel_job_config


  def get_drmaa_implementation(self):
    if self._config_parser == None or self._drmaa_implementation != None:
      return self._drmaa_implementation
    self._drmaa_implementation = None
    if self._config_parser != None and \
       self._config_parser.has_option(self._resource_id, 
                                      OCFG_DRMAA_IMPLEMENTATION):
      self._drmaa_implementation = self._config_parser.get(self._resource_id,                    
                                                      OCFG_DRMAA_IMPLEMENTATION)
    return self._drmaa_implementation

  def get_login(self):
    if self._config_parser == None or self._login != None:
      return self._login
    self._login = None
    if self._config_parser != None and \
       self._config_parser.has_option(self._resource_id, 
                                      OCFG_DRMAA_IMPLEMENTATION):
      self._login = self._config_parser.get(self._resource_id,                    
                                            OCFG_LOGIN)
    return self._login

  def get_path_translation(self):
    if self._config_parser == None or self.path_translation != None:
      return self.path_translation

    self.path_translation = {}
    if self._config_parser.has_option(self._resource_id, 
                                      OCFG_PATH_TRANSLATION_FILES):
      translation_files_str = self._config_parser.get(self._resource_id, 
                                                    OCFG_PATH_TRANSLATION_FILES)
      #logger.info("Path translation files configured:")
      for ns_file_str in translation_files_str.split():
        ns_file = ns_file_str.split("{")
        namespace = ns_file[0]
        filename = ns_file[1].rstrip("}")
        #logger.info(" -namespace: " + namespace + ", translation file: " + filename)
        try: 
          f = open(filename, "r")
        except IOError, e:
          raise ConfigurationError("Can not read the translation file %s" %
                                    (filename))
        
        if not namespace in self.path_translation.keys():
          self.path_translation[namespace] = {}
        line = f.readline()
        while line:
          splitted_line = line.split(None,1)
          if len(splitted_line) > 1:
            uuid = splitted_line[0]
            content = splitted_line[1].rstrip()
            #logger.info("    uuid: " + uuid + "   translation:" + content)
            self.path_translation[namespace][uuid] = content
          line = f.readline()
        f.close()

    return self.path_translation
      

  def get_name_server_host(self):
    if self._config_parser == None or self._name_server_host != None:
      return self._name_server_host
    self._name_server_host = None
    if self._config_parser != None:
      self._name_server_host = self._config_parser.get(self._resource_id, 
                                                       CFG_NAME_SERVER_HOST)
    return self._name_server_host


  def get_server_name(self):
    if self._config_parser == None or self._server_name != None:
      return self._server_name
    if not self._config_parser.has_option(self._resource_id,
                                          CFG_SERVER_NAME):
      raise ConfigurationError("Can not find the configuration item %s " 
                                "for the resource %s, in the configuration " "file %s." %
                                (CFG_SERVER_NAME,
                                  self._resource_id,
                                  self._config_path))
    self._server_name = self._config_parser.get(self._resource_id, 
                                  CFG_SERVER_NAME)
    return self._server_name

  
  def change_queue_limits(self, queue_name, queue_limit):
    '''
    * queue_name *string*

    * queue_limit *int*
    '''
    self.get_queue_limits()
    self._queue_limits[queue_name] = queue_limit
    self.notifyObservers(Configuration.QUEUE_LIMITS_CHANGED)
  

  def get_queue_limits(self):
    if self._config_parser == None or len(self._queue_limits) != 0:
      return self._queue_limits

    self._queue_limits = {}
    if self._config_parser.has_option(self._resource_id, 
                                      OCFG_MAX_JOB_IN_QUEUE):
      queue_limits_str = self._config_parser.get(self._resource_id,
                                                 OCFG_MAX_JOB_IN_QUEUE)
      for info_str in queue_limits_str.split():
        info = info_str.split("{")
        if len(info[0]) == 0:
          queue_name = None
        else:
          queue_name = info[0]
        max_job = int(info[1].rstrip("}"))
        self._queue_limits[queue_name] = max_job

    return self._queue_limits

  
  def get_queues(self):
    if self._config_parser == None or len(self._queues) !=  0:
      return self._queues

    self._queues = []
    if self._config_parser.has_option(self._resource_id, OCFG_QUEUES):
      self._queues.extend(self._config_parser.get(self._resource_id,
                                                  OCFG_QUEUES).split())
    return self._queues


  def get_engine_log_info(self):
    if self._config_parser != None and self._config_parser.has_option(self._resource_id, OCFG_ENGINE_LOG_DIR):
      engine_log_dir = self._config_parser.get(self._resource_id, 
                                               OCFG_ENGINE_LOG_DIR)
      if self._config_parser.has_option(self._resource_id,
                                        OCFG_ENGINE_LOG_FORMAT):
        engine_log_format = self._config_parser.get(self._resource_id,
                                                    OCFG_ENGINE_LOG_FORMAT,
                                                    1)
      else:
        engine_log_format = "%(asctime)s => %(module)s line %(lineno)s: %(message)s"
      if self._config_parser.has_option(self._resource_id,
                                        OCFG_ENGINE_LOG_LEVEL):
        engine_log_level = self._config_parser.get(self._resource_id,
                                                   OCFG_ENGINE_LOG_LEVEL)
      else:
        engine_log_level = "WARNING"
      return (engine_log_dir, engine_log_format, engine_log_level)
    else:
      return (None, None, None)



  def get_server_log_info(self):
    if self._config_parser != None and self._config_parser.has_option(self._resource_id, OCFG_SERVER_LOG_FILE):
      server_log_file = self._config_parser.get(self._resource_id,  
                                                OCFG_SERVER_LOG_FILE)
      if self._config_parser.has_option(self._resource_id,
                                        OCFG_SERVER_LOG_FORMAT):
        server_log_format = self._config_parser.get(self._resource_id,
                                                    OCFG_SERVER_LOG_FORMAT, 
                                                    1)
      else:
        server_log_format = "%(asctime)s => %(module)s line %(lineno)s: %(message)s"
      if self._config_parser.has_option(self._resource_id,
                                        OCFG_SERVER_LOG_LEVEL):
        server_log_level = self._config_parser.get(self._resource_id,
                                                    OCFG_SERVER_LOG_LEVEL)
      else:
        server_log_level = "WARNING"
      return (server_log_file, server_log_format, server_log_level)
    else:
      return (None, None, None)


  def save_to_file(self, config_path=None):
    pass 

    #home_dir = Configuration.get_home_dir() 

    # disabled for now because it erases the commented part of the configuration
    #if not config_path:
      #if self._config_path != None:
        #config_path = self._config_path
      #else:
        #config_path = Configuration.search_config_path()
        #if config_path == None:
          #config_path = os.path.join(home_dir, ".soma-workflow.cfg")
        #print config_path

    #config_parser = ConfigParser.ConfigParser()
    #config_parser.read(config_path)

    #if not config_parser.has_section(self._resource_id):
      #config_file = open(config_path, "w")
      #config_parser.write(config_file)
      #config_file.close()
      #raise ConfigurationError("The configuration can not be saved."
                               #"The resource " + repr(self._resource_id) + " "
                               #"can not be found in the configuration "
                               #"file " + repr(config_path) + ".")

    #self.get_queue_limits()
    #if self._queue_limits != None and len(self._queue_limits):
      #queue_limits_str = ""
      #for queue, limit in self._queue_limits.iteritems():
        #if queue == None:
          #queue_limits_str = queue_limits_str + "{" + repr(limit) + "} "
        #else:
          #queue_limits_str = queue_limits_str + queue + "{" + repr(limit) + "} "
      #print "queue_limits_str " + queue_limits_str
      #config_parser.set(self._resource_id, 
                        #OCFG_MAX_JOB_IN_QUEUE, 
                        #queue_limits_str)

    #config_file = open(config_path, "w")
    #config_parser.write(config_file)
    #config_file.close() 


class LocalSchedulerCfg(observer.Observable):
  '''
  Local scheduler configuration.
  '''

  # number of processus which can run in parallel
  _proc_nb = None

  # interval (second)
  _interval = None

  # path of the configuration file
  _config_path = None


  PROC_NB_CHANGED = 0
  INTERVAL_CHANGED = 1

  def __init__(self, proc_nb=1, interval=1):
    '''
    * proc_nb *int*
      Number of processus which can run in parallel
    
    * interval *int*
      Update interval in second
    '''

    super(LocalSchedulerCfg, self).__init__()
    self._proc_nb = proc_nb
    self._interval = interval


  @classmethod
  def load_from_file(cls,
                     config_file_path=None):

    hostname = socket.gethostname()
    if config_file_path:
      config_path = config_file_path
    else:
      config_path = Configuration.search_config_path()

    config_parser = ConfigParser.ConfigParser()
    config_parser.read(config_path)

    if not config_parser.has_section(hostname):
      raise ConfigurationError("Wrong config file format. Can not find "
                               "section " + hostname + " in configuration " + "file: " + config_path)

    proc_nb = None
    interval = None
    
    if config_parser.has_option(hostname, 
                                OCFG_SCDL_CPU_NB):
      proc_nb_str = config_parser.get(socket.gethostname(),
                                      OCFG_SCDL_CPU_NB)
      proc_nb = int(proc_nb_str)
    if config_parser.has_option(hostname, 
                                OCFG_SCDL_INTERVAL):
      interval_str = config_parser.get(hostname,
                                       OCFG_SCDL_INTERVAL)
      interval = int(interval_str)

    if proc_nb == None and interval == None:
      config = cls()
    elif proc_nb == None and interval != None:
      config = cls(interval=interval)
    else:
      config = cls(proc_nb=proc_nb, interval=interval)
    config._config_path = config_path
    return config

  
  @staticmethod
  def search_config_path():
    '''
    returns the path of the soma workflow configuration file
    '''
    hostname = socket.gethostname()
    home_dir = Configuration.get_home_dir() 
    section_exist = False
    config_path = os.path.join(home_dir, ".soma-workflow-scheduler.cfg")
    if os.path.isfile(config_path):
      config_parser = ConfigParser.ConfigParser()
      config_parser.read(config_path)
      section_exist = config_parser.has_section(hostname)
    if not section_exist:
      config_path = os.path.dirname(__file__)
      config_path = os.path.join(config_path, "etc/soma-workflow-scheduler.cfg")
      if os.path.isfile(config_path):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_path)
        section_exist = config_parser.has_section(hostname)
    if not section_exist:
      config_path = "/etc/soma-workflow-scheduler.cfg"
      if os.path.isfile(config_path):
        config_parser = ConfigParser.ConfigParser()
        config_parser.read(config_path)
        section_exist = config_parser.has_section(hostname)
    if not section_exist:
      config_path = None

    return config_path

  def get_proc_nb(self):
    return self._proc_nb

  def get_interval(self):
    return self._interval

  def set_proc_nb(self, proc_nb):
    self._proc_nb = proc_nb
    self.notifyObservers(LocalSchedulerCfg.PROC_NB_CHANGED)
  
  def set_interval(self, interval):
    self._interval = interval
    self.notifyObservers(LocalSchedulerCfg.INTERVAL_CHANGED)

  def save_to_file(self, config_path=None):
    hostname = socket.gethostname()
    if not config_path:
      if self._config_path != None:
        
        config_path = self._config_path
      else:
        config_path = LocalSchedulerCfg.search_config_path()
        if config_path == None:
          home_dir = Configuration.get_home_dir()
          config_path = os.path.join(home_dir, ".soma-workflow-scheduler.cfg")

    config_parser = ConfigParser.ConfigParser()
    config_parser.read(config_path)

    if not config_parser.has_section(hostname):
      config_parser.add_section(hostname)

    config_parser.set(hostname, 
                      OCFG_SCDL_CPU_NB, 
                      str(self._proc_nb))
    config_parser.set(hostname, 
                      OCFG_SCDL_INTERVAL, 
                      str(self._interval))
    config_file = open(config_path, "w")
    config_parser.write(config_file)
    config_file.close()

