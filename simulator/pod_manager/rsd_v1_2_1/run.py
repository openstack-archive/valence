# -*- coding: utf-8 -*-

# !flask/bin/python


from flask import Flask
from flask_restful import Api

from simulator.pod_manager.rsd_v1_2_1.resources import init_data_generation
from simulator.pod_manager.rsd_v1_2_1.route import init_routes


# initialize flask and flask restful
app = Flask(__name__)
app.config['SECRET_KEY'] = "Valence-Simulator"
app.debug = True

api = Api(app)

if __name__ == "__main__":
    init_data_generation()
    init_routes(api)
    app.run(host='0.0.0.0',
            port=443,
            ssl_context=(
                __file__.replace('run.py', 'server.crt'),
                __file__.replace('run.py', 'server.key'))
            )
