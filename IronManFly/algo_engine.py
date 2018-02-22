import sys
import logging
import importlib
from flask import json
try:
    from inspect import signature, _empty
except:
    from funcsigs import signature, _empty
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Algo Engine')
PY2 = (sys.version_info.major == 2)
PY3 = (sys.version_info.major == 3)


        
class ValidationError(Exception):
    pass        
class AlgoEngine:
    """A algo recommendation engine
    """
    @staticmethod
    def json_encode(data):
        result = json.dumps(data)
        if PY2:
            result = result.decode('utf-8')
        return result
    @staticmethod
    def validate_args(function, kwargs):
        function_signature = signature(function)
        try:
            function_signature.bind(**kwargs)
        except TypeError as err:
            raise ValidationError(str(err))
    @staticmethod
    def load_function(function_spec, path=None, name=None):
        if "." not in function_spec:
            raise Exception("Invalid function: {}, please specify it as module.function".format(function_spec))
        mod_name, func_name = function_spec.rsplit(".", 1)
        try:
            mod = importlib.import_module(mod_name)
            func = getattr(mod, func_name)
        except (ImportError, AttributeError) as err:
            print("Failed to load {}: {}".format(function_spec, str(err)))
            raise
        path = path or "/"+func_name
        name = name or func_name
        return (path, name, func)
    #@staticmethod
    def load_functions(self,function_specs):
        return [self.load_function(function_spec) for function_spec in function_specs]
    def call_func(self,func_path,**kwargs):
        try:
            self.validate_args(self.mapping[func_path], kwargs)
        except ValidationError as err:
            logger.warn("Function failed with ValidationError: %s.", err) 
        logger.info("calling function %s", func_path)
        result=self.mapping[func_path](**kwargs)
        result_json=json.dumps(result)
        return result_json
    def __init__(self, function_list, function_name=None):
        self.functions = self.load_functions(function_list)
        self.mapping={}
        #self.name = function_name or self.function.__name__
        #self.doc = function.__doc__ or ""
        #logger.info("calling function %s", self.name)
        for i in range(len(self.functions)):
            path=self.functions[i][0]
            func_name=self.functions[i][1]
            func=self.functions[i][2]
            self.mapping[path]=func