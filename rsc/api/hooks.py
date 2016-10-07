from oslo_config import cfg
from pecan.hooks import PecanHook


class CORSHook(PecanHook):

    def after(self, state):
        state.response.headers['Access-Control-Allow-Origin'] = '*'
        state.response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, PUT, LIST, OPTIONS'
        state.response.headers['Access-Control-Allow-Headers'] = 'origin, authorization, content-type, accept'
        if not state.response.headers['Content-Length']:
            state.response.headers['Content-Length'] = str(len(state.response.body))

