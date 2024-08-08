from bson import ObjectId
from fastapi import APIRouter, status, Security, HTTPException
from fastapi_jwt import JwtAuthorizationCredentials
from notes_backend.auth.login_utilities import access_security
from notes_backend.collections import get_collection, Collections
from notes_backend.models import StatusResponse

router = APIRouter()


@router.get('/', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def check_server_health():
    return StatusResponse(status=True)


@router.get('/check-key', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def check_key_health(credentials: JwtAuthorizationCredentials = Security(access_security)):
    user_id = credentials.subject['id']
    db_check_user = get_collection(Collections.USER_COLLECTION).find_one({'_id': ObjectId(user_id)})

    if not db_check_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail='there is no user with this id anymore')

    return StatusResponse(status=True)
