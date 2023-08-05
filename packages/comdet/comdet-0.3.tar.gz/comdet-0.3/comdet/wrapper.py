class Node:
    sno = 0
    node_name = ""
    elems = []
    def __init__(self):
        self.elems = []

    def add_elem(self, elem):
        self.elems.append(elem)

    def no_of_elems(self):
        return len(elems)

    def display_elems(self):
        for e in self.elems:
            print '\t\t%s' % e
        #print '\n'.join(self.elem) 
 
class Pool:
    nodes = {}
    def __init__(self):
        self.nodes = {}

    def add_node(self, node):
        n = Node()
        n.node_name = node
        self.nodes[node] = n
        return n
    
    def get_node(self, node):
        return self.nodes[node] if node in self.nodes else None
 
    def no_of_nodes(self):
        return len(self.nodes.keys())
    def display_node(self):
        for n in self.nodes.values(): 
            print n.node_name
            n.display_elems()

'''
p1 = Pool()

n1 = p1.add_node('A')
n1.add_elem('1')
n1.add_elem('2')
n1.add_elem('3')

n2 = p1.add_node('B')
n2.add_elem('1')
n2.add_elem('2')

p1.display_node() 
'''
