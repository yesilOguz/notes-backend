import math
import random
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, status, HTTPException, Security, Body
from fastapi_jwt import JwtAuthorizationCredentials

from notes_backend.auth.login_utilities import access_security
from notes_backend.collections import get_collection, Collections
from notes_backend.core.NotesBaseModel import ObjectIdPydanticAnnotation
from notes_backend.group.models import GroupCreateModel, GroupGetResponse, GroupDBModel, GroupUpdateModel
from notes_backend.models import StatusResponse
from notes_backend.notes.models import NotesDBModel
from notes_backend.user.models import UserDBModel, UserType, UserGetResponseModel

router = APIRouter()


FREE_PLAN_CAPACITY = 2
PAID_PLAN_CAPACITY = 2
FAMILY_PLAN_CAPACITY = 5


def check_group_code(group_code: str):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    check_group_code_for_existence_collection = GROUP_COLLECTION.find_one({'group_code': group_code})

    return check_group_code_for_existence_collection is not None


def generate_group_code():
    digits = "0123456789abcdefghijklmnoprstuvyz"
    code = ''

    for i in range(6):
        code += digits[math.floor(random.random() * len(digits))]

    check_code = check_group_code(code)

    if check_code:
        return generate_group_code()

    return code


def makeGroupGetResponse(group: GroupDBModel):
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)
    NOTE_COLLECTION = get_collection(Collections.NOTE_COLLECTION)

    owner_user_collection = USER_COLLECTION.find_one({'_id': group.group_owner})
    owner_user = UserGetResponseModel.from_mongo(owner_user_collection)

    attendee_list = []
    for attendee in group.attendees:
        user_collection = USER_COLLECTION.find_one({'_id': attendee})
        user = UserGetResponseModel.from_mongo(user_collection)

        attendee_list.append(user)

    note_list = []
    for note_id in group.notes:
        note_collection = NOTE_COLLECTION.find_one({'_id': note_id})
        note = NotesDBModel.from_mongo(note_collection)

        note_list.append(note)

    return GroupGetResponse(
        id=group.id,
        group_owner=owner_user,
        group_code=group.group_code,
        group_name=group.group_name,
        attendees=attendee_list,
        notes=note_list
    )


@router.post('/create-group', status_code=status.HTTP_201_CREATED, response_model=GroupGetResponse)
def create_group(group: GroupCreateModel = Body(...),
                 credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    user_collection = USER_COLLECTION.find_one({'_id': ObjectId(credentials.subject['id'])})
    user = UserDBModel.from_mongo(user_collection)

    group_code = group.group_code

    if group_code and user.plan == UserType.FREE_PLAN.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='Bu özelliği kullanmak için abone olmanız gerekiyor')

    if not group_code:
        group_code = generate_group_code()
    else:
        check_code = check_group_code(group_code)
        if check_code:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                detail='Bu grup koduyla bir grup zaten var.')

    group.attendees = [user.id]
    group.group_code = group_code
    group.group_owner = user.id
    inserted_group_id = GROUP_COLLECTION.insert_one(group.to_mongo())
    inserted_group_collection = GROUP_COLLECTION.find_one({'_id': inserted_group_id.inserted_id})

    inserted_group = GroupDBModel.from_mongo(inserted_group_collection)

    user.groups.append(inserted_group.id)

    USER_COLLECTION.find_one_and_update(filter={'_id': user.id},
                                        update={'$set': user.to_mongo(exclude_unset=False)})

    group_get = makeGroupGetResponse(inserted_group)
    return group_get


@router.post('/update-group/{group_id}', status_code=status.HTTP_200_OK, response_model=GroupGetResponse)
def update_group(group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation],
                 group_data: GroupUpdateModel,
                 credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    group_collection = GROUP_COLLECTION.find_one({'_id': group_id})
    group = GroupDBModel.from_mongo(group_collection)

    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='grup bulunamadı')

    if group.group_owner != user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail='grup özelliklerini güncelleyebilmek için grup sahibi olmanız gerekli')

    GROUP_COLLECTION.find_one_and_update(filter={'_id': group.id},
                                         update={'$set': group_data.to_mongo(exclude_none=True)})

    updated_group_collection = GROUP_COLLECTION.find_one({'_id': group.id})
    updated_group = GroupDBModel.from_mongo(updated_group_collection)

    updated_group_to_return = makeGroupGetResponse(updated_group)
    return updated_group_to_return


@router.get('/invite/{group_code}', status_code=status.HTTP_200_OK)
def get_group_data():
    # Burda mobil taraf için deep linking yapılacak
    # Uygulamaya yönlendirmesi için dosyaları burda sunucaz
    pass


@router.get('/join-group/{group_code}', status_code=status.HTTP_200_OK, response_model=GroupGetResponse)
def join_group(group_code: str,
               credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    check_group_code_collection = GROUP_COLLECTION.find_one({'group_code': group_code})
    group = GroupDBModel.from_mongo(check_group_code_collection)

    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='bu grup koduyla bir grup yok')

    group_owner_collection = USER_COLLECTION.find_one({'_id': group.group_owner})
    group_owner = UserDBModel.from_mongo(group_owner_collection)

    user_collection = USER_COLLECTION.find_one({'_id': user_id})
    user = UserDBModel.from_mongo(user_collection)

    if not group_owner:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='grup sahibi olmadığı için gruba giremezsiniz.')

    owner_plan = group_owner.plan
    num_of_group_participants = len(group.attendees)

    max_capacity = 0

    if owner_plan == UserType.FREE_PLAN.value:
        max_capacity = FREE_PLAN_CAPACITY
    elif owner_plan == UserType.PAID_PLAN.value:
        max_capacity = PAID_PLAN_CAPACITY
    elif owner_plan == UserType.FAMILY_PLAN.value:
        max_capacity = FAMILY_PLAN_CAPACITY

    if num_of_group_participants >= max_capacity:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='grup dolu')

    group.attendees.append(user.id)
    user.groups.append(group.id)

    GROUP_COLLECTION.find_one_and_update(filter={'_id': group.id},
                                         update={'$set': group.to_mongo(exclude_unset=False)})
    USER_COLLECTION.find_one_and_update(filter={'_id': user.id},
                                        update={'$set': user.to_mongo(exclude_unset=False)})

    updated_group_db_collection = GROUP_COLLECTION.find_one({'_id': group.id})
    updated_group_db = GroupDBModel.from_mongo(updated_group_db_collection)

    updated_group = makeGroupGetResponse(updated_group_db)
    return updated_group


@router.get('/get-my-groups', status_code=status.HTTP_200_OK, response_model=list[GroupGetResponse])
def get_my_groups(credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])
    user_collection = USER_COLLECTION.find_one({'_id': user_id})
    user = UserDBModel.from_mongo(user_collection)

    groups = []
    for group in user.groups:
        user_group_collection = GROUP_COLLECTION.find_one({'_id': group})
        user_group = GroupDBModel.from_mongo(user_group_collection)

        group_get_model = makeGroupGetResponse(user_group)
        groups.append(group_get_model)

    return groups


@router.get('/leave-group/{group_code}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def leave_group(group_code: str,
                credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])
    user_collection = USER_COLLECTION.find_one({'_id': user_id})
    user = UserDBModel.from_mongo(user_collection)

    check_group_code_collection = GROUP_COLLECTION.find_one({'group_code': group_code})
    group = GroupDBModel.from_mongo(check_group_code_collection)

    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='grup bulunamadı')

    if group.group_owner == user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            detail='kendi grubunuzdan ayrılamazsınız.')

    if user.id not in group.attendees:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='Zaten grupta değilsiniz.')

    group.attendees.remove(user.id)
    user.groups.remove(group.id)

    USER_COLLECTION.find_one_and_update(filter={'_id': user.id},
                                        update={'$set': user.to_mongo(exclude_unset=False)})
    GROUP_COLLECTION.find_one_and_update(filter={'_id': group.id},
                                         update={'$set': group.to_mongo(exclude_unset=False)})

    return StatusResponse(status=True)


# notlar da silinecek
@router.get('/delete-group/{group_id}', status_code=status.HTTP_200_OK, response_model=StatusResponse)
def delete_group(group_id: Annotated[ObjectId, ObjectIdPydanticAnnotation],
                 credentials: JwtAuthorizationCredentials = Security(access_security)):
    GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)
    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    user_id = ObjectId(credentials.subject['id'])

    group_collection = GROUP_COLLECTION.find_one({'_id': group_id})
    group = GroupDBModel.from_mongo(group_collection)

    if not group:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail='grup bulunamadı')

    if group.group_owner != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            detail='bu işlemi yapamazsınız')

    for user in group.attendees:
        group_user_collection = USER_COLLECTION.find_one({'_id': user})
        group_user = UserDBModel.from_mongo(group_user_collection)

        group_user.groups.remove(group.id)

        USER_COLLECTION.find_one_and_update(filter={'_id': group_user.id},
                                            update={'$set': group_user.to_mongo(exclude_unset=False)})

    GROUP_COLLECTION.find_one_and_delete({'_id': group.id})
    return StatusResponse(status=True)
