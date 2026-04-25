class UserNotFoundError(Exception):
    """Пользователь не найден."""
    pass


class WrongPasswordError(Exception):
    """Неверный пароль."""
    pass


class LoginIsExistsError(Exception):
    """Логин уже существует."""
    pass


class EmailIsExistsError(Exception):
    """Email уже существует."""
    pass


class LoginAlreadyExistsError(Exception):
    """Логин уже зарегистрирован."""
    pass


class EmailAlreadyExistsError(Exception):
    """Email уже зарегистрирован."""
    pass


class FieldCannotBeChangedError(Exception):
    """Поле нельзя изменить."""
    pass


class AddAuthUserError(Exception):
    """Ошибка при создании пользователя."""
    pass


class RegisterAuthUserError(Exception):
    """Ошибка регистрации пользователя."""
    pass


class ReadPostError(Exception):
    """Ошибка при получении поста."""
    pass


class AddPostError(Exception):
    """Ошибка при создании поста."""
    pass


class UpdatePostError(Exception):
    """Ошибка при обновлении поста."""
    pass


class DeletePostError(Exception):
    """Ошибка при удалении поста."""
    pass


class TogglePostLikeError(Exception):
    """Ошибка при переключении лайка поста."""
    pass


class ReadPostCommentError(Exception):
    """Ошибка при получении комментария."""
    pass


class AddPostCommentError(Exception):
    """Ошибка при создании комментария."""
    pass


class UpdatePostCommentError(Exception):
    """Ошибка при обновлении комментария."""
    pass


class DeletePostCommentError(Exception):
    """Ошибка при удалении комментария."""
    pass


class ToggleCommentLikeError(Exception):
    """Ошибка при переключении лайка комментария."""
    pass


class RefreshTokenNotFoundError(Exception):
    """Refresh токен не найден."""
    pass


class RefreshTokenExpiredError(Exception):
    """Refresh токен истёк."""
    pass
