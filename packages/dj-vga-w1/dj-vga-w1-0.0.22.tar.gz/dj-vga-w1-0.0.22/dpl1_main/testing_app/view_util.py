"""Functions and decorators used by the views (`home.views`)
"""
import functools
from django.core.urlresolvers import reverse

from django.http import HttpResponseRedirect

from dpl1_main.testing_app.models import Page, Test
from dpl1_main.testing_app.session_util import TestSession


def disable_navigation(func):
    """Disables navigation for a view

    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        """Redirects to current page

        :param request:
        :param args:
        :param kwargs:
        """
        #determine where we came from
        return render_last_page(request)

    return wrapper


def is_page_sequence_valid(test_id, page_id, last_test_id, last_page_id):
    """Checks whether the current test page is in the right sequence with
    regards to the last.

    Given the current test_id and page_id, this function checks the
    HTTP_REFERER (last page) to see if

    :param last_test_id:
    :param referer:
    """
    # test_session = TestSession(request.session)
    # if test_session is None:
    #     raise KeyError('Unable to determine page sequence')

    # last_test_id, last_page_id = test_session.get_last_test_page()
    #check if first page is right
    if last_page_id is None:
        return int(page_id) == Test.get_first_page_for(test_id)

    if last_page_id == page_id:
        return True

    #check if next page is right (next or results page)
    if int(page_id) != get_next_page(last_test_id, last_page_id):
        return False

    return True


def get_last_rel_url(request):
    """Returns the relative URL of the last page (the referer)
    :param request: the request obj
    """
    return request.META.get('HTTP_REFERER')


def render_last_page(request):
    """Returns a request for the last page

    :param request:
    """
    referer_url = request.META.get('HTTP_REFERER')
    if not referer_url:
        raise UrlModifiedError()
    response = HttpResponseRedirect(referer_url)

    return response


def render_default_page(request):
    """ When possible returns the last page, or the testing_app page

    :param request: a HttpRequest object
    """
    try:
        default_page = render_last_page(request)
    except UrlModifiedError:
        default_page = HttpResponseRedirect(reverse('testing_app'))
    return default_page


def validate_navigation(func):
    """Decorator: Makes sure the workflow of the testing_app application is respected.

    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        """
                :param kwargs:
                :param args:
                :param request:
                """
        # if current path is the 'testing_app' path, allow navigation
        if request.path == reverse('testing_app'):
            return func(request, *args, **kwargs)

        #check if the current page is a valid successor for the test pages

        test_id = kwargs.get('test_id', None)
        page_id = kwargs.get('page_id', None)
        test_session = TestSession(request.session)
        last_test_id, last_page_id = test_session.get_last_test_page()

        if test_id is not None and page_id is not None:
            if is_page_sequence_valid(test_id, page_id, last_test_id,
                                      last_page_id):
                result = func(request, *args, **kwargs)
                return result
            else:
                return render_default_page(request)
        else:
            return HttpResponseRedirect(reverse('testing_app'))

    return wrapper


def get_next_page(test_id, page_id):
    """Determines the next test page.

    Either the next page in the test that has questions,
        or 0 - meaning the results page.
    :param page_id: id of the testing_app.models.Page
    :param test_id: if of the testing_app.models.Test
    """
    return Test.get_next_page_for(test_id, page_id)
    # next_pages = Page.objects.filter(id__gt=page_id, test__id=test_id)
    #
    # for page in next_pages:
    #     if page.question_set.count() > 0:
    #         return page.id
    # else:
    #     return 0


def save_answers(func):
    """Updates the session with the answers from the form on the last page.
    :param func: function being decorated
    """

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        """Wraps the function to be decorated

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        test_id = kwargs.get('test_id', None)
        page_id = kwargs.get('page_id', None)
        test_session = TestSession(request.session)
        test_session.test_id = test_id
        test_session.update_results(request.POST, test_id, page_id)
        return func(request, *args, **kwargs)

    return wrapper


def validate_results(func):
    """Either allow displaying of the results page, or return to the default
        page
    """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        """Decorator func wrapper
        """
        test_session = TestSession(request.session)
        if test_session.can_display_results():
            return func(request, *args, **kwargs)
        else:
            return render_default_page(request)
    return wrapper


class UrlModifiedError(Exception):
    """Thrown if the user executed an arbitrary URL
    """
    pass