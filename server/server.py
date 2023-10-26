import logging
from app import app
from models import db, text, Embedding
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
    from pgvector.psycopg2 import register_vector
    with app.app_context():
        db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        try:
            pass
            # index = db.Index('my_index', Embedding.embedding,
            #     postgresql_using='ivfflat',
            #     # postgresql_with={'lists': 100},
            #     postgresql_ops={'embedding': 'vector_l2_ops'}
            # )
            # index.create(db.engine)
        except Exception as e:
            logging.error(e)
        register_vector(db.engine.raw_connection())
        db.create_all()


if __name__ == "__main__":
    from sys import argv
    if len(argv) > 1:
        app.run(port=80, host="0.0.0.0")