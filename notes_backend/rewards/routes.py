from fastapi import APIRouter, Request, HTTPException, status
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
import base64
import requests

from notes_backend.models import StatusResponse

router = APIRouter()

GOOGLE_PEM_URL = 'https://www.gstatic.com/admob/reward/verifier-keys.json'

def get_public_keys():
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

def verify_signature(data_to_verify, signature, key_id, public_keys):
    public_key = public_keys.get(key_id)
    if not public_key:
        raise ValueError(f"Cannot find verifying key with key id: {key_id}")

    try:
        public_key.verify(signature, data_to_verify, ec.ECDSA(hashes.SHA256()))
    except Exception as e:
        raise ValueError(f"Verification failed: {str(e)}")

@router.get('/ssv', status_code=status.HTTP_200_OK, response_model=StatusResponse)
async def groups_ssv(request: Request):
    query_params = dict(request.query_params)
    key_id = query_params.get("key_id")
    signature = query_params.get("signature")

    if not key_id or not signature:
        raise HTTPException(status_code=400, detail="Missing key_id and/or signature parameters.")

    try:
        public_keys = get_public_keys()

        query_string = request.url.query
        payload = query_string[:query_string.index("signature") - 1].encode('utf-8')

        signature_bytes = base64.urlsafe_b64decode(signature)

        verify_signature(payload, signature_bytes, int(key_id), public_keys)
        return StatusResponse(status=True)
    except Exception as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='invalid signature')

