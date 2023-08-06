# -*- coding: utf-8 -*-

import pytest

def pytest_addoption(parser):
    parser.addoption("--username", help="username")
    parser.addoption("--password", help="password")

@pytest.fixture
def username(request):
    return request.config.getoption("--username")

@pytest.fixture
def password(request):
    return request.config.getoption("--password")
