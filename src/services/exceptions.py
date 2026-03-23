class UserNotFoundError(Exception):
    pass


class WrongPasswordError(Exception):
    pass


class LoginIsExistsError(Exception):
    pass


class EmailIsExistsError(Exception):
    pass


class RegisterAuthUserError(Exception):
    pass


class ReadPostError(Exception):
    pass


class UpdatePostError(Exception):
    pass


class DeletePostError(Exception):
    pass


class ReadPostCommentError(Exception):
    pass


class UpdatePostCommentError(Exception):
    pass


class DeletePostCommentError(Exception):
    pass


class AddPostCommentError(Exception):
    pass


class ToggleCommentLikeError(Exception):
    pass


class TogglePostLikeError(Exception):
    pass


class LoginAlreadyExistsError(Exception):
    pass


class EmailAlreadyExistsError(Exception):
    pass


class FieldCannotBeChangedError(Exception):
    pass


class AddAuthUserError(Exception):
    pass


class AddPostError(Exception):
    pass


class RefreshTokenNotFoundError(Exception):
    pass


class RefreshTokenExpiredError(Exception):
    pass