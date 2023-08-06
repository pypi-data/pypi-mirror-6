from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.core.paginator import EmptyPage
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client

# Create your tests here.

from django.test.client import RequestFactory
from dpl1_main.testing_app.models import Test, Page, Question, Answer, Result
from dpl1_main.testing_app.session_util import TestSession, TestPaginator
from dpl1_main.testing_app.views import pages_view, show_result_view

Q_VERONICA_MICLE = "how's veronica micle"

Q_HOWS_VETA = "how's veta?"

ANSWER_3 = "answer3"
ANSWER_2 = "answer2"
ANSWER_1 = "answer1"
Q_ARE_YOU_SURE = "are you sure?"
TEST_1_NAME = "test 1"
TEST_1_DESCRIPTION = "test 1 lol"
RESULT_1_VERY_GOOD = "very good!"
RESULT_3_NO_DESCRIPTION = "no description - 3"
BAD = "bad!"
NO_DESCRIPTION_2 = "no description - 2"
NO_DESCRIPTION_1 = "no description - 1"
ALMOST_GOOD = "almost good!"


class TestAbstract(TestCase):
    def setUp(self):
        """
        Test 1  >   Page 1  >   Question 1  >   Answer 1, 2, 3
                >   Page 2  >
                >   Page 3  >   Question 2
                >   Page 4  >   Question 3  >   Answer 4, 5, 6
                >   Page 5  >   Question 4  >   Answer 7, 8, 9
        """
        self.test1 = Test.objects.create(name=TEST_1_NAME,
                                         description=TEST_1_DESCRIPTION)
        self.t1_result1 = Result.objects.create(test=self.test1,
                                                text=RESULT_1_VERY_GOOD,
                                                description=NO_DESCRIPTION_1,
                                                max_points=1000)
        self.t1_result2 = Result.objects.create(test=self.test1,
                                                text=ALMOST_GOOD,
                                                description=NO_DESCRIPTION_2,
                                                max_points=99)
        self.t1_result3 = (
            Result.objects.create(test=self.test1, text=BAD,
                                  description=RESULT_3_NO_DESCRIPTION,
                                  max_points=10))
        self.t1_page1 = Page.objects.create(test=self.test1, sequence=1)
        self.t1_p1_question1 = Question.objects.create(page=self.t1_page1,
                                                       text=Q_ARE_YOU_SURE,
                                                       sequence=1,
                                                       multiple_answers=0)
        self.t1_p1_q1_answer1 = Answer.objects.create(
            question=self.t1_p1_question1,
            text=ANSWER_1,
            points=1)
        self.t1_p1_q1_answer2 = Answer.objects.create(
            question=self.t1_p1_question1,
            text=ANSWER_2,
            points=10)
        self.t1_p1_q1_answer3 = Answer.objects.create(
            question=self.t1_p1_question1,
            text=ANSWER_3,
            points=100)

        #page with no questions
        self.t1_page2 = Page.objects.create(test=self.test1, sequence=2)

        #page with questions, but no answers
        self.t1_page3 = Page.objects.create(test=self.test1, sequence=3)
        self.t1_p3_q1 = Question.objects.create(page=self.t1_page3,
                                                text=Q_HOWS_VETA, sequence=1,
                                                multiple_answers=0)

        #page with questions and answers
        self.t1_p4 = Page.objects.create(test=self.test1, sequence=4)
        self.t1_p4_q1 = Question.objects.create(page=self.t1_p4,
                                                text=Q_VERONICA_MICLE,
                                                sequence=1, multiple_answers=1)
        self.t1_p4_q1_a1 = Answer.objects.create(question=self.t1_p4_q1,
                                                 text=ANSWER_1, points=4)
        self.t1_p4_q1_a2 = Answer.objects.create(question=self.t1_p4_q1,
                                                 text=ANSWER_2, points=90)

        #third page with valid answers
        self.t1_p5 = Page.objects.create(test=self.test1, sequence=5)
        self.t1_p5_q1 = Question.objects.create(page=self.t1_p5,
                                                text=Q_VERONICA_MICLE,
                                                sequence=1, multiple_answers=1)
        self.t1_p5_q1_a1 = Answer.objects.create(question=self.t1_p5_q1,
                                                 text=ANSWER_1, points=4)
        self.t1_p5_q1_a2 = Answer.objects.create(question=self.t1_p5_q1,
                                                 text=ANSWER_2, points=90)
        self.client = Client()

    def _get_response(self, view_name='pages', **kwargs):
        path = reverse(view_name, kwargs=kwargs)
        response = self.client.get(path)
        return response

    def _post_response(self, view_name='pages', *args, **kwargs):
        path = reverse(view_name, kwargs=kwargs, *args)
        response = self.client.post(path)
        return response


class HomeTest(TestAbstract):
    def test_home_200(self):
        """Check if testing_app page works with a few tests available
        """
        response = self._get_response('testing_app')
        self.assertEqual(200, response.status_code)

    def test_home_empty(self):
        """Check if testing_app page works empty
        """
        Test.objects.all().delete()
        response = self._get_response('testing_app')
        # self.assertTrue(
        #     'Welcome to the awesomest testing site' in response.content)
        templates = [template.name for template in response.templates]
        target_template = 'testing_app/index.html'
        self.assertTrue(target_template in templates)

    def test_home_has_answers(self):
        response = self._get_response("testing_app")
        self.assertTrue(TEST_1_NAME in response.content)


class PagesTest(TestAbstract):
    fixtures = ['initial_data']

    def test_first_page(self):
        response = self._get_response(test_id=self.test1.id,
                                      page_id=self.t1_page1.id)
        self.assertTrue(Q_ARE_YOU_SURE in response.content)

    def test_answers_on_page(self):
        response = self._get_response(test_id=self.test1.id,
                                      page_id=self.t1_page1.id)
        self.assertTrue(ANSWER_1 in response.content)
        self.assertTrue(ANSWER_2 in response.content)
        self.assertTrue(ANSWER_3 in response.content)

    def test_invalid_first_page(self):
        path = reverse('pages', kwargs={'test_id': self.test1.id,
                                        'page_id': self.t1_page2.id})
        #follow = True mi-o aratat DAN... ca sa followeasca redirecturile
        response = self.client.get(path, follow=True)
        self.assertEqual(response.request['PATH_INFO'], reverse('testing_app'))


class ResultsTest(TestAbstract):
    def test_empty_response_page(self):
        path = reverse('results', kwargs={'test_id': self.test1.id})
        response = self.client.get(path, follow=True)
        self.assertEqual(200, response.status_code)

    def test_err_msg_response(self):
        path = reverse('results', kwargs={'test_id': self.test1.id})
        response = self.client.get(path, follow=True)
        self.assertRedirects(response, reverse('testing_app'))


class NavigationValidationTest(TestAbstract):
    """Tests for the navigation validator `testing_app.view_util
    .validate_navigation`
    """

    def test_navigation_to_first_page_simple(self):
        """Navigate to first page (by coincidence page 1)
        """
        first_page_id = Test.get_first_page_for(self.test1.id)
        response = self._get_response(test_id=self.test1.id,
                                      page_id=first_page_id)
        self.assertEqual(200, response.status_code)

    def test_navigate_to_first_page_complex(self):
        """Navigate to the first page, even if this doesn't have sequence 1
        """
        page_1_id = Test.get_first_page_for(self.test1.id)
        self.test1.page_set.first().delete()

        first_page_id = Test.get_first_page_for(self.test1.id)
        self.assertNotEqual(page_1_id, first_page_id)
        response = self._get_response(test_id=self.test1.id,
                                      page_id=first_page_id)
        self.assertEqual(200, response.status_code)


class TestWorkflow(TestAbstract):
    def test_get_to_next_page(self):
        first_page_path = reverse('pages',
                                  kwargs={'test_id': self.test1.id,
                                          'page_id': self.t1_page1.id})

        first_page_answers = {
            str(self.t1_p1_question1.as_form_id()): str(
                self.t1_p1_q1_answer1.id)}
        response = self.client.post(first_page_path,
                                    first_page_answers, follow=True)
        next_page_id = Test.get_next_page_for(self.test1.id, self.t1_page1.id)
        next_page_path = reverse('pages', kwargs={'test_id': self.test1.id,
                                                  'page_id': next_page_id})
        self.assertRedirects(response, next_page_path)

    def test_complete_test_200(self):
        final_page_path = reverse('pages', kwargs={'test_id': self.test1.id,
                                                   'page_id': self.t1_p5.id})
        final_page_answers = {'question_1': '1', 'question_3': '4',
                              'question_4': '7', 'test_id': self.test1.id,
                              'page_id': self.t1_p5.id,
                              'last_page_id': self.t1_p4.id}
        session = SessionStore('1234abcd')
        session['last_page_id'] = unicode(self.t1_p4.id)
        session.save()

        response = self.client.post(final_page_path, final_page_answers,
                                    follow=True)
        results_url = reverse('results', kwargs={'test_id': self.test1.id})
        # self.assertRedirects(response, results_url)
        self.fail("Couldn't manage to do this test with django test client"
                  "...should try with selenium or django-webtest")

    def _create_session(self, **kwargs):
        session = SessionStore("3c3c3c4b4b4b")
        session.update(
            {'last_page_id': self.t1_p4.id, 'test_id': self.test1.id,
             'page_id': self.t1_p5.id})
        session.update(kwargs)
        session.save()
        return session

    def test_complete_test_200_factory(self):
        factory = RequestFactory()
        answers = {'question_1': '1', 'question_3': '4', 'question_4': '7'}
        request_redirect = factory.post('/tests/1/5',
                                        answers)
        request_redirect.session = self._create_session(**answers)

        response_redirected = pages_view(request_redirect,
                                         test_id=self.test1.id,
                                         page_id=self.t1_p5.id)
        # self.assertEqual(302, response_redirected.status_code)
        # request_results = factory.get(response_redirected.url,
        #                               {'answers': answers})
        # request_results.session = self._create_session(**answers)
        # response_results = show_result_view(request_results)
        # self.assertEqual(200, response_redirected.status_code)
        self.fail("Couldn't manage to do this test with django test client"
                  "...should try with selenium or django-webtest")


class QueryDictDummy(dict):
    """Dummy for the query dict
    """

    def getlist(self, key):
        """Dummy getlist method

        :param key:
        :return:
        """
        return self[key]


class TestSessionTest(TestAbstract):
    """Tests for the testing_app.session_util.TestSession
    """

    def _create_test_session(self, answers):
        session = SessionStore('asdf1234')
        session.update({'answers': answers})
        test_session = TestSession(session)
        return test_session

    def _get_answers(self):
        """Returns a dummy list of 4 answers for all the answerable questions
        """
        questions = Question.get_answerable_questions()
        question_tags = [question.as_form_id() for question in questions]
        answers = {tag: [str(num) for num in range(4)] for tag in
                   question_tags}
        return answers

    def test_initialization_keeps_answers(self):
        answers = self._get_answers()
        test_session = self._create_test_session(answers)
        self.assertEqual(test_session.answers, answers)

    def test_update_adds_answers(self):
        answers = self._get_answers()
        test_session = self._create_test_session(answers)
        new_answers = QueryDictDummy(answers)
        new_answers.update({'question_654': ['9', '8', '7']})

        test_session.update_results(new_answers, 0, 0)
        self.assertTrue('question_654' in test_session.answers.keys())

    def test_clear_answers(self):
        """Tests if the answers are cleared
        """
        answers = self._get_answers()
        test_session = self._create_test_session(answers)
        test_session.clear_session()
        self.assertTrue(
            not set(answers.keys()).issubset(test_session.answers.keys()))

    def test_can_display_answers(self):
        """The results page should be displayed if all questions got an answer
        """
        answers = self._get_answers()
        test_session = self._create_test_session(answers)
        self.assertTrue(test_session.can_display_results())

    def test_can_not_display_results(self):
        """The results page shouldn't be displayed if not all questions got an
            answer.
        """
        answers = self._get_answers()
        answers.popitem()
        test_session = self._create_test_session(answers)
        self.assertFalse(test_session.can_display_results())


class TestModelTest(TestAbstract):
    def test_has_first_page(self):
        self.assertTrue(self.test1.is_available())


class SessionDummy(dict):
    """Mock for a session - supplies the `save` method and the default
        dict behavior
    """

    def save(self):
        """Dummy method, used for mocking a session object
        """
        pass


class TestPaginatorTest(TestAbstract):
    def _get_paginator(self):
        dummy_session = SessionDummy()
        collection = [1, 2, 3, 4, 5, 6, 7, 8]
        test_paginator = TestPaginator(dummy_session, collection, 3)
        return test_paginator

    def test_spawn_at_page_1(self):
        test_paginator = self._get_paginator()
        page = test_paginator.goto_page()

        self.assertEqual(1, page.number)

    def test_first_has_no_previos_page(self):
        """Checks that the first page shouldn't have a previous page
        """
        test_paginator = self._get_paginator()
        page = test_paginator.goto_page()

        self.assertRaises(EmptyPage, page.previous_page_number)

    def test_first_has_next_page(self):
        """Checks that the first page has a next page
        """
        test_paginator = self._get_paginator()
        page = test_paginator.goto_page()

        self.assertEqual(2, page.next_page_number())

    def test_goto_next_page(self):
        """Tests navigation to the 'next' page
        """
        test_paginator = self._get_paginator()
        page = test_paginator.goto_page(True)

        self.assertEqual(2, page.number)

    def test_goto_first_page(self):
        """Tests navigation to the 'first' page
        """
        test_paginator = self._get_paginator()
        test_paginator.goto_page(True)
        page = test_paginator.goto_page(first=True)

        self.assertEqual(1, page.number)

    def test_goto_previous_page(self):
        """Tests navigating to the previous page
        """
        test_paginator = self._get_paginator()
        test_paginator.goto_page(True)
        page = test_paginator.goto_page(previous=True)
        self.assertEqual(1, page.number)

    def test_goto_last_page(self):
        """Tests navigation to the last page
        """
        test_paginator = self._get_paginator()
        page = test_paginator.goto_page(last=True)

        self.assertEqual(3, page.number)
