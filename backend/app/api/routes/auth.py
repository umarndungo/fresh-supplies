from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import get_auth_service, get_current_user
from app.application.auth_service import AuthService
from app.application.schemas import AuthTokensOut, LoginRequest, RegisterRequest, UserOut
from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.domain.entities import User

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=_REFRESH_COOKIE_MAX_AGE,
        path="/",
    )


def _tokens_payload(user: User, access_token: str, expires_in: int) -> dict:
    tokens = AuthTokensOut(access_token=access_token, expires_in=expires_in, user=UserOut.model_validate(user))
    return {"data": tokens.model_dump(by_alias=True)}


@router.post("/register", status_code=201)
async def register(
    payload: RegisterRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, access_token, expires_in, refresh_token = await auth_service.register(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        role=payload.role,
        organization_name=payload.organization_name,
    )
    _set_refresh_cookie(response, refresh_token)
    return _tokens_payload(user, access_token, expires_in)


@router.post("/login")
async def login(
    payload: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user, access_token, expires_in, refresh_token = await auth_service.login(
        email=payload.email, password=payload.password
    )
    _set_refresh_cookie(response, refresh_token)
    return _tokens_payload(user, access_token, expires_in)


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_token:
        raise UnauthorizedError("No refresh token was provided.")

    _user, access_token, _expires_in, new_refresh_token = await auth_service.refresh(refresh_token)
    _set_refresh_cookie(response, new_refresh_token)
    return {"data": {"accessToken": access_token}}


@router.post("/logout", status_code=204)
async def logout(response: Response) -> None:
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")


@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"data": UserOut.model_validate(current_user).model_dump(by_alias=True)}
