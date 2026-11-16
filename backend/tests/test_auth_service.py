from app.services import auth_service
import pytest

async def test_register_user(user_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None
    assert user.email == 'test_user@example.com'
    assert user.hashed_password != 'password123'

async def test_login_user(user_repo, token_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None

    result = await auth_service.login_user(email='test_user@example.com', password='password123', user_repo=user_repo, token_repo=token_repo)

    assert isinstance(result['access_token'], str) == True
    assert isinstance(result['refresh_token'], str) == True



    refresh_token =  await token_repo.get_by_hash(auth_service.hash_token(result['refresh_token']))

    assert refresh_token is not None
    assert refresh_token.user_id == user.id
    assert refresh_token.token_hash == auth_service.hash_token(result['refresh_token'])
    assert refresh_token.revoked_at is None


async def test_service_does_not_login_user_with_invalid_credentials(user_repo, token_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None

    with pytest.raises(ValueError, match='Invalid credentials'):
        await auth_service.login_user(email=user.email, password='invalid', user_repo=user_repo, token_repo=token_repo)

async def test_logout_user(user_repo, token_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None

    tokens = await auth_service.login_user(email=user.email, password='password123', user_repo=user_repo, token_repo=token_repo)

    assert tokens is not None
    assert isinstance(tokens['access_token'], str) == True
    assert isinstance(tokens['refresh_token'], str) == True

    refresh_token = await token_repo.get_by_hash(auth_service.hash_token(tokens['refresh_token']))

    assert refresh_token.user_id == user.id
    assert refresh_token.token_hash == auth_service.hash_token(tokens['refresh_token'])
    assert refresh_token.revoked_at is None

    await auth_service.logout_user(tokens['refresh_token'], token_repo)

    assert refresh_token.revoked_at is not None

async def test_refresh_tokens(user_repo, token_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None

    tokens = await auth_service.login_user(email=user.email, password='password123', user_repo=user_repo, token_repo=token_repo)

    assert tokens is not None
    assert isinstance(tokens['access_token'], str) == True
    assert isinstance(tokens['refresh_token'], str) == True

    refresh_token = await token_repo.get_by_hash(auth_service.hash_token(tokens['refresh_token']))

    assert refresh_token is not None
    assert refresh_token.user_id == user.id
    assert refresh_token.token_hash == auth_service.hash_token(tokens['refresh_token'])

    refreshed = await auth_service.refresh_tokens(raw=tokens['refresh_token'], token_repo=token_repo, user_repo=user_repo)

    assert refresh_token.revoked_at is not None

    assert refreshed['refresh_token'] != tokens['refresh_token']

async def test_service_does_not_refresh_revoked_tokens(user_repo, token_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None

    tokens = await auth_service.login_user(email='test_user@example.com', password='password123', user_repo=user_repo, token_repo=token_repo)

    assert tokens is not None

    assert isinstance(tokens['access_token'], str) == True
    assert isinstance(tokens['refresh_token'], str) == True

    refresh_token = await token_repo.get_by_hash(auth_service.hash_token(tokens['refresh_token']))

    assert refresh_token is not None
    assert refresh_token.user_id == user.id
    assert refresh_token.token_hash == auth_service.hash_token(tokens['refresh_token'])
    assert refresh_token.revoked_at is None

    await token_repo.revoke_all(user.id)

    refresh_token = await token_repo.get_by_hash(auth_service.hash_token(tokens['refresh_token']))

    assert refresh_token.revoked_at is not None

    with pytest.raises(ValueError, match='Invalid refresh token'):
        await auth_service.refresh_tokens(raw=tokens['refresh_token'], token_repo=token_repo, user_repo=user_repo)


async def test_service_does_not_refresh_tokens_for_inactive_user(user_repo, token_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None

    tokens = await auth_service.login_user(email=user.email, password='password123', user_repo=user_repo, token_repo=token_repo)

    user.is_active = False
    await user_repo.update(user)

    with pytest.raises(ValueError, match='Invalid refresh token'):
        await auth_service.refresh_tokens(raw=tokens['refresh_token'], token_repo=token_repo, user_repo=user_repo)

async def test_get_current_user(user_repo, token_repo):

    user = await auth_service.register(email='test_user@example.com', password='password123', user_repo=user_repo)

    assert user is not None

    tokens = await auth_service.login_user(email=user.email, password='password123', user_repo=user_repo, token_repo=token_repo)

    assert tokens is not None

    current_user = await auth_service.get_current_user(token=tokens['access_token'], user_repo=user_repo)

    assert current_user is not None

    assert current_user.id == user.id





