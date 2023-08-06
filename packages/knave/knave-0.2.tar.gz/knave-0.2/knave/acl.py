# Copyright 2014 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""\
An ACL is a mapping of users to permissions via roles.

The base ACL object requires two mappings:

1. Permissions to roles (what roles are authorized for permission X?)
2. User to roles (what roles is user Y a member of?)

Using these two mappings, the ACL is able to determine whether authorization
should be granted or not.
"""
from collections import defaultdict
from . import roles, identity, predicates

__all__ = ['ACL', 'Role', 'Permission']


class ACL(roles.RoleProvider):

    environ_key = 'knave.acl'

    def __init__(self, role_providers, permissions_map,
                 identity_adapter=identity.RemoteUserIdentityAdapter()):

        self.get_identity = identity_adapter
        self.role_provider = make_role_provider(role_providers)
        self._permission_roles = defaultdict(set)

        for p, roles in permissions_map.items():
            self._permission_roles[p] |= roles

    def add_role(self, name, permissions):
        role = Role(name)
        for p in permissions:
            self.roles_for_permssion[p].add(role)

    def has_permission(self, permission, environ, context=None):
        """\
        Return `True` if the identified user has the given permission in
        ``context``
        """
        satisfy_roles = self._permission_roles[permission]
        identity = self.get_identity(environ)
        return self.role_provider.has_any(satisfy_roles, identity, environ,
                                          context)

    def has_role(self, role, environ, context=None):
        """\
        Return `True` if the identified user has the given role in ``context``
        """
        return self.role_provider.has_any({role}, self.get_identity(environ),
                                          environ, context)

    def roles_subset(self, roles, identity, environ, context=None):
        """
        Implement the role provider interface
        """
        return self.role_provider.member_subset(roles, identity, environ,
                                                context)

    @classmethod
    def of(cls, environ):
        return environ[cls.environ_key]


@predicates.make_predicate
def is_authenticated(environ, context=None):
    """\
    The ``is_authenticated`` predicate returns True if a user is authenticated,
    regardless of whether they have any permssions assigned.
    """
    return ACL.of(environ).get_identity.is_authenticated(environ)


class Permission(predicates.Predicate):
    """\
    A permission predicate checks the user's access rights against a
    list of permissions.
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Permission %r>' % (self.name,)

    def __call__(self, environ, context=None):
        return ACL.of(environ).has_permission(self, environ, context)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Role(predicates.Predicate):
    """\
    A role predicate checks the user is assigned the given role
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % (self.name,)

    def __call__(self, environ, context):
        return ACL.of(environ).has_role(self, environ, context)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


def make_role_provider(role_providers):
    """
    Wrap multiple role providers in MultiRoleProvider and
    CachingRoleProvider to allow simple, fast querying
    """

    if len(role_providers) == 1:
        role_provider = role_providers[0]
    else:
        role_provider = roles.MultiRoleProvider(*role_providers)

    return roles.CachingRoleProvider(role_provider)
