from abc import ABCMeta, abstractmethod


class AAuthenticator(metaclass=ABCMeta):

    def __init__(self, app, request):
        self.app = app
        self.request = request

    @property
    @abstractmethod
    def user_id(self):
        """Ensure user exists and return user ID.

        If the user doesn't exist, ``None`` will be returned.

        """
        raise NotImplementedError

    @abstractmethod
    def remember(self, user_id=None, validate=False):
        """Remember the user.

        If ``validate`` is set, make sure the user exists before
        remembering.

        Return ``True`` if remembered, ``False`` if not.

        """
        raise NotImplementedError

    @abstractmethod
    def forget(self, user_id=None):
        """Forget the user.

        Return ``True`` if remembered, ``False`` if not.

        """
        raise NotImplementedError


class AAuthorizer(metaclass=ABCMeta):

    # TODO: Given User and permission, find roles

    def __init__(self, app, request):
        self.app = app
        self.request = request

    @abstractmethod
    def authorized(self, user_id, permission):
        raise NotImplementedError
