import contextvars

# Create a context variable for storing user information
_user_context = contextvars.ContextVar("user_context", default=None)


class UserContext:
    @staticmethod
    def set(user_info):
        """Set user information in the context."""
        token = _user_context.set(user_info)
        return token

    @staticmethod
    def get():
        """Retrieve the user information from the context."""
        return _user_context.get()

    @staticmethod
    def reset(token):
        """Reset or clear the context after the request is processed."""
        _user_context.reset(token)
