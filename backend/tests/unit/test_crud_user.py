from app.crud.user import create_user, get_user_by_email, authenticate_user
from app.schemas.user import UserCreate


def make_user(db):
    user_in = UserCreate(
        email="test@example.com",
        full_name="Test User",
        password="testpassword123"
    )
    return create_user(db=db, user_in=user_in)


def test_create_user(db):
    user = make_user(db)
    assert user is not None
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    # password must never be stored in plain text
    assert user.hashed_password != "testpassword123"


def test_get_user_by_email(db):
    created = make_user(db)
    fetched = get_user_by_email(db=db, email="test@example.com")
    assert fetched is not None
    assert fetched.id == created.id


def test_get_user_by_email_not_found(db):
    result = get_user_by_email(db=db, email="nonexistent@example.com")
    assert result is None


def test_authenticate_user_success(db):
    make_user(db)
    user = authenticate_user(
        db=db,
        email="test@example.com",
        password="testpassword123"
    )
    assert user is not None
    assert user.email == "test@example.com"


def test_authenticate_user_wrong_password(db):
    make_user(db)
    result = authenticate_user(
        db=db,
        email="test@example.com",
        password="wrongpassword"
    )
    assert result is None


def test_authenticate_user_not_found(db):
    result = authenticate_user(
        db=db,
        email="nonexistent@example.com",
        password="testpassword123"
    )
    assert result is None