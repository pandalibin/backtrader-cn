"""
Test cases for libs.moels.py
"""
import random
import arctic

from backtradercn.libs import models


RUN_TEST_LIBRARY = 'just_for_run_test_library'


def test_get_store():
    store = models.get_store()
    assert isinstance(store, arctic.arctic.Arctic)

def test_create_library():
    lib = models.create_library(RUN_TEST_LIBRARY)
    assert isinstance(lib, arctic.store.version_store.VersionStore)

def test_get_library_exist():
    lib = models.get_library(RUN_TEST_LIBRARY)
    assert isinstance(lib, arctic.store.version_store.VersionStore)

def test_get_library_not_exist():
    lib_name = '{}{}'.format(RUN_TEST_LIBRARY, random.randint(1, 100))
    lib = models.get_library(lib_name)
    assert lib is None

def test_get_or_create_library_exist():
    lib = models.get_or_create_library(RUN_TEST_LIBRARY)
    assert isinstance(lib, arctic.store.version_store.VersionStore)

def test_get_or_create_library_not_exist():
    lib_name = '{}{}'.format(RUN_TEST_LIBRARY, random.randint(1, 100))
    lib = models.get_or_create_library(lib_name)
    assert isinstance(lib, arctic.store.version_store.VersionStore)

    models.drop_library(lib_name)
    assert models.get_library(lib_name) is None

def test_drop_library_exist():
    models.drop_library(RUN_TEST_LIBRARY)
    assert models.get_library(RUN_TEST_LIBRARY) is None

def test_get_cn_stocks():
    stocks = models.get_cn_stocks()
    assert isinstance(stocks, list)
