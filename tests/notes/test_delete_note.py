from bson import ObjectId
from notes_backend.collections import get_collection, Collections


class TestDeleteNote:
    def test_delete_note(self, test_client, UserDBFactory, GroupDBModelFactory, NoteDBFactory, login):
        user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)
        note = NoteDBFactory(group_id=group.id)

        note_collection_count_before_delete = get_collection(Collections.NOTE_COLLECTION).count_documents({})
        assert note_collection_count_before_delete == 1

        login_header = login(user)
        response = test_client.get(f'/note/delete-note/{group.id}/note/{note.id}', headers=login_header)

        assert response.status_code == 200
        assert response.json()['status'] is True

        note_collection_count_after_delete = get_collection(Collections.NOTE_COLLECTION).count_documents({})
        assert note_collection_count_after_delete == 0

    def test_delete_note_if_group_not_exist(self, test_client, UserDBFactory, NoteDBFactory, login):
        user = UserDBFactory()
        group_id = ObjectId()
        note = NoteDBFactory(group_id=group_id)

        login_header = login(user)
        response = test_client.get(f'/note/delete-note/{group_id}/note/{note.id}', headers=login_header)

        assert response.status_code == 404

    def test_delete_note_if_note_not_in_the_group(self, test_client, UserDBFactory, GroupDBModelFactory, NoteDBFactory, login):
        user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)
        another_group = GroupDBModelFactory(owner_id=user.id)
        note = NoteDBFactory(group_id=another_group.id)

        note_collection_count_before_delete = get_collection(Collections.NOTE_COLLECTION).count_documents({})
        assert note_collection_count_before_delete == 1

        login_header = login(user)
        response = test_client.get(f'/note/delete-note/{group.id}/note/{note.id}', headers=login_header)

        assert response.status_code == 404

        note_collection_count_after_delete = get_collection(Collections.NOTE_COLLECTION).count_documents({})
        assert note_collection_count_after_delete == 1

    def test_delete_note_if_user_not_in_the_group(self, test_client, UserDBFactory, GroupDBModelFactory, NoteDBFactory, login):
        user = UserDBFactory()
        owner_user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=owner_user.id)
        note = NoteDBFactory(group_id=group.id)

        note_collection_count_before_delete = get_collection(Collections.NOTE_COLLECTION).count_documents({})
        assert note_collection_count_before_delete == 1

        login_header = login(user)
        response = test_client.get(f'/note/delete-note/{group.id}/note/{note.id}', headers=login_header)

        assert response.status_code == 403

        note_collection_count_after_delete = get_collection(Collections.NOTE_COLLECTION).count_documents({})
        assert note_collection_count_after_delete == 1
