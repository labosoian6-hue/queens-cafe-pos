"""
auth.py - Session management and access control
"""
import database


class AuthError(Exception):
    pass


class PermissionError(Exception):
    pass


class Session:
    _user = None

    @classmethod
    def login(cls, username: str, password: str) -> dict:
        user = database.verify_password(username, password)
        if not user:
            raise AuthError("Invalid username or password.")
        cls._user = user
        return user

    @classmethod
    def logout(cls):
        cls._user = None

    @classmethod
    def get_current_user(cls) -> dict:
        return cls._user

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._user is not None

    @classmethod
    def require_admin(cls):
        if not cls._user or cls._user.get("role") != "admin":
            raise PermissionError("Admin access required.")

    @classmethod
    def is_admin(cls) -> bool:
        return cls._user is not None and cls._user.get("role") == "admin"
