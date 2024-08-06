from datetime import timedelta

from fastapi_jwt import JwtAccessBearer

from notes_backend.auth.models import Tokens, AuthResponse, RefreshResponse
from notes_backend.user.models import UserDBModel, UserGetResponseModel

import os

SECRET = os.getenv('SECRET', None)

access_security = JwtAccessBearer(secret_key=SECRET, auto_error=True, access_expires_delta=timedelta(days=5))
refresh_security = JwtAccessBearer(secret_key=SECRET, auto_error=True)


def auth(user: UserDBModel):
    subject = {'id': str(user.id)}

    access_token = access_security.create_access_token(subject=subject)
    refresh_token = refresh_security.create_refresh_token(subject=subject)

    tokens = Tokens(access_token=access_token, refresh_token=refresh_token)

    user_get_model = UserGetResponseModel.from_mongo(user.to_mongo())

    return_model = AuthResponse(user=user_get_model, tokens=tokens)
    return return_model


def refresh(subject):
    access_token = access_security.create_access_token(subject=subject)
    refresh_token = refresh_security.create_refresh_token(subject=subject)

    response = RefreshResponse(access_token=access_token, refresh_token=refresh_token)

    return response
