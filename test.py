import main
from main import app, login
import unittest,socketio

class FlaskTestCase(unittest.TestCase):

    # Ensure that flask was setup correctly

    def test_index(self):
        tester = app.test_client(self)
        response=tester.get('/login',content_type='html/text')
        self.assertEqual(response.status_code,200)

        # Ensure that login page loads correctly

    def test_login_page_loads(self):
            tester = app.test_client(self)
            response = tester.get('/login', content_type='html/text')
            self.assertTrue('Please sign in'.encode() in response.data)

        # Ensure that main page requires user login

    # def test_main_route_requires_login(self):
    #     response = self.client.get('/dashboard', follow_redirects=True)
    #     self.assertIn(b'Please log in to access this page', response.data)

        # Ensure that welcome page loads

    def test_home_page_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue('Disaster Prediction'.encode() in response.data)


    # Ensure that registration page loads

    def test_registration_page_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/signup', content_type='html/text')
        self.assertTrue('SignUp'.encode() in response.data)



     # Ensure that logout page requires user login

    def test_logout_route_requires_login(self):
        tester = app.test_client(self)
        response=tester.get('/logout',follow_redirects=True)
        self.assertTrue('Please sign in'.encode() in response.data)

        # Ensure that dashboard page requires user login

    def test_dashboard_route_requires_login(self):
        tester = app.test_client(self)
        response = tester.get('/dashboard', follow_redirects=True)
        self.assertTrue('Please sign in'.encode() in response.data)


        # Ensure login behaves correctly given the correct credentials

    def test_correct_login(self):
        # log in via HTTP
        tester = app.test_client(self)
        r = tester.post('/login', data={'username': 'python', 'password': 'is-great!'})
        assert r.status_code == 200



if __name__ == '__main__':
    unittest.main()



