from collections import defaultdict


class Graph():
    """
    A graph_layout stores vertices and edges with weights.

    Parameters:
    ----------
    data : dictionary that represents a graph_layout, for example:

    {'1': {'2': 3},
     '2': {'1': 3},
     '3': {}
    }
    The keys ('1', '2', '3') are vertices,
    the values describe edges ('1' and '2' are connected by an edge with weight = 3).

    """

    def __init__(self, data):
        self.data = data
        self._vertices = self.data.keys()
        self._paths = None

    def __eq__(self, other):
        """
        Two graphs are equal, if their dictionary representations are equal.
        """
        return cmp(self.data, other.data) == 0

    def __neq__(self, other):
        """
        Two graphs are not equal, if their dictionary representations are not equal.
        """
        return cmp(self.data, other.data) != 0

    def decompose_into_connected_components(self):
        """
        Returns the list of the connected components of a graph_layout.
        Uses BFS algorithm.
        """
        connected_components = []
        visited = []

        for v in self._vertices:
            if v in visited:
                continue
            component = [v]
            q = [v]
            visited.append(v)
            while q:
                v = q.pop()
                for adj_v in self.data[v].keys():
                    if not adj_v in visited:
                        visited.append(adj_v)
                        component.append(adj_v)
                        q.append(adj_v)
            connected_components.append(component)

        if len(connected_components) == 1:
            return [self]

        graphs = []
        for component in connected_components:
            data = {}
            for v in component:
                data[v] = self.data[v]
            graphs.append(Graph(data))
        return graphs

    def find_shortest_paths(self):
        """
        Returns the dictionary of the shortest paths for each pair of the vertices.
        Uses Floyd-Warshall algorithm (http://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm).
        """

        paths = defaultdict(dict)

        for v1 in self._vertices:
            for v2 in self._vertices:
                if v1 == v2:
                    paths[v1][v2] = 0
                    continue
                if not v2 in self.data[v1].keys():
                    paths[v1][v2] = float('inf')
                else:
                    paths[v1][v2] = self.data[v1][v2]

        for v1 in self._vertices:
            for v2 in self._vertices:
                for v3 in self._vertices:
                    if paths[v2][v1] + paths[v1][v3] < paths[v2][v3]:
                        paths[v2][v3] = paths[v2][v1] + paths[v1][v3]

        return paths

    @property
    def paths(self):
        if not self._paths:
            self._paths = self.find_shortest_paths()
        return self._paths

    @property
    def vertices(self):
        return self._vertices


