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

__all__ = ['RoleProvider', 'StaticRoleProvider']


class RoleProvider(object):

    def has_all(self, roles, identity, environ, context=None):
        """\
        Return True if the identified user has all roles assigned in the given
        context.

        :param roles: A set of roles
        :type roles: :class:`set`
        :param identity: The user identity. Any type can be used as the
                         `identity` parameter, it is up to the specific
                         implementation to interpret this appropriately.
        :param environ: The WSGI request environ.
        :rtype: bool
        """
        if not roles:
            raise ValueError("Expected at least one role")
        return len(self.member_subset(roles, identity, environ, context)) == \
                len(roles)

    def has_any(self, roles, identity, environ, context=None):
        """\
        Return true if the identified user is a member of any of the specified
        roles.

        :param roles: A set of roles
        :type roles: :class:`set`
        :param identity: The user identity. Any type can be used as the
                         `identity` parameter, it is up to the specific
                         implementation to interpret this appropriately.
        :param environ: The WSGI request environ.
        :rtype: bool
        """
        if not roles:
            raise ValueError("Expected at least one role")
        return len(self.member_subset(roles, identity, environ, context)) > 0

    def member_subset(self, roles, identity, environ, context=None):
        """
        Return the subset of ``roles`` to which the currently identified user
        is assigned.

        :param roles: A set of roles
        :type roles: :class:`set`
        :param identity: The user identity. Any type can be used as the
                         `identity` parameter, it is up to the specific
                         implementation to interpret this appropriately.
        :param environ: The WSGI request environ.
        :param context: Any context object (optional)
        :return: The subset of roles that the current user is a member of
        :rtype: :class:`bool`
        """
        raise NotImplementedError


class CachingRoleProvider(RoleProvider):
    """\
    A role provider that wraps another and caches the results of lookups for
    the duration of the request
    """

    def __init__(self, provider):
        self.provider = provider

    def cached_roles(self, environ, context=None):
        """\
        Return two sets of roles:
        - The set of roles which the current user is known to be in
        - The set of roles which the current user is known NOT to be in
        """
        cached_roles = environ.get('auth.cached_roles', None)
        if cached_roles is None:
            cached_roles = environ['auth.cached_roles'] = {}
        return cached_roles.setdefault(context, (set(), set()))

    def has_any(self, roles, identity, environ, context=None):
        if not roles:
            raise ValueError("Expected at least one role")

        cached_is_in, cached_not_in = self.cached_roles(environ, context)

        # Can we answer the query from the cache?
        if roles & cached_is_in:
            return True

        if roles.issubset(cached_not_in):
            return False

        # The cache doesn't contain enough information to answer the query. Ask
        # the downstream provider to fill in the gaps
        not_cached = roles - cached_is_in - cached_not_in

        member_roles = self.provider.member_subset(not_cached, identity,
                                                   environ, context)

        # Cache the roles to which the environ is known to belong or not,
        cached_is_in |= member_roles
        cached_not_in |= not_cached - member_roles
        return bool(roles & member_roles)

    def has_all(self, roles, identity, environ, context=None):
        if not roles:
            raise ValueError("Expected at least one role")

        cached_is_in, cached_not_in = self.cached_roles(environ, context)

        # Can we answer the query from the cache?
        if roles.issubset(cached_is_in):
            return True

        if roles & cached_not_in:
            return False

        # The cache doesn't contain enough information to answer the query. Ask
        # the downstream provider to fill in the gaps
        not_cached = roles - cached_is_in - cached_not_in

        member_roles = self.provider.member_subset(not_cached, identity,
                                                   environ, context)

        # Cache the roles to which the environ is known to belong or not,
        cached_is_in |= member_roles
        cached_not_in |= not_cached - member_roles

        return len(member_roles) == len(roles)

    def member_subset(self, roles, identity, environ, context=None):

        cached_is_in, cached_not_in = self.cached_roles(environ, context)

        # Remove those roles we know immediately do not apply
        roles = roles - cached_not_in

        # Can we answer the query from the cache?
        if roles.issubset(cached_is_in):
            return roles

        # The cache doesn't contain enough information to answer the query. Ask
        # the downstream provider to fill in the gaps
        not_cached = roles - cached_is_in

        member_roles = self.provider.member_subset(not_cached, identity,
                                                   environ, context)

        # Cache the roles to which the environ is known to belong or not,
        cached_is_in |= member_roles
        cached_not_in |= not_cached - member_roles

        return member_roles


class MultiRoleProvider(RoleProvider):
    """\
    Role adapter that can handles multiple role providers.
    """

    def __init__(self, *providers):
        self.providers = list(providers)

    def member_subset(self, roles, identity, environ, context=None):
        result = set()
        for item in self.providers:
            result |= item.member_subset(roles, identity, environ, context)
        return result


class StaticRoleProvider(RoleProvider):
    """
    A statically configured role provider
    """

    def __init__(self, user_roles):
        """\
        :param user_roles: a mapping from user identifier to member roles
        """
        self.user_roles = dict((userid, set(roles))
                               for userid, roles in user_roles.items())

    def member_subset(self, roles, identity, environ, context=None):
        return roles & self.user_roles.get(identity, set())
