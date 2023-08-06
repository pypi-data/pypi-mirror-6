from .abcs import AAuthorizer

from tangled.decorators import reify


class SimpleAuthorizer(AAuthorizer):

    def __init__(self, app, request, has_permission):
        super().__init__(app, request)
        self.has_permission = has_permission

    def authorized(self, user_id, permission):
        return self.has_permission(self.request, user_id, permission)
