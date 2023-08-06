"""Define the views used in the application `home`
"""
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
import django.http

from dpl1_main.testing_app.forms import create_form_for_questions
from dpl1_main.testing_app.models import Test, Question

# from dpl1_main.testing_app.session_util import TestSession
from dpl1_main.testing_app.session_util import TestSession, TestPaginator
from dpl1_main.testing_app.view_util import (get_next_page, save_answers,
                                             validate_navigation,
                                             validate_results)


def error_view(request):
    """The default error view
    :param request:
    :return:
    """
    return django.http.Http404()


def home_view(request):
    #instantiate the template in the dir given (project dir - cuz
    # of TEMPLATES_DIR ) name in the settings module of the project
    #create the context for the view - just fill the list of crap here
    """The view for the testing_app page

    :param request:
    """
    all_tests = Test.objects.all()
    test_session = TestSession(request.session)
    test_session.clear_session()

    paginator = TestPaginator(request.session, all_tests, 3)
    next_page = request.GET.get('next_page', False)
    previous_page = request.GET.get('previous_page', False)
    last_page = request.GET.get('last_page', False)
    first_page = request.GET.get('first_page', False)

    page = paginator.goto_page(next_page, previous_page, first_page, last_page)
    context = {'tests': page.object_list, 'page': page}
    result = render(request, 'testing_app/index.html', context)
    return result


@validate_results
def show_result_view(request, test_id):
    """Shows the results page for the corresponding test_id

    :param test_id: id of the testing_app.models.Test
    :param request:
    """
    #TODO: this also needs to be tested with django-webtest
    context = {}
    test_session = TestSession(request.session)
    test_result = test_session.get_test_result(test_id)
    context['result'] = test_result
    if test_result is None:
        context['no_result'] = True

    context['home_url'] = request.build_absolute_uri(reverse('testing_app'))
    return render(request, 'testing_app/results.html', context)


@save_answers
@validate_navigation
def pages_view(request, test_id, page_id=1):
    """Handles the logic for the test pages view:
        "testing_app/test_page.html"
        :param request
        :param test_id
        :param page_id
    """
    #Determine next page: either normal page, or results page
    next_page_id = get_next_page(test_id, page_id)

    if request.method == 'POST':
        old_questions = Question.objects.filter(page__test_id=test_id,
                                                page_id=page_id)
        form = create_form_for_questions(old_questions)(request.POST)

        if form.is_valid():
            if int(page_id) == Test.get_last_page_for(test_id):
                redirect_to = reverse('results', kwargs={'test_id': test_id})
            else:
                redirect_to = reverse('pages', kwargs={'test_id': test_id,
                                                       'page_id':
                                                       next_page_id})
            return HttpResponseRedirect(redirect_to)
    else:
        questions = Question.objects.filter(page__test_id=test_id,
                                            page_id=page_id)
        form = create_form_for_questions(questions)()

    context = {'test_id': test_id, 'page_id': page_id, 'form': form}
    if form.submittable is False:
        context['parent_url'] = request.META.get('HTTP_REFERER')

    result = render(request, 'testing_app/test_page.html', context)
    return result