import unittest
from recommender import Recommender

class RecommendationTests(unittest.TestCase):
    def setUp(self):
        self.model = Recommender({i: {"title": str(i)} for i in range(1, 5)}, [(1, 1, 5, 1), (2, 1, 5, 1), (2, 2, 5, 2), (3, 3, 2, 1)])

    def test_seen_and_unrated_movies_excluded(self):
        ids = [mid for mid, _ in self.model.recommend(1)]
        self.assertNotIn(1, ids)
        self.assertNotIn(4, ids)
        self.assertEqual(ids[0], 2)
        self.assertEqual(len(ids), len(set(ids)))

    def test_new_user_uses_popularity(self):
        self.assertEqual(self.model.recommend(999), self.model.recommend(999, popular_only=True))

    def test_invalid_count(self):
        with self.assertRaises(ValueError):
            self.model.recommend(1, n=0)

if __name__ == "__main__":
    unittest.main()
