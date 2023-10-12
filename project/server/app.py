from fastapi import FastAPI, Depends, HTTPException, Cookie
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi_sessions import SessionManager
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi import HTTPException
from redis import Redis
from datetime import timedelta
import os

app = FastAPI(__name__)
# 从环境变量中获取配置项,这里的配置项名为FASTAPI_CONFIG，可以根据需要修改
config_value = os.environ.get("FASTAPI_CONFIG")
# 将配置项添加到FastAPI应用的配置中
if config_value:
    app.config_example = config_value
else:
    app.config_example = "default_value"




redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)
# 初始化Session
session_manager = SessionManager(
    token_url="/token",  # 登录接口的路径
    lifetime_seconds=SESSION_COOKIE.total_seconds(),
    token_refresh_lifetime_seconds=3600,
    storage='redis',  # 使用Redis作为存储后端
    redis=redis,  # Redis客户端实例
)
# OAuth2密码授权模式的令牌获取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 创建CORS中间件实例
app.add_middleware(CORSMiddleware,allow_credentials=True,allow_headers=["Authorization", "X-Requested-With"],)


