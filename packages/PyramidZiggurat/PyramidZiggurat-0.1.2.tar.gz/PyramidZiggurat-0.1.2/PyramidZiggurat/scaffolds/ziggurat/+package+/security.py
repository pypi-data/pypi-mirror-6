from StringIO import StringIO
import traceback

from pyramid.security import authenticated_userid

from .models import User, UserGroup, Group, DBSession


def group_finder(email, request):
    u = User.get_by_email(email)
    if not u:
        return []
    if u.id == 1:
        return ['Admin']
    r = []        
    for group_id in UserGroup.get_by_email(email):
        group = DBSession.query(Group).get(group_id)
        r.append(group.group_name)
    return r
        
def get_user(request):
    username = authenticated_userid(request)
    if username:
        return User.get_by_identity(username)
