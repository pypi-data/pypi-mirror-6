from graph_layout.classes.graph import Graph
import unittest


class ConnectedComponentsTests(unittest.TestCase):
    def test_from_disconnected(self):
        disconnected_graph = Graph(
            {'1': {'2': 3},
             '2': {'1': 3},
             '3': {'4': 5, '6': 1},
             '4': {'3': 5},
             '5': {'6': 2},
             '6': {'3': 1, '5': 2}})

        result = disconnected_graph.decompose_into_connected_components()
        expected = [
            Graph({'1': {'2': 3},
                   '2': {'1': 3}}),
            Graph({'3': {'4': 5, '6': 1},
                   '4': {'3': 5},
                   '5': {'6': 2},
                   '6': {'3': 1, '5': 2}})]
        self.assertEqual(expected, result)

    def test_from_connected(self):
        connected_graph = Graph(
            {'1': {'2': 3, '3': 5},
             '2': {'1': 3},
             '3': {'1': 5}})
        result = connected_graph.decompose_into_connected_components()
        expected = [connected_graph]
        self.assertEqual(expected, result)


class ShortestPathTests(unittest.TestCase):
    def test_find_shortest_paths(self):
        graph = Graph(
            {'1': {'3': -2},
             '2': {'1': 4, '3': 3},
             '3': {'4': 2},
             '4': {'2': -1}})

        result = graph.find_shortest_paths()
        expected = {
            '1': {'1': 0, '2': -1, '3': -2, '4': 0},
            '2': {'1': 4, '2': 0, '3': 2, '4': 4},
            '3': {'1': 5, '2': 1, '3': 0, '4': 2},
            '4': {'1': 3, '2': -1, '3': 1, '4': 0},
        }
        self.assertEqual(expected, result)


if __name__ == "__main__":
    unittest.main()