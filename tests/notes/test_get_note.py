from bson import ObjectId


class TestGetNote:
    def test_get_note(self, test_client, UserDBFactory, GroupDBModelFactory, NoteDBFactory, login):
        user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)
        note = NoteDBFactory(group_id=group.id)

        login_header = login(user)
        response = test_client.get(f'/note/get-note/{group.id}/note/{note.id}', headers=login_header)

        assert response.status_code == 200
        assert response.json()['group_id'] == str(note.group_id)

    def test_get_note_if_group_not_exist(self, test_client, UserDBFactory, NoteDBFactory, login):
        user = UserDBFactory()
        group_id = ObjectId()
        note = NoteDBFactory(group_id=group_id)

        login_header = login(user)
        response = test_client.get(f'/note/get-note/{group_id}/note/{note.id}', headers=login_header)

        assert response.status_code == 404

    def test_get_note_if_not_in_group(self, test_client, UserDBFactory, GroupDBModelFactory, NoteDBFactory, login):
        user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=user.id)
        another_group = GroupDBModelFactory(owner_id=user.id)
        note = NoteDBFactory(group_id=another_group.id)

        login_header = login(user)
        response = test_client.get(f'/note/get-note/{group.id}/note/{note.id}', headers=login_header)

        assert response.status_code == 404

    def test_get_note_if_user_not_in_group(self, test_client, UserDBFactory, JoinGroups, NoteDBFactory, login):
        user = UserDBFactory()
        another_user = UserDBFactory()
        group = JoinGroups(user=another_user, count_of_group=1)[0]
        note = NoteDBFactory(group_id=group.id)

        login_header = login(user)
        response = test_client.get(f'/note/get-note/{group.id}/note/{note.id}', headers=login_header)

        assert response.status_code == 403

