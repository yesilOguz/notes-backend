from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, status
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import base64
import requests

from typing import Dict

from notes_backend.collections import get_collection, Collections
from notes_backend.models import StatusResponse
from notes_backend.user.models import UserDBModel
from notes_backend.user.routes import user_login

router = APIRouter()

GOOGLE_PEM_URL = 'https://www.gstatic.com/admob/reward/verifier-keys.json'

def get_public_keys() -> Dict[int, ec.EllipticCurvePublicKey]:
    response = requests.get(GOOGLE_PEM_URL)
    response.raise_for_status()
    keys_json = response.json()["keys"]

    public_keys = {}
    for key in keys_json:
        key_id = key["keyId"]
        base64_key = key["base64"]
        public_key_bytes = base64.urlsafe_b64decode(base64_key)
        public_key = serialization.load_der_public_key(public_key_bytes, backend=default_backend())
        public_keys[key_id] = public_key

    return public_keys

def verify_signature(data_to_verify: bytes, signature: bytes, key_id: int, public_keys: Dict[int, ec.EllipticCurvePublicKey]) -> None:
    public_key = public_keys.get(key_id)
    if not public_key:
        raise ValueError(f"Cannot find verifying key with key id: {key_id}")

    try:
        public_key.verify(signature, data_to_verify, ec.ECDSA(hashes.SHA256()))
    except Exception as e:
        raise ValueError(f"Verification failed: {str(e)}")

@router.get('/ssv', response_model=StatusResponse)
async def ssv(request: Request):
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    query_params = dict(request.query_params)
    key_id = query_params.get("key_id")
    signature = query_params.get("signature")

    user_id = ObjectId(query_params.get('user_id'))
    reward_item = query_params.get('reward_item')

    if 'credit' not in reward_item:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='you are not allowed to do this')

    if not key_id or not signature:
        raise HTTPException(status_code=400, detail="Missing key_id and/or signature parameters.")

    try:
        public_keys = get_public_keys()

        query_string = request.url.query
        payload = query_string[:query_string.index("signature") - 1].encode('utf-8')

        signature_bytes = base64.urlsafe_b64decode(signature)

        verify_signature(payload, signature_bytes, int(key_id), public_keys)
    except Exception as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail='Invalid signature')

    print(user_id)
    print(type(user_id))

    check_user_collection = USER_COLLECTION.find_one({'_id': user_id})
    check_user = UserDBModel.from_mongo(check_user_collection)

    print(check_user_collection)
    print(check_user)

    if not check_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='there is no user with this id!')

    try:
        credits_of_user = getattr(check_user, reward_item)
        setattr(check_user, reward_item, credits_of_user+1)
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='there is no type of credit')

    USER_COLLECTION.find_one_and_update(filter={'_id': check_user.id},
                                        update={'$set': check_user.to_mongo()})

    return StatusResponse(status=True)
