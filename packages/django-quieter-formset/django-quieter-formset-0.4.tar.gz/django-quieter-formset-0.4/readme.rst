django-quieter-formset
===========================

A formset that validates its data and puts them into non-form errors
as opposed to raising 500 errors.

Usage::

    from quieter_formset.formset import BaseFormSet, BaseModelFormSet

    modelformset_factory(User, formset=BaseModelFormSet)
    formset_factory(ArticleForm, formset=BaseFormSet)

Errors will be pushed into non_form_errors. Make sure you show those in your form.
Because the management form breaks, we don't know information about the form and
so form data will be lost and the form breaks. However it was going to do this anyway.

Version 0.4 requires Django 1.6 or later.

License: BSD

Author: Andy McKay, amckay@mozilla.com
