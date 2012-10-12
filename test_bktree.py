# Dan Girshovich, 6/12

import unittest
from BKTree import BKTree
from Levenshtein import distance as get_distance

class BKTreeTest(unittest.TestCase):
    '''test inserts and queries for this tree:
                    abcd
                1           2
            abcde           bcde
            2               2   1
        abc               bc    bbcde
        1
    abcz
    '''


    def runTest(self):

        root = ['abcd']  # needs to be mutable for nested access, stupid python
        tree = BKTree.create_tree(root[0])

        def _check_insert(node, tree_depth):
            BKTree.insert(tree, root[0], node, get_distance)
            self.assertEqual(BKTree.get_depth(tree, root[0]), tree_depth)          

        def _check_query(query, max_d, num_hit, true_result):
            result, perc_hit = BKTree.find(tree, root[0], query, max_d, get_distance, profile = True) 
            self.assertEqual(set(result), set(true_result))
            self.assertEqual(perc_hit, num_hit / 7.0)        

        # 0 indexed depth
        self.assertEqual(BKTree.get_depth(tree, root[0]), 0)

        #inserts
        nodes = ['abcde', 'bcde', 'abc', 'bc', 'bbcde', 'abcz']
        tree_depths = [1, 1, 2, 2, 2, 3]
        map(_check_insert, nodes, tree_depths)

        #queries
        _check_query('abc', 0, 3, ['abc'])
        _check_query('abc', 1, 6, ['abcd', 'abc', 'abcz', 'bc'])
        _check_query('abcd', 2, 7, ['abcd', 'abcde', 'abc', 'abcz', 'bcde', 'bc', 'bbcde'])
        _check_query('bc', 1, 7, ['bc', 'abc'])

        self.assertEqual(BKTree.get_average_distance(tree), 1.5)

if __name__ == '__main__':
    unittest.main()