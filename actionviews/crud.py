from .base import View


class CRUDActionsMixin:
    """do_list, do_detail, do_create, do_update, do_delete"""


class ModelCRUDMixin:
    """get_queryset, get_object, create_object, update_object, delete_object"""


class CRUDView(View, CRUDActionsMixin):
    pass


class ModelCRUDView(CRUDView, ModelCRUDMixin):
    pass
