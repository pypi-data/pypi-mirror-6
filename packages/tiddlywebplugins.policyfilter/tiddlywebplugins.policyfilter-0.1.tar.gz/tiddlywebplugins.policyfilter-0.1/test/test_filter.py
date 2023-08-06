
from tiddlyweb.filters import FilterError, recursive_filter, parse_for_filters
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.store import Store

from tiddlywebplugins.policyfilter import init
from tiddlyweb.config import config

import pytest


def setup_module(module):
    init(config)
    environ = {
        'tiddlyweb.config': config,
        'tiddlyweb.usersign': {'name': 'cdent', 'roles': ['COW', 'MOO']}
    }
    module.store = Store(config['server_store'][0],
            config['server_store'][1],
            environ)
    environ['tiddlyweb.store'] = module.store

    module.environ = environ


def test_filtering_bags():
    bag1 = Bag('bag1')
    bag1.policy.create = ['cdent']
    bag2 = Bag('bag2')
    bag2.policy.create = ['R:COW']
    bag3 = Bag('bag3')
    bag3.policy.create = []
    bag4 = Bag('bag4')
    bag4.policy.create = ['NONE']

    bags = [bag1, bag2, bag3, bag4]

    for bag in bags:
        store.put(bag)

    found_bags = list(filter('select=policy:create', bags))

    assert len(found_bags) == 3
    names = [bag.name for bag in found_bags]
    assert 'bag1' in names
    assert 'bag2' in names
    assert 'bag3' in names
    assert 'bag4' not in names


def test_filter_recipes():
    recipe1 = Recipe('recipe1')
    recipe1.policy.create = ['cdent']
    recipe2 = Recipe('recipe2')
    recipe2.policy.create = ['R:COW']
    recipe3 = Recipe('recipe3')
    recipe3.policy.create = []
    recipe4 = Recipe('recipe4')
    recipe4.policy.create = ['NONE']

    recipes = [recipe1, recipe2, recipe3, recipe4]

    for recipe in recipes:
        store.put(recipe)

    found_recipes = list(filter('select=policy:create', recipes))

    assert len(found_recipes) == 3
    names = [recipe.name for recipe in found_recipes]
    assert 'recipe1' in names
    assert 'recipe2' in names
    assert 'recipe3' in names
    assert 'recipe4' not in names

def test_filter_tiddlers():
    """
    This should error.
    """
    tiddler1 = Tiddler('tiddler1', 'bag1')
    tiddler1.text = 'foo'
    store.put(tiddler1)

    with pytest.raises(AttributeError):
        found_tiddlers = list(filter('select=policy:create', [tiddler1]))


def filter(filter_string, entities):
    return recursive_filter(parse_for_filters(
        filter_string, environ)[0], entities)
