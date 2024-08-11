from notes_backend.collections import get_collection, Collections
from notes_backend.user.models import AdminRegisterModel
import hashlib


def create_system_admins():
    admins = [
        AdminRegisterModel(
            email='admin@system.com',
            password=hashlib.md5('admin'.encode()).hexdigest()
        )
    ]

    USER_COLLECTION = get_collection(Collections.USER_COLLECTION)

    for admin in admins:
        check_collection = USER_COLLECTION.find_one(admin.to_json())

        if not check_collection:
            USER_COLLECTION.insert_one(admin.to_mongo(exclude_unset=False))
