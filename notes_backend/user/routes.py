import re

from bson import ObjectId
from fastapi import APIRouter, status, Body, HTTPException, Security

from fastapi_jwt import JwtAuthorizationCredentials

from notes_backend.auth.login_utilities import access_security, refresh_security, refresh, auth
from notes_backend.auth.models import RefreshResponse, AuthResponse
from notes_backend.models import StatusResponse
from notes_backend.patterns import Patterns
from notes_backend.user.models import UserRegisterModel, UserLoginModel, UserDBModel
from notes_backend.collections import get_collection, Collections

router = APIRouter()


@router.post('/user-register', status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
def user_register(user: UserRegisterModel = Body(...)):
    if not re.match(Patterns.EMAIL.value, user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='email is not correct')

    check_email = get_collection(Collections.USER_COLLECTION).find_one({'email': user.email})

    if check_email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='bu email zaten kayıtlı.')

    inserted = get_collection(Collections.USER_COLLECTION).insert_one(user.to_mongo())

    inserted_user_collection = get_collection(Collections.USER_COLLECTION).find_one({'_id': inserted.inserted_id})
    inserted_user = UserDBModel.from_mongo(inserted_user_collection)

    return auth(inserted_user)


@router.post('/login', status_code=status.HTTP_200_OK, response_model=AuthResponse)
def user_login(user: UserLoginModel = Body(...)):
    if not re.match(Patterns.EMAIL.value, user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='email is not correct')

    check_user_collection = get_collection(Collections.USER_COLLECTION).find_one({'email': user.email,
                                                                                  'password': user.password})

    if not check_user_collection:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail='email veya şifre hatalı.')

    check_user = UserDBModel.from_mongo(check_user_collection)
    return auth(check_user)


@router.get('/refresh-token', status_code=status.HTTP_200_OK, response_model=RefreshResponse)
def refresh_token(credentials: JwtAuthorizationCredentials = Security(refresh_security)):
    subject = credentials.subject

    return refresh(subject)


@router.get('/delete-user/{user_id}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def delete_user(user_id: str,
                credentials: JwtAuthorizationCredentials = Security(access_security)):
    if user_id != credentials.subject['id']:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail='başkasının hesabını silemezsin')

    deleted = get_collection(Collections.USER_COLLECTION).find_one_and_delete({'_id': ObjectId(user_id)})
    if deleted:
        return StatusResponse(stautus=True)

    return StatusResponse(status=False)
