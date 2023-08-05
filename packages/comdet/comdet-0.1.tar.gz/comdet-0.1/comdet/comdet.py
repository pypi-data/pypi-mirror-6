import os
import wrapper
import community

# inputfile name and no of passes
def detect(filename, nop = -1, debug = False):
     fileinput = open('input', 'r')
     lines = fileinput.readlines()
     p1 = wrapper.Pool()
     for line in lines:
        line = line.strip()
        if not line:
           continue
        split = line.split(' ')
        n1 = p1.get_node(split[0])
        if not n1:
            n1 = p1.add_node(split[0])
        n1.add_elem(split[1])
     if not os.path.exists('tmp'):
        os.mkdir('tmp')
     os.chdir('tmp')
     com_t = community.community()
     result = com_t.start(p1, nop, debug)
     return result
