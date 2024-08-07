from notes_backend.user.models import UserType


class TestCreateNote:
    def test_create_note(self, test_client, UserDBFactory, GroupDBModelFactory, NoteCreateModelFactory, login):
        user = UserDBFactory(group_and_note_credit=1)
        group = GroupDBModelFactory(owner_id=user.id)

        note_model = NoteCreateModelFactory()

        login_headers = login(user)
        response = test_client.post(f'/note/create-note/{group.group_code}', json=note_model.to_json(), headers=login_headers)

        assert response.status_code == 201

    def test_create_note_if_user_has_no_credit(self, test_client, UserDBFactory, GroupDBModelFactory, NoteCreateModelFactory, login):
        user = UserDBFactory(group_and_note_credit=0)
        group = GroupDBModelFactory(owner_id=user.id)

        note_model = NoteCreateModelFactory()

        login_headers = login(user)
        response = test_client.post(f'/note/create-note/{group.group_code}', json=note_model.to_json(), headers=login_headers)

        assert response.status_code == 403

    def test_create_note_if_user_has_notification_credits(self, test_client, UserDBFactory, GroupDBModelFactory, NoteCreateModelFactory, login):
        user = UserDBFactory(notification_credit=1)
        group = GroupDBModelFactory(owner_id=user.id)

        note_model = NoteCreateModelFactory()

        login_headers = login(user)
        response = test_client.post(f'/note/create-note/{group.group_code}', json=note_model.to_json(), headers=login_headers)

        assert response.status_code == 403

    def test_create_note_if_user_has_no_credit_but_user_in_paid_plan(self, test_client, UserDBFactory, GroupDBModelFactory, NoteCreateModelFactory, login):
        user = UserDBFactory(plan=UserType.PAID_PLAN)
        group = GroupDBModelFactory(owner_id=user.id)

        note_model = NoteCreateModelFactory()

        login_headers = login(user)
        response = test_client.post(f'/note/create-note/{group.group_code}', json=note_model.to_json(), headers=login_headers)

        assert response.status_code == 201

    def test_create_note_if_user_has_no_credit_but_user_in_family_plan(self, test_client, UserDBFactory, GroupDBModelFactory, NoteCreateModelFactory, login):
        user = UserDBFactory(plan=UserType.FAMILY_PLAN)
        group = GroupDBModelFactory(owner_id=user.id)

        note_model = NoteCreateModelFactory()

        login_headers = login(user)
        response = test_client.post(f'/note/create-note/{group.group_code}', json=note_model.to_json(), headers=login_headers)

        assert response.status_code == 201

    def test_create_note_if_group_not_exist(self, test_client, UserDBFactory, NoteCreateModelFactory, login):
        user = UserDBFactory(group_and_note_credit=1)
        group_code = 'not-exist'

        note_model = NoteCreateModelFactory()

        login_headers = login(user)
        response = test_client.post(f'/note/create-note/{group_code}', json=note_model.to_json(), headers=login_headers)

        assert response.status_code == 404

    def test_create_note_if_user_not_in_group(self, test_client, UserDBFactory, GroupDBModelFactory, NoteCreateModelFactory, login):
        user = UserDBFactory(group_and_note_credit=1)
        owner_user = UserDBFactory()
        group = GroupDBModelFactory(owner_id=owner_user.id)

        note_model = NoteCreateModelFactory()

        login_headers = login(user)
        response = test_client.post(f'/note/create-note/{group.group_code}', json=note_model.to_json(), headers=login_headers)

        assert response.status_code == 403
