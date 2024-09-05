import datetime
import math
import random
import re
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, status, Body, HTTPException, Security

from fastapi_jwt import JwtAuthorizationCredentials

from notes_backend.auth.login_utilities import access_security, refresh_security, refresh, auth
from notes_backend.auth.models import RefreshResponse, AuthResponse
from notes_backend.core.NotesBaseModel import ObjectIdPydanticAnnotation
from notes_backend.core.email_service import EmailService
from notes_backend.models import StatusResponse
from notes_backend.patterns import Patterns
from notes_backend.user.models import UserRegisterModel, UserLoginModel, UserDBModel, UserGetResponseModel, \
    UserOTPCreateModel, UserOTPModel, UserRenewPassword
from notes_backend.collections import get_collection, Collections
from notes_backend.user.otp_types import OTP_TYPES

router = APIRouter()

OTP_CODE_EXPIRES_IN = datetime.timedelta(days=1)

def generate_otp_code():
    OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

    digits = "0123456789"
    otp = ''

    for i in range(6):
        otp += digits[math.floor(random.random() * 10)]

    check_otp_code_for_existence_collection = OTP_COLLECTION.find_one({'otp_code': otp})
    check_otp_code_for_existence = UserOTPModel.from_mongo(check_otp_code_for_existence_collection)

    if check_otp_code_for_existence:
        if check_otp_code_for_existence.end_time < datetime.datetime.now():
            OTP_COLLECTION.find_one_and_delete({'otp_code': otp})
        else:
            return generate_otp_code()

    return otp

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
def user_register(user: UserRegisterModel = Body(...)):
    if not re.match(Patterns.EMAIL.value, user.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='mail doğru değil')

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
                            detail='mail doğru değil')

    check_user_collection = get_collection(Collections.USER_COLLECTION).find_one({'email': user.email,
                                                                                  'password': user.password})

    if not check_user_collection:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='email veya şifre hatalı.')

    check_user = UserDBModel.from_mongo(check_user_collection)
    return auth(check_user)


@router.get('/get-user/{user_id}', status_code=status.HTTP_200_OK, response_model=UserGetResponseModel)
def get_user(user_id: Annotated[ObjectId, ObjectIdPydanticAnnotation],
             credentials: JwtAuthorizationCredentials = Security(access_security)):
    wanted_user_collection = get_collection(Collections.USER_COLLECTION).find_one({'_id': user_id})
    wanted_user = UserGetResponseModel.from_mongo(wanted_user_collection)

    if not wanted_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='there is no user with this id')

    return wanted_user


@router.get('/refresh-token', status_code=status.HTTP_200_OK, response_model=RefreshResponse)
def refresh_token(credentials: JwtAuthorizationCredentials = Security(refresh_security)):
    user_id = credentials.subject['id']
    db_check_user = get_collection(Collections.USER_COLLECTION).find_one({'_id': ObjectId(user_id)})

    if not db_check_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail='there is no user with this id anymore')

    return refresh(credentials.subject)


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


@router.get('/send-forgot-otp/{email}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def send_forgot_otp(email: str):
    if not re.match(Patterns.EMAIL.value, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='email is not correct')

    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)
    OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

    check_email_collection = USER_COLLECTION.find_one({'email': email})
    check_email = UserDBModel.from_mongo(check_email_collection)

    if not check_email:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='there is no user with this email')

    now = datetime.datetime.now()

    generated_code = generate_otp_code()
    new_otp = UserOTPCreateModel(requested_by=check_email.id,
                                 created_time=now,
                                 end_time=now + OTP_CODE_EXPIRES_IN,
                                 otp_code=generated_code,
                                 otp_type=OTP_TYPES.PASSWORD_RESET)

    OTP_COLLECTION.insert_one(new_otp.to_mongo())
    try_send_mail = EmailService.send_email(email, EmailService.generate_otp_content(generated_code, new_otp.otp_type))

    return StatusResponse(status=try_send_mail)


@router.get('/check-otp/{email}/{otp_code}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def check_otp(email: str, otp_code: str):
    if not re.match(Patterns.EMAIL.value, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='email is not correct')

    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)
    OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

    check_email_collection = USER_COLLECTION.find_one({'email': email})
    check_email = UserDBModel.from_mongo(check_email_collection)

    if not check_email:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='there is no user with this email')

    check_otp_correction_collection = OTP_COLLECTION.find_one({'requested_by': check_email.id, 'otp_code': otp_code})
    check_otp_correction = UserOTPModel.from_mongo(check_otp_correction_collection)

    if not check_otp_correction or check_otp_correction.end_time < datetime.datetime.now() or check_otp_correction.otp_type != OTP_TYPES.PASSWORD_RESET.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='otp is invalid')

    return StatusResponse(status=True)


@router.post('/renew-password/{email}/{otp_code}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def renew_password(email: str, otp_code: str, user_renew_password: UserRenewPassword = Body(...)):
    if not re.match(Patterns.EMAIL.value, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='email is not correct')

    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)
    OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

    check_email_collection = USER_COLLECTION.find_one({'email': email})
    check_email = UserDBModel.from_mongo(check_email_collection)

    if not check_email:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='there is no user with this email')

    check_otp_correction_collection = OTP_COLLECTION.find_one({'requested_by': check_email.id, 'otp_code': otp_code})
    check_otp_correction = UserOTPModel.from_mongo(check_otp_correction_collection)

    if not check_otp_correction or check_otp_correction.end_time < datetime.datetime.now():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='otp is invalid')

    check_email.password = user_renew_password.password
    USER_COLLECTION.find_one_and_update(filter={'_id': check_email.id},
                                        update={'$set': check_email.to_mongo()})

    OTP_COLLECTION.find_one_and_delete({'_id': check_otp_correction.id})

    return StatusResponse(status=True)


@router.get('/send-delete-account-otp/{email}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def send_delete_account_otp(email: str):
    if not re.match(Patterns.EMAIL.value, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='email is not correct')

    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)
    OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

    check_email_collection = USER_COLLECTION.find_one({'email': email})
    check_email = UserDBModel.from_mongo(check_email_collection)

    if not check_email:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='there is no user with this email')

    now = datetime.datetime.now()

    generated_code = generate_otp_code()
    new_otp = UserOTPCreateModel(requested_by=check_email.id,
                                 created_time=now,
                                 end_time=now + OTP_CODE_EXPIRES_IN,
                                 otp_code=generated_code,
                                 otp_type=OTP_TYPES.REMOVE_ACC)

    OTP_COLLECTION.insert_one(new_otp.to_mongo())
    try_send_mail = EmailService.send_email(email, EmailService.generate_otp_content(generated_code, new_otp.otp_type))

    return StatusResponse(status=try_send_mail)


@router.get('/confirm-to-delete/{email}/{otp_code}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def confirm_to_delete(email: str, otp_code: str):
    if not re.match(Patterns.EMAIL.value, email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='email is not correct')

    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)
    OTP_COLLECTION = get_collection(Collections.OTP_COLLECTION)

    check_email_collection = USER_COLLECTION.find_one({'email': email})
    check_email = UserDBModel.from_mongo(check_email_collection)

    if not check_email:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='there is no user with this email')

    check_otp_correction_collection = OTP_COLLECTION.find_one({'requested_by': check_email.id, 'otp_code': otp_code})
    check_otp_correction = UserOTPModel.from_mongo(check_otp_correction_collection)

    if not check_otp_correction or check_otp_correction.end_time < datetime.datetime.now() or check_otp_correction.otp_type != OTP_TYPES.REMOVE_ACC.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='otp is invalid')


    OTP_COLLECTION.find_one_and_delete({'_id': check_otp_correction.id})

    return StatusResponse(status=True)
