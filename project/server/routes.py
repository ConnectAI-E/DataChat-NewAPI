from app import app



# 定义登录接口
@app.post("/token")
async def login_for_access_token(token: str = Depends(oauth2_scheme), session=Depends(manager)):
    # 在此验证用户身份，如果验证成功，返回包含用户信息的访问令牌
    # 如果验证失败，可以抛出HTTPException
    # 如果使用fastapi_security库，可以使用security模块提供的authenticate_user函数来验证用户身份
    pass

# 定义需要会话验证的保护资源
@app.get("/protected")
async def protected_route(session=Depends(manager)):
    # 如果会话验证通过，返回受保护资源的响应
    return {"message": "This is a protected resource."}