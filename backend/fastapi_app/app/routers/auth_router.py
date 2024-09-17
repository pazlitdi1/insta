from fastapi import APIRouter, status, HTTPException, Depends
from fastapi_app.app.database import Session, ENGINE
from fastapi_app.app.models import User
from fastapi_app.app.schemas import Settings, LoginSchema, RegisterSchema
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
import datetime

session = Session(bind=ENGINE)

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@auth_router.get("/")
async def auth():
    return {"message": "Auth router"}


@auth_router.post("/login")
async def login(request: LoginSchema, authorization: AuthJWT = Depends()):
    user_check = session.query(User).filter(
        or_(
            User.username == request.username_or_email,
            User.email == request.username_or_email
        )
    ).first()
    if user_check is not None:
        if check_password_hash(user_check.password, request.password):
            access_token = authorization.create_access_token(subject=request.username_or_email, expires_time=datetime.timedelta(minutes=1))
            refresh_token = authorization.create_refresh_token(subject=request.username_or_email, expires_time=datetime.timedelta(days=1))
            response = {
                "status_code": 200,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "detail": "Login successful"
            }
            return jsonable_encoder(response)
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")


@auth_router.post("/register")
async def register(request: RegisterSchema):
    try:
        check_user = session.query(User).filter(
            or_(
                User.email == request.email,
                User.username == request.username
            )
        ).first()
        if check_user:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already registered")

        new_user = User(
            email=request.email,
            username=request.username,
            password=generate_password_hash(request.password)
        )
        session.add(new_user)
        session.commit()
        return HTTPException(status_code=status.HTTP_201_CREATED, detail="User registered")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating user")


@auth_router.get("/token/verify")
def verify_token(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        return {"status_code": 200, "detail": "JWT Token Verified"}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token is expired or invalid")


@auth_router.get("/users")
async def users():
    users = session.query(User).all()
    return users
