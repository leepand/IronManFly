#coding=utf-8
import time, sys, cherrypy, os
import argparse
import yaml
from paste.translogger import TransLogger
from app import create_app
import flask_profiler
from modelDB.db import does_model_exist,create_new_model,update_model
from haikunator import Haikunator
import numpy as np, os, shutil
import datetime
from log.log import logger
from colorama import Fore
from storage import DBStore
"""
模型随机信息生成（激活时间、default模型名称）
"""
import datetime

haikunator = Haikunator()
epoch = datetime.datetime.utcfromtimestamp(0)
"""
随机生成default模型名称）
"""
def generate_random_model_name():
    return haikunator.haikunate(token_length=0)
"""
激活时间转换
"""
def convert_dt_to_epoch(dt):
    return (dt - epoch).total_seconds() * 1000.0
import os, shutil

"""
 创建模型路径
"""
STORAGE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'model_storage/')

def create_storage_dir(override=False):
    if override or not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    return STORAGE_DIR
"""
 创建模型版本路径
"""
def get_model_dir(name, version=1, create_if_needed=False):
    path = os.path.join(STORAGE_DIR, name, 'v%d' % version)

    if create_if_needed:
        if os.path.exists(path):
            logger.info(Fore.YELLOW,'warning','Model/version path already exists.')
            #print 'Model/version path already exists.'
        else:
            os.makedirs(path)

    return path
"""
 拷贝模型文件至相应版本文件夹
"""
from distutils.dir_util import copy_tree
def copy_model_files_to_internal_storage(modelpath, name, version=1):
    model_dir = get_model_dir(name, version, create_if_needed=True)
    if os.path.isdir(modelpath):
        #if os.path.exists(modelpath):
        #    continue
        # Copy the original model directory into its corresponding internal model storage folder
        copy_tree(modelpath, model_dir)
    else:
        # Copy the model file to its corresponding internal model storage folder
        shutil.copy2(modelpath, model_dir)
"""
 保存模型信息至数据库
"""
def save_model_to_db(name, model_function,version=1,activated=True, last_deployed=None,model_desc='defalut description'):
    #model = self.model
    model_obj = {
        'name' : name,
        'version' : version,
        'activated' : activated,
        'path' : get_model_dir(name, version)
    }
    model_obj['last_deployed'] = last_deployed
    model_obj['model_desc']=model_desc
    model_obj['model_func']=model_function
    # Generate an input spec for this model
    # Check if this model/version already exists in the db.
    # If it doesn't, store this model's metadata in the db.
    if not does_model_exist(name, version):
        create_new_model(model_obj)
    else:
        return (False, 'Model/version already exists.')
    return (True, None)



cherrypy.log.error_log.propagate = False
cherrypy.log.access_log.propagate = False
class FireflyError(Exception):
    pass
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-t", "--token", help="token to authenticate the requests")
    p.add_argument("-b", "--bind", dest="ADDRESS", default="127.0.0.1:8000")
    p.add_argument("-c", "--config", dest="config_file", default=None)
    p.add_argument("functions", nargs='*', help="functions to serve")
    return p.parse_args()
def parse_config_file(config_file):
    if not os.path.exists(config_file):
        raise FireflyError("Specified config file does not exist..")
    with open(config_file) as f:
        config_dict = yaml.safe_load(f)
    return config_dict

def parse_config_data(config_dict):
    functions = [f["function"]
            for name, f in config_dict["functions"].items()]
    token = config_dict.get("token", None)
    return functions, token

class Microservices(object):
    """
    Allow creation of predict and other microservices
    aws_key : str, optional
       aws key
    aws_secret : str, optional
       aws secret
    """
    def __init__(self,aws_key=None,aws_secret=None):
        self.aws_key = aws_key
        self.aws_secret = aws_secret
    def run_server(self,app,port=5412,host='127.0.0.1'):
        # Enable WSGI access logging via Paste
        app_logged = TransLogger(app)
 
        # Mount the WSGI callable object (app) on the root directory
        cherrypy.tree.graft(app_logged, '/')
 
        # Set the configuration of the web server
        cherrypy.config.update({
            'engine.autoreload.on': True,
            'log.screen': True,
            'server.socket_port': port,
            'server.socket_host': '%s'%(host)
        })
 
        # Start the CherryPy WSGI web server
        cherrypy.engine.start()
        cherrypy.engine.block()
 

    def create_prediction_microservice(self,model_list,yml_conf=False,port=5412,host='127.0.0.1',model_info={}):
        """
        Create a prediction Flask/cherrypy microservice app
        Parameters
        ----------
        func_name : list
           location of pipeline
        model_name : str
           model name to use for this pipeline
        """
        def run_sanity_checks():
            create_storage_dir(override=False)

        STORAGE_DIR=create_storage_dir(override=False)
        

        #函数来自配置文件
        if yml_conf:
            function_specs, token = parse_config_data(parse_config_file(yml_conf))
        else:
            function_specs=model_list
        #模型信息注册
        #print function_specs
        if model_info:
            if model_info.has_key('model_desc'):
                model_desc=model_info['model_desc']
            if model_info.has_key('model_name'):
                name=model_info['model_name']
            else:
                name=generate_random_model_name()
                model_info['model_name']=name
            version=model_info['version']
            modelpath=model_info['modelpath']
            copy_model_files_to_internal_storage(modelpath,name, version)
            model_storage_path=get_model_dir(name, version, create_if_needed=True)
            #if not does_model_exist(name, version):
            #   create_new_model(model_info)
            #else:
            #    update_model(name, version, {'activated' : True})
            #    return ('Model/version already exists.')
        
        #model_info['model_storage_path']=model_storage_path
        """
         保存模型元数据信息
        """
        model_function=function_specs
        save_model_to_db(name,model_function=model_function, version=version, activated=True,\
                         last_deployed=convert_dt_to_epoch(datetime.datetime.now()),model_desc=model_desc)
        logger.info(Fore.GREEN, 'Model Deploy','\n\nYour "%s" model (version: %s) has been successfully deployed.' % (name, version))
        logger.info(Fore.CYAN, 'Model Function', 'Your deployed model function is: %s'%(function_specs))
        logger.info(Fore.CYAN, 'Usage', 'You can now access it at the following endpoint:')
        logger.info(Fore.CYAN, 'Endpoint', '\n\n\t\t/models/' + name + '/v' + str(version) + '/predict\n\n')
        #print '\n\nYour "%s" model (version: %s) has been successfully deployed.' % (name, version)
        
        #print 'You can now access it at the following endpoint:'
        
        #print '\n\n\t\t/models/' + name + '/v' + str(version) + '/predict\n\n'

        app = create_app(function_specs,model_info)
        app.config['flask_profiler']={"enabled": True,"storage": {"engine": "mongodb"},"basicAuth":{"enabled": True,"username": "leepand","password":"admin"},"ignore": ["^/static/.*"]}
        flask_profiler.init_app(app)
        # start web server
        self.run_server(app,port,host)