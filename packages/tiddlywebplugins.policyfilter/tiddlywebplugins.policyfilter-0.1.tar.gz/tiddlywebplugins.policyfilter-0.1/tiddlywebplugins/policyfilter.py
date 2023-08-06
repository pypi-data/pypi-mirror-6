"""
Test entity policies against the current user to
filter bags and recipes.
"""

from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.filters.select import ATTRIBUTE_SELECTOR


def policy_allows(entity, attribute, value):
    environ = entity.store.environ
    usersign = environ['tiddlyweb.usersign']
    policy = entity.policy
    try:
        policy.allows(usersign, value)
        return True
    except PermissionsError:
        return False

def init(config):
    ATTRIBUTE_SELECTOR['policy'] = policy_allows
