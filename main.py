from fastapi import FastAPI
from pydantic import BaseModel









app = FastAPI()



@app.get("/")
def name():
    return {'vishwanathan'}


@app.get("/hello")
def hello():
    return {'hello world'}
