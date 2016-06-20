#!/usr/bin/env python

from calenvite.rest import build_api
from calenvite.calenvite import Calenvite

import pytest

@pytest.fixture
def app():
    return build_api(Calenvite(), {'--verbose': 0}, testing=True)
