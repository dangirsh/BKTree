# Dan Girshovich
# 7/12

from collections import defaultdict
from collections import OrderedDict

class BKTree():
    ''' Group of functions for a dictionary backed BKTree.
        See: http://hamberg.no/erlend/posts/2012-01-17-BK-trees.html 
        for details about BKTrees.
        
        - tree = <dict> {node : <dict> {distance : child_node}}
        - get_distance must be a integral metric distance function on
        strings/sequences (like levenshtein, not jaro)
        - distance keys are strings (to play nicely with mongo)
        
        Example tree: {'abc' : {'1' : 'bc'}, 'bc' : {}} represents
        the tree with root 'abc' and its one child 'bc' at distance 1.
        
        Do not mutate the tree dict outside of this class.'''

    @staticmethod
    def create_tree(root):
        return {root : {}}

    @staticmethod
    def add_node(tree, parent, distance, node):
        tree[parent][distance] = node
        tree[node] = {}

    @staticmethod
    def is_leaf(tree, node):
        return tree[node] == {}

    @staticmethod
    def has_child(tree, node, distance):
        return tree[node].has_key(distance)

    @staticmethod
    def get_child(tree, node, distance):
        return tree[node][distance]    

    @staticmethod
    def get_child_distances(tree, node):
        return tree[node].keys()

    @staticmethod
    def get_children(tree, node):
        return tree[node].values()

    @staticmethod
    def traverse(tree, root, traverse_func):
        ''' Depth-first traversal starting at the root and uses 
            traverse_func(tree, current_node) -> [children to traverse]. '''
        stack = [root]
        while stack:
            stack += traverse_func(tree, stack.pop())

    @staticmethod
    def insert(tree, root, new_node, get_distance):
        ''' Adds new_node to tree using get_distance(node1, node2) -> dist
            to compute the distances. '''
            
        def insert_traverse_func(tree, node):
            distance = str(get_distance(node, new_node))
            if BKTree.has_child(tree, node, distance):
                return [BKTree.get_child(tree, node, distance)]
            else:
                BKTree.add_node(tree, node, distance, new_node)
                return [] # termiate traversal
        
        BKTree.traverse(tree, root, insert_traverse_func)

    @staticmethod
    def find(tree, root, query, max_distance, get_distance, limit = None, profile = False):
        ''' Returns the top 'limit' best matches to query that satisfy 
            get_distance(query, result) <= max_distance sorted by distance. 
            Returns all results if limit is None.
            Returns [] if max_distance or limit < 0. Performance 
            decreases as max_distance increases. Appends the percent of nodes
            hit by the query to the return value when profiling is on. 
            See: http://www.kafsemo.org/2010/08/03_bk-tree-performance-notes.html .
        '''
        if max_distance < 0 or (limit is not None and limit < 0):
            return []
        results = defaultdict(list)
        profile_ctr = [0] # need to be mutable to get nested access, stupid python

        def find_traverse_func(tree, node):
            if profile:
                profile_ctr[0] += 1
            int_distance = get_distance(node, query)
            if int_distance <= max_distance: 
                results[int_distance].append(node)
            lower_bound = max(0, int_distance - max_distance)
            upper_bound = int_distance + max_distance
            search_range = set(map(str, range(lower_bound, upper_bound + 1)))
            child_dists = set(BKTree.get_child_distances(tree, node))
            dists_to_traverse = list(search_range.intersection(child_dists))
            return [BKTree.get_child(tree, node, d) for d in dists_to_traverse]
        
        # get results
        BKTree.traverse(tree, root, find_traverse_func)            
        # sort by distance
        results = sorted(results.items(), key = lambda t : t[0])
        # remove distances
        results = map(lambda (dist, node_list) : node_list, results)
        # flatten
        results = [node for node_list in results for node in node_list]
        if limit:
            results = results[:limit]    
        if profile:
            return (results, float(profile_ctr[0]) / len(tree))
        else:
            return results

    @staticmethod
    def get_depth(tree, root):
        ''' Returns the maximum zero-indexed depth of the tree. Only use for 
            metrics because this needs to hit every node. '''              
        max_depth = -1
        stack = [(root, 0)]
        while stack:
            node, depth = stack.pop()
            if BKTree.is_leaf(tree, node):
                if depth > max_depth:
                    max_depth = depth
            else:
                depth += 1                              
                stack += [(c, depth) for c in BKTree.get_children(tree, node)]
        return max_depth

    @staticmethod
    def get_average_distance(tree):
        ''' Returns the average distance between nodes in the tree. '''
        tot_dist = 0
        num_edges = 0
        for node in tree:
            tot_dist += sum(map(int, BKTree.get_child_distances(tree, node)))
            num_edges += len(BKTree.get_children(tree, node))
        return float(tot_dist) / num_edges