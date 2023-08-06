"""Wrapper around the test session
"""
import itertools
from django.core.paginator import Paginator
from dpl1_main.testing_app.models import Answer, Result, Test, Question


class TestSession(object):
    """Uses the session as a container for the test logic """

    def __init__(self, session):
        """Initializes the answers list
        """
        #todo :WISH:- efectiv n-am nevoie de dict, ci de o lista de raspunsuri.
        self.answers = session.get('answers', {})
        self.test_id = session.get('test_id', None)
        self.page_id = session.get('page_id', None)
        self.last_page_id = session.get('last_page_id', None)
        self.last_test_id = session.get('last_test_id', None)
        self.session = session

    def update_results(self, post_dict, test_id, page_id):
        """Update the answers list from the POST object of the request

        :param post_dict: the request.POST which contains the form data
        :param test_id: id of the testing_app.models.Test
        :param page_id: the id of the testing_app.models.Page
        """
        form_dict = {key: post_dict.getlist(key) for key in post_dict if
                     'question' in key}
        self.answers.update(form_dict)
        self.session['last_page_id'] = self.page_id
        self.test_id = test_id
        self.session['test_id'] = test_id
        self.session['page_id'] = page_id
        self.page_id = page_id
        self.save_to_session()

    def get_test_result(self, test_id):
        """Return the test result that the user got, at the end of the test.

        :param test_id: id of the testing_app.models.Test
        """
        answer_lists = (self.answers[question] for question in
                        self.answers.keys() if 'question' in question)
        answer_ids = itertools.chain(*answer_lists)
        answers = Answer.objects.filter(id__in=answer_ids)
        total_points = 0
        for answer in answers:
            total_points += answer.points

        test_results = Result.objects.filter(
            max_points__lte=total_points, test__id=test_id).order_by(
            '-max_points')
        #2 compare with test results
        if test_results.count() > 0:
            return test_results[0]
        else:
            return None

    def get_last_test_page(self):
        """Return the last test page that the user submitted.
        """
        return self.session['test_id'], self.session['last_page_id']

    def save_to_session(self):
        """Save the currently managed test data to the user session.
        """
        self.session['answers'] = self.answers
        self.session.save()

    def clear_session(self):
        """Clears the answers of the previous user session."""
        if 'answers' in self.session:
            self.session.pop('answers')
        if 'last_page_id' in self.session:
            self.session.pop('last_page_id')
        if 'last_test_id' in self.session:
            self.session.pop('last_test_id')
        if 'page_id' in self.session:
            self.session.pop('page_id')
        self.answers = {}
        self.session.save()

    def can_display_results(self):
        """Returns True if the last test page was submitted
        :return:
        """
        #Just check if all the questions with answers were answered
        answerable_questions = Question.get_answerable_questions()

        for question in answerable_questions:
            if question.as_form_id() not in self.answers.keys():
                return False
        return True


class TestPaginator(object):
    """Paginates the tests on the testing_app page
    """

    def __init__(self, session, collection, num_entries, current_page=None):
        self.session = session
        self.collection = collection
        self.num_entries = num_entries
        if current_page is not None:
            self.current_home_page = current_page
        else:
            self.current_home_page = session.get('current_home_page', 1)
        session['current_home_page'] = self.current_home_page
        self._save_session()

    def _set_current_page(self, page):
        self.current_home_page = page
        self.session['current_home_page'] = page
        self._save_session()

    def _save_session(self):
        self.session.save()

    def _increment_current_page(self, inc=1):
        self.current_home_page += inc
        self.session['current_home_page'] = self.current_home_page
        self._save_session()

    def _get_page(self, paginator, page=None):
        """Returns either the specified page, or the current page of the
            paginator

        :param paginator:
        :param page:
        :return:
        """
        if page is not None:
            return paginator.page(page)
        else:
            return paginator.page(self.current_home_page)

    def _convert_to_bool(self, next_, previous, first,
                         last):
        """Returns the values of the 4 strings to the correct bool
            representation
        :returns a tuple of bools
        """
        true_values = ['True', 'true', '1', True, u'true', u'True', u'1']
        next_ = next_ in true_values
        previous = previous in true_values
        first = first in true_values
        last = last in true_values
        return next_, previous, first, last

    def goto_page(self, next_=False, previous=False, first=False, last=False):
        """If none of the arguments are true, returns the current page.

        Else, navigates to the one specified by the first parameter that is
         true, in the same order as the parameters.

        :param next_:
        :param previous:
        :param first:
        :param last:
        :return:
        """
        next_, previous, first, last = self._convert_to_bool(next_, previous,
                                                             first, last)
        paginator = Paginator(self.collection, self.num_entries)
        if not (next_ or previous or first or last):
            return paginator.page(self.current_home_page)

        if next_:
            self._increment_current_page()
            return self._get_page(paginator)

        if previous:
            self._increment_current_page(-1)
            return self._get_page(paginator)

        if first:
            self._set_current_page(1)
            return self._get_page(paginator)

        if last:
            self._set_current_page(paginator.num_pages)
            return self._get_page(paginator)