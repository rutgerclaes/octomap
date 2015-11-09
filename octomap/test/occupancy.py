import unittest
import math

from octomap.occupancy import OccupancyOctoNode


class OccupancyOctoNodeTestCase(unittest.TestCase):

    def test_probability(self):
        prob = 0.44
        node = OccupancyOctoNode( prob )
        self.assertEqual( prob, node.probability )

    def test_unsplitted_node(self):
        node = OccupancyOctoNode()
        self.assertTrue( node.is_leaf() )
        node._split()
        self.assertFalse( node.is_leaf() )

    def test_probability_at_of_leaf(self):
        node = OccupancyOctoNode( 0.2 )
        self.assertEqual( node.probability, node.probability_at( (.5, .5, .5 ), (0,0,0), 1 ) )

    def test_update_with_max_depth(self):
        node = OccupancyOctoNode( 0.2 )
        node.update( (0,0,0), 0.3, (0,0,0), 2, 0 )
        self.assertTrue( node.is_leaf() )

    def test_update_with_split(self): # TODO test further splitting
        prior = 0.2
        child = 0.7
        node = OccupancyOctoNode( prior )
        node.update( ( 0.5, 0.5, 0.5 ), child, ( 0, 0, 0 ), 2, 1 )
        posteriori_log_odds = math.log( prior / ( 1 - prior ) ) + math.log( child / ( 1 - child ) )
        posteriori_odds = math.pow( math.e, posteriori_log_odds )
        posteriori_prob = posteriori_odds / ( 1 + posteriori_odds )

        self.assertEqual( posteriori_prob, node.probability_at( (0.5, 0.5, 0.5 ), (0,0,0), 2 ) )

    def test_splitted_children(self):
        node = OccupancyOctoNode()
        node._split()
        self.assertEqual( node.probability, node.probability_at( ( 0, 0, 0 ), ( 0, 0, 0 ), 2 ) )
        self.assertEqual( node.probability, node.probability_at( ( 1, 0, 0 ), ( 0, 0, 0 ), 2 ) )
        self.assertEqual( node.probability, node.probability_at( ( 0, 1, 0 ), ( 0, 0, 0 ), 2 ) )
        self.assertEqual( node.probability, node.probability_at( ( 0, 0, 1 ), ( 0, 0, 0 ), 2 ) )
        self.assertEqual( node.probability, node.probability_at( ( 1, 1, 0 ), ( 0, 0, 0 ), 2 ) )
        self.assertEqual( node.probability, node.probability_at( ( 0, 1, 1 ), ( 0, 0, 0 ), 2 ) )
        self.assertEqual( node.probability, node.probability_at( ( 1, 0, 1 ), ( 0, 0, 0 ), 2 ) )
        self.assertEqual( node.probability, node.probability_at( ( 1, 1, 1 ), ( 0, 0, 0 ), 2 ) )

    def test_indexing(self):
        node = OccupancyOctoNode()
        # Assuming node with dimension 2 and origin 0,0,0
        origin = (0,0,0)

        self.assertEqual( node.index( origin, origin, 2 ), 0 )

        self.assertEqual( node.index( ( 0.5, 0.5, 0.5 ), origin, 2), 0 )
        self.assertEqual( node.index( ( 0, 0.5, 0.5 ), origin, 2), 0 )
        self.assertEqual( node.index( ( 0.5, 0, 0.5 ), origin, 2), 0 )
        self.assertEqual( node.index( ( 0.5, 0.5, 0 ), origin, 2), 0 )

        self.assertEqual( node.index( ( 1.5, 0.5, 0.5 ), origin, 2), 1 )
        self.assertEqual( node.index( ( 1, 0, 0 ), origin, 2), 1 )

        self.assertEqual( node.index( ( 0.5, 1.5, 0.5 ), origin, 2 ), 2)
        self.assertEqual( node.index( ( 0, 1, 0 ), origin, 2 ), 2)

        self.assertEqual( node.index( ( 1.5, 1.5, 0.5 ), origin, 2), 3 )
        self.assertEqual( node.index( ( 1, 1, 0 ), origin, 2), 3 )

        self.assertEqual( node.index( ( 0.5, 0.5, 1.5 ), origin, 2), 4 )
        self.assertEqual( node.index( ( 0, 0, 1 ), origin, 2), 4 )

        self.assertEqual( node.index( ( 1.5, 0.5, 1.5 ), origin, 2), 5 )
        self.assertEqual( node.index( ( 1, 0, 1 ), origin, 2), 5 )

        self.assertEqual( node.index( ( 0.5, 1.5, 1.5 ), origin, 2), 6 )
        self.assertEqual( node.index( ( 0, 1, 1 ), origin, 2), 6 )

        self.assertEqual( node.index( ( 1.5, 1.5, 1.5 ), origin, 2), 7 )
        self.assertEqual( node.index( ( 1, 1, 1 ), origin, 2), 7 )

    def test_contains(self):
        node = OccupancyOctoNode()
        first_origin = ( 0, 0, 0 )
        self.assertTrue( node.contains( ( 0.5, 0.5, 0.5 ), first_origin, 1 ) )
        self.assertTrue( node.contains( ( 0, 0.5, 0.5 ), first_origin, 1 ) )
        self.assertTrue( node.contains( ( 0, 0, 0.5 ), first_origin, 1 ) )
        self.assertTrue( node.contains( ( 0, 0, 0 ), first_origin, 1 ) )

        self.assertFalse( node.contains( ( 1.5, 0.5, 0.5 ), first_origin, 1 ) )
        self.assertFalse( node.contains( ( 0.5, 1.5, 0.5 ), first_origin, 1 ) )
        self.assertFalse( node.contains( ( 0.5, 0.5, 1.5 ), first_origin, 1 ) )
        self.assertFalse( node.contains( ( -0.5, 0.5, 0.5 ), first_origin, 1 ) )
        self.assertFalse( node.contains( ( 0.5, -0.5, 0.5 ), first_origin, 1 ) )
        self.assertFalse( node.contains( ( 0.5, 0.5, -0.5 ), first_origin, 1 ) )

        second_origin = ( -1, -1, -1 )
        self.assertTrue( node.contains( ( -0.5, -0.5, -0.5 ), second_origin, 1 ) )
        self.assertTrue( node.contains( ( -1, -1, -1 ), second_origin, 1 ) )
        self.assertFalse( node.contains( ( 0, 0, 0 ), second_origin, 1 ) )
        self.assertTrue( node.contains( ( 0, 0, 0 ), second_origin, 2 ) )

    def test_invalid_indexing(self):
        node = OccupancyOctoNode()
        origin = ( 0, 0, 0 )
        self.assertRaises( ValueError, node.index, ( 0.5, 0.5, 1.5 ), origin, 1 )
        self.assertRaises( ValueError, node.index, ( 0.5, 1.5, 0.5 ), origin, 1 )
        self.assertRaises( ValueError, node.index, ( 1.5, 0.5, 0.5 ), origin, 1 )
        self.assertRaises( ValueError, node.index, (1, 1, 1 ), origin, 1 )

    def test_origin(self):
        node = OccupancyOctoNode()
        origin = ( 0, 0, 0 )
        self.assertEquals( ( 0, 0, 0 ), node.origin( 0, origin, 2 ) )
        self.assertEquals( ( 1, 0, 0 ), node.origin( 1, origin, 2 ) )
        self.assertEquals( ( 0, 1, 0 ), node.origin( 2, origin, 2 ) )
        self.assertEquals( ( 1, 1, 0 ), node.origin( 3, origin, 2 ) )
        self.assertEquals( ( 0, 0, 1 ), node.origin( 4, origin, 2 ) )
        self.assertEquals( ( 1, 0, 1 ), node.origin( 5, origin, 2 ) )
        self.assertEquals( ( 0, 1, 1 ), node.origin( 6, origin, 2 ) )
        self.assertEquals( ( 1, 1, 1 ), node.origin( 7, origin, 2 ) )