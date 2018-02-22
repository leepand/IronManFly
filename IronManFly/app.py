# -*- coding:utf-8 -*-  
from flask import Blueprint
from flask import json
from flask import request
from algo_engine import AlgoEngine
import logging
import threading
from modelDB.db import get_all_models,validation_model,does_model_exist,update_model,delete_model_from_db
from modelDB.storage import delete_model_storage
from log.log import logger
from colorama import Fore
from storage import DBStore
#import auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
main = Blueprint('main', __name__)
ctx = threading.local()
ctx.request = None

from flask import Flask, request
from functools import wraps
from flask import jsonify
flasklog=Flask(__name__)
class CCode:  
    def str(self, content, encoding='utf-8'):  
        # 只支持json格式  
        # indent 表示缩进空格数  
        return json.dumps(content, encoding=encoding, ensure_ascii=False, indent=4)  
        pass  
  
    pass      
'''
@main.route("/predict/<function>", methods=["POST"])
def predict(function):
    ctx.request = request
    logger.debug("Model name %s ", function)
    req=json.dumps(request.json)
    top_ratings = recommendation_engine.call_func('/s',x=1,y=2)%(function)
    ctx.request = None
    return json.dumps(top_ratings)
'''

def check_auth(username, password):
    return username == 'admin' and password == 'secret'

def authenticate():
    message = {'message': "Not Authenticate."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth: 
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

#@main.route("/predict/<function>", methods = ["POST"])
@main.route("/models/<string:name>/v<int:version>/predict", methods = ["POST"])
@requires_auth
def api_predict_func(name):
    ctx.request = request
    if request.headers['Content-Type'] == 'text/plain':
        req_data=request.data
    elif request.headers['Content-Type'] == 'application/json':
        req_data=json.dumps(request.json)
    else:
        req_data='some thing wrong!'
    fun_name=('/%s')%(str(name).decode('utf-8'))
    fun_path=fun_name
    result=algo_engine.call_func(fun_path,**request.json)
    ctx.request = None
    return result

@main.route('/info', methods = ['GET'])
def api_info():
    ctx.request = request
    #path = request.path_info
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        return "WANDA_ML Server Message: " + json.dumps(request.json)

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"
@main.route('/messages', methods = ['POST'])
def api_message():
    ctx.request = request
    #path = request.path_info
    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"
@main.route('/')
def index():
    return jsonify({'status' : 'OK'})

@main.route('/models/list')
def models_list():
    flasklog.logger.info('info log')
    model = get_all_models()
    num_models = len(model)

    #list_of_models = [{
    #   'name' : model['name'], 
    #    'version' : model['version'], 
    #   'last_deployed' : model['last_deployed'], 
    #   'api_activated' : model['activated']
    #}]#'backend_adapter' : model['adapter']} for model in models]
    userip=request.remote_addr
    #userip='127.0.0.1'
    #logger.info(Fore.GREEN, 'User IP', 'IP of request from user is: %s'%(userip))
    return jsonify({'num_models' : num_models, 'models' : model,'userip':userip})

@main.route('/models/<string:name>/v<int:version>/')
def model_detail(name, version=1):

    model = get_model(name, version)
    del model['path']

    if not model['activated']:
        return jsonify({'success':False, 'message' : 'The specified model is deactivated.'})

    return jsonify(model)
#@main.route('/models/predict/<function>', methods=['POST'])
@main.route('/models/<string:name>/v<int:version>/predict/<function>', methods=['POST'])
def model_predict(function,name,version=1):
    
    ctx.request = request
    #userip=request.remote_addr
    if not does_model_exist(name,version):
        return jsonify({'success':False, 'message' : 'The specified model is not deployed.'})
    model_info= validation_model(name,version)
    if request.headers['Content-Type'] == 'text/plain':
        req_data=request.data
    elif request.headers['Content-Type'] == 'application/json':
        req_data=json.dumps(request.json)
    else:
        req_data='some thing wrong!'
    if model_info:
        if model_info['activated']==True:
            fun_name=('/%s')%(str(function).decode('utf-8'))
            fun_path=fun_name
            result=algo_engine.call_func(fun_path,**request.json)
            return jsonify({'success':True, 'response' : result})
        else:
            return jsonify({'success':False, 'message' : 'The specified model is deactivated.'})
    else:
        return jsonify({'success':False, 'message' : 'The specified model is not deployed.'})
    ctx.request = None
    #ctx.request = None
@main.route('/models/deactivate/<string:name>/v<int:version>/')    
def deactivate(name, version=1):
    """ Remove a model from the API model server. """
    if not does_model_exist(name, version):
        print 'The specified model/version doesn\'t exist!'
        return jsonify({'success':False,'message':'The specified model/version doesn\'t exist!'}) 


    update_model(name, version, {'activated' : False})
    return jsonify({'success':True,'message':'Successfully deactivated the model\'s API.\nPlease restart your server for these changes to take effect.'}) 

@main.route('/models/activate/<string:name>/v<int:version>/')    
def activate(name, version=1):
    """ Expose a model via the API model server. """
    if not does_model_exist(name, version):
        print 'The specified model/version doesn\'t exist!'
        return jsonify({'success':False,'message':'The specified model/version doesn\'t exist!'})
    update_model(name, version, {'activated' : True})
    return jsonify({'success':True,'message':'Successfully activated the model\'s API.\nPlease restart your server for these changes to take effect.'})


@main.route('/models/delete/<string:name>/v<int:version>/')    
def delete(name, version=1):
    """
    Delete a specific model version.
    """
    if not does_model_exist(name, version):
        print 'The specified model/version doesn\'t exist!'
        return jsonify({'success':False,'message':'The specified model/version doesn\'t exist!'})

    # delete the model from the db
    delete_model_from_db(name, version)
    # delete the model from the file storage
    delete_model_storage(name, version)

    return  jsonify({'success':True,'message':'The model (v%d) and its files were successfully deleted.' % version})

    

    #request.get_data()

    #preds = get_predictions_for_model(name, version, request.json)

    #return jsonify(preds)

@main.route("/modelaction/<string:actiontype>/", methods = ["POST"])
def model_action(actiontype):
    cCode = CCode()
    #ctx.request = request  
    #req_data=json.dumps(request.get_data().decode("utf-8"))
    req_data=request.get_json(force=True)#cCode.str(request.get_data())
    '''
    if request.headers['Content-Type'] == 'text/plain':
        req_data=request.data
    elif request.headers['Content-Type'] == 'application/json':
        req_data=json.dumps(request.get_data())
    else:
        req_data='some thing wrong!'
        #req_data=request.json
    '''
    #return jsonify({'re':data})#jsonify({'success':True, 'response' : data['d']})
    #ctx.request = None
    
    if 'dbuser' in req_data:
        user=req_data['dbuser']
    else:
        user='leepand'
    if 'dbpasswd' in  req_data:
        passwd=req_data['dbpasswd']
    else:
        passwd='lipd@123'
    if 'dbbame' in req_data:
        dbname=req_data['dbname']
    else:
        dbname='leepand'
    if 'host' in req_data:
        host=req_data['host']
    else:
        host='localhost'
    if 'port' in req_data:
        port=req_data['port']
    else:
        port=5432
    db=DBStore.DBStore(user=user, password=passwd, db=dbname, host=host, port=port)#DBStore(user='leepand', password='lipd@123', db='leepand', host='localhost', port=5432)
    if actiontype=='save':
        model_id=req_data['model_id']
        model_name=req_data['model_name']
        model_version=req_data['model_version']
        model_request=req_data['model_request']
        model_result=req_data['model_result']
        model_action=req_data['model_action']
        user_id=req_data['user_id']
        business_id=req_data['business_id']
        create_time=req_data['create_time']
        
        result=db.saveActionData(model_id=model_id,\
          model_name=model_name,\
          model_version=model_version,\
          model_request=model_request,
          model_result=model_result,
          model_action=model_action,
          user_id=user_id,
          business_id=business_id,
          create_time=create_time)
        result={'status' : 'action data was successfully inserted !'}
    else:
        query_condition=req_data['query_condition']
        result=db.getActionData(query_condition=query_condition)
    #return jsonify({'success':True, 'response' : result})
    
    return jsonify({'success':True, 'response' : result})
    #ctx.request = None
    
def create_app(function_specs,model_info):
    global algo_engine,modelinfo
    modelinfo=model_info
    algo_engine = AlgoEngine(function_specs)    
    
    app = Flask(__name__)
    app.register_blueprint(main)


    
    return app 
