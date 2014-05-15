def test_import():
    from actionviews import View
    from actionviews.base import View as base_View

    assert View is base_View
