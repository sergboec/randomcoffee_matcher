from unittest import TestCase

from matcher import matcher_handler

class test_matcher_handler(TestCase):
    def test_matcher_handler(self):

        matcher_handler({
            "user_0": {"history": [], "interests": ["a","b"], "remote": True, "lang": ["ru"],"location": "space"},
            "user_1": {"history":[],"interests":["b","c"],"remote":True,"lang": ["ru"], "location": "space"},
            "user_2": {"history": [], "interests": ["c"], "remote": True, "lang": ["ru"], "location": "space"},
            "user_3": {"history": [], "interests": ["a","d"], "remote": True, "lang": ["ru"], "location": "space"}
        },None)

        return



