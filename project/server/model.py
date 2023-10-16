from es import Es
import uuid
#class User(es):
class NotFound(Exception): pass

def init():
    Es.create_index("User")
    Es.create_index("Collection")
    Es.create_index("Document")
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
    response = Es.search_docunmet(index="User",query=query)
    if not response:
        user_id = uuid.uuid4()
        user = Es.index_document(index="User",id =user_id,data=user_data)
    else:
        user_id = response["id"]
        user = Es.es.update(index="User",id = user_id,doc=user_data)
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
            "description": description,
            "status": 0
        }

    Es.index_document(index="Collection", id=collecton_id, data=collecton_data)

def update_collection_by_id(user_id, collection_id, name, description):
    collection_data = {
        "user_id": user_id,
        "name": name,
        "description": description
        "status": 0
    }
    Es.es.update(index="Collection", id=collection_id, doc=collection_data)

def delete_collection_by_id(user_id, collection_id):
    collection_update_data ={
        "source": "ctx._source.status=-1"
    }
    Es.es.update(index="Collection", id=collection_id, script= collection_update_data)
    query = {'term':{'collection_id':collection_id}}
    bot_update_data ={
        "source": "ctx._source.collection = '' "
    }
    Es.es.update_by_query(index= "Bot",query=query,script=bot_update_data)

def get_document_id_by_uniqid(collection_id, uniqid):
    Es
def get_documents_by_collection_id(user_id, collection_id):
    collection = get_collection_by_id(user_id, collection_id)
    assert collection, '找不到对应知识库'
    query = {'term':{
        'collection_id':collection_id,
        'status' : 0
    }}
    total = Es.es.count(index="Document",query=query)["count"]
    if total == 0:
        return [], 0
    return Es.es.search(index="Document",query=query), total

def remove_document_by_id(user_id, collection_id, document_id):
    collection = get_collection_by_id(user_id, collection_id)
    assert collection, '找不到对应知识库'
    update_data = {
        "source": "ctx._source.status=-1"
    }
    Es.es.update(index="Documents", id=document_id, script=update_data)
    query = {'term':{'document_id':document_id}}
    Es.es.update_by_query(index="Embedding",query=query, script=update_data)

def purge_document_by_id(document_id):
    Es.es.delete(index="Document",id=document_id)
    query = {'term': {'document_id': document_id}}
    Es.es.delete_by_query(index="Embedding", query=query)

def set_document_summary(document_id, summary):
    update_data = {
        "source": "ctx._source.summary = "
    }
    Es.es.update(index="Documents", id=document_id, script=update_data)