# coding: utf-8
from django.db.models import Field as ModelField
from floppyforms import fields


def monkeypatch_method(cls):
    """
    Monkeypatches a class method.
    The original method is saved with the prefix _old_ enabling
    the new method to use it.
    """
    def decorator(func):
        fname = func.__name__
        backup = '_old_%s' % fname

        # patch if we can
        if hasattr(cls, fname) and not hasattr(cls, backup):
            setattr(cls, backup, getattr(cls, fname))
            setattr(cls, fname, func)

        return func

    return decorator


# Define and patch!
@monkeypatch_method(ModelField)
def formfield(self, form_class=None, choices_form_class=None, **kwargs):
    """
    A function to replace Django's Field.formfield forcing the usage of
    floppy's form fields.
    """
    # update known fields to floppy
    if form_class:
        form_class = getattr(fields, form_class.__name__, form_class)

    if choices_form_class:
        choices_form_class = getattr(fields, choices_form_class.__name__,
                                     choices_form_class)

    # If not defined, set floppy defaults
    if not form_class:
        form_class = getattr(fields, 'CharField')

    if not choices_form_class:
        choices_form_class = getattr(fields, 'TypedChoiceField')

    return self._old_formfield(form_class, choices_form_class, **kwargs)
