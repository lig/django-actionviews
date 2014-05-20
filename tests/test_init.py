def test_import_view():
    from actionviews import View
    from actionviews.base import View as base_View

    assert View is base_View


def test_import_template_view():
    from actionviews import TemplateView
    from actionviews.base import TemplateView as base_TemplateView

    assert TemplateView is base_TemplateView


def test_import_action_response():
    from actionviews import ActionResponse
    from actionviews.exceptions import (
        ActionResponse as exceptions_ActionResponse)

    assert ActionResponse is exceptions_ActionResponse
