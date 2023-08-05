'''
@author: Soizic Laguitton
@organization: U{IFR 49<http://www.ifr49.org>}
@license: U{CeCILL version 2<http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>}
'''
__docformat__ = "epytext en"

''' 
soma-workflow client classes

The WorkflowController instances allow to submit, control and monitor jobs and
workflows on local or remote resources where the WorkflowDatabaseServer runs.
The contrustor takes a resource id, login and password as parameters and 
connects to the resource. One WorkflowController instance is connected to 
only one resource.

The other classes (Workflow, Job, Group, FileTransfer and SharedResourcePath) are made to build the jobs, workflows, and file transfers 
objects to be used in the WorkflowControler interface.

Definitions:
A Parallel job is a job requiring more than one node to run.
DRMS: distributed resource management system
'''

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import os
import hashlib
import stat
import operator
import random
import pickle

#import cProfile

import soma.workflow.connection as connection
from soma.workflow.constants import *
from soma.workflow.configuration import Configuration

#-------------------------------------------------------------------------------
# Classes and functions
#-------------------------------------------------------------------------------

class Job(object):
  '''
  Job representation.
  
  .. note::
    The command is the only argument required to create a Job.
    It is also useful to fill the job name for the workflow display in the GUI.

  **command**: *sequence of string or/and FileTransfer or/and SharedResourcePath or/and tuple (relative_path, FileTransfer) or/and sequence of FileTransfer or/and sequence of SharedResourcePath or/and sequence of tuple (relative_path, FileTransfers.)*
    
    The command to execute. It can not be empty. In case of a shared file system 
    the command is a sequence of string. 

    In the other cases, the FileTransfer and SharedResourcePath objects will be 
    replaced by the appropriate path before the job execution. 

    The tuples (relative_path, FileTransfer) can be used to refer to a file in a 
    transfered directory.

    The sequences of FileTransfer, SharedResourcePath or tuple (relative_path, 
    FileTransfer) will be replaced by the string "['path1', 'path2', 'path3']" 
    before the job execution. The FileTransfer, SharedResourcePath or tuple
    (relative_path, FileTransfer) are replaced by the appropriate path inside 
    the sequence.

  **name**: *string*
    Name of the Job which will be displayed in the GUI
  
  **referenced_input_files**: *sequence of FileTransfer*
    List of the FileTransfer which are input of the Job. In other words, 
    FileTransfer which are requiered by the Job to run. It includes the
    stdin if you use one.

  **referenced_output_files**: *sequence of FileTransfer*
    List of the FileTransfer which are output of the Job. In other words, the 
    FileTransfer which will be created or modified by the Job.

  **stdin**: *string or FileTransfer or SharedRessourcePath*
    Path to the file which will be read as input stream by the Job.
  
  **join_stderrout**: *boolean*
    Specifies whether the error stream should be mixed with the output stream.

  **stdout_file**: *string or FileTransfer or SharedRessourcePath*
    Path of the file where the standard output stream of the job will be 
    redirected.

  **stderr_file**: *string or FileTransfer or SharedRessourcePath*
    Path of the file where the standard error stream of the job will be 
    redirected.

  .. note::
    Set stdout_file and stderr_file only if you need to redirect the standard 
    output to a specific file. Indeed, even if they are not set the standard
    outputs will always be available through the WorklfowController API.

  **working_directory**: *string or FileTransfer or SharedRessourcePath*
    Path of the directory where the job will be executed. The working directory
    is useful if your Job uses relative file path for example.

  **parallel_job_info**: *tuple(string, int)*
    The parallel job information must be set if the Job is parallel (ie. made to 
    run on several CPU).
    The parallel job information is a tuple: (name of the configuration, 
    maximum number of CPU used by the Job).
    The configuration name is the type of parallel Job. Example: MPI or OpenMP.

  .. warning::
    The computing resources must be configured explicitly to use this feature.

  ..
    **disposal_time_out**: int
    Only requiered outside of a workflow

  '''

  # sequence of sequence of string or/and FileTransfer or/and SharedResourcePath or/and tuple (relative_path, FileTransfer) or/and sequence of FileTransfer or/and sequence of SharedResourcePath or/and sequence of tuple (relative_path, FileTransfers.)
  command = None

  # string
  name = None

  # sequence of FileTransfer
  referenced_input_files = None
  
  # sequence of FileTransfer
  referenced_output_files = None
 
  # string (path)
  stdin = None
  
  # boolean
  join_stderrout = None

  # string (path)
  stdout_file = None
 
  # string (path)
  stderr_file = None
 
  # string (path)
  working_directory = None
  
  # tuple(string, int)
  parallel_job_info = None

  # int (in hours)
  disposal_timeout = None
 
  def __init__( self, 
                command,
                referenced_input_files=None,
                referenced_output_files=None,
                stdin=None,
                join_stderrout=False,
                disposal_timeout=168,
                name=None,
                stdout_file=None,
                stderr_file=None,
                working_directory=None,
                parallel_job_info=None):
    if not name:
      self.name = command[0]
    else:
      self.name = name
    self.command = command
    if referenced_input_files: 
      self.referenced_input_files = referenced_input_files
    else: self.referenced_input_files = set([])
    if referenced_output_files:
      self.referenced_output_files = referenced_output_files
    else: self.referenced_output_files = set([]) 
    self.stdin = stdin
    self.join_stderrout = join_stderrout
    self.disposal_timeout = disposal_timeout
    self.stdout_file = stdout_file
    self.stderr_file = stderr_file
    self.working_directory = working_directory
    self.parallel_job_info = parallel_job_info


class Workflow(object):
  '''
  Workflow representation.

  **jobs**: *sequence of Job*
    Workflow jobs.

  **dependencies**: *sequence of tuple (Job, Job)*
    Dependencies between the jobs of the workflow.
    If a job_a needs to be executed before a job_b can run: the tuple 
    (job_a, job_b) must be added to the workflow dependencies. job_a and job_b
    must belong to workflow.jobs.

  **name**: *string*
    Name of the workflow which will be displayed in the GUI. 
    Default: workflow_id once submitted

  **root_group**: *sequence of Job and/or Group*
    Recursive description of the workflow hierarchical structure. For displaying
    purpose only.

  .. note::
    root_group is only used to display nicely the workflow in the GUI. It
    does not have any impact on the workflow execution.
    
    If root_group is not set, all the jobs of the workflow will be 
    displayed at the root level in the GUI tree view.
  '''
  # string
  name = None

  # sequence of Job
  jobs = None

  # sequence of tuple (Job, Job)
  dependencies = None

  # sequence of Job and/or Group 
  root_group = None

  # sequence of Groups built from the root_group
  groups = None

  def __init__(self, 
               jobs, 
               dependencies, 
               root_group = None,
               disposal_timeout = 168,):

    self.name = None
    self.jobs = jobs
    self.dependencies = dependencies
    self.disposal_timeout = 168
    
    # Groups
    if root_group:
      if isinstance(root_group, Group):
        self.root_group = root_group.elements
      else:
        self.root_group = root_group
      self.groups = []
      to_explore = []
      for element in self.root_group:
        if isinstance(element, Group):
          to_explore.append(element)
      while to_explore:
        group = to_explore.pop()
        self.groups.append(group)
        for element in group.elements:
          if isinstance(element, Group):
            to_explore.append(element)
    else:
      self.root_group = self.jobs
      self.groups = []


  
class Group(object):
  '''
  Hierarchical structure of a workflow.

  .. note:
    It only has a displaying role and does not have any impact on the workflow 
    execution.

  **name**: *string*
    Name of the Group which will be displayed in the GUI.

  **elements**: *sequence of Job and/or Group*
    The elements (Job or Group) belonging to the group.
  '''
  #string
  name = None

  #sequence of Job and/or Group
  elements = None
  
  def __init__(self, elements, name):
    '''
    @type  elements: sequence of Job and/or Group
    @param elements: the elements belonging to the group
    @type  name: string
    @param name: name of the group
    '''
    self.elements = elements
    self.name = name


class FileTransfer(object):
  '''
  File/directory transfer representation
  
  .. note::
    FileTransfers objects are only required if the user and computing resources
    have a separate file system.
  
  **client_path**: *string*
    Path of the file or directory on the user's file system.

  **initial_status**: *constants.FILES_DO_NOT_EXIST or constants.FILES_ON_CLIENT*
    * constants.FILES_ON_CLIENT for workflow input files
      The file(s) will need to be transfered on the computing resource side
    * constants.FILES_DO_NOT_EXIST for workflow output files
      The file(s) will be created by a job on the computing resource side.

  **client_paths**: *sequence of string*
    Sequence of path. Files to transfer if the FileTransfers concerns a file
    series or if the file format involves several associated files or
    directories (see the note below).

  **name**: *string*
    Name of the FileTransfer which will be displayed in the GUI. 
    Default: client_path + "transfer"
 
  .. note::
    Use client_paths if the transfer involves several associated files and/or 
    directories. Examples:

      * file series
      * file format associating several file and/or directories 
        (ex: a SPM images are stored in 2 associated files: .img and .hdr)
        In this case, set client_path to one the files (ex: .img) and 
        client_paths contains all the files (ex: .img and .hdr files)

     In other cases (1 file or 1 directory) the client_paths must be set to None.
  '''

  # string
  client_path = None

  # sequence of string
  client_paths = None

  # constants.FILES_DO_NOT_EXIST constants.FILES_ON_CLIENT
  initial_status = None

  # int (hours)
  disposal_timeout = None

  # string
  name = None

  def __init__( self,
                is_input,
                client_path, 
                disposal_timeout = 168,
                name = None,
                client_paths = None,
                ):
    if name:
      ft_name = name
    else:
      ft_name = client_path + "transfer"
    self.name = ft_name

    self.client_path = client_path
    self.disposal_timeout = disposal_timeout

    self.client_paths = client_paths
  
    if is_input:
      self.initial_status = FILES_ON_CLIENT
    else:
      self.initial_status = FILES_DO_NOT_EXIST


class SharedResourcePath(object):
  '''
  Representation of path which is valid on either user's or computing resource 
  file system.

  .. note::
    SharedResourcePath objects are only required if the user and computing
    resources have a separate file system.

  **namespace**: *string*
    Namespace for the path. That way several applications can use the same 
    identifiers without risk.

  **uuid**: *string*
    Identifier of the absolute path. 

  **relative_path**: *string*
    Relative path of the file if the absolute path is a directory path. 

  .. warning::
    The namespace and uuid must exist in the translations files configured on 
    the computing resource side.  
  '''
  
  relative_path = None
  
  namespace = None

  uuid = None

  def __init__(self,
               relative_path,
               namespace,
               uuid,
               disposal_timeout = 168):
    self.relative_path = relative_path
    self.namespace = namespace
    self.uuid = uuid
    self.disposal_timout = disposal_timeout



class WorkflowController(object):
  '''
  Submission, control and monitoring of Job, FileTransfer and Workflow 
  objects.
  '''

  _mode = None

  _connection = None

  _engine_proxy = None

  config = None
  
  def __init__(self, 
               resource_id, 
               login=None, 
               password=None,
               config_path=None,
               rsa_key_pass=None):
    '''
    Sets up the connection to the computing resource. 
    Looks for a soma-workflow configuration file (if not specified in the 
    *config_path* argument).

    * resource_id *string*
        Identifier of the computing resource to connect to.

    * login *string*
        Required if the computing resource is remote.

    * password *string*
        Required if the computing resource is remote and not RSA key where
        configured to log on the remote machine with ssh.

    * config_path *string*
        Optional path to the configuration file.

    * rsa_key_pass *string*
        Required if the RSA key is protected with a password.

    .. note::
      The login and password are only required for a remote computing resource.
    '''
    
    self.config = Configuration(resource_id)
    self._mode = self.config.get_mode()
    print  self._mode + " mode"

    # LOCAL MODE
    if self._mode == 'local':
      self._connection = connection.LocalConnection(resource_id, "")
      self._engine_proxy = self._connection.get_workflow_engine()
    
    # REMOTE MODE
    elif self._mode == 'remote':
      submitting_machines = self.config.get_submitting_machines()
      sub_machine = submitting_machines[random.randint(0,   
                                                    len(submitting_machines)-1)]
      cluster_address = self.config.get_cluster_address()
      print 'cluster address: ' + cluster_address
      print 'submission machine: ' + sub_machine
      self._connection = connection.RemoteConnection(login, 
                                                     password, 
                                                     cluster_address, 
                                                     sub_machine, 
                                                     resource_id, 
                                                     "",
                                                     rsa_key_pass)
      self._engine_proxy = self._connection.get_workflow_engine()
   
    # LIGHT MODE
    elif self._mode == 'light':
      self._engine_proxy = _embedded_engine_and_server(self.config)
      self._connection = None


  def disconnect(self):
    '''
    Simulates a disconnection for TEST PURPOSE ONLY.
    !!! The current instance will not be usable anymore after this call !!!!
    '''
    if self._connection:
      self._connection.stop()

   

  ########## SUBMISSION / REGISTRATION ####################################
  
  def submit_workflow(self, 
                      workflow, 
                      expiration_date=None, 
                      name=None, 
                      queue=None):
    '''
    Submits a workflow and returns a workflow identifier.
    
    * workflow *client.Workflow*
        Workflow description.
    
    * expiration_date *datetime.datetime*
        After this date the workflow will be deleted.

    * name *string*
        Optional workflow name.

    * queue *string*
        Optional name of the queue where to submit jobs. If it is not specified
        the jobs will be submitted to the default queue.

    * returns: *int*
        Workflow identifier.

    Raises *WorkflowError* or *JobError* if the workflow is not correct.
    '''

    #cProfile.runctx("wf_id = self._engine_proxy.submit_workflow(workflow, expiration_date, name, queue)", globals(), locals(), "/home/soizic/profile/profile_submit_workflow")

    wf_id = self._engine_proxy.submit_workflow(workflow, 
                                               expiration_date, 
                                               name,
                                               queue)
    return wf_id


  def submit_job(self, job, queue=None):
    '''
    Submits a job which is not part of a workflow.
    Returns a job identifier.

    If the job used transfered files the list of involved file transfer **must 
    be** specified setting the arguments: *referenced_input_files* and 
    *referenced_output_files*.
    
    Each path must be reachable from the computing resource.
  
    * job *client.Job*

    * queue *string*
        Name of the queue where to submit the jobs. If it is not 
        specified the job will be submitted to the default queue.

    * returns: int
      Job identifier.
  
    Raises *JobError* if the job is not correct.
    '''
   
    engine_job = self._engine_proxy.submit_job(job, queue)
    return engine_job


  def register_transfer(self, file_transfer):
    '''
    Registers a file transfer which is not part of a workflow and returns a 
    file transfer identifier.
    
    * file_transfer *client.FileTransfer*

    * returns *EngineTransfer*
    '''

    engine_transfer = self._engine_proxy.register_transfer(file_transfer)
    return engine_transfer

  ########## WORKFLOWS, JOBS and FILE TRANSFERS RETRIEVAL ###################

  def workflow(self, workflow_id):
    '''
    * workflow_id *workflow_identifier*
    
    * returns: *Workflow*
  
    Raises *UnknownObjectError* if the workflow_id is not valid
    '''
    return self._engine_proxy.workflow(workflow_id)

  def workflows(self, workflow_ids=None):
    '''
    Lists the identifiers and general information about all the workflows 
    submitted by the user, or about the workflows specified in the 
    *workflow_ids* argument.  

    * workflow_ids *sequence of workflow identifiers*
  
    * returns: *dictionary: workflow identifier -> tuple(date, string)*
        workflow_id -> (workflow_name, expiration_date)
    '''
    return self._engine_proxy.workflows(workflow_ids)


  def jobs(self, job_ids=None):
    '''
    Lists the identifiers and general information about all the jobs submitted 
    by the user and which are not part of a workflow, or about the jobs 
    specified in the *job_ids* argument.

    * job_ids *sequence of job identifiers*

    * returns: *dictionary: job identifiers -> tuple(string, string, date)*
        job_id -> (name, command, submission date)
    '''
    return self._engine_proxy.jobs(job_ids)


  def transfers(self, transfer_ids=None):
    '''
    Lists the identifiers and information about all the user's file transfers 
    which are not part of a workflow or about the file transfers specified in
    the *transfer_ids* argument.

    * transfer_ids *sequence of FileTransfer identifiers*
        
    * returns: *dictionary: string -> tuple(string, date, None or sequence of string)*
        transfer_id -> (
                        * client_path: client file or directory path
                        * expiration_date: after this date the file copied
                          on the computing resource and all the transfer 
                          information will be deleted, unless an existing 
                          job has declared this file as output or input.
                        * client_paths: sequence of file or directory path or None)
    '''
    return self._engine_proxy.transfers(transfer_ids)

  ########## WORKFLOW MONITORING #########################################

  def workflow_status(self, workflow_id):
    '''
    * workflow_id *workflow identifier*
      
    * returns: *string or None*
        Status of the workflow: see :ref:`workflow-status` or the 
        constants.WORKFLOW_STATUS list.

    Raises *UnknownObjectError* if the workflow_id is not valid
    '''
    return self._engine_proxy.workflow_status(workflow_id)
  
  
  def workflow_elements_status(self, workflow_id, group = None):
    '''
    Gets back the status of all the workflow elements at once, minimizing the
    communication with the server and request to the database.
    TO DO => make it more user friendly.
    
    * workflow_id *workflow identifier*

    * returns: tuple (sequence of tuple (job_id, status, exit_info, (submission_date, execution_date, ending_date)), sequence of tuple (transfer_id, (status, progression_info)), workflow_status)

    Raises *UnknownObjectError* if the workflow_id is not valid
    '''
    wf_status = self._engine_proxy.workflow_elements_status(workflow_id)
     # special processing for transfer status:
    new_transfer_status = []
    for engine_path, client_path, status, transfer_action_info in wf_status[1]:
      progression = self._transfer_progress(engine_path, 
                                            client_path, 
                                            transfer_action_info)
      new_transfer_status.append((engine_path, (status, progression)))
      
    new_wf_status = (wf_status[0],new_transfer_status, wf_status[2])
    return new_wf_status


  ########## JOB MONITORING #############################################

  def job_status( self, job_id ):
    '''
    * job_id *job identifier*
      
    * returns: *string*
        Status of the job: see :ref:`job-status` or the list 
        constants.JOB_STATUS.
    
    Raises *UnknownObjectError* if the job_id is not valid
    '''
    return self._engine_proxy.job_status(job_id)


  def job_termination_status(self, job_id ):
    '''
    Information related to the end of the job.
   
    * job_id *job identifier*

    * returns: *tuple(string, int or None, string or None, string) or None*
        * exit status: status of the terminated job: see 
          :ref:`job-exit-status` or the constants.JOB_EXIT_STATUS list.
        * exit value: operating system exit code of the job if the job 
          terminated normally.
        * terminating signal: representation of the signal that caused the 
          termination of the job if the job terminated due to the receipt of 
          a signal.
        * resource usage: resource usage information provided as an array of 
          strings where each string complies with the format <name>=<value>.
          The information provided depends on the DRMS and DRMAA implementation.

    Raises *UnknownObjectError* if the job_id is not valid
    '''
    return self._engine_proxy.job_termination_status(job_id)


  def retrieve_job_stdouterr(self, 
                             job_id, 
                             stdout_file_path, 
                             stderr_file_path = None, 
                             buffer_size = 512**2):
    '''
    Copies the job standard output and error to specified file.

    * job_id *job identifier*

    * stdout_file_path *string*
        Path of the file where to copy the standard output.

    * stderr_file_path *string*
        Path of the file where to copy the standard error.

    * buffer_size *int*
        The file is transfered piece by piece of size buffer_size.

    Raises *UnknownObjectError* if the job_id is not valid
    '''
    
    engine_stdout_file, stdout_transfer_action_info, engine_stderr_file, stderr_transfer_action_info = self._engine_proxy.stdouterr_transfer_action_info(job_id)
    
    open(stdout_file_path, 'wb') 
    if engine_stdout_file and stdout_transfer_action_info:
      self._transfer_file_from_cr(stdout_file_path, 
                                  engine_stdout_file, 
                                  stdout_transfer_action_info[0], 
                                  stdout_transfer_action_info[1], 
                                  buffer_size)
  
    if stderr_file_path:
      open(stderr_file_path, 'wb') 
      if engine_stderr_file and stderr_transfer_action_info:
          self._transfer_file_from_cr(stderr_file_path, 
                                      engine_stderr_file, 
                                      stderr_transfer_action_info[0], 
                                      stderr_transfer_action_info[1], 
                                      buffer_size)
    

  ########## FILE TRANSFER MONITORING ###################################

  def transfer_status(self, transfer_id):
    '''
    File transfer status and information related to the transfer progress.

    * transfer_id *transfer identifier*

    * returns: *tuple(transfer_status or None, tuple or None)*
        * Status of the file transfer : see :ref:`file-transfer-status` or the    
          constants.FILE_TRANSFER_STATUS list.
        * None if the transfer status in not 
          constants.TRANSFERING_FROM_CLIENT_TO_CR or 
          constants.TRANSFERING_FROM_CR_TO_CLIENT.
          tuple (file size, size already transfered) if it is a file transfer.
          tuple (cumulated size, sequence of tuple (relative_path, file_size, size already transfered) if it is a directory transfer.

    Raises *UnknownObjectError* if the transfer_id is not valid 
    '''
    
    status = self._engine_proxy.transfer_status(transfer_id)
    transfer_action_info =  self._engine_proxy.transfer_action_info(transfer_id)
    transfer_id, client_path, expiration_date, workflow_id, client_paths = self._engine_proxy.transfer_information(transfer_id)
    progression = self._transfer_progress(transfer_id, client_path, transfer_action_info)
    return (status, progression)


  ########## WORKFLOW CONTROL ############################################

  def restart_workflow(self, workflow_id):
    '''
    Restarts the jobs of the workflow which failed. The jobs will be submitted
    again. 
    The workflow status has to be constants.WORKFLOW_DONE.
    
    * workflow_id *workflow identifier*

    * returns: *boolean* 
        True if some jobs were restarted.
    
    Raises *UnknownObjectError* if the workflow_id is not valid
    '''
    return self._engine_proxy.restart_workflow(workflow_id)
    

  def delete_workflow(self, workflow_id):
    '''
    Deletes the workflow and all its associated elements (FileTransfers and Jobs). The worklfow_id will become invalid and can not be used anymore. The workflow jobs which are running will be killed.

    Raises *UnknownObjectError* if the workflow_id is not valid
    '''
    #cProfile.runctx("self._engine_proxy.delete_workflow(workflow_id)", globals(), locals(), "/home/soizic/profile/profile_delete_workflow")

    self._engine_proxy.delete_workflow(workflow_id)


  def change_workflow_expiration_date(self, workflow_id, new_expiration_date):
    '''
    Sets a new expiration date for the workflow.
      
    * workflow_id *workflow identifier*

    * new_expiration_date *datetime.datetime*
    
    * returns: *boolean* 
        True if the expiration date was changed.

    Raises *UnknownObjectError* if the workflow_id is not valid
    '''
    return self._engine_proxy.change_workflow_expiration_date(workflow_id, new_expiration_date)


  ########## JOB CONTROL #################################################

  def wait_job( self, job_ids, timeout = -1):
    '''
    Waits for all the specified jobs to finish. 
    
    * job_ids *sequence of job identifier* 
        Jobs to wait for.

    * timeout *int* 
        The call to wait_job exits before timeout seconds.
        A negative value means that the method will wait indefinetely.

    Raises *UnknownObjectError* if the job_id is not valid
    '''
    self._engine_proxy.wait_job(job_ids, timeout)

  def kill_job( self, job_id ):
    '''
    Kills a running job. The job will not be deleted from the system (the job
    identifier remains valid). 
    Use the restart_job method to restart the job.

    Raises *UnknownObjectError* if the job_id is not valid
    '''
    self._engine_proxy.kill_job(job_id)
   
  
  def restart_job( self, job_id ):
    '''   
    Restarts a job which status is constants.FAILED or constants.WARNING.
   
    * job_id *job identifier*
    * returns: *boolean* 
        True if the job was restarted.

    Raises *UnknownObjectError* if the job_id is not valid
    '''
    self._engine_proxy.restart_job(job_id)


  def delete_job( self, job_id ):
    '''
    Deletes a job which is not part of a workflow.
    The job_id will become invalid and can not be used anymore.
    The job is killed if it is running.

    Raises *UnknownObjectError* if the job_id is not valid
    '''
    
    self._engine_proxy.delete_job(job_id)


  ########## FILE TRANSFER CONTROL #######################################

  def transfer_files(self, transfer_id, buffer_size = 512**2):
    '''
    Transfer file(s) associated to the transfer_id.
    If the files are only located on the client side (that is the transfer 
    status is constants.FILES_ON_CLIENT) the file(s) will be transfered from the 
    client to the computing resource.
    If the files are located on the computing resource side (that is the 
    transfer status is constants.FILES_ON_CR or 
    constants.FILES_ON_CLIENT_AND_CR) 
    the files will be transfered from the computing resource to the client.

    * transfer_id *FileTransfer identifier*

    * buffer_size *int*
        The files are transfered piece by piece. The size of each piece can be
        tuned using the buffer_size argument.

    * returns: *boolean*
        The transfer was done. (TBI right error management)

    Raises *UnknownObjectError* if the transfer_id is not valid 
    '''

    status, status_info = self.transfer_status(transfer_id)
    transfer_id, client_path, expiration_date, workflow_id, client_paths = self._engine_proxy.transfer_information(transfer_id)

    transfer_action_info = self._engine_proxy.transfer_action_info(transfer_id)

    if status == FILES_ON_CLIENT or \
       status == TRANSFERING_FROM_CLIENT_TO_CR:
      # transfer from client to computing resource
      transfer_from_scratch = False
      if not transfer_action_info or \
         transfer_action_info[2] == TR_FILE_CR_TO_C or \
         transfer_action_info[2] == TR_DIR_CR_TO_C or \
         transfer_action_info[2] == TR_MFF_CR_TO_C:
        # transfer reset
        transfer_from_scratch = True
        transfer_action_info = self.initialize_transfer(transfer_id)
      
      if transfer_action_info[2] == TR_FILE_C_TO_CR:
        if not transfer_from_scratch:
          transmitted = status_info[2]
          #(file_size, transmitted) = self._engine_proxy.transfer_progression_status(engine_path, transfer_action_info)
        else:
          transmitted = 0
        self._transfer_file_to_cr(client_path,
                                  transfer_id,
                                  buffer_size,
                                  transmitted)
        return True

      if transfer_action_info[2] == TR_DIR_C_TO_CR:
        for relative_path in transfer_action_info[1]:
          transfer_ended = False 
          if transfer_from_scratch:
              transmitted = 0
          else:
            for r_path, f_size, trans in status_info[2]:
              if r_path == relative_path:
                transmitted = trans
                transfer_ended = f_size == trans
                break
          if not transfer_ended:
            self._transfer_file_to_cr(client_path, 
                            transfer_id, 
                            buffer_size,
                            transmitted=transmitted,
                            relative_path=relative_path)
        return True

      if transfer_action_info[2] == TR_MFF_C_TO_CR:
        for relative_path in transfer_action_info[1]:
          transfer_ended = False 
          if transfer_from_scratch:
              transmitted = 0
          else:
            for r_path, f_size, trans in status_info[2]:
              if r_path == relative_path:
                transmitted = trans
                transfer_ended = f_size == trans
                break
          if not transfer_ended:
            self._transfer_file_to_cr(os.path.dirname(client_path), 
                                      transfer_id, 
                                      buffer_size, 
                                      transmitted=transmitted,
                                      relative_path=relative_path)
        return True

      return False

    if status == FILES_ON_CR or \
       status == TRANSFERING_FROM_CR_TO_CLIENT or \
       status == FILES_ON_CLIENT_AND_CR:
      # transfer from computing resource to client
      transfer_from_scratch = False
      if not transfer_action_info or \
         transfer_action_info[2] == TR_FILE_C_TO_CR or \
         transfer_action_info[2] == TR_DIR_C_TO_CR or \
         transfer_action_info[2] == TR_MFF_C_TO_CR :
        transfer_action_info = self.initialize_transfer(transfer_id)
        transfer_from_scratch = True
        # TBI remove existing files 

      if transfer_action_info[2] == TR_FILE_CR_TO_C:
        # file case
        (file_size, md5_hash, transfer_type) = transfer_action_info
        self._transfer_file_from_cr(client_path, 
                                    transfer_id, 
                                    file_size, 
                                    md5_hash, 
                                    buffer_size)
        return True
      if transfer_action_info[2] == TR_DIR_CR_TO_C:
        (cumulated_file_size, file_transfer_info, transfer_type) = transfer_action_info
        for relative_path, file_info in file_transfer_info.iteritems(): 
          (file_size, md5_hash) = file_info
          self._transfer_file_from_cr(client_path, 
                                      transfer_id, 
                                      file_size, 
                                      md5_hash, 
                                      buffer_size,
                                      relative_path)

        return True
      if transfer_action_info[2] == TR_MFF_CR_TO_C:
        (cumulated_file_size, file_transfer_info, transfer_type) = transfer_action_info
        for relative_path, file_info in file_transfer_info.iteritems(): 
          (file_size, md5_hash) = file_info
          self._transfer_file_from_cr(os.path.dirname(client_path), 
                                      transfer_id, 
                                      file_size, 
                                      md5_hash, 
                                      buffer_size,
                                      relative_path)
        return True 

      return False
    
 

  def initialize_transfer(self, transfer_id):
    '''
    Initializes the transfer and returns the transfer action information.

    * transfer_id *FileTransfer identifier*

    * returns: *tuple*
        * (file_size, md5_hash) in the case of a file transfer
        * (cumulated_size, dictionary relative path -> (file_size, md5_hash)) in
          case of a directory transfer.

    Raises *UnknownObjectError* if the transfer_id is not valid 
    '''
    status = self._engine_proxy.transfer_status(transfer_id)
    transfer_id, client_path, expiration_date, workflow_id, client_paths = self._engine_proxy.transfer_information(transfer_id)

    if status == FILES_ON_CLIENT:
      if not client_paths:
        if os.path.isfile(client_path):
          stat = os.stat(client_path)
          file_size = stat.st_size
          md5_hash = hashlib.md5( open( client_path, 'rb' ).read() ).hexdigest() 
          transfer_action_info = self._engine_proxy.init_file_transfer_to_cr(transfer_id, 
                                                      file_size, 
                                                      md5_hash)
        elif os.path.isdir(client_path):
          full_path_list = []
          for element in os.listdir(client_path):
            full_path_list.append(os.path.join(client_path, element))
          content = WorkflowController.dir_content(full_path_list)
          transfer_action_info = self._engine_proxy.init_dir_transfer_to_cr(transfer_id, 
                                                     content,
                                                     TR_DIR_C_TO_CR)

      else: #client_paths
        content = WorkflowController.dir_content(client_paths)
        transfer_action_info = self._engine_proxy.init_dir_transfer_to_cr(transfer_id,
                                                   content,
                                                   TR_MFF_C_TO_CR)
      return transfer_action_info
    elif status == FILES_ON_CR or FILES_ON_CLIENT_AND_CR:
      (transfer_action_info, dir_content) = self._engine_proxy.init_transfer_from_cr(transfer_id)
      if transfer_action_info[2] == TR_MFF_CR_TO_C:
        WorkflowController.create_dir_structure(os.path.dirname(client_path), 
                                                dir_content)
      if transfer_action_info[2] == TR_DIR_CR_TO_C:
        WorkflowController.create_dir_structure(client_path, 
                                                dir_content)
      return transfer_action_info
    
    return None
  


  def write_to_computing_resource_file(self, 
                                       transfer_id, 
                                       data, 
                                       relative_path=None):
    '''
    Writes a piece of data to a file located on the computing resource.

    * transfer_id *FileTransfer identifier*

    * data *string* to write to the file.

    * relative_path *string*
         Mandatory in case of a directory transfer to identify the file.
         None in case of a file transfer.

    * returns: *boolean*
        True if the file transfer ended. (TBI right error management)
        Note that in case of a directory transfer, it does not mean that the 
        whole directory transfer ended. 

    Raises *UnknownObjectError* if the transfer_id is not valid 
    '''

    status = self._engine_proxy.transfer_status(transfer_id)
    if not status == TRANSFERING_FROM_CLIENT_TO_CR:
      self.initialize_transfer(transfer_id)
    transfer_ended = self._engine_proxy.write_to_computing_resource_file(
                                                                  transfer_id, 
                                                                  data, 
                                                                 relative_path)
    return transfer_ended


  def read_from_computing_resource_file(self, 
                                        transfer_id, 
                                        buffer_size, 
                                        transmitted,
                                        relative_path=None):
    '''
    Reads a piece of data from a file located on the computing resource.

    * transfer_id *FileTransfer identifier*

    * buffer_size *int*
        Size of the data to read.

    * transmitted *int* 
        Size of the data already read.

    * relative_path *string*
        Mandatory in case of a directory transfer to identify the file.
        None in case of a file transfer.

    * returns: *string* read from the file at the position *transmitted*

    '''
    
    data = self._engine_proxy.read_from_computing_resource_file(transfer_id, 
                                                                buffer_size, 
                                                                transmitted,
                                                                relative_path)
    if not data:
      # check if the whole transfer ended
      transfer_action_info = self._engine_proxy.transfer_action_info(transfer_id)
      if not transfer_action_info == None: # None if stdout and stderr
        assert(transfer_action_info[2] == TR_FILE_CR_TO_C or        
              transfer_action_info[2] == TR_DIR_CR_TO_C or 
              transfer_action_info[2] == TR_MFF_CR_TO_C)
        (status, progression) = self.transfer_status(transfer_id)
        if transfer_action_info[2] == TR_FILE_CR_TO_C:
          (file_size, transfered) = progression
          if file_size == transfered:
            self._engine_proxy.set_transfer_status(transfer_id,   
                                                  FILES_ON_CLIENT_AND_CR)
        if transfer_action_info[2] == TR_DIR_CR_TO_C or \
          transfer_action_info[2] == TR_MFF_CR_TO_C:
          (cumulated_file_size, 
          cumulated_transmissions, 
          files_transfer_status) = progression
          if cumulated_transmissions == cumulated_file_size:
            self._engine_proxy.set_transfer_status(transfer_id,   
                                                  FILES_ON_CLIENT_AND_CR)

    return data


  def delete_transfer(self, transfer_id):
    '''
    Deletes the FileTransfer and the associated files and directories on the 
    computing resource side. The transfer_id will become invalid and can not be 
    used anymore. If some jobs reference the FileTransfer as an input or an 
    output the FileTransfer will not be deleted immediately but as soon as these 
    jobs will be deleted.

    Raises *UnknownObjectError* if the transfer_id is not valid
    '''
    self._engine_proxy.delete_transfer(transfer_id)


  ########## PRIVATE #############################################          

  def _transfer_file_to_cr(self, 
                           client_path, 
                           engine_path, 
                           buffer_size = 512**2, 
                           transmitted = 0, 
                           relative_path = None):
    '''
    Transfer a file from the client to the computing resource.

    @param client_path: file path on the client side
    @param engine_path: file path on the computing resource side
    @param buffer_size: the file is transfered piece by piece of size buffer_size
    @param transmitted: size already transfered
    '''
      
    if relative_path:
      r_path = os.path.join(client_path, relative_path)
    else:
      r_path = client_path
    f = open(r_path, 'rb')
    if transmitted:
      f.seek(transmitted)
    transfer_ended = False
    while not transfer_ended:
      transfer_ended = self.write_to_computing_resource_file(engine_path,   
                                                       f.read(buffer_size),
                                                       relative_path)
    f.close()


  def _transfer_file_from_cr(self, 
                             client_path, 
                             engine_path, 
                             file_size, 
                             md5_hash, 
                             buffer_size = 512**2, 
                             relative_path = None):
    '''
    Transfer a file from the computing resource to client side.

    @param client_path: file path on the client side
    @param engine_path: file path on the computing resource side
    @param buffer_size: the file is transfered piece by piece of size buffer_size
    @param transmitted: size already transfered
    '''
    if relative_path:
      r_path = os.path.join(client_path, relative_path)
    else:
      r_path = client_path
    print "copy file to " + repr(r_path)
    f = open(r_path, 'ab')
    fs = f.tell()
    #if fs > file_size:
      #open(r_path, 'wb')
    data = self.read_from_computing_resource_file(engine_path, 
                                                  buffer_size, 
                                                  fs, 
                                                  relative_path)
    f.write(data)
    fs = f.tell()
    while data:
      data = self.read_from_computing_resource_file(engine_path, 
                                                    buffer_size, 
                                                    fs, 
                                                    relative_path)
      f.write(data)
      fs = f.tell()

    if fs > file_size:
        f.close()
        open(r_path, 'wb')
        raise Exception('read_from_computing_resource_file: Transmitted data exceed expected file size.')
    else:
      if md5_hash is not None and \
         hashlib.md5( open( r_path, 'rb' ).read() ).hexdigest() != md5_hash:
          # Reset file
          f.close()
          open( r_path, 'wb' )
          raise Exception('read_from_computing_resource_file: Transmission error detected.')
    f.close()


            
  def _transfer_progress(self, engine_path, client_path, transfer_action_info):
    progression_info = None
    if transfer_action_info == None :
      return None
    if transfer_action_info[2] == TR_FILE_C_TO_CR or \
       transfer_action_info[2] == TR_DIR_C_TO_CR or \
       transfer_action_info[2] == TR_MFF_C_TO_CR:
      return self._engine_proxy.transfer_progression_status(engine_path, 
                                                            transfer_action_info)

    if transfer_action_info[2] == TR_FILE_CR_TO_C:
      (file_size, md5_hash, transfer_type) = transfer_action_info
      if os.path.isfile(client_path):
        transmitted = os.stat(client_path).st_size
      else:
        transmitted = 0
      return (file_size, transmitted)

    elif transfer_action_info[2] == TR_MFF_CR_TO_C or \
         transfer_action_info[2] == TR_DIR_CR_TO_C:
      (cumulated_file_size, 
       dir_element_action_info, 
       transfer_type) = transfer_action_info
      files_transfer_status = []
      for relative_path, (file_size, md5_hash) in dir_element_action_info.iteritems():
        if transfer_type == TR_MFF_CR_TO_C:
          full_path = os.path.join(os.path.dirname(client_path), 
                                   relative_path)
        else: #TR_DIR_CR_TO_C
          full_path = os.path.join(client_path, 
                                   relative_path)
        if os.path.isfile(full_path):
          transmitted = os.stat(full_path).st_size
        else:
          transmitted = 0
        files_transfer_status.append((relative_path, file_size, transmitted))
      cumulated_transmissions = reduce( operator.add, (i[2] for i in files_transfer_status) )
      return (cumulated_file_size, 
              cumulated_transmissions, 
              files_transfer_status)
       
    return None
    
  @staticmethod
  def dir_content(path_seq, md5_hash=False):
    result = []
    for path in path_seq:
      s = os.stat(path)
      if stat.S_ISDIR(s.st_mode):
        full_path_list = []
        for element in os.listdir(path):
          full_path_list.append(os.path.join(path, element))
        content = WorkflowController.dir_content(full_path_list, md5_hash)
        result.append((os.path.basename(path), content, None))
      else:
        if md5_hash:
          result.append( ( os.path.basename(path), s.st_size, hashlib.md5( open( path, 'rb' ).read() ).hexdigest() ) )
        else:
          result.append( ( os.path.basename(path), s.st_size, None ) )
    return result

  @staticmethod     
  def create_dir_structure(path, content, subdirectory = ""):
    if not os.path.isdir(path):
      os.makedirs(path)
    for item, description, md5_hash in content:
      relative_path = os.path.join(subdirectory,item)
      full_path = os.path.join(path, relative_path)
      if isinstance(description, list):
        if not os.path.isdir(full_path):
          os.mkdir(full_path)
        WorkflowController.create_dir_structure(path, description, relative_path)

 
def _embedded_engine_and_server(config):
  '''
  Creates the workflow engine and workflow database server in the client 
  process.
  The client process can not finish before the workflows and jobs are done.
  Using serveral client process simultaneously (thus several database server 
  with the same database file) can cause error (notably database locked problems) 

  * config: *soma.workflow.configuration.Configuration*

  * returns: *WorkflowEngine*
  '''
  import logging

  from soma.workflow.engine import Drmaa, WorkflowEngine, WorkflowEngineLoop, EngineLoopThread
  from soma.workflow.database_server import WorkflowDatabaseServer
  
  (engine_log_dir,
   engine_log_format,
   engine_log_level) = config.get_engine_log_info()
  if engine_log_dir:
    logfilepath = engine_log_dir + "log_light_mode"
    logging.basicConfig(
        filename=logfilepath,
        format=engine_log_format,
        level=eval("logging." + engine_log_level))
    logger = logging.getLogger('engine')
    logger.info(" ")
    logger.info("****************************************************")
    logger.info("****************************************************")

  # database server
  database_server = WorkflowDatabaseServer(config.get_database_file(), 
                                           config.get_transfered_file_dir())

  drmaa = Drmaa(config.get_drmaa_implementation(), 
                config.get_parallel_job_config())

  engine_loop = WorkflowEngineLoop(database_server,
                                   drmaa,
                                   config.get_path_translation(),
                                   config.get_queue_limits())

  workflow_engine = WorkflowEngine(database_server, 
                                   engine_loop)

  engine_loop_thread = EngineLoopThread(engine_loop)
  engine_loop_thread.setDaemon(True)
  engine_loop_thread.start()

  return workflow_engine


class Helper(object):

  def __init__(self):
    pass


  @staticmethod
  def transfer_input_files(workflow, 
                           wf_ctrl, 
                           buffer_size = 512**2):
    to_transfer = []
    for ft in workflow.registered_tr.itervalues():
      status, info = wf_ctrl.transfer_status(ft.engine_path)
      if status == FILES_ON_CLIENT:
        to_transfer.append((0, ft.engine_path))
      if status == TRANSFERING_FROM_CLIENT_TO_CR:
        to_transfer.append((info[1], ft.engine_path))
          
    to_transfer = sorted(to_transfer, key = lambda element: element[1])
    for transmitted, engine_path in to_transfer:
      wf_ctrl.transfer_files(engine_path, buffer_size)


  @staticmethod
  def transfer_output_files(workflow,
                            wf_ctrl,
                            buffer_size = 512**2):
    to_transfer = []
    for ft in workflow.registered_tr.itervalues():
      status, info = wf_ctrl.transfer_status(ft.engine_path)
      if status == FILES_ON_CR:
        to_transfer.append((0, ft.engine_path))
      if status == TRANSFERING_FROM_CR_TO_CLIENT:
        to_transfer.append((info[1], ft.engine_path))

    to_transfer = sorted(to_transfer, key = lambda element: element[1])
    for transmitted, engine_path in to_transfer:
      print "retrieve " + engine_path + " already transmitted size" + repr(transmitted)
      wf_ctrl.transfer_files(engine_path, buffer_size)


  @staticmethod
  def serialize(file_path, workflow):
    try:
      file = open(file_path, "w")
      pickle.dump(workflow, file)
      file.close()
    except Exception, e:
      raise SerializationError("%s: %s" %(type(e), e))

  @staticmethod
  def unserialize(file_path):
    try:
      file = open(file_path, "r")
      workflow = pickle.load(file)
      file.close()
    except Exception, e:
      raise SerializationError("%s: %s" %(type(e), e))
    return workflow




