from django.core.exceptions import ValidationError
from django.forms.formsets import (TOTAL_FORM_COUNT, INITIAL_FORM_COUNT,
                                   MAX_NUM_FORM_COUNT,
                                   BaseFormSet as DjangoBaseFormSet)
from django.forms.models import BaseModelFormSet as DjangoBaseModelFormSet
from django.forms.formsets import ManagementForm
from django.utils.functional import cached_property
from django.utils.datastructures import MultiValueDictKeyError


__all__ = ['BaseFormSet', 'BaseModelFormSet']


err = ('ManagementForm data is missing or has been tampered with. Form data '
       'could have been lost.')


class QuieterBaseFormset:
    def _management_form(self):
        """Returns the ManagementForm instance for this FormSet."""
        if self.is_bound:
            form = ManagementForm(self.data, auto_id=self.auto_id,
                                  prefix=self.prefix)
            if not form.is_valid():
                self._non_form_errors = err
        else:
            form = ManagementForm(auto_id=self.auto_id,
                                  prefix=self.prefix,
                                  initial={
                                    TOTAL_FORM_COUNT: self.total_form_count(),
                                    INITIAL_FORM_COUNT: self.initial_form_count(),
                                    MAX_NUM_FORM_COUNT: self.max_num,
                                  })
        return form
    management_form = property(_management_form)

    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors. Copes with forms
        that failed to be constructed, as long as non_form_errors has been
        set.
        """
        self._errors = []
        if not self._non_form_errors:
            self._non_form_errors = self.error_class()
        if not self.is_bound: # Stop further processing.
            return
        for i in range(0, self.total_form_count()):
            try:
                form = self.forms[i]
                self._errors.append(form.errors)
            except IndexError:
                # If the form is not there, but there's nothing in non-form
                # errors, that's bad.
                if not self._non_form_errors:
                    raise

        # Give self.clean() a chance to do cross-form validation.
        try:
            self.clean()
        except ValidationError, e:
            self._non_form_errors = self.error_class(e.messages)


class BaseFormSet(QuieterBaseFormset, DjangoBaseFormSet):
    # Quieter handling for mangled management forms
    def total_form_count(self):
        if self.data or self.files:
            cleaned_data = getattr(self.management_form, 'cleaned_data', {})
            return cleaned_data.get(TOTAL_FORM_COUNT, 0)
        else:
            return DjangoBaseFormSet.total_form_count(self)

    def initial_form_count(self):
        if self.data or self.files:
            cleaned_data = getattr(self.management_form, 'cleaned_data', {})
            return cleaned_data.get(INITIAL_FORM_COUNT, 0)
        else:
            return DjangoBaseFormSet.initial_form_count(self)

    def is_valid(self):
        """
        Returns True if form.errors is empty for every form in self.forms
        or there are non_form_errors.
        """
        if self._non_form_errors:
            return False
        return super(BaseFormSet, self).is_valid()


class BaseModelFormSet(QuieterBaseFormset, DjangoBaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseModelFormSet, self).__init__(*args, **kwargs)
        # DjangoBaseModelFormSet's `forms` attribute is lazily
        # initialized. We initialize it here to avoid circularity
        # problems in form validation.
        self.forms

    # Quieter handling for mangled management forms
    def total_form_count(self):
        if self.data or self.files:
            cleaned_data = getattr(self.management_form, 'cleaned_data', {})
            return cleaned_data.get(TOTAL_FORM_COUNT, 0)
        else:
            return DjangoBaseModelFormSet.total_form_count(self)

    def initial_form_count(self):
        if self.data or self.files:
            cleaned_data = getattr(self.management_form, 'cleaned_data', {})
            return cleaned_data.get(INITIAL_FORM_COUNT, 0)
        else:
            return DjangoBaseModelFormSet.initial_form_count(self)

    # Handling of invalid data on form construction
    @cached_property
    def forms(self):
        forms = []
        for i in xrange(self.total_form_count()):
            try:
                forms.append(self._construct_form(i))
            except MultiValueDictKeyError, err:
                self._non_form_errors = err
            except KeyError, err:
                self._non_form_errors = u'Key not found on form: %s' % err
            except (ValueError, IndexError), err:
                self._non_form_errors = err
        return forms

    def is_valid(self):
        """
        Returns True if form.errors is empty for every form in self.forms
        or there are non_form_errors.
        """
        if self._non_form_errors:
            return False
        return super(BaseModelFormSet, self).is_valid()
