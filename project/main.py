from fastapi import Body, FastAPI, Form, Request,Depends
from fastapi.responses import JSONResponse,RedirectResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_server_session import SessionManager
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi_server_session import SessionManager, RedisSessionInterface, Session
from worker import create_task
from server import model
import requests
import redis
import base64
import json
from time import time
import logging


class InternalError(Exception): pass
class PermissionDenied(Exception): pass
class NeedAuth(Exception): pass

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
session_manager = SessionManager(
    interface=RedisSessionInterface(redis.Redis(host="redis",port=6379,decode_responses=True))
)


def create_access_token(user,session):
    extra = user.extra.to_dict()
    # 同时兼容<has_privilege, expires>和<active, exp_time>
    if "exp_time" in extra:
        expires = extra["exp_time"]
    elif "permission" in extra:
        permission = extra["permission"]
        if "expires" in permission:
            expires = permission["expires"]
        else: expires = 0
    else: expires = 0
    if "active" in extra:
        privilege = extra["active"]
    elif "permission" in extra:
        permission = extra["permission"]
        if "has_privilege" in permission:
            privilege = permission["has_privilege"]
        else: privilege = False
    else:
        privilege = False
    #privilege = extra.get('active', extra.get('permission', {}).get('has_privilege', False))
    logging.debug("create_access_token %r expires %r time %r", user.extra, expires, time())
    #if privilege and expires > time():
    if isinstance(expires, (int, float)) and privilege and expires > time():
        return session.session_id, int(expires)
    raise PermissionDenied()




@app.get('/login')
def login_form():
    # 模拟客户的登录页面，

    html_content = '''
<h1>登录</h1>
<form action="/login" method="post">
  <input name="name" /><br />
  <input name="passwd" type="password" /><br />
  <button type="submit">登录</button>
</form>
    '''
    return HTMLResponse(html_content,status_code=200)




@app.post('/login')
def login_form(name: str = Form(...), passwd: str = Form(...)):
    logging.info("debug %r", (name, passwd))
    # TODO 这里模拟登录，不校验用户名密码，只要能
    # TODO 后面需要完善注册登录逻辑
    user = {
        'name': name,
        'openid': base64.urlsafe_b64encode(name.encode()).decode(),
        'permission': {
            'has_privilege': True,
            'expires': time() + 100,
            # TODO
            # 'collection_size': 10,
            # 'bot_size': 1,
        }
    }
    code = base64.b64encode(json.dumps(user).encode()).decode()
    return RedirectResponse('{}/api/login?code={}'.format("http://192.168.110.226:8004", code),status_code=303)


@app.get('/favicon.ico')
def faviconico():
    return ''

@app.get('/')
def home():
    html_content = '<h1>首页</h1><a href="/api/login">登录</a>'
    return HTMLResponse(html_content,status_code=200)

@app.get('/api/code2session')
def code2session(code: str = ''):
    # 模拟客户的code2session接口
    user = json.loads(base64.urlsafe_b64decode(code).decode())
    logging.debug('user %r', user)
    return JSONResponse({'data': user})

@app.get('/api/login')
def login_check(code: str= "",session: Session = Depends(session_manager.use_session)):
    # 如果没有权限，
    # user_id = session.get('user_id', '')
    # if user_id:
    #     return redirect('/api/login?code={}'.format(code))

    if not code:
        # 这里使用配置的站点的登录url
        return RedirectResponse("http://192.168.110.226:8004/login")

    user_info = requests.get('{}?code={}'.format(
        "http://192.168.110.226:8004/api/code2session", code,
    )).json()

    try:
        assert 'data' in user_info and 'openid' in user_info['data'], '获取用户信息失败'
        user = model.save_user(**user_info['data'])
        access_token, expired = create_access_token(user,session=session)
        # set session
        session['access_token'] = access_token
        session['expired'] = expired
        session['openid'] = user.openid
        session['user_id'] = str(user.meta.id)
        # return redirect('/')
        # 使用html进行跳转
        resp = HTMLResponse('<meta http-equiv="refresh" content="0;url={}/">'.format("http://192.168.110.226:8004"))
        resp.set_cookie("__sid__", session.session_id, max_age=86400)
        logging.info("session %r", session)
        # 登录成功，返回前端首页
        return resp
    except Exception as e:
        logging.error(e)
        return HTMLResponse('<h1>无访问权限</h1>')















@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", context={"request": request})

@app.post("/tasks", status_code=201)
def run_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})

@app.get("/test/init")
def run_test_init():
    return model.init()

'''
@app.get('/api/collection')
def api_collections(user_id):
    collections, total = model.get_collections(user_id=user_id)
    return JSONResponse({
        'code': 0,
        'msg': 'success',
        'data': [{
            'id': collection.hits.meta.id,
            'name': collection.hits.name,
            'description': collection.hits.description,
            'document_count': collection.hits.document_count,
            'created': int(collection.hits.created.timestamp() * 1000),
        } for collection in collections],
        'total': total,
    })'''
@app.post('/api/collection')
def api_save_collection(name, description,session: Session = Depends(session_manager.use_session)):
    user_id = session.get('user_id', '')
    app.logger.info("debug %r", [name, description])
    collection_id = model.save_collection(user_id, name, description)
    return JSONResponse({
        'code': 0,
        'msg': 'success',
        'data': {
            'id': collection_id,
            'collection_id': collection_id,
        },
    })

@app.put("/test/save_col/{user_id}/{name}/{description}")
def run_test_save_col(user_id,name,description):
    return model.save_collection(user_id=user_id,name=name,description=description)

@app.get("/test/grt_col/{user_id}")
def run_test_get_user(user_id):
    return model.get_collections(user_id=user_id)


@app.get("/test/{user_id}")
def run_test_get_user(user_id):
    return model.get_user(user_id)

@app.put("/test/{openid}/{name}")
def run_test_save(openid,name):
    return model.save_user(openid=openid,name=name)
@app.post("/test")
def run_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})




@app.get("/tasks/{task_id}")
def get_status(task_id):
    return JSONResponse(task_id)
