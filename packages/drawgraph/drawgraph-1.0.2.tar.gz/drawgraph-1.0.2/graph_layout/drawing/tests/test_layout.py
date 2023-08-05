from graph_layout.classes.graph import Graph
from graph_layout.drawing.layout import _max_path, _compute_strengths, circle_layout, kamada_kawai_layout, plot_graph
import unittest
import math
import copy


graph = Graph(
    {'1': {'2': 3, '3': 5},
     '2': {'1': 3},
     '3': {'1': 5}})


def distance(v1, v2):
    return math.sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2)


class LayoutTests(unittest.TestCase):
    def test__max_path(self):
        result = _max_path(copy.deepcopy(graph))
        expected = 8
        self.assertEqual(expected, result)

    def test__compute_strengths(self):
        result = _compute_strengths(copy.deepcopy(graph), 2.0)
        expected = {'1': {'1': 0, '2': 2.0/9, '3': 2.0/25},
                    '2': {'1': 2.0/9, '2': 0, '3': 2.0/64},
                    '3': {'1': 2.0/25, '2': 2.0/64, '3': 0}}
        self.assertEqual(expected, result)

    def test_circle_layout(self):
        result = circle_layout(copy.deepcopy(graph), 2)
        self.assertEqual(1, result[0].x)
        self.assertEqual(0, result[0].y)
        self.assertEqual(math.cos(2*math.pi/3), result[1].x)
        self.assertEqual(math.sin(2*math.pi/3), result[1].y)
        self.assertEqual(math.cos(4*math.pi/3), result[2].x)
        self.assertEqual(math.sin(4*math.pi/3), result[2].y)

    def test_kamada_kawai_layout(self):
        g = Graph({'1': {'2': 1, '3': 5},
                   '2': {'1': 1},
                   '3': {'1': 5}})
        result = kamada_kawai_layout(g, 100.0)
        v1 = v2 = v3 = None
        for v in result:
            if v.obj == '1':
                v1 = v
            if v.obj == '2':
                v2 = v
            if v.obj == '3':
                v3 = v
        self.assertAlmostEquals(distance(v1, v2), 100.0/6, delta=1)
        self.assertAlmostEquals(distance(v2, v3), 100.0, delta=1)
        self.assertAlmostEquals(distance(v1, v3), 100.0/6*5, delta=1)

    def test_plot_graph(self):
        disconnected_graph = Graph(
            {'1': {'2': 3},
             '2': {'1': 3},
             '3': {'4': 5},
             '4': {'3': 5}})
        result = plot_graph(disconnected_graph, threshold=0.01)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()