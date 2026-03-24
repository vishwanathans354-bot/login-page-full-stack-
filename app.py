from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel,EmailStr,Field
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime,timedelta
from fastapi.security import OAuth2AuthorizationCodeBearer


app=FastAPI()



    
    