import logging

import bcrypt

from .model import User

from tangled.util import constant_time_compare


log = logging.getLogger(__name__)


def user_id_validator(request, user_id):
    """Ensure user (still) exists and return canonical ID.

    This is called by the registered Authenticator. ``user_id`` *must*
    be an integer, because that's what we store in the session as the
    user's canonical ID.

    """
    if not isinstance(user_id, int):
        log.error('User ID was not an int: {}'.format(int))
        request.abort(400)
    return request.db_session.query(User.id).filter_by(id=user_id).scalar()


def has_permission(request, user_id, permission):
    """Check to see if the user has the specified ``permission``.

    This is called by the registered Authorizer. ``user_id`` *must* be
    an integer, because that's what we store in the session as the
    user's canonical ID.

    """
    user = request.db_session.query(User).get(user_id)
    return user is not None and user.has_permission(permission)


def get_canonical_user_id(request, user_id):
    """Get canonical user ID.

    ``user_id`` can be a username or an email address. ``None`` is
    returned to indicate that the user doesn't exit.

    """
    if user_id is None:
        return None
    user_id = user_id.strip().lower()
    q = request.db_session.query(User.id)
    # Check by email
    canonical_id = q.filter_by(email=user_id).scalar()
    if canonical_id is not None:
        log.debug('Found user {} by email address'.format(canonical_id))
        return canonical_id
    # Check by username
    canonical_id = q.filter_by(username=user_id).scalar()
    if canonical_id is not None:
        log.debug('Found user {} by username'.format(canonical_id))
        return canonical_id
    log.debug('User does not exist: {}'.format(user_id))


def check_credentials(request, user_id, plain_text_password):
    """Check credentials.

    ``user_id`` may be a username or an email address.

    Returns the canonical user ID if the user exists and the credentials
    are valid. Returns ``None`` otherwise.

    """
    user_id = get_canonical_user_id(request, user_id)
    if user_id is None:
        log.debug('Unknown user: {}'.format(user_id))
        return None
    q = request.db_session.query(User.password)
    q = q.filter_by(id=user_id)
    hashed_password = q.scalar()
    if passwords_equal(plain_text_password, hashed_password):
        log.debug('Valid credentials')
        return user_id
    log.debug('Invalid credentials')


def hash_password(plain_text_password, salt=None):
    """Convert a plain text password to salted/hashed form."""
    plain_text_password = plain_text_password.encode('utf-8')
    if salt is None:
        salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password, salt)
    return hashed_password


def passwords_equal(plain_text_password, hashed_password):
    """Compare a plain text password to a hashed password."""
    plain_text_password_hashed = hash_password(
        plain_text_password, hashed_password)
    return constant_time_compare(plain_text_password_hashed, hashed_password)


def sign_up(request, email, plain_text_password, username=None):
    if get_canonical_user_id(request, email):
        log.debug('User exists with email: {}'.format(email))
        return None
    if get_canonical_user_id(request, username):
        log.debug('User exists with username: {}'.format(username))
        return None
    user = User(email=email, password=plain_text_password, username=username)
    request.db_session.add(user)
    request.db_session.flush([user])
    return user.id
