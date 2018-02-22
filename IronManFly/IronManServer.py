

from IronManFly.microservice import Microservices
m = Microservices()
funcs=['simple.predict']
app = m.create_prediction_microservice(model_list=funcs)
#app.run(host="0.0.0.0", debug=False)