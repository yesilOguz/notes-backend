from enum import Enum

from notes_backend.core.mongo_database import DB


class Collections(Enum):
    USER_COLLECTION = 'user'
    GROUP_COLLECTION = 'group'


def get_collection(collection_name: Collections):
    return DB[collection_name.value]

