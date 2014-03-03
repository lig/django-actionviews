import pytest

from actionviews import ActionView
from actionviews.base import ActionView as base_ActionView


def test_import():
    assert ActionView is base_ActionView
