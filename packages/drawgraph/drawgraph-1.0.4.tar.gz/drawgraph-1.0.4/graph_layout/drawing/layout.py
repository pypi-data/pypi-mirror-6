from collections import defaultdict
from graph_layout.classes.vertex import Vertex
import math
import copy


def magnitude(x, y):
    return math.sqrt(x*x + y*y)


def circle_layout(graph, side=10.0):
    """
    Result:
    ------------
    List of a graph's vertices, placed on the nodes 
    of the regular n-polygon circumscribed by a circle with the given radius.

    Parameters:
    ------------
    graph : an instance of the Graph class from graph_layout.classes.graph or
    of a class that has paths and vertices properties (dictionaries).
    side : diameter of a circle.
    """
    vertices = [Vertex(v) for v in graph.vertices]
    angle = 0
    unit_angle = 2 * math.pi / len(vertices)
    for v in vertices:
        v.x = math.cos(angle) * side/2
        v.y = math.sin(angle) * side/2
        angle += unit_angle
    return vertices


def _max_path(graph):
    """
    Result:
    ------------
    Maximum path from the shortest paths between every two vertices of the graph.

    Parameters:
    ------------
    graph : an instance of the Graph class from graph_layout.classes.graph or
    of a class that has paths propery (dictionary).

    Used by kamada_kawai_layout().
    """
    return max([path for v1, row in graph.paths.iteritems() for path in row.values()])


def _compute_strengths(graph, K=1.0):
    """
    Result:
    ------------
    Dictionary of spring strengths.

    Parameters:
    ------------
    graph : an instance of the Graph class from graph_layout.classes.graph or
    of a class that has paths and vertices properties (dictionaries).
    K : a spring constant (default to 1.0).
    Used by kamada_kawai_layout().

    Reference:
    -----------
    Kamada, Tomihisa; Kawai, Satoru (1989), "An algorithm for drawing general undirected graphs"
    http://dx.doi.org/10.1016%2F0020-0190%2889%2990102-6
    Equation (3)

    Used by kamada_kawai_layout().

    """
    strengths = defaultdict(dict)
    for v1 in graph.vertices:
        for v2 in graph.vertices:
            if v1 == v2:
                strengths[v1][v1] = 0
                continue
            strengths[v1][v2] = K / (graph.paths[v1][v2] ** 2)
    return strengths


def _partial_derivatives(v, vertices, strengths, lengths):
    """
    Result:
    ------------
    A tuple (dE/dx, dE/dy), where E is a total energy of the spring system.

    Parameters:
    ------------
    v : the Vertex object (must have x and y properties).
    vertices : the list of all vertices.
    strengths : the dictionary of the spring strengths.
    lengths : the dictionary of the desirable lengths.

    Reference:
    -----------
    Kamada, Tomihisa; Kawai, Satoru (1989), "An algorithm for drawing general undirected graphs"
    http://dx.doi.org/10.1016%2F0020-0190%2889%2990102-6
    Equations (7), (8)

    Used by kamada_kawai_layout().
    """
    de_x = 0
    de_y = 0
    for other in vertices:
        if v == other:
            continue
        dx = v.x - other.x
        dy = v.y - other.y
        diff = magnitude(dx, dy)
        common_part = lengths[v.obj][other.obj]/diff
        de_x += strengths[v.obj][other.obj] * (dx - common_part * dx)
        de_y += strengths[v.obj][other.obj] * (dy - common_part * dy)
    return de_x, de_y


def _compute_deltas(v, vertices, strengths, lengths, partial_derivatives):
    """
    Result:
    ------------
    A tuple (dx, dy), where dx and dy are changes in a vertex's position.

    Parameters:
    ------------
    v : a Vertex object (must have x and y properties).
    vertices : a list of all vertices.
    strengths : a dictionary of the spring strengths.
    lengths : a dictionary of the desirable lengths.
    partial_derivatives : a list of tuples of first-order derivatives for each vertex.
    Computed by _partial_derivatives()

    Reference:
    -----------
    Kamada, Tomihisa; Kawai, Satoru (1989), "An algorithm for drawing general undirected graphs"
    http://dx.doi.org/10.1016%2F0020-0190%2889%2990102-6
    Equations (11), (12)

    Used by kamada_kawai_layout().
    """
    de_x_x = de_x_y = de_y_x = de_y_y = 0
    for other in vertices:
        if v == other:
            continue
        dx = v.x - other.x
        dy = v.y - other.y
        common_denominator = (dx ** 2 + dy ** 2) ** 1.5
        ldx = lengths[v.obj][other.obj] * dx
        ldy = lengths[v.obj][other.obj] * dy
        ldxdy = ldy * dx

        de_x_x += strengths[v.obj][
            other.obj] * (1 - ldy * dy / common_denominator)
        de_x_y += strengths[v.obj][other.obj] * ldxdy / common_denominator
        de_y_x += strengths[v.obj][other.obj] * ldxdy / common_denominator
        de_y_y += strengths[v.obj][
            other.obj] * (1 - ldx * dx / common_denominator)

    de_x = partial_derivatives[vertices.index(v)][0]
    de_y = partial_derivatives[vertices.index(v)][1]

    # Cramer's rule for 2x2
    determinant = de_x_x * de_y_y - de_x_y * de_y_x
    dx = (-de_x * de_y_y + de_x_y * de_y) / determinant
    dy = (-de_x_x * de_y + de_y_x * de_x) / determinant

    return dx, dy


def kamada_kawai_layout(graph, side=10.00, threshold=0.001, K=2.0):
    """
    Result:
    ------------
    A list of Vertex object from graph_layout.classes.vertex.

    Parameters:
    ------------
    graph : a connected, weighted graph, that has paths and vertices properties.
    side : a length of a side of display square area. 
    threshold : a tolerance value.
    K : a spring constant (default to 2.0).

    Reference:
    -----------
    Kamada, Tomihisa; Kawai, Satoru (1989), "An algorithm for drawing general undirected graphs"
    http://dx.doi.org/10.1016%2F0020-0190%2889%2990102-6

    """
    def worst_vertex():
        return max(enumerate([magnitude(*d) for d in partial_derivs]), key=lambda x: x[1])

    L = side / _max_path(graph)

    lengths = defaultdict(dict)
    for v1 in graph.vertices:
        for v2 in graph.vertices:
            lengths[v1][v2] = graph.paths[v1][v2]*L

    strengths = _compute_strengths(graph, K)

    vertices = circle_layout(graph, side/2)

    partial_derivs = [_partial_derivatives(v, vertices, strengths, lengths) for v in vertices]
    worst_v_index, max_dm = worst_vertex()

    vertice_iterations = [0 for i in range(len(vertices))]

    while max_dm > threshold:
        while max_dm > threshold:
            v = vertices[worst_v_index]
            for i in range(len(vertices)):
                if i == worst_v_index:
                    vertice_iterations[worst_v_index] += 1
                else:
                    vertice_iterations[i] = 0

            if vertice_iterations[worst_v_index] > 20:
                v.random_position(side, side)
                vertice_iterations[worst_v_index] = 0
                break

            dx, dy = _compute_deltas(v, vertices, strengths, lengths, partial_derivs)
            v.x += dx
            v.y += dy

            partial_derivs[worst_v_index] = _partial_derivatives(v, vertices, strengths, lengths)
            max_dm = magnitude(*partial_derivs[worst_v_index])

        partial_derivs = [_partial_derivatives(v, vertices, strengths, lengths) for v in vertices]
        worst_v_index, max_dm = worst_vertex()

    return vertices


def _find_x_upper_bound(vertices):
    """
    Result:
    ------------
    A maximum value of x coordinate

    Parameters:
    ------------
    vertices : a list of vertices

    Used by plot_graph.
    """
    return max([v.x for v in vertices])


def plot_graph(graph, layout_algorithm=kamada_kawai_layout, side=10.00, **kwargs):
    """
    Result:
    ------------
    A list of vertices.

    Parameters:
    ------------
    graph : a weighted graph, that don't need to be connected, that has paths and vertices properties.
    layout_algorithm : algorithm to draw the graph with (default to kamada_kawai_layout)
    side : a length of a side of display square area.
    **kwargs: the rest of the keyword parameters for a layout_algorithm.
    """
    components = graph.decompose_into_connected_components()
    if len(components) == 1:
        return layout_algorithm(graph, side, **kwargs)
    vertices = []
    x_start = 0
    for component in components:
        if len(component.vertices):
            result = [Vertex(component.vertices[0], 0, side/2)]
        else:
            max_path = _max_path(component)
            result = layout_algorithm(component, side=side*max_path, **kwargs)

        for v in result:
            v.x += x_start
        vertices += result
        x_start = _find_x_upper_bound(result)

    return vertices
