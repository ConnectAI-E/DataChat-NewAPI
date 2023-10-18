from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from worker import create_task
from server import model
import requests

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

@app.get("/test/<user_id>")
def run_test_get(user_id):
    return model.get_user(user_id)

@app.put("/test")
def run_test_save():
    name = requests.json.get('name')
    openid = requests.json.get('openid')
    return model.save_user(openid=openid,name=name)
@app.post("/test")
def run_task(payload = Body(...)):
    task_type = payload["type"]
    task = create_task.delay(int(task_type))
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    return JSONResponse(task_id)
