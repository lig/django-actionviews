
def test_import():
    from actionviews import ActionView
    from actionviews.base import ActionView as base_ActionView

    assert ActionView is base_ActionView
