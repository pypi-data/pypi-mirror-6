# -*- coding: utf-8 -*-

#
# library for Robot Framework to inspect python modules
# 

import inspect
import imp
import variables

class PythonModule(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, modulePath):
        self.modulePath = modulePath

    def get_module_variables(self):
        pass

    def variable_presented(self,name):
        #import sys, pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        module = imp.load_source("module", self.modulePath)
        value = getattr(module,name)
        if not value:
            raise AssertionError("module: %s has no variable '%s'" % (self.modulePath, name))
    
    def is_type_of(self, element, reference):
        if type(element) != reference:
            raise AssertionError("wrong type")

    def file_is_valid(self,result):
        if not result.valid:
            raise AssertionError("attribute 'valid' must be True")
        pass

    def file_is_not_valid(self,result):
        if result.valid:
            raise AssertionError("attribute 'valid' must be False")

    def call(self, module_name, method_name, *args):
        """ calls method from module with *args
        """
        pass

    def is_boolean(self, value):
        if type(value) != type(bool):
            raise AssertionError("value must be Boolean")

    def result_has_success_value_for_clean_test_file(self, result):
        if result.UUID_of_content != variables.UUID:
            raise AssertionError("UUID_of_content must contains UUID that was in a request")
        if result.content_is_clean != True:
            raise AssertionError("Content_is_clean should be True")

    def result_has_success_value_for_nonclean_test_file(self, result):
        if result.UUID_of_content != variables.UUID:
            raise AssertionError("UUID_of_content must contains UUID that was in a request")
        if result.content_is_clean != False:
            raise AssertionError("Content_is_clean should be False")
