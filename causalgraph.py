import itertools

class Node(object):
    """
        A node in the graph.
    """
    
    def __init__(
        self, 
        name=None, 
        children=None,
        parents=None,
        conditioned=False
    ):
        self.name = name
        
        if children == None:
            self.children = []
        else:
            self.children = children
        
        if parents == None:
            self.parents = []
        else:
            self.parents = parents
            
        
        self.conditioned = conditioned
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
#         return "Node: { name: '" + \
#             self.name + \
#             "', conditioned: " + \
#             repr(self.conditioned) + \
#         "}"
        
        return "Node: { name: '" + \
            self.name + \
            "', conditioned: " + \
            repr(self.conditioned) + \
            ", parents: " + \
            str([str(i) for i in self.parents]) + \
            ", children: " + \
            str([str(i) for i in self.children]) + \
        "}"

    def set_conditioned(self, conditioned=False):
        self.conditioned = conditioned
        
    def is_not_adjacent_to(self, node=None):
        return not self.is_adjacent_to(node)
    
    def is_adjacent_to(self, node=None):
        return node in self.get_children() or node in self.get_parents()
    
    def is_conditioned(self):
        return self.conditioned
    
    def is_not_conditioned(self):
        return not self.is_conditioned()
    
    def is_chain(self):
        return self.has_parents() and self.has_children()
    
    def is_fork(self):
        return len(self.get_children()) > 1
    
    def is_collider(self):
        return len(self.get_parents()) > 1
    
    def is_not_collider(self):
        return not self.is_collider()
    
    def equals(self, node=None):
        return node.get_name() == self.get_name()
        
    def add_child(self, child=None):
        self.children.append(child)
        child.parents.append(self)
        
    def add_parent(self, parent=None):
        self.parents.append(parent)
        parent.children.append(self)
        
    def has_parents(self):
        return len(self.get_parents()) > 0
    
    def has_children(self):
        return len(self.get_children()) > 0
        
    def get_name(self):
        return self.name
    
    def get_children(self):
        return self.children
    
    def get_parents(self):
        return self.parents
    
    def get_descendants(self):
        descendants = self.get_children()
        
        for _child in self.children:
            descendants = list(set(descendants) | set(_child.get_children()))
            
        return descendants
            
    def get_ancestors(self):
        ancestors = self.get_parents()
        
        for _parent in self.parents:
            ancestors = list(set(ancestors) | set(_parent.get_parents()))
    
        return ancestors
    
    def set_children(self, children):
        self.children = children
        
    def set_parents(self, parents):
        self.parents = parents
        
    def has_conditioned_dependents(self):
        for desc in self.get_descendants():
            if desc.is_conditioned():
                return True
        
        return False
    
    def has_no_conditioned_dependents(self):
        return not self.has_conditioned_dependents()

class Paths(object):
    """ Paths between two nodes """
    
    def __init__(self, paths=None, between_nodes=None):
        if len(between_nodes) != 2:
            raise Exception("between_nodes length should be 2.")
        self.between_nodes = between_nodes
        
        if paths == None:
            self.paths = []
        else:
            self.paths = paths
            
    
    def _maybe_minimize_independencies_set(
        self, 
        independencies=None,
        minimal_set=True
    ):
        if minimal_set == False:
            return independencies
        
        min_num_cond_nodes = 10000000
        
        for independence in independencies:
            min_num_cond_nodes = min(
                min_num_cond_nodes, 
                len(independence.conditional_nodes)
            )
        #set_trace()
        
        return [independence for independence in independencies if len(independence.conditional_nodes) == min_num_cond_nodes]
    def implied_conditional_independencies(self, minimal_set=True):
        # make all pssible combinations of middle nodes
        # for each combo, see if paths are blocked
        
        implied_conditional_independencies = []
        
        middle_nodes = self.get_middle_nodes()
        
        if not middle_nodes and self.between_nodes[0].is_not_adjacent_to(self.between_nodes[-1]):
            
            implied_conditional_independencies.append(
                ConditionalIndependence(
                    independent_nodes=[
                        self.between_nodes[0], 
                        self.between_nodes[-1]
                    ]
                )
            )
            
            return implied_conditional_independencies

        
        combinations = itertools.product([True, False], repeat=len(middle_nodes))

        # See which combinations work
        for combo in combinations:
            conditioned_nodes = []

            # Set combo on nodes
            for i in range(len(combo)):
                condition = combo[i]
                middle_nodes[i].set_conditioned(condition)

                if condition == True:
                    conditioned_nodes.append(middle_nodes[i])
            
            
            # choose nodes to condition out of the middle nodes
            if self.blocked():
                
                implied_conditional_independencies.append(
                    ConditionalIndependence(
                        independent_nodes=[self.between_nodes[0], self.between_nodes[-1]],
                        conditional_nodes=conditioned_nodes
                    )
                )
            
            # reset
            for middle_node in middle_nodes:
                middle_node.set_conditioned(False)
                
        
        return self._maybe_minimize_independencies_set(
            independencies=implied_conditional_independencies,
            minimal_set=minimal_set
        )
    
    def blocked(self):
        if not self.paths:
            return True
        
        for path in self.paths:
            if not path.is_blocked():
                return False
            
        return True
    
    def __str__(self):
        return self.__repr__()
        
    def __repr__(self):
        return "Paths: { between_nodes: " + \
            str(self.between_nodes) + \
            ", paths: " + repr(self.paths) + \
            "}"
    
    def print(self):
        for path in self.paths:
            path.print()
        
    def get_middle_nodes(self):
        collection = []
        
        for path in self.paths:
            collection = list(set(collection) | set(path.get_middle_nodes()))
                              
        return collection
    
    @classmethod
    def between(cls, first_node=None, second_node=None):
        collection = []
        
        cls.find_path(
            node=first_node,
            node_to_find=second_node,
            explored_nodes=[first_node],
            collection=collection
        )
        
        return Paths(paths=collection, between_nodes=[first_node, second_node])
        
    @classmethod
    def find_path(
        cls,
        node=None, 
        node_to_find=None, 
        explored_nodes=None,
        collection=None
    ):
        """ """
        if node_to_find == node:
            path = PathGenerator(list(explored_nodes)).perform()
            collection.append(path)
            return
        
        
        parents = node.get_parents()
        children = node.get_children()
        
        
        unexplored_nodes = list(
            (set(parents) | set(children)) - set(explored_nodes)
        )
        
        explored_nodes_copy = list(explored_nodes)
        
        for unexplored_node in unexplored_nodes:
            explored_nodes_copy.append(unexplored_node)
            
            cls.find_path(
                node=unexplored_node, 
                node_to_find=node_to_find, 
                explored_nodes=explored_nodes_copy,
                collection=collection
            )
            
            # prevents showing incorrect parents
            del explored_nodes_copy[-1]

class Nodes(object):
    def __init__(self, nodes=None):
        self.nodes = nodes
        
    def __str__(self):
        return str(self.nodes)
    
    def __repr__(self):
        return "Nodes { nodes: " + str(self.nodes) + "}"
    
    def get_names(self):
        return list(map(lambda x: x.get_name(), self.nodes))

class NodePair(object):
    def __init__(self, nodes=None):
        if nodes == Node:
            self.nodes = []
        else:
            self.nodes = nodes
            
        if len(self.nodes) != 2:
            raise Exception("Need to have two nodes. Given only " + str(len(self.nodes)))
            
    def __str__(self):
        return str(self.nodes)
    
    def __repr__(self):
        return "NodePair: { nodes: " + repr(self.nodes) + "}"
    
    def __eq__(self, other):
        return not (list(set(self.nodes) - set(other.nodes)) ) and not (list(set(other.nodes) - set(self.nodes)) )
    
    def get_paths(self):
        return Paths.between(self.nodes[0], self.nodes[1])
    
    def implied_conditional_independencies(self, minimal_set=True):
        return self.get_paths().implied_conditional_independencies(minimal_set=minimal_set)

class Graph(object):
    def __init__(self, nodes=None):
        if nodes == None:
            self.nodes = []
        else:
            self.nodes = nodes
            
    def __repr__(self):
        return "Graph: { nodes: " + repr(self.nodes) + "}"
            
    def find_paths_between(self, first_node=None, second_node=None):
        return Paths.between(
            first_node, 
            second_node
        )
    
    def uncondition_all_nodes(self):
        for node in self.nodes:
            node.set_condition(False)
            
    def get_pairs(self):
        return list(itertools.product(self.nodes, self.nodes))
    
    def find_implied_conditional_independencies(
        self,
        minimal_set=True
    ):
        # could be moved to nodepairs
        node_pairs = []
        implied_conditional_independencies = []
        
        for node_i, node_j in self.get_pairs():
            node_pair = NodePair(nodes=[node_i, node_j])
            
            if node_i.is_adjacent_to(node_j) or node_i == node_j or node_pair in node_pairs:
                continue
            
            implied_conditional_independencies.append(
                node_pair.implied_conditional_independencies(minimal_set=minimal_set)
            )
            node_pairs.append(node_pair)
        
        return '\n'.join([str(i) for i in list(itertools.chain.from_iterable(implied_conditional_independencies))])

    def print_nodes(self, nodes=None):
        return ' '.join(list(map(lambda x: x.get_name(), nodes)))

class PathGenerator(object):
    """
        Convert adjacent nodes into a simple path. Wraps nodes with PathNodes
    """
    
    def __init__(self, nodes=None):
        if nodes == None:
            self.nodes = []
        else:
            self.nodes = nodes

    def perform(self):
        path_nodes = [PathNode(node) for node in self.nodes]
        
        offset = len(self.nodes) - 1
        
        for i in range(0, offset):
            current_node = self.nodes[i]
            next_node = self.nodes[i+1]
            
            current_node_path_node = path_nodes[i]
            next_node_path_node = path_nodes[i+1]
            
            # Assumes Directed Acyclic Graph

            if next_node in current_node.get_parents():
                current_node_path_node.add_parent(next_node_path_node)
            else:
                current_node_path_node.add_child(next_node_path_node)
            
        return Path(path_nodes=path_nodes)

class PathNode(object):
    """
        Represents a graph node in a path.We want something like this to
        make it easier to see if a node is a collider in the context of 
        a path (which might not be the case in a different path). If it is
        a collider, we're also interested to see if descendants of a collider
        are conditioned (which is more global), so having access to a node
        and its children are useful.
    """
    
    def __init__(self, node=None):
        self.node = node
        
        # might make sense to use null obj.
        self.parents = []
        self.children = []
    
    def __repr__(self):
        return "PathNode: { collider(): " + \
            str(self.is_collider()) + \
            ", is_conditioned(): " + \
            str(self.is_conditioned()) + \
            ", parents: " + \
            str([str(i) for i in self.parents]) + \
            ", children: " + \
            str([str(i) for i in self.children]) + \
            ", node: " + str(self.node) + "}"
    
    def __str__(self):
        return str(self.node)
    
    def get_name(self):
        return self.node.get_name()
    
    def get_children(self):
        return self.children
    
    def get_parents(self):
        return self.parents
    
    def is_adjacent_to(self, other):
        return self.node.is_adjacent_to(other)
    
    def is_not_adjacent_to(self, other):
        return self.is_adjacent_to(other)
    
    def add_child(self, child=None):
        self.children.append(child)
        child.parents.append(self)
        
    def add_parent(self, parent=None):
        self.parents.append(parent)
        parent.children.append(self)
        
    def is_collider(self):
        return len(self.parents) == 2
    
    def is_not_collider(self):
        return not self.is_collider()
    
    def is_conditioned(self):
        return self.node.is_conditioned()
    
    def is_not_conditioned(self):
        return self.node.is_not_conditioned()
    
    def has_conditioned_dependents(self):
        return self.node.has_conditioned_dependents()
    
    def has_no_conditioned_dependents(self):
        return self.node.has_no_conditioned_dependents()
    
    def set_conditioned(self, condition):
        self.node.set_conditioned(condition)

class ConditionalIndependence(object):
    """ 
        Helper class to make it easier to keep list of conditional independencies unique
        in other classes.
    """
    
    def __init__(
        self,
        independent_nodes=None,
        conditional_nodes=None
    ):
        if len(independent_nodes) != 2:
            raise Exception('independent_nodes must have length 2')
        self.independent_nodes = independent_nodes    
        
        if not conditional_nodes:
            self.conditional_nodes = []
        else:
            self.conditional_nodes = conditional_nodes
    
    def unconditionally_independent(self):
        return not self.conditional_nodes
    
    def conditionally_independent(self):
        return not self.unconditionally_independent()
    
    def __eq__(self, other):
        return len(
            set(self.independent_nodes) & set(other.independent_nodes)
        ) == len(self.independent_nodes) and \
        len(
            set(self.conditional_nodes) & set(other.conditional_nodes)
        ) == len(self.conditional_nodes)
        
    def __repr__(self):
        return "ConditionalIndependence: { __str__: " + \
            self.__str__() + \
            ", independent_nodes: " + \
            repr(self.independent_nodes) + \
            ", conditional_nodes: " + \
            repr(self.conditional_nodes) +\
        "}"
    
    def __str__(self):
        if self.unconditionally_independent():
            return self.independent_nodes[0].get_name() + \
                ' _||_ ' + \
                self.independent_nodes[1].get_name() 
        else:
            return self.independent_nodes[0].get_name() + \
                ' _||_ ' + \
                self.independent_nodes[1].get_name() + \
                ' | ' + \
                ', '.join(list(map(lambda x: x.get_name(), self.conditional_nodes)))

class Path(object):
    """ 
        Simple paths from the first path_node to the last path_node
    """ 
    
    def __init__(
        self,
        path_nodes=None
    ):
        
        if len(path_nodes) < 2:
            raise Exception("Need at least two nodes")
        else:
            self.path_nodes = path_nodes
        
    def implied_conditional_independencies(self):
        implied_conditional_independencies = []
        
        middle_nodes = self.get_middle_path_nodes()
        
        if not middle_nodes and self.path_nodes[0].is_not_adjacent_to(self.path_nodes[-1]):
            implied_conditional_independencies.append(
                ConditionalIndependence(
                    independent_nodes=[
                        self.path_nodes[0], 
                        self.path_nodes[-1]
                    ]
                )
            )
            
            return implied_conditional_independencies

        
        combinations = itertools.product([True, False], repeat=len(middle_nodes))

        # See which combinations work
        for combo in combinations:
            conditioned_nodes = []

            for i in range(len(combo)):
                condition = combo[i]
                middle_nodes[i].set_conditioned(condition)

                if condition == True:
                    conditioned_nodes.append(middle_nodes[i])

            # choose nodes to condition out of the middle nodes
            if self.is_blocked():
                implied_conditional_independencies.append(
                    ConditionalIndependence(
                        independent_nodes=[self.path_nodes[0], self.path_nodes[-1]],
                        conditional_nodes=conditioned_nodes
                    )
                )
            
            # reset
            for middle_node in middle_nodes:
                middle_node.set_conditioned(False)
        
        return implied_conditional_independencies
            
    def get_middle_nodes(self):
        if len(self.path_nodes) < 3:
            return []
        
        to_return = [path.node for path in self.path_nodes[1:-1]]

        return to_return
    
    def get_middle_path_nodes(self):
        if len(self.path_nodes) < 3:
            return []
        
        return self.path_nodes[1:-1]
    
    def get_blockers(self):
        blockers = []
        
        #set_trace()
        for middle_node in self.get_middle_nodes():
            if middle_node.is_not_collider() and middle_node.is_conditioned():
                blockers.append(middle_node)
            elif middle_node.is_collider() \
                and middle_node.is_not_conditioned() \
                and middle_node.has_no_conditioned_dependents():
                blockers.append(middle_node)
                    
        return Nodes(blockers)
        
                
    def is_blocked(self):
        # absence of middle_nodes does not mean it is blocked.
        # we want to ensure that the two nodes are not adjacent as well.
        # and we aren't doing an intervention.
        
        if not self.get_middle_nodes():
            return True
        
        # Assumes there are at least three nodes in the path?
        for middle_node in self.get_middle_path_nodes():
            if middle_node.is_not_collider() and middle_node.is_conditioned():
                return True
            elif middle_node.is_collider() \
                and middle_node.is_not_conditioned() \
                and middle_node.has_no_conditioned_dependents():
                return True
                
        return False
    
    def __repr__(self):
        return "Path: " + \
            "{ __str__: " + self.__str__() + \
            ", is_blocked: " + \
            str(self.is_blocked()) + \
            ", blockers: " + str(self.get_blockers().get_names()) + \
        " }"
    
    def __str__(self):
        return self._readable()
        
    def _readable(self):
        collection = []
        
        if len(self.path_nodes) == 1:
            return self.path_nodes.get_name(0)
        
        for i in range(0, len(self.path_nodes) - 1):
            current_path_node = self.path_nodes[i]
            next_path_node = self.path_nodes[i+1]
            
            collection.append(current_path_node.get_name())
            collection.append(self.print_arrow(
                current_path_node=current_path_node,
                next_path_node=next_path_node
            ))
            
        collection.append(self.path_nodes[-1].get_name())
        return ' '.join(collection)
    
            

    def print_arrow(self, current_path_node=None, next_path_node=None):
        if current_path_node in next_path_node.get_children():
            return '<-'
        else:
            return '->'

if __name__ == "__main__":
    a = Node(name='A')
    b = Node(name='B')
    c = Node(name='C')
    d = Node(name='D')

    a.add_child(child=b)
    b.add_child(child=c)
    a.add_child(child=d)
    d.add_child(child=c)

    # might make sense for the graph to take in a string to build the graph
    graph = Graph(
        nodes=[a,b,c,d]
    )
    paths = graph.find_paths_between(a, c)

    graph.find_implied_conditional_independencies()