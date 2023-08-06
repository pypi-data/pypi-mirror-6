from sqlalchemy import event
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import BINARY, String

from .base import Base, BaseMixin


class User(Base, BaseMixin):

    email = Column(String(length=100), nullable=False, unique=True)
    name = Column(String(length=100))
    username = Column(String(length=100), unique=True)
    password = Column(BINARY(60), nullable=False)

    roles = relationship('Role', secondary='user_role')

    @property
    def permissions(self):
        perms = set()
        for role in self.roles:
            perms.update(role.permissions)
        return perms

    def has_role(self, key):
        keys = set(role.key for role in self.roles)
        if 'sudo' in keys:
            return True
        return key in keys

    def has_permission(self, key):
        keys = set(permission.key for permission in self.permissions)
        if 'sudo' in keys:
            return True
        return key in keys


@event.listens_for(User.password, 'set', retval=True)
def hash_password(user, plain_text_password, old_hashed_password, event):
    import tangled.site.auth
    return tangled.site.auth.hash_password(plain_text_password)


class Permission(Base):

    __tablename__ = 'permission'

    key = Column(String(length=50), primary_key=True)
    description = Column(String(length=100))


class Role(Base):

    __tablename__ = 'role'

    key = Column(String(length=50), primary_key=True)
    description = Column(String(length=100))

    permissions = relationship(Permission, secondary='role_permission')


role_permission_table = Table(
    'role_permission', Base.metadata,
    Column('role_key', ForeignKey(Role.key), primary_key=True),
    Column('permission_key', ForeignKey(Permission.key), primary_key=True))


user_role_table = Table(
    'user_role', Base.metadata,
    Column('user_id', ForeignKey(User.id), primary_key=True),
    Column('role_key', ForeignKey(Role.key), primary_key=True))
