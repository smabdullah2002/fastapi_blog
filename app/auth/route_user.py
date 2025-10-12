from .schemas import SignupSchema, LoginSchema
from .services import (
    create_user,
    sign_in_user,
    sign_out_user,
    get_current_user,
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: SignupSchema):
    new_user = await create_user(user)
    return new_user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(from_data: OAuth2PasswordRequestForm = Depends()):
    try:
        login_data = {"email": from_data.username, "password": from_data.password}
        user_schema = LoginSchema(**login_data)
        logged_in_user = await sign_in_user(user_schema)

        session = logged_in_user.get("session")

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        access_token = getattr(session, "access_token", None) or session.get(
            "access_token"
        )
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No access token returned",
            )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/protected_route")
async def protected_route(current_user=Depends(get_current_user)):
    return {"message": f"Hello, user, {current_user.email}"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    await sign_out_user()
    return {"message": "Logged out successfully"}
