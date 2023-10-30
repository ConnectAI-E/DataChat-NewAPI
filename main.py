import psycopg2,json,ast
import pandas as pd
from sqlalchemy import create_engine
from elasticsearch_dsl import (
    Date,
    Integer,
    Document as ESDocumentBase,
    Keyword,
    Object,
    Text,
    connections,
    DenseVector
)

connections.create_connection(hosts="http://192.168.110.34:9200", basic_auth=('elastic', 'fsMxQANdq1aZylypQWZD'))
#con = psycopg2.connect(database = "know",host="192.168.110.226", port="49199",user = "postgres",password="postgres")
engine = create_engine("postgresql+psycopg2://postgres:postgres@192.168.110.226:49199/know")
class ESDocument(ESDocumentBase):
    @property
    def id(self):
        return self.meta.id

    @property
    def created_at(self):
        return int(self.created.timestamp() * 1000)


class User(ESDocument):
    openid = Keyword()
    name = Text(fields={"keyword": Keyword()})
    status = Integer()
    extra = Object()    # 用于保存 JSON 数据
    created = Date()
    modified = Date()

    class Index:
        name = 'user'


class Collection(ESDocument):
    user_id = Keyword()  # 将字符串作为文档的 ID 存储
    name = Text(analyzer='ik_max_word')
    description = Text(analyzer='ik_max_word')  #知识库描述
    summary = Text(analyzer='ik_max_word')  #知识库总结
    status = Integer()
    created = Date()
    modified = Date()      #

    class Index:
        name = 'collection'


#Documents区别于固有的Docunment
class Documents(ESDocument):
    collection_id = Keyword()  # 将字符串作为文档的 ID 存储
    type = Keyword()    #文档类型用keyword保证不分词
    path = Keyword()    #文档所在路径
    name = Text(analyzer='ik_max_word')
    chunks = Integer() #文档分片个数
    uniqid = Keyword()  #去重的唯一ID
    summary = Text(analyzer='ik_max_word')  #文档摘要
    status = Integer()
    created = Date()
    modified = Date()  # 用于保存最后一次修改的时间

    class Index:
        name = 'document'


class Embedding(ESDocument):
    document_id = Keyword()     #文件ID
    collection_id = Keyword()    #知识库ID
    chunk_index = Keyword()    #文件分片索引
    chunk_size = Integer()  #文件分片大小
    document = Text(analyzer='ik_max_word')       #分片内容
    # embedding = DenseVector(dims=768, index=True, similarity="l2_norm")
    embedding = DenseVector(dims=768, index=True, similarity="cosine")
    status = Integer()
    created = Date()
    modified = Date()  # 用于保存最后一次修改的时间

    class Index:
        name = 'embedding'


class Bot(ESDocument):
    user_id = Keyword()  # 用户ID
    collection_id = Keyword()  # 知识库ID
    hash = Integer()    #hash
    extra = Object()    #机器人配置信息
    status = Integer()
    created = Date()
    modified = Date()  # 用于保存最后一次修改的时间

    class Index:
        name = 'bot'




def init():
    User.init()
    Collection.init()
    Documents.init()
    Collection.init()
    Bot.init()


def move_userdata():
    sql = "select ENCODE(id, 'hex') as id,openid,name,extra,status,created,modified from public.user "
    df = pd.read_sql_query(sql, con=engine)
    for index,row in df.iterrows():
        id = row['id']
        print(id)
        openid = row['openid']
        name = row['name']
        status = row['status']
        extra = json.loads(row['extra'])
        #print(extra)
        modified = row['modified']
        created = row['created']
        user = User(
            meta={'id':id},
            openid=openid,
            name=name,
            status=status,
            extra=extra,
            created = created,
            modified = modified,
        )
        user.save()

def move_documentdata():
    sql = "select ENCODE(id, 'hex') as id,ENCODE(collection_id, 'hex') as collection_id,name,type,path,chunks,summary,status,uniqid,created,modified from public.documents "
    df = pd.read_sql_query(sql, con=engine)
    for index,row in df.iterrows():
        id = row['id']
        print(id)
        collection_id = row['collection_id']
        name = row['name']
        type = row['type']
        path = row['path']
        chunks = row['chunks']
        uniqid = row['uniqid']
        status = row['status']
        summary = row['summary']
        # print(extra)
        modified = row['modified']
        created = row['created']
        document = Documents(
            meta={'id': id},
            collection_id=collection_id,
            name=name,
            type=type,
            path=path,
            uniqid=uniqid,
            chunks=chunks,
            summary=summary,
            status= status,
            created=created,
            modified=modified,
        )
        document.save()

def move_collectiondata():
    sql = "select ENCODE(id, 'hex') as id,ENCODE(user_id, 'hex') as user_id,name,description,summary,status,created,modified from public.collection "
    df = pd.read_sql_query(sql, con=engine)
    for index,row in df.iterrows():
        id = row['id']
        print(id)
        user_id = row['user_id']
        name = row['name']
        status = row['status']
        description = row['description']
        summary = row['summary']
        # print(extra)
        modified = row['modified']
        created = row['created']
        collection = Collection(
            meta={'id': id},
            user_id=user_id,
            name=name,
            description=description,
            summary=summary,
            status= status,
            created=created,
            modified=modified,
        )
        collection.save()

def move_embeddingbdata():
    sql = "select ENCODE(id, 'hex') as id,ENCODE(collection_id, 'hex') as collection_id,ENCODE(document_id, 'hex') as document_id,chunk_index,chunk_size,document,embedding,status,created,modified from public.embedding"
    df = pd.read_sql_query(sql, con=engine)
    for index,row in df.iterrows():
        id = row['id']
        print(id)
        collection_id = row['collection_id']
        document_id = row['document_id']
        chunk_index = row['chunk_index']
        chunk_size = row['chunk_size']
        status = row['status']
        document = row['document']
        embedding = ast.literal_eval(row['embedding'])
        # print(extra)
        modified = row['modified']
        created = row['created']
        embeddings = Embedding(
            meta={'id': id},
            collection_id=collection_id,
            document_id=document_id,
            chunk_index=chunk_index,
            chunk_size=chunk_size,
            document=document,
            embedding=embedding,
            status=status,
            created=created,
            modified=modified,
        )
        embeddings.save()

def move_botdata():
    sql = "select ENCODE(id, 'hex') as id,ENCODE(collection_id, 'hex') as collection_id,ENCODE(user_id, 'hex') as user_id,hash,extra,status,created,modified from public.bot "
    df = pd.read_sql_query(sql, con=engine)
    for index, row in df.iterrows():
        id = row['id']
        print(id)
        collection_id = row['collection_id']
        user_id = row['user_id']
        hash = row['hash']
        status = row['status']
        extra = json.loads(row['extra'])
        # print(extra)
        modified = row['modified']
        created = row['created']
        bot = Bot(
            meta={'id': id},
            collection_id=collection_id,
            user_id=user_id,
            hash=hash,
            extra=extra,
            status=status,
            created=created,
            modified=modified,
        )
        bot.save()

if __name__ == '__main__':
    """cur = con.cursor()
    cur.execute("SELECT * FROM public.user ")
    columns = [desc[0] for desc in cur.description]
    # 获取查询结果的列信息（表头）
    columns = [desc[0] for desc in cur.description]
    # 获取所有查询结果
    rows = cur.fetchall()
    # 将查询结果写入CSV文件
    with open('user.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        # 写入表头
        csvwriter.writerow(columns)

        # 写入查询结果
        csvwriter.writerows(rows)

    # 关闭游标和连接
    cur.close()
    con.close()"""
    init()
    #df['id'] = df['id'].apply(lambda x: bytes(x).decode('ISO-8859-1'))
    #print(df)
    #move_userdata()
    #move_collectiondata()
    #move_documentdata()
    move_embeddingbdata()
    #move_botdata()
