from fastapi import APIRouter, Request, HTTPException, status
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
import base64
import requests

from notes_backend.models import StatusResponse

router = APIRouter()

GOOGLE_PEM_URL = 'https://www.gstatic.com/admob/reward/verifier-keys.json'

@router.get('/ssv', status_code=status.HTTP_200_OK, response_model=StatusResponse)
async def groups_ssv(request: Request):
    pem_response = requests.get(GOOGLE_PEM_URL)
    pem_response_json = pem_response.json()
    pem = pem_response_json['keys'][0]['pem']

    params = request.query_params
    google_public_key = serialization.load_pem_public_key(pem.encode())

    signature = params.get("signature")
    signed_data = f"{params.get('ad_network')},{params.get('ad_unit')},{params.get('reward_amount')},{params.get('reward_item')},{params.get('transaction_id')},{params.get('user_id')},{params.get('timestamp')}"

    try:
        google_public_key.verify(
            base64.b64decode(signature),
            signed_data.encode(),
            ec.ECDSA(hashes.SHA256())
        )

        print('başarılı')
        print(params.get('user_id'))
    except Exception as e:
        raise HTTPException(status_code=403, detail="Unauthorized request: Invalid signature")

    return StatusResponse(status=True)

