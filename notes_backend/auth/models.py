from notes_backend.core.NotesBaseModel import NotesBaseModel
from notes_backend.user.models import UserGetResponseModel


class Tokens(NotesBaseModel):
    access_token: str
    refresh_token: str


class AuthResponse(NotesBaseModel):
    user: UserGetResponseModel
    tokens: Tokens


class RefreshResponse(NotesBaseModel):
    access_token: str
    refresh_token: str
