from es import Es
import uuid
#class User(es):
class NotFound(Exception): pass

def init():
    Es.create_index("User")
def get_user(user_id):
    user = Es.get_document_by_id(user_id)
    if not user:
        raise NotFound()
    return user

def save_user(openid='', name='', **kwargs):
    query = {
        "match": {
            "openid": openid,
            "name" : name
        }
    }
    user_data = {
        "openid": openid,
        "name": name,
        "extra": kwargs
    }
    if not Es.search_docunmet(index="User",query=query):
        id = uuid.uuid4()

        user = Es.index_document(index="User",id =id,data=user_data)
    else:
        user = Es.es.update(index="User",id = id,doc=user_data)
    return user

class CollectionWithDocumentCount():
    collection_id = ?
    document_count = Es.search_docunmet(index="Document",query={
        "query": {
            "match": {
                "collection_id": collection_id  # 替换为你的查询条件
                "status": 0
            }
        }
    })["count"]
    def get_collections(user_id):
        response = Es.search_docunmet(index="Collection", query={
            "query": {
                "match": {
                    "user_id": user_id,
                    "status": 0
                }
            }
        })
        total = response[]
        if total == 0:
            return  0
        return  total

    def get_collection_by_id(user_id, collection_id):
        return Es.search_docunmet(index="Collection", query={
            "query": {
                "match": {
                    "user_id": user_id,
                    "collection_id":collection_id,
                    "status": 0
                }
            }
        })

    def save_collection(user_id, name, description):
        collecton_id = uuid.uuid4()
        collecton_data = {
            "user_id": user_id,
            "name": name,
            "description": description
        }

        Es.index_document(index="Collection", id=collecton_id, data=collecton_data)

