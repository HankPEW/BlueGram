from src.api.users.schemas import ReadProfileResponse
from src.models import AuthUser


class UserMapper:

    @staticmethod
    def to_response(auth_user: AuthUser) -> ReadProfileResponse:
        profile = auth_user.profile

        return ReadProfileResponse(
            login=auth_user.login,
            email=auth_user.email,
            created_at=auth_user.created_at,
            first_name=profile.first_name,
            last_name=profile.last_name,
            gender=profile.gender,
            birth=profile.birth,
            career=profile.career,
            education=profile.education,
            phone_number=profile.phone_number,
            marital_status=profile.marital_status,
            hometown=profile.hometown,
            about_me=profile.about_me
        )
