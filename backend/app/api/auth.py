from fastapi import APIRouter, HTTPException, status
from app.api.dependencies import CurrentUser, TokenRepo, UserRepo
from app.schemas.auth import RefreshBody, Credentials, TokenResponse
from app.schemas.user import UserRead
from app.services import auth_service


router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register(body: Credentials, user_repo: UserRepo):
    try:
        user = await auth_service.register(body.email, body.password, user_repo)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')

    return user

@router.post('/login', status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login(body: Credentials, user_repo: UserRepo, token_repo: TokenRepo):
    try:
        return await auth_service.login_user(body.email, body.password, user_repo, token_repo)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')

@router.post('/refresh', status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def refresh(body: RefreshBody, user_repo: UserRepo, token_repo: TokenRepo):
    try:
        return await auth_service.refresh_tokens(body.refresh_token, user_repo=user_repo, token_repo=token_repo)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshBody, token_repo: TokenRepo):
    await auth_service.logout_user(body.refresh_token, token_repo)

@router.post('/logout/all', status_code=status.HTTP_204_NO_CONTENT)
async def logout_from_all_devices(current_user: CurrentUser, token_repo: TokenRepo):
    await auth_service.logout_from_all_devices(user_id=current_user.id, token_repo=token_repo)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=UserRead)
async def get_me(user: CurrentUser):
    return user




