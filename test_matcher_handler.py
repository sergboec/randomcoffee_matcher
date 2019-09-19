from unittest import TestCase

from matcher import matcher_handler

class test_matcher_handler(TestCase):
    def test_matcher_handler(self):

        matcher_handler({
            "user_0": {"history": ["user_1"], "interests": [], "remote": True, "lang": "ru","location": "space"},
            "user_1": {"history":["user_0"],"interests":[],"remote":True,"lang": "ru", "location": "space"},
            "user_2": {"history": [], "interests": [], "remote": True, "lang": "ru", "location": "space"}
        },None)

        return



