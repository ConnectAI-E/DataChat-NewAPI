from elasticsearch import Elasticsearch

# 创建 Elasticsearch 连接
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# 定义索引的映射（文档结构）
User_mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},  # 使用 keyword 类型用于精确匹配
            "openid": {"type": "keyword"},
            "data": {"type": "text"},  # 使用 text 类型用于存储文本数据
            "expiry": {"type": "date"}  # 使用 date 类型用于存储日期时间
        }
    }
}

# 创建索引，如果索引已存在，则忽略
index_name = "User"  # 索引的名称为 "sessions"
es.indices.create(index=index_name, body=User_mapping, ignore=400)