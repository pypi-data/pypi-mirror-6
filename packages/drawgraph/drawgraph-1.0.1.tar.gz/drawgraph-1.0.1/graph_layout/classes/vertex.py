class Vertex():
    """
    Vertex in a 2 dimensional space.
    Contains object (vertex) and a position.

    Parameters:
    -----------
    obj : any object, will be accessible by v.obj
    x : x coordinate
    y : y y coordinate
    """
    def __init__(self, obj, x=0, y=0):
        self.obj = obj
        self.x = x
        self.y = y

    def __repr__(self):
        return "%s in (%d, %d)"%(self.obj, self.x, self.y)