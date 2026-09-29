import numpy as np
from django.test import SimpleTestCase

from recommender.management.commands.train_clusters import _fit_kmeans, _silhouette


class ClusteringTest(SimpleTestCase):
    def test_dua_kelompok_terpisah_dan_reproduktif(self):
        points = np.array([[0.0], [0.1], [0.2], [9.8], [9.9], [10.0]])
        first = _fit_kmeans(points, 2)
        second = _fit_kmeans(points, 2)
        self.assertEqual(first[0], second[0])
        self.assertEqual(len(set(first[2][:3])), 1)
        self.assertEqual(len(set(first[2][3:])), 1)
        self.assertNotEqual(first[2][0], first[2][3])
        self.assertGreater(_silhouette(points, first[2]), 0.9)
