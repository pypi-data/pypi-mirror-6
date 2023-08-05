# -*- coding: utf-8 -*-
'''
@author: Soizic Laguitton
@organization: U{IFR 49<http://www.ifr49.org>}
@license: U{CeCILL version 2<http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>}
'''

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import soma.workflow.constants as constants

#-------------------------------------------------------------------------------
# Classes and functions
#-------------------------------------------------------------------------------


class Job(object):
  '''
  Job representation.

  .. note::
    The command is the only argument required to create a Job.
    It is also useful to fill the job name for the workflow display in the GUI.

  **command**: *sequence of string or/and FileTransfer or/and SharedResourcePath or/and tuple (FileTransfer, relative_path) or/and sequence of FileTransfer or/and sequence of SharedResourcePath or/and sequence of tuple (FileTransfer, relative_path)*

    The command to execute. It can not be empty. In case of a shared file system
    the command is a sequence of string.

    In the other cases, the FileTransfer and SharedResourcePath objects will be
    replaced by the appropriate path before the job execution.

    The tuples (FileTransfer, relative_path) can be used to refer to a file in a
    transfered directory.

    The sequences of FileTransfer, SharedResourcePath or tuple (FileTransfer,
    relative_path) will be replaced by the string "['path1', 'path2', 'path3']"
    before the job execution. The FileTransfer, SharedResourcePath or tuple
    (FileTransfer, relative_path) are replaced by the appropriate path inside
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

  **priority**: *int*
    Job priority: 0 = low priority. If several Jobs are ready to run at the 
    same time the jobs with higher priority will be submitted first.

  **native_specification**: *string*
    Some specific option/function of the computing resource you want to use 
    might not be available among the list of Soma-workflow Job attributes.
    Use the native specification attribute to use these specific functionalities. 
    If a native_specification is defined here, the configured native 
    specification will be ignored (documentation configuration item: NATIVE_SPECIFICATION).

    *Example:* Specification of a job walltime and more:
      * using a PBS cluster: native_specification="-l walltime=10:00:00,pmem=16gb" 
      * using a SGE cluster: native_specification="-l h_rt=10:00:00"

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

  # int 
  priority = None

  # string
  native_specification = None

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
                parallel_job_info=None,
                priority=0,
                native_specification=None):
    if not name:
      self.name = command[0]
    else:
      self.name = name
    self.command = command
    if referenced_input_files:
      self.referenced_input_files = referenced_input_files
    else: self.referenced_input_files = []
    if referenced_output_files:
      self.referenced_output_files = referenced_output_files
    else: self.referenced_output_files = []
    self.stdin = stdin
    self.join_stderrout = join_stderrout
    self.disposal_timeout = disposal_timeout
    self.stdout_file = stdout_file
    self.stderr_file = stderr_file
    self.working_directory = working_directory
    self.parallel_job_info = parallel_job_info
    self.priority = priority
    self.native_specification = native_specification

  
  def _attributs_equal(self, el_list, other_el_list):
    if not len(el_list) == len(other_el_list):
      return False
    for i in range(0, len(el_list)):
      if isinstance(el_list[i], FileTransfer) or\
         isinstance(el_list[i], SharedResourcePath):
        if not el_list[i].attributs_equal(other_el_list[i]):
          return False
      elif isinstance(el_list[i], tuple):
        if not isinstance(other_el_list[i], tuple) or\
           not len(el_list[i]) == len(other_el_list[i]):
          return False
        if not el_list[i][0].attributs_equal(other_el_list[i][0]):
          return False
        if not el_list[i][1] == other_el_list[i][1]:
          return False
      elif isinstance(el_list[i], list):
        if not isinstance(other_el_list[i], list):
          return False
        if not self._attributs_equal(el_list[i], other_el_list[i]):
          return False
      elif not el_list[i] == other_el_list[i]:
        return False
    return True

  def attributs_equal(self, other):
    # TODO a better solution would be to overload __eq__ and __neq__ operator
    # however these operators are used in soma-workflow to test if 
    # two objects are the same instancete. These tests have to be replaced 
    # first using the id python function.
    if not isinstance(other, self.__class__):
      return False
    seq_attributs = [
                     "command", 
                     "referenced_input_files",
                     "referenced_output_files"]
    for attr_name in seq_attributs:
      attr = getattr(self, attr_name)
      other_attr = getattr(other, attr_name)
      if not self._attributs_equal(attr, other_attr):
        return False

    attributs = [
                 "name", 
                 "stdin",
                 "join_stderrout",
                 "stdout_file",
                 "stderr_file",
                 "working_directory",
                 "priority",
                 "native_specification",
                 "parallel_job_info",
                 "disposal_timeout",
                 ]
    for attr_name in attributs:
      attr = getattr(self, attr_name)
      other_attr = getattr(other, attr_name)
      if isinstance(attr, FileTransfer) or\
         isinstance(attr, SharedResourcePath):
        if not attr.attributs_equal(other_attr):
          return False
      elif not attr == other_attr:
        return False
    return True


  @classmethod
  def from_dict(cls,
                d, 
                tr_from_ids,
                srp_from_ids):
    '''
     * d *dictionary*
     * tr_from_id *id -> FileTransfer*
     * srp_from_id *id -> SharedResourcePath*
    '''
    job = cls(command=d["command"])
    for key, value in d.iteritems():
      setattr(job, key, value)
  
    new_command = list_from_serializable(job.command,
                                       tr_from_ids,
                                       srp_from_ids)
    job.command = new_command
  
    if job.referenced_input_files:
      ref_in_files = list_from_serializable(job.referenced_input_files,
                                          tr_from_ids,
                                          srp_from_ids)
      job.referenced_input_files = ref_in_files
  
    if job.referenced_output_files:
      ref_out_files = list_from_serializable(job.referenced_output_files,
                                           tr_from_ids,
                                           srp_from_ids)
      job.referenced_output_files = ref_out_files
  
    if job.stdin:
      job.stdin = from_serializable(job.stdin,
                                    tr_from_ids,
                                    srp_from_ids)
    if job.stdout_file:
      job.stdout_file = from_serializable(job.stdout_file,
                                          tr_from_ids,
                                          srp_from_ids)
    if job.stderr_file:
      job.stderr_file = from_serializable(job.stderr_file,
                                          tr_from_ids,
                                          srp_from_ids)
    if job.working_directory:  
      job.working_directory = from_serializable(job.working_directory,
                                                tr_from_ids,
                                                srp_from_ids)
  
    return job
  
  def to_dict(self,
              id_generator, 
              transfer_ids, 
              shared_res_path_id):
    '''
    * id_generator *IdGenerator*
    * transfer_ids *dict: client.FileTransfer -> int*
        This dictonary will be modified.
    * shared_res_path_id *dict: client.SharedResourcePath -> int*
        This dictonary will be modified.
    '''
    job_dict = {}
  
    attributs = [
                 "name", 
                 "join_stderrout",
                 "priority",
                 "native_specification",
                 "parallel_job_info",
                 "disposal_timeout",
                ]
  
    for attr_name in attributs:
      job_dict[attr_name] = getattr(self, attr_name)
  
    # command, referenced_input_files, referenced_output_files   
    # stdin, stdout_file, stderr_file and working_directory
    # can contain FileTransfer et SharedResourcePath.
   
    ser_command = list_to_serializable(self.command, 
                                       id_generator, 
                                       transfer_ids, 
                                       shared_res_path_id)
  
  
    job_dict['command'] = ser_command  
  
    if self.referenced_input_files:
      ser_ref_in_files = list_to_serializable(self.referenced_input_files, 
                                              id_generator, 
                                              transfer_ids, 
                                              shared_res_path_id)
      job_dict['referenced_input_files'] = ser_ref_in_files
  
    if self.referenced_output_files:
      ser_ref_out_files = list_to_serializable(self.referenced_output_files, 
                                               id_generator, 
                                               transfer_ids, 
                                               shared_res_path_id)
      job_dict['referenced_output_files'] = ser_ref_out_files
  
  
    if self.stdin:
      job_dict['stdin'] = to_serializable(self.stdin,
                                          id_generator, 
                                          transfer_ids, 
                                          shared_res_path_id)
  
    if self.stdout_file:
      job_dict['stdout_file'] = to_serializable(self.stdout_file,
                                                id_generator, 
                                                transfer_ids, 
                                                shared_res_path_id)
  
  
    if self.stderr_file:
      job_dict['stderr_file'] = to_serializable(self.stderr_file,
                                                id_generator, 
                                                transfer_ids, 
                                                shared_res_path_id)
  
  
    if self.working_directory:  
      job_dict['working_directory'] = to_serializable(self.working_directory,
                                                      id_generator, 
                                                      transfer_ids, 
                                                      shared_res_path_id)
  
  
    return job_dict




class Workflow(object):
  '''
  Workflow representation.

  **name**: *string*

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

  # for special user storage
  user_storage = None

  def __init__(self,
               jobs,
               dependencies=None,
               root_group=None,
               disposal_timeout=168,
               user_storage=None,
               name=None):

    self.name = name
    self.jobs = jobs
    if dependencies != None:
      self.dependencies = dependencies
    else:
      self.dependencies = []
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

  def attributs_equal(self, other):
    if not isinstance(other, self.__class__):
      return False
    seq_attributs = [
                     "jobs",
                     "dependencies",
                     "root_group",
                     "groups"
                     ]
    for attr_name in seq_attributs:
      attr = getattr(self, attr_name)
      other_attr = getattr(other, attr_name)
      if not len(attr) == len(other_attr):
        return False
      for i in range(0, len(attr)):
        if isinstance(attr[i], Job) or\
         isinstance(attr[i], Group):
          if not attr[i].attributs_equal(other_attr[i]):
            return False
        elif isinstance(attr[i], tuple):
          if not isinstance(other_attr[i], tuple) or\
             not len(attr[i]) == len(other_attr[i]):
            return False
          if not attr[i][0].attributs_equal(other_attr[i][0]):
            return False
          if not attr[i][1].attributs_equal(other_attr[i][1]):
            return False
        elif not attr[i] == other_attr[i]:
          return False
    return self.name == other.name

  def to_dict(self):
    '''
    The keys must be string to serialize with JSON.
    '''
    #TODO user_storage
    id_generator = IdGenerator()
    job_ids = {} # Job -> id
     
    wf_dict = {}
  
    wf_dict["name"] = self.name
   
    new_jobs = []
    for job in self.jobs:
      ident = id_generator.generate_id()
      new_jobs.append(ident)
      job_ids[job] = ident
    wf_dict["jobs"] = new_jobs
    
    new_dependencies = []
    for dep in self.dependencies:
      if dep[0] not in job_ids or dep[1] not in job_ids:
        raise Exception("Unknown jobs in dependencies.")
      new_dependencies.append((job_ids[dep[0]], job_ids[dep[1]]))
    wf_dict["dependencies"] = new_dependencies
  
    group_ids = {}
    new_groups = []
    for group in self.groups:
      ident = id_generator.generate_id()
      new_groups.append(ident)
      group_ids[group] = ident
    wf_dict["groups"] = new_groups
  
    new_root_group = []
    for element in self.root_group:
      if element in job_ids:
        new_root_group.append(job_ids[element])
      elif element in group_ids:
        new_root_group.append(group_ids[element])
      else:
        raise Exception("Unknown root group element.") 
    wf_dict["root_group"] = new_root_group
  
    ser_groups = {}
    for group, group_id in group_ids.iteritems():
     ser_groups[str(group_id)] = group.to_dict(group_ids, job_ids)
    wf_dict["serialized_groups"] = ser_groups
  
    ser_jobs = {}
    transfer_ids = {} # FileTransfer -> id
    shared_res_path_ids = {} #SharedResourcePath -> id
    for job, job_id in job_ids.iteritems():
      ser_jobs[str(job_id)] = job.to_dict(id_generator,
                                          transfer_ids,
                                          shared_res_path_ids)
    wf_dict["serialized_jobs"] = ser_jobs
  
    ser_transfers = {}
    for file_transfer, transfer_id in transfer_ids.iteritems():
      ser_transfers[str(transfer_id)] = file_transfer.to_dict()
    wf_dict["serialized_file_transfers"] = ser_transfers
  
    ser_srp = {}
    for srp, srp_id in shared_res_path_ids.iteritems():
      ser_srp[str(srp_id)] = srp.to_dict()
    wf_dict["serialized_shared_res_paths"] = ser_srp
  
    return wf_dict 
  
  @classmethod
  def from_dict(cls, d):
    name = d["name"]
    
    #shared resource paths
    serialized_srp = d["serialized_shared_res_paths"]
    srp_from_ids = {}
    for srp_id, srp_d in serialized_srp.iteritems():
      srp = SharedResourcePath.from_dict(srp_d)
      srp_from_ids[int(srp_id)] = srp
  
    #file transfers
    serialized_tr = d["serialized_file_transfers"]
    tr_from_ids = {}
    for tr_id, tr_d in serialized_tr.iteritems():
      file_transfer = FileTransfer.from_dict(tr_d)
      tr_from_ids[int(tr_id)] = file_transfer
    
    #jobs
    serialized_jobs = d["serialized_jobs"]
    job_from_ids = {}
    for job_id, job_d in serialized_jobs.iteritems():
      job = Job.from_dict(job_d, tr_from_ids, srp_from_ids)
      job_from_ids[int(job_id)] = job
    jobs = job_from_ids.values()
  
    #groups
    serialized_groups = d["serialized_groups"]
    group_from_ids = {}
    to_convert = serialized_groups.keys()
    converted_or_stuck = False
    while not converted_or_stuck  :
      new_converted = []
      for group_id in to_convert: 
        group = Group.from_dict(serialized_groups[group_id],
                                group_from_ids,
                                job_from_ids)
        if group != None:
          new_converted.append(group_id)
          group_from_ids[int(group_id)] = group
      for group_id in new_converted: to_convert.remove(group_id)
      converted_or_stuck = not to_convert or not new_converted
    groups = group_from_ids.values()
            
    #root group
    id_root_group = d["root_group"] 
    root_group = []
    for el_id in id_root_group:
      if el_id in group_from_ids:
        root_group.append(group_from_ids[el_id])
      elif el_id in job_from_ids:
        root_group.append(job_from_ids[el_id])
  
    #dependencies
    dependencies = []
    id_dependencies = d["dependencies"]
    for id_dep in id_dependencies:
      dep = (job_from_ids[id_dep[0]], job_from_ids[id_dep[1]])
      dependencies.append(dep)
  
    workflow = cls(jobs, 
                   dependencies, 
                   root_group=root_group,
                   user_storage=None,
                   name=name)  
  
    return workflow
   
  




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

  def attributs_equal(self, other):
    if not isinstance(other, self.__class__):
      return False
    if len(self.elements) != len(other.elements):
      return False
    for i in range(0, len(self.elements)):
      if not self.elements[i].attributs_equal(other.elements[i]):
        return False
    if self.name != other.name:
      return False
    return True

  def to_dict(self, group_ids, job_ids):
    group_dict = {}
    group_dict["name"] = self.name
    new_gp_elements = []
    for element in self.elements:
      if element in job_ids:
        new_gp_elements.append(job_ids[element])
      elif element in group_ids:
        new_gp_elements.append(group_ids[element])
      else:
        raise Exception("Unknown group element.")
    group_dict["elements"] = new_gp_elements
    return group_dict
  
  @classmethod
  def from_dict(cls, d, group_from_ids, job_from_ids):
    id_elements = d["elements"]
    elements = []
    for el_id in id_elements:
      if el_id in job_from_ids:
        elements.append(job_from_ids[el_id])
      elif el_id in group_from_ids:
        elements.append(group_from_ids[el_id])
      else:
        return None
    
    name = d["name"]
    group = cls(elements, name)
    return group
  


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
      self.initial_status = constants.FILES_ON_CLIENT
    else:
      self.initial_status = constants.FILES_DO_NOT_EXIST

  def attributs_equal(self, other):
    if not isinstance(other, self.__class__):
      return False
    attributs = [
                "client_path",
                "client_paths",
                "initial_status",
                "disposal_timeout",
                "name",
                ]
    for attr_name in attributs:
      attr = getattr(self, attr_name)
      other_attr = getattr(other, attr_name)
      if not other_attr == attr:
        return False
    return True

  def to_dict(self):
    transfer_dict = {}
    attributs = [
                 "client_path",
                 "client_paths",
                 "initial_status",
                 "disposal_timeout",
                 "name",
                ]
    for attr_name in attributs:
      transfer_dict[attr_name] = getattr(self, attr_name)
  
    return transfer_dict
  
  @classmethod
  def from_dict(cls, d):
    transfer = cls(is_input=True, 
                   client_path="foo")
    for key, value in d.iteritems():
      setattr(transfer, key, value)
    return transfer
  




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

  def attributs_equal(self, other):
    if not isinstance(other, self.__class__):
      return False
    attributs = [
                "relative_path",
                "namespace",
                "uuid",
                ]
    for attr_name in attributs:
      attr = getattr(self, attr_name)
      other_attr = getattr(other, attr_name)
      if not attr == other_attr:
        return False
    return True

  def to_dict(self):
    srp_dict = {}
    attributs = [
                  "relative_path",
                  "namespace",
                  "uuid",
                  ]
    for attr_name in attributs:
      srp_dict[attr_name] = getattr(self, attr_name)
  
    return srp_dict
  
  @classmethod
  def from_dict(cls, d):
    shared_res_path = cls(relative_path="toto",
                          namespace="toto",
                          uuid="toto")
    for key, value in d.iteritems():
      setattr(shared_res_path, key, value)
    return shared_res_path



class IdGenerator(object):
  def __init__(self):
    self.current_id = 0

  def generate_id(self):
    current_id = self.current_id
    self.current_id = self.current_id + 1
    return current_id  

def to_serializable(element, 
                    id_generator,
                    transfer_ids,
                    shared_res_path_ids):
  if isinstance(element, FileTransfer):
    if element in transfer_ids:
      return transfer_ids[element]
    else:
      ident = id_generator.generate_id()
      transfer_ids[element] = ident
      return ident
  elif isinstance(element, SharedResourcePath):
    if element in shared_res_path_ids:
      return shared_res_path_ids[element]
    else:
      ident = id_generator.generate_id()
      shared_res_path_ids[element] = ident
      return ident
  elif isinstance(element, list):
    return list_to_serializable(element,
                                id_generator,
                                transfer_ids,
                                shared_res_path_ids)
  elif isinstance(element, tuple):
    return ["soma-workflow-tuple", 
            to_serializable(element[0],
            id_generator,
            transfer_ids,
            shared_res_path_ids),
            element[1]]
  else:
    return element

def from_serializable(element,
                      tr_from_ids,
                      srp_from_ids):
  if isinstance(element, list):
    if element[0] == "soma-workflow-tuple" and len(element) == 3:
      return (from_serializable(element[1], 
                                tr_from_ids, 
                                srp_from_ids),
              element[2])
   
    else:
      return list_from_serializable(element, tr_from_ids, srp_from_ids)
  elif element in tr_from_ids:
    return tr_from_ids[element]
  elif element in srp_from_ids:
    return srp_from_ids[element]
  else:
    return element

def list_to_serializable(list_to_convert,
                         id_generator,
                         transfer_ids,
                         shared_res_path_ids):
  ser_list = []
  for element in list_to_convert:
    ser_element = to_serializable(element,
                                  id_generator,
                                  transfer_ids,
                                  shared_res_path_ids)
    ser_list.append(ser_element)
  return ser_list

def list_from_serializable(list_to_convert,
                           tr_from_ids,
                           srp_from_ids):
  us_list = []
  for element in list_to_convert:
    us_element = from_serializable(element,
                                   tr_from_ids,
                                   srp_from_ids)
    us_list.append(us_element)
  return us_list



