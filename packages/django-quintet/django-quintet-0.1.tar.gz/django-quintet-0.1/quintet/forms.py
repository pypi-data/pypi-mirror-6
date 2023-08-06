# -*- coding: utf-8 -*-

def modelform_with_extras(form_cls, **extra_kwargs):
    """
    Wrap a ModelForm in a class that creates the ModelForm-instance with
    extra paramaters to the constructor.

    This function is ment to to be returned by ModelAdmin.get_form in order
    to easily supply extra parameters to admin forms.
    """
    class ModelFormWithExtras(form_cls):
        def __new__(cls, *args, **kwargs):
            kwargs.update(extra_kwargs)
            return form_cls(*args, **kwargs)
    return ModelFormWithExtras
