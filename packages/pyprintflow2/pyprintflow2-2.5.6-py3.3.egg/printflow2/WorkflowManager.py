'''
Created on Sep 16, 2013

@author: "Colin Manning"
'''
import traceback
import utils

class WorkflowManager(object):
    '''
    Maintain workflows and manage execution etc
    '''

    workflows = {}
    logger = None

    def __init__(self, logger):
        self.logger = logger
    
    def registerWorkflow(self, workflow_config):
            workflow_class = utils.get_class(workflow_config['class_name'])
            workflow_object = workflow_class(workflow_config)
            self.workflows[workflow_config['name']] = workflow_object
    
    def execute(self, workflow_name):
        if workflow_name in self.workflows:
            try:
                workflow = self.workflows[workflow_name]
                workflow.prepare()
                workflow.start()
                workflow.stop()
            except:
                workflow.abort()
                self.logger.error(traceback.format_exc())
                traceback.print_exc()
                
    def findFolderWorkflow(self, path):
        result = None
        for name in self.workflows:
            wf = self.workflows[name]
            if self.workflows[name].source_folder is None:
                continue
            wf_folder_bits = self.workflows[name].source_folder.split('/')
            path_bits = path.split('/')
            if (len(path_bits) == len(wf_folder_bits)) and (path_bits[-1] == wf_folder_bits[-1]):
                result = name
                break
            
        return result
    