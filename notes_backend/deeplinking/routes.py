from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get('/apple-app-site-association', response_class=FileResponse)
def apple_deeplink():
    return FileResponse('./deeplink/apple-app-site-association')


@router.get('/assetlinks.json', response_class=FileResponse)
def android_deeplink():
    return FileResponse('./deeplink/assetlinks.json')
