# -*- coding: utf-8 -*-
import sys
import unittest
from unittest.mock import MagicMock

sys.path.append(".") # Adds the directory from which the script is being run for tests
from vimeo_connection import VimeoConnection

class TestVimeo(unittest.TestCase):
    def setUp(self):
        self.vimeoconnection = VimeoConnection(
            token='YOUR_ACCESS_TOKEN',
            key='YOUR_CLIENT_ID',
            secret='YOUR_CLIENT_SECRET'
        )
        print(self.vimeoconnection)
        print(self.vimeoconnection.account_infos())

    """
    def test_account_infos(self):
        # Mock the response from the Vimeo API
        expected_response = {'name': 'John Doe'}
        self.vimeo_general.client.get = MagicMock(return_value=expected_response)

        # Call the method being tested
        response = self.vimeoconnection.account_infos()

        # Check that the response matches the expected response
        self.assertEqual(response, expected_response)
    """
    
if __name__ == '__main__':
    unittest.main()
