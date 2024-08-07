from typing import Optional, Annotated

import pytest
from bson import ObjectId
from faker import Faker

from notes_backend.collections import get_collection, Collections
from notes_backend.core.NotesBaseModel import ObjectIdPydanticAnnotation
from notes_backend.group.models import GroupDBModel
from notes_backend.notes.models import Color, NotesCreateModel, NotesDBModel

Faker.seed(3)
faker = Faker()


@pytest.fixture()
def NoteCreateModelFactory():
    def _func(color=faker.rgb_color()):
        color_values = color.split(',')
        color_obj = Color(r=color_values[0], g=color_values[1], b=color_values[2], alpha=1)
        create_note_obj = NotesCreateModel(color=color_obj)

        return create_note_obj
    return _func


@pytest.fixture()
def NoteDBFactory():
    def _func(color=faker.rgb_color(), group_id: Optional[Annotated[ObjectId, ObjectIdPydanticAnnotation]] = None):
        color_values = color.split(',')
        color_obj = Color(r=color_values[0], g=color_values[1], b=color_values[2], alpha=1)
        create_note_obj = NotesCreateModel(color=color_obj, group_id=group_id)

        NOTES_COLLECTION = get_collection(Collections.NOTE_COLLECTION)
        GROUP_COLLECTION = get_collection(Collections.GROUP_COLLECTION)

        group_collection = GROUP_COLLECTION.find_one({'_id': group_id})
        group = GroupDBModel.from_mongo(group_collection)

        inserted_note = NOTES_COLLECTION.insert_one(create_note_obj.to_mongo())

        note_collection = NOTES_COLLECTION.find_one({'_id': inserted_note.inserted_id})
        note = NotesDBModel.from_mongo(note_collection)

        if group:
            group.notes.append(note.id)
            GROUP_COLLECTION.find_one_and_update(filter={'_id': group.id},
                                                 update={'$set': group.to_mongo(exclude_unset=False)})

        return note
    return _func
