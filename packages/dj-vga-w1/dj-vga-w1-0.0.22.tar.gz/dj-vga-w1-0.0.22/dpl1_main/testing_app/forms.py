from django import forms
from django.core.exceptions import ValidationError


class CustomForm(forms.Form):
    """Validates the entire page
    """

    def clean(self):
        """Checks if an answer was given to all the questions on the page

        :return: :raise ValidationError: if condition not satisfied
        """
        if set(self.fields.keys()).issubset(self.changed_data):
            return self.cleaned_data
        else:
            raise ValidationError("All questions have to be answered",
                                  code="invalid")


def create_form_for_questions(questions):
    """Creates a dynamic form instance, given the questions in a page

    :param questions: django.db.models.QuerySet of testing_app.models.Question
    :return: django.forms.Form instance
    """
    bases = (CustomForm,)
    attributes = {}
    if questions.count() == 0:
        attributes["submittable"] = False
        return type("EmptyDynamicForm", bases, attributes)
    for question in questions.all():
        if question.answer_set.count() == 0:
            continue
        choices = []
        for answer in question.answer_set.all():
            choices.append((answer.id, answer.text))
        #Found this field - widget combination to work
        if question.multiple_answers is True:
            form_type = forms.MultipleChoiceField
            widget = forms.CheckboxSelectMultiple
        else:
            widget = forms.RadioSelect
            form_type = forms.ChoiceField
        attributes[question.as_form_id()] = (
            form_type(widget=widget,
                      choices=choices,
                      label=question.text)
        )
    attributes['submittable'] = True
    form = type("DynamicPageForm", bases, attributes)
    return form
