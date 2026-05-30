from app.schemas.user import User


def get_dummy_users() -> list[User]:
    return [
        User(id=1, email="user1@example.com", is_active=True),
        User(id=2, email="user2@example.com", is_active=False),
    ]
