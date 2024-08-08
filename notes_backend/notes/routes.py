from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Body, status, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials
from notes_backend.auth.login_utilities import access_security
from notes_backend.collections import get_collection, Collections
from notes_backend.core.NotesBaseModel import ObjectIdPydanticAnnotation
from notes_backend.group.models import GroupDBModel
from notes_backend.models import StatusResponse
from notes_backend.notes.models import NotesGetModel, NotesCreateModel, NotesDBModel
from notes_backend.user.models import UserDBModel, UserType

router = APIRouter()


@router.post('/create-note/{group_code}', status_code=status.HTTP_201_CREATED, response_model=NotesGetModel)
def create_note(group_code: str, note: NotesCreateModel = Body(...),
                credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)
    NOTE_COLLECTION = get_collection(Collections.NOTE_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    user_collection = USER_COLLECTION.find_one({'_id': user_id})
    user = UserDBModel.from_mongo(user_collection)

    if user.group_and_note_credit == 0 and user.plan == UserType.FREE_PLAN.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='not oluşturmak için yeterli krediniz yok')

    group_collection = GROUP_COLLECTION.find_one({'group_code': group_code})
    group = GroupDBModel.from_mongo(group_collection)

    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='grup bulunamadı')

    if user.id not in group.attendees:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='bu gruba üye değilsiniz')

    if user.plan == UserType.FREE_PLAN.value:
        user.group_and_note_credit -= 1

        USER_COLLECTION.find_one_and_update(filter={'_id': user.id},
                                            update={'$set': user.to_mongo(exclude_unset=False)})

    note.group_id = group.id
    inserted_note = NOTE_COLLECTION.insert_one(note.to_mongo())
    inserted_collection = NOTE_COLLECTION.find_one({'_id': inserted_note.inserted_id})
    inserted = NotesGetModel.from_mongo(inserted_collection)

    group.notes.append(inserted.id)

    return inserted


@router.get('/get-note/{group_id}/note/{note_id}', status_code=status.HTTP_200_OK, response_model=NotesGetModel)
def get_note(group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation],
             note_id: Annotated[ObjectId, ObjectIdPydanticAnnotation],
             credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    NOTE_COLLECTION = get_collection(Collections.NOTE_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    group_collection = GROUP_COLLECTION.find_one({'_id': group_id})
    group = GroupDBModel.from_mongo(group_collection)

    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='grup bulunamadı')

    if note_id not in group.notes:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='not bulunumadı')

    if user_id not in group.attendees:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='bu nota erişiminiz yoktur')

    note_collection = NOTE_COLLECTION.find_one({'_id': note_id})
    note = NotesGetModel.from_mongo(note_collection)

    return note


@router.get('/delete-note/{group_id}/note/{note_id}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def delete_note(group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation],
                note_id: Annotated[ObjectId, ObjectIdPydanticAnnotation],
                credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    NOTE_COLLECTION = get_collection(Collections.NOTE_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    group_collection = GROUP_COLLECTION.find_one({'_id': group_id})
    group = GroupDBModel.from_mongo(group_collection)

    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='grup bulunamadı')

    if note_id not in group.notes:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='not bulunumadı')

    if user_id not in group.attendees:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='bu nota erişiminiz yoktur')

    NOTE_COLLECTION.find_one_and_delete({'_id': note_id})

    return StatusResponse(status=True)
