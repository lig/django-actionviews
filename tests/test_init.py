def test_import():
    from actionviews import TemplateView
    from actionviews.base import TemplateView as base_TemplateView

    assert TemplateView is base_TemplateView
