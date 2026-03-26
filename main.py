from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# ================= CONFIG =================
SECRET_KEY = "secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= STATIC =================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================= DATABASE =================
client = MongoClient("mongodb://localhost:27017/")
db = client["auth_db"]
users = db["users"]

# ================= PASSWORD =================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p):
    return pwd_context.hash(p)

def verify_password(p, h):
    return pwd_context.verify(p, h)

# ================= TOKEN =================
def create_token(data: dict):
    data.update({"exp": datetime.utcnow() + timedelta(minutes=30)})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise HTTPException(401, "Invalid token")

        user = users.find_one({"email": email})
        if not user:
            raise HTTPException(401, "User not found")

        return email

    except JWTError as e:
        print("JWT ERROR:", e)
        raise HTTPException(401, "Invalid token")

# ================= MODELS =================
class User(BaseModel):
    email: EmailStr
    password: str

# ================= ROUTES =================

@app.get("/")
def home():
    return FileResponse("static/login.html")

@app.get("/register-page")
def register_page():
    return FileResponse("static/register.html")

@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")

# REGISTER
@app.post("/register")
def register(user: User):
    try:
        print("REGISTER HIT:", user.email)

        if users.find_one({"email": user.email}):
            raise HTTPException(400, "User already exists")

        users.insert_one({
            "email": user.email,
            "password": hash_password(user.password)
        })

        return {"message": "Registered successfully"}

    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(500, "Server error")

# LOGIN
@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):
    try:
        print("LOGIN HIT:", form.username)

        db_user = users.find_one({"email": form.username})
        print("DB USER:", db_user)

        if not db_user:
            raise HTTPException(400, "User not found")

        if not verify_password(form.password, db_user["password"]):
            raise HTTPException(400, "Wrong password")

        token = create_token({"sub": form.username})

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except Exception as e:
        print("LOGIN ERROR:", e)
        raise HTTPException(500, "Server error")

# PROTECTED
@app.get("/protected")
def protected(user: str = Depends(get_current_user)):
    return {"message": f"Welcome {user}"}