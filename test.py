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

from elasticsearch import Elasticsearch
import bson

class ObjID():
    def new_id():
        return str(bson.ObjectId())
    def is_valid(value):
        return bson.ObjectId.is_valid(value)
class User(Document):
    __tablename__ = 'user'
    openid = Long()
    name = Text(fields={"keyword": Keyword()})
    status = Integer()
    extra = Object()    # 用于保存 JSON 数据
    created = Date()
    modified = Date()  # 用于保存最后一次修改的时间

    class Index:
        name = 'user'



def save_user(openid='', name='', **kwargs):
    s = Search(using="es", index="user").filter("term",status=0).filter("term",openid=openid)
    response = s.execute()
    if not response.hits.total.value :
        user = User(
            meta={'id': ObjID.new_id()},
            openid=openid,
            name=name,
            status =0,
            extra=kwargs,
        )
        user.save(using="es")
        return user
    else:
        user = User.get(using="es",id = response.hits[0].meta.id)
        user.update(using="es",openid=openid,name=name,extra=kwargs)
        return  user


if __name__ == '__main__':
    '''es = Elasticsearch( "http://192.168.239.128:9200",basic_auth=('elastic', 'fsMxQANdq1aZylypQWZD'))
    print(es)'''
    connections.create_connection(alias="es", hosts="http://192.168.110.47:9200",basic_auth=('elastic', 'fsMxQANdq1aZylypQWZD'))
    User.init(using="es")
    #print(save_user(1,2))
