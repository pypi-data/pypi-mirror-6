__author__ = 'tarzan'

import colander
from deform import widget
import importlib
from pyramid_backend_vgid_oauth2 import get_roles_from_settings
from datetime import datetime
_SQLALCHEMY_INSTALLED = True
try:
    import sqlalchemy
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, types
except ImportError:
    _SQLALCHEMY_INSTALLED = False
    sqlalchemy = None
    declarative_base = lambda: object

    class Column(object):
        def __init__(self, *args, **kwargs):
            pass
    types = object()


Base = declarative_base()
dbsession = None
""":type : sqlalchemy.orm.session.Session"""

_ROLES = []

@colander.deferred
def _deferred_roles_checkbox_list(node, kw):
    return widget.CheckboxChoiceWidget(values=zip(_ROLES, _ROLES))


class BackendUserSchema(colander.Schema):
    email = colander.SchemaNode(colander.String())
    name = colander.SchemaNode(colander.String())
    roles = colander.SchemaNode(colander.Set(),
                                widget=_deferred_roles_checkbox_list)

    def deserialize(self, cstruct=colander.null):
        data = super(BackendUserSchema, self).deserialize(cstruct)
        data['roles'] = u','.join(data['roles'])
        return data


class BackendUser(Base):
    __backend_schema_cls__ = BackendUserSchema

    __tablename__ = 'backend_user'

    id = Column(types.Integer, autoincrement=True, primary_key=True)
    email = Column(types.VARCHAR(255), unique=True)
    name = Column(types.Text)
    roles = Column(types.Text)
    last_modified_time = Column(types.TIMESTAMP,
                                default=datetime.now,
                                onupdate=datetime.now)
    def __unicode__(self):
        return u'%s<%s>' % (self.name, self.email)

    def __str__(self):
        return self.__unicode__().encode('utf-8')



def put_user_callback(acc):
    """
    :type acc: dict
    :return object phai co 1 field la .id
    """
    u = dbsession.query(BackendUser).filter(BackendUser.email == acc['email']).first()
    if u is None:
        u = BackendUser()
        u.email = acc['email']
        u.name = acc['name']
        dbsession.add(u)
        dbsession.flush()
    return u


def get_user_callback_for_auth_policy(userid, request):
    """
    :type request: pyramid.request.Request
    """
    uid = request.unauthenticated_userid
    user = dbsession.query(BackendUser).filter(BackendUser.id == uid).first()
    if user:
        if user.roles:
            return user.roles.split(',')
        return []
    return None


def get_user_for_request(request):
    """
    :type request: pyramid.request.Request
    """
    uid = request.authenticated_userid
    return dbsession.query(BackendUser).filter(BackendUser.id == uid).first()


def initialize_from_settings(settings):
    global dbsession
    global _ROLES

    if not _SQLALCHEMY_INSTALLED:
        return False
    dbsession_path = settings.get('pyramid_backend_vgid_oauth2.sa.dbsession')
    if not dbsession_path:
        return False
    _module, _var = dbsession_path.rsplit('.', 1)
    _module = importlib.import_module(_module, package=None)
    dbsession = getattr(_module, _var)

    _ROLES = get_roles_from_settings(settings)

    return True