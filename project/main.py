from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from worker import create_task
from server import model




app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



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

@app.get("/test01")
def sum(a,b):
    return {"a":a,"b":b}



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
