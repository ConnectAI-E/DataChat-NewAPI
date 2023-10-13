from elasticsearch import Elasticsearch, NotFoundError


# 插入文档

class Es():
    ELASTIC_PASSWORD = "<password>"
    CLOUD_ID = "deployment-name:dXMtZWFzdDQuZ2Nw..."
    es = Elasticsearch(
        cloud_id=CLOUD_ID,
        basic_auth=("elastic", ELASTIC_PASSWORD)
    )

    def create_index(index):
        # 创建索引，如果索引已存在，则抛出异常
        try:
            es.indices.create(index=index)
        except Elasticsearch.ElasticsearchException as es1:
            print('Index already exists!!')

    def index_document(index, id, data):
        try:
            # 使用 op_type="create" 参数来确保文档在索引中不存在时才会被创建
            es.index(index=index, id=id, body=data, op_type="create")
        except Elasticsearch.ElasticsearchException as e:
            # 如果文档已存在，抛出异常
            print('document already exists!!')

    def get_document_by_id(index, id):
        try:
            response = es.get(index=index, id=id)
            return response
        except NotFoundError:
            return None

    def search_docunmet(index,query):
        try:
            response = es.search(index="User", query=query)
            return response
        except NotFoundError:
            return None
