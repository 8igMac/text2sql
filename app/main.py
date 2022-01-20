from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import app.db as db
import app.rule as rule

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class UserIn(BaseModel):
    text: str

class UserOut(BaseModel):
    sql: str
    result: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {
        "page": "Home page",
    }

    return templates.TemplateResponse("page.html", {"request": request, "data": data})

@app.post("/query", response_model=UserOut)
def query(input: UserIn):
    # try:
    #     sql = rule.text2sql(input.text)
    #     result_dict = db.execute(sql)
    #     result_str = str(result_dict) # TODO: do anything with the dictionary.
    #     return {"sql": sql, "result": result_str}
    # except Exception as e:
    #     return {"sql": '', "result": str(e)}
    sql = rule.text2sql(input.text)
    result_dict = db.execute(sql)
    result_str = str(result_dict) # TODO: do anything with the dictionary.
    return {"sql": sql, "result": result_str}
        

@app.get("/getall")
def get_all():
    result_dict = db.get_all_data()
    return result_dict
