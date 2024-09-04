from notes_backend.collections import get_collection, Collections
from notes_backend.user.models import UserType, UserDBModel


class TestSendGroupCredit:
    def test_send_group_credit(self, test_client, UserDBFactory, login):
        admin = UserDBFactory(plan=UserType.ADMIN_USER)
        user = UserDBFactory()

        amount = 100

        login_header = login(admin)
        response = test_client.get(f'/websocket/send-group-credit/{user.email}/{amount}', headers=login_header)

        db_check_collection = get_collection(Collections.USER_COLLECTION).find_one({'_id': user.id})
        db_check = UserDBModel.from_mongo(db_check_collection)

        assert response.status_code == 200
        assert db_check.group_and_note_credit == 100

    def test_send_group_credit_if_user_not_admin(self, test_client, UserDBFactory, login):
        not_admin = UserDBFactory()
        user = UserDBFactory()

        amount = 100

        login_header = login(not_admin)
        response = test_client.get(f'/websocket/send-group-credit/{user.email}/{amount}', headers=login_header)

        assert response.status_code == 403

    def test_send_group_credit_if_amount_negative(self, test_client, UserDBFactory, login):
        admin = UserDBFactory(plan=UserType.ADMIN_USER)
        user = UserDBFactory(group_and_note_credit=100)

        amount = -100

        login_header = login(admin)
        response = test_client.get(f'/websocket/send-group-credit/{user.email}/{amount}', headers=login_header)

        db_check_collection = get_collection(Collections.USER_COLLECTION).find_one({'_id': user.id})
        db_check = UserDBModel.from_mongo(db_check_collection)

        assert response.status_code == 200
        assert db_check.group_and_note_credit == 0

    def test_send_group_credit_if_email_not_found(self, test_client, UserDBFactory, login):
        admin = UserDBFactory(plan=UserType.ADMIN_USER)
        user_email = "fake@fake.com"

        amount = 100

        login_header = login(admin)
        response = test_client.get(f'/websocket/send-group-credit/{user_email}/{amount}', headers=login_header)

        assert response.status_code == 404
