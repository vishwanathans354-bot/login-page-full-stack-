from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer

# ================== BASIC CONFIG ==================
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# ================== CORS ==================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== DATABASE ==================
client = MongoClient("mongodb://localhost:27017/")
db = client["auth_db"]
users = db["users"]

# ================== PASSWORD ==================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# ================== TOKEN ==================
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ================== MODELS ==================
class User(BaseModel):
    email: EmailStr
    password: str

# ================== ROUTES ==================

# Test route (VERY IMPORTANT)
@app.get("/")
def home():
    return {"message": "Backend running successfully"}

# Register
@app.post("/register")
def register(user: User):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="User already exists")

    users.insert_one({
        "email": user.email,
        "password": hash_password(user.password)
    })

    return {"message": "User registered"}

# Login
@app.post("/login")
def login(user: User):
    db_user = users.find_one({"email": user.email})

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"sub": user.email})

    return {"access_token": token}

# Protected route
@app.get("/protected")
def protected(user: str = Depends(get_current_user)):
    return {"message": f"Welcome {user}"}