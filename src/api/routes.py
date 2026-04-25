from fastapi import APIRouter

from src.api.auth.router import auth_router
from src.api.comments.router import comments_router
from src.api.posts.router import posts_router
from src.api.users.router import users_router


main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(users_router)
main_router.include_router(posts_router)
main_router.include_router(comments_router)


@main_router.get("/", tags=["General"])
def index():
    return {"message": "Welcome to BlueGram!"}


@main_router.get("/about", tags=["General"])
def about():
    return {"about": f"BlueGram is a social network "
                     f"made for people's communication all over the world!"}


@main_router.get("/tech_support", tags=["General"])
def tech_support():
    return {"message": f"You can contact for tech support here: "
                       f"'kind of phone number or email'."}
