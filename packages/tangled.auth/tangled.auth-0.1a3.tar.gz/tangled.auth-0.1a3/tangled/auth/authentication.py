import logging

from tangled.decorators import reify

from .abcs import AAuthenticator


log = logging.getLogger(__name__)


class SessionAuthenticator(AAuthenticator):

    """Stores user ID in session."""

    def __init__(self, app, request, session_key, user_id_validator):
        super().__init__(app, request)
        self.session_key = session_key
        self.user_id_validator = user_id_validator

    @reify
    def user_id(self):
        user_id = self.request.session.get(self.session_key)
        if user_id is None:
            log.debug('No user ID in session')
            return None
        log.debug('User ID from session: {}'.format(user_id))
        validated_user_id = self.validate_user_id(user_id)
        if validated_user_id is None:
            log.info('Bad user ID: ()'.format(user_id))
        else:
            log.debug('Valid user ID: {}'.format(user_id))
            return validated_user_id

    def validate_user_id(self, user_id):
        user_id = self.user_id_validator(self.request, user_id)
        return user_id

    def remember(self, user_id):
        self.request.session[self.session_key] = user_id
        self.request.session.save()
        log.debug('Remembered {}'.format(user_id))
        return True

    def forget(self):
        if self.session_key in self.request.session:
            del self.request.session[self.session_key]
            self.request.session.save()
            log.debug('Forgot {}'.format(self.user_id))
            return True
        else:
            log.debug('No user logged in')
            return False
