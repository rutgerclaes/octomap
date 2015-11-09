import math

class OccupancyOctoMap:
    """
    OctoMap to store 3D probabilistic occupancy information.  Based on
    "OctoMap: An Efficien Probabilistic 3D Mapping Framwork Based on Octrees" by
    A. Hornung, K. M. Wurm, M. Bennewitz, C. Stachniss and W. Burgard.
    (http://octomap.github.io).

    This python implementation is meant as an experiment for use in small demo
    applications.
    """

    def __init__(self, center, resolution, max_depth, prior_prob = 0.5 ):
        """
        Create a new OccupancyOctoMap.

        The map will be centered around the `center` position specified by the
        user and will have a width of `resolution` times 2 to the power of `max_depth`

        Args:
            center: center of the map -- (x,y,z) tuple
            resolution: maximal resolution
            max_depth: maximum depth
            prior_prob: prior occupancy probability

        Returns: a new map
        """
        self._center = center
        self._resolution = resolution
        self._max_depth = max_depth

        self.root = OccupancyOctoNode(prior_prob)

    def contains(self, point):
        """
        Returns whether point is contained by this map.

        Args:
            point: point to check -- (x,y,z) tuple

        Returns:
            True if the point is contained by this map

        Raises:
            ValueError: if the tuple does not have length 3
        """
        if not len(point) == 3:
            raise ValueError( "Point should be tuple containing x, y, z" )
        radius = self.radius
        return \
            self._center[0] - radius <= point[0] < self._center[0] + radius and \
            self._center[1] - radius <= point[1] < self._center[1] + radius and \
            self._center[2] - radius <= point[2] < self._center[2] + radius

    @property
    def radius(self):
        """Returns the radius (the width / 2)."""
        return math.pow(self._resolution, self._max_depth - 1)

    @property
    def width(self):
        """Return the width of the cube represented by this octomap."""
        return math.pow(self._resolution, self._max_depth)

    def origin(self):
        """Returns the origin of this map"""
        radius = self.radius
        return ( self._center[0] - radius,
                self._center[1] - radius,
                self._center[2] - radius )

    def update( self, point, probability = 1.0 ):
        """
        Add an observation to the octo map.

        Args:
            point: the location of the observation, a tuple containing x, y, z
            probability: the probability of occupancy (default 1.0)
        """
        if not len( point ) == 3:
            raise ValueError( "Point should be tuple (x,y,z)" )
        if not 0 < probability < 1:
            raise ValueError( "Probability should be between 0.0 and 1.0" )

        self.root.update( point, probability, self.origin, self.width, self._max_depth )

    def probability(self, point):
        """
        Returns the probability of occupancy at a given point.

        Args:
            point: point to get probability at -- (x,y,z) tuple

        Returns:
            probability of occupancy at that point

        Raises:
            ValueError: if the point is not contained by this map
        """
        if not self.contains( point ):
            raise ValueError( "Invalid point" )
        return self.root.probability_at( point, self.origin, self.width )


class OccupancyOctoNode:
    """
    OctoMap node keeping track of possibility of occupancy.

    An OccupancyOctoNode represents a 3D cube that could be occupied (filled).
    The probability of this 3D cube being occupied can be updated given new
    evidence.  If the 3D cube represented by this node is too coarse given the
    resolution of the OctoMap container, the node will split into 8 children
    and update their occupancy to achieve the desired resolution.

    Objects of this class don't store their position or size.  That would greatly
    increase the memory requirements of the datastructure.  Rather, the size and
    position (origin) of the cube are calculated ad hoc given the arguments.

    OccupancyOctoNodes are not to be used directly.  The OccupancyOctoMap acts as
    a facade in front of them.
    """

    def __init__(self, prior_prob=0.5):
        """
        Initiates a new OccupancyOctoNode

        Args:
            prior_prob: the prior probability of this node being occupied
        """
        self._children = None
        self._log_odds = math.log(prior_prob / (1 - prior_prob))

    def is_leaf(self):
        """Returns whether this is a leaf node."""
        return self._children is None

    def _split(self):
        """
        Splits the node into 8 child nodes.

        Child nodes are given the occupancy of this parent node as the initial probability
        of occupancy.
        """
        if not self.is_leaf(): return
        self._children = (
        OccupancyOctoNode(self.probability), OccupancyOctoNode(self.probability), OccupancyOctoNode(self.probability),
        OccupancyOctoNode(self.probability), OccupancyOctoNode(self.probability), OccupancyOctoNode(self.probability),
        OccupancyOctoNode(self.probability), OccupancyOctoNode(self.probability))

    def index(self, point, origin, width):
        """Calculates the index of the child containing point"""
        if not self.contains(point, origin, width):
            raise ValueError("point is not contained in node")

        return (1 if point[0] >= origin[0] + width / 2 else 0) + \
               (2 if point[1] >= origin[1] + width / 2 else 0) + \
               (4 if point[2] >= origin[2] + width / 2 else 0)

    def contains(self, point, origin, width):
        """Returns whether the point is contained by this node"""
        return origin[0] <= point[0] < origin[0] + width and \
               origin[1] <= point[1] < origin[1] + width and \
               origin[2] <= point[2] < origin[2] + width

    def origin(self, index, origin, width):
        """Calculates the origin of the node with given index."""
        hwidth = width / 2;
        return (origin[0] + (hwidth if index & 1 else 0),
                origin[1] + (hwidth if index & 2 else 0),
                origin[2] + (hwidth if index & 4 else 0))

    def update(self, point, probability, origin, width, max_depth):
        """
        Updates the node with a new observation.

        Args:
            point: the point of the observation
            probability: probability of occupancy
            origin: origin of this node
            width: width of this node
            max_depth: maximum depth this node can be branched

        Raises:
            ValueError: If the point is not contained by the cube specified by origin and width

        """
        if max_depth == 0:
            self._update_probability(probability)
        else:
            if self.is_leaf():
                self._split()  # TODO check whether we really need to split given the observation
            child_index = self.index(point, origin, width)
            self._children[child_index].update(point, probability, self.origin(child_index, origin, width), width / 2,
                                               max_depth - 1)

    def _update_probability(self, probability):
        """Updates the probability of occupancy"""
        self._log_odds += math.log(probability / (1 - probability))

    @property
    def probability(self):
        """Returns probability of occupancy."""
        odds = math.pow(math.e, self._log_odds)
        return odds / (odds + 1)

    def probability_at(self, point, origin, width):
        """
        Returns probability of occupancy at a given point.

        Args:
            point: point at which the occupancy needs to be calculated
            origin: origin of this node
            width: width of this node

        Returns:
            the probability
        """
        if self.is_leaf():
            return self.probability
        else:
            child_index = self.index(point, origin, width)
            return self._children[child_index].probability_at(point, self.origin(child_index, origin, width), width / 2)