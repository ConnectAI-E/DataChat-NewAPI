import logging
from app import app
from models import init
from elasticsearch_dsl import connections
from routes import *


@app.errorhandler(Exception)
def api_exception(e):
    logging.exception(e)
    if isinstance(e, PermissionDenied):
        return jsonify({'code': -1, 'msg': str(e)}), 403
    if isinstance(e, NeedAuth):
        return jsonify({'code': -1, 'msg': str(e)}), 401
    return jsonify({'code': -1, 'msg': str(e)}), 500


if __name__ == "__main__":
        connections.create_connection(hosts="http://192.168.110.47:9200", basic_auth=('elastic', 'fsMxQANdq1aZylypQWZD'))
        try:
            init()
        except Exception as e:
            logging.error(e)




if __name__ == "__main__":
    from sys import argv
    if len(argv) > 1:
        app.run(port=80, host="0.0.0.0")
