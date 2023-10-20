import bson
from elasticsearch_dsl import (
    UpdateByQuery,
    Search,
    Q,
    Boolean,
    Date,
    Integer,
    Document,
    InnerDoc,
    Join,
    Keyword,
    Long,
    Nested,
    Object,
    Text,
    connections,
    DenseVector
)
class NotFound(Exception): pass
connections.create_connection(alias="es", hosts="http://192.168.239.128:9200",basic_auth=('elastic', 'fsMxQANdq1aZylypQWZD')

class ObjID():
    def new_id():
        return str(bson.ObjectId())
    def is_valid(value):
        return bson.ObjectId.is_valid(value)

class User(Document):
    __tablename__ = 'user'
    openid = Long()
    name = Text(fields={"keyword": Keyword()})
    status = Integer(default=0)
    extra = Object()    # 用于保存 JSON 数据
    created = Date(default='now')
    modified = Date(default='now')  # 用于保存最后一次修改的时间

    class Index:
        name = 'user'


class Collection(Document):
    __tablename__ = 'collection'
    user_id = Long()
    name = Text(analyzer='ik_max_word')
    description = Text(analyzer='ik_max_word')  #知识库描述
    summary = Text(analyzer='ik_max_word')  #知识库总结
    status = Integer(default=0)
    created = Date(default='now')
    modified = Date(default='now')      # 用于保存最后一次修改的时间

#Documents区别于固有的Docunment
class Documents(Document):
    __tablename__ = 'document'
    uniqid = Long()     #唯一性id,去重用
    collection_id = Long()
    type = Keyword()    #文档类型用keyword保证不分词
    path = Keyword()    #文档所在路径
    name = Text(analyzer='ik_max_word')
    chunks = Integer(default=0) #文档分片个数
    summary = Text(analyzer='ik_max_word')  #文档摘要
    status = Integer(default=0)
    created = Date(default='now')
    modified = Date(default='now')  # 用于保存最后一次修改的时间


class Embedding(Document):
    __tablename__ = 'embedding'
    document_id = Long()    #文件ID
    collection_id = Long()    #知识库ID
    chunk_index = Long()    #文件分片索引
    chunk_size = Integer()  #文件分片大小
    document = Text(analyzer='ik_max_word')       #分片内容
    embedding = DenseVector(dims=768)
    status = Integer(default=0)
    created = Date(default='now')
    modified = Date(default='now')  # 用于保存最后一次修改的时间

class Bot(Document):
    __tablename__ = 'bot'
    user_id = Long()  # 用户ID
    collection_id = Long()  # 知识库ID
    hash = Integer()    #hash
    extra = Object()    #机器人配置信息
    status = Integer(default=0)
    created = Date(default='now')
    modified = Date(default='now')  # 用于保存最后一次修改的时间


'''def init():
    Es.create_index("User")
    Es.create_index("Collection")
    Es.create_index("Document")'''


def get_user(user_id):
    user = User.get(using= "es",id= user_id)
    if not user:
        raise NotFound()
    return user


def save_user(openid='', name='', **kwargs):
    s = Search(using="es", index="user").filter("term", status=0).filter("term", openid=openid)
    response = s.execute()
    if not response.hits.total.value == 0:
        user = User(
            meta={'id': ObjID.new_id()},
            openid=openid,
            name=name,
            extra=kwargs,
        )
        user.save()
        return user
    else:
        user = User.get(using="es",id = response.hits[0].meta.id)
        user.update(using="es",openid=openid,name=name,extra=kwargs)
        return user
'''
class CollectionWithDocumentCount(Collection):
    s = Documents.search(using=connections,index="Document").filter("term",collection_id = Collection.id,status = 0)
    response = s.execute()
    document_count = response.hits.total.value

def get_collections(user_id):
    s = Search(using=connections, index="Collection").filter("term", user_id=user_id)
    # 执行查询
    response = s.execute()
    total = response.hits.total.value
    # 返回搜索结果（文档实例的列表）
    if total == 0:
        return  [],0
    return  list(response),total

def get_collection_by_id(user_id, collection_id):
    collection = Collection.get(id = collection_id)
    if collection :
        if collection.user_id == user_id:
            return collection
        else:
            return None
    else:
        return collection

def save_collection(user_id, name, description):
    collection_id = ObjID.new_id()
    collection = Collection(
        id=collection_id,
        user_id=user_id,
        name=name,
        description=description,
        summary='',
    )
    collection.save()

def update_collection_by_id(user_id, collection_id, name, description):
    update_query = UpdateByQuery(index="Collection").filter("term", user_id=user_id, id=collection_id).update(
        script={
            "source": """
                               ctx._source.name=params.name;
                               ctx._source.description=params.description;
                           """,
            "lang": "painless",
            "params": {
                "name": name,
                "description": description,
            }
        }
    )
    update_query.execute()

def delete_collection_by_id(user_id, collection_id):
    update_query = UpdateByQuery(using=connections,index="Collection").filter("term", user_id=user_id, id=collection_id)

    update_query.execute()
    s = Search(using=connections, index="Bot").filter("term", collection_id=collection_id)
    response = s.execute()
    for document in response:
        document.update(collection_id = "")

def get_document_id_by_uniqid(collection_id, uniqid):
    s = Search(using=connections, index="Docunment").filter("term", uniqid=uniqid)
    response = s.execute()
    return list(response)

def get_documents_by_collection_id(user_id, collection_id):
    collection = get_collection_by_id(user_id, collection_id)
    assert collection, '找不到对应知识库'
    s = Search(using=connections, index="Docunment").filter("term", collection_id =collection_id,status = 0).sort({"created": {"order": "desc"}})
    response = s.execute()
    total = response.hits.total.value
    # 返回搜索结果（文档实例的列表）
    if total == 0:
        return [], 0
    return list(response), total

def remove_document_by_id(user_id, collection_id, document_id):
    collection = get_collection_by_id(user_id, collection_id)
    assert collection, '找不到对应知识库'
    s = Search(using=connections, index="Document").filter("term", id=document_id)
    response = s.execute()
    # 遍历搜索结果中的每个文档，将 status 更新为 -1
    for document in response:
        document.update(status=-1)
    s = Search(using=connections, index="Embedding").filter("term", document_id=document_id)
    response = s.execute()
    # 遍历搜索结果中的每个文档，将 status 更新为 -1
    for document in response:
        document.update(status=-1)


def purge_document_by_id(document_id):
    s = Search(using=connections, index="Document").filter("term", id=document_id)
    response = s.execute()
    for document in response:
        document.delete()
    s = Search(using=connections, index="Embedding").filter("term", document_id=document_id)
    response = s.execute()
    # 遍历搜索结果中的每个文档，将 status 更新为 -1
    for document in response:
        document.delete()

def set_document_summary(document_id, summary):
    s = Search(using=connections, index="Embedding").filter("term", id=document_id)
    response = s.execute()
    for document in response:
        document.update(summary = summary)


def get_document_by_id(document_id):
    s = Search(using=connections, index="Document").filter("term", id=document_id)
    response = s.execute()
    if response.hits.total.value > 0:
        first = response.hits[0]
        return first
    else:
        return None'''


