import os
import sys
import shutil
import struct
import wrapper
#from sets import Set


class KeyError(Exception):
    def __init__(self, arg):
        self.msg = arg

class modularity:
    c_inner = 0.0     # sum of link of weight inside Community
    inci_c = 0.0      # sum of link of weight incident to nodes in C
    inci_i = 0.0      # sum of link of weight incident to node i
    i_inci_c = 0.0    # sum of link of weight from i to node in community
    total = 0.0       # sum of link of weight of all nodes in the network
    def display(self):
        print "c_inner   %f" % self.c_inner
        print "inci_c    %f" % self.inci_c
        print "inci_i    %f" % self.inci_i
        print "i_inci_c  %f" % self.i_inci_c
        print "total     %f" % self.total
    
    def calculate(self):
        try:
            tmp1 = (self.c_inner + self.i_inci_c + self.i_inci_c)/(self.total + self.total)
            tmp1 = tmp1 - ((self.inci_c + self.inci_i)/(self.total + self.total)) * ((self.inci_c + self.inci_i)/(self.total + self.total))
            tmp2 = (self.c_inner)/(self.total + self.total)
            tmp2 = tmp2 - (self.inci_c / (self.total + self.total))*(self.inci_c / (self.total + self.total))
            tmp2 = tmp2 - (self.inci_i / (self.total + self.total))*(self.inci_i / (self.total+self.total))
            tmp1=tmp1-tmp2;
            return tmp1
        except ZeroDivisionError:
            return 0 

class community:
    nop = -1
    debug = False
    iter = -1
    phase = -1

    def error_process(flg, msg):
         print "Error %s" % msg

    def debugger(self, msg):
        if self.debug:
            print "#Pass %d# Phase %d# %s" % (self.iter, self.phase, msg)

    def getint(self, str):
        return int(str.strip())

    def format(self, var):
        var = str(var)
        var = var.strip() + '\n'
        return var

    def getcommunity(self, iter, prevnodeindex = 0):
        try:
            if (iter <= 0): return 
            communityFile = "PASS%d" % iter
            fr = open(communityFile, 'r')
            lines = fr.readlines()
            noc = self.getint(lines[0])
            line_pos = 1
            # For each community
            result = []
            nodeindex = 0
            # For only one community result would be appended, i.e community whose index is same to the prev community node index 
            for cn in range(noc):  # community number
                 non = self.getint(lines[line_pos])
                 line_pos += 1 
                 # For each node
                 for j in range(non):
                     node_name = lines[line_pos].strip()
                     line_pos += 1
                     if  cn == prevnodeindex and iter == 1:  # if community number is same as prev community node index and iteration is 1
                         result.append(node_name)
                     elif cn == prevnodeindex:               # Recurse for next pass with current node index and append the result to final results
                         out = self.getcommunity(iter-1, nodeindex)
                         if not out: continue
                         result.append(out)
                     nodeindex += 1
            return result
        except Exception as e:
             self.error_process("normal", traceback.format_exc())           

    # Determines nodei modularity
    def find_modularity(self, communityFile, nodei, iter):
        mod = modularity()
        fc = open(communityFile, 'r')
        lines_read = fc.readlines()
        total = self.getint(lines_read[0])
        nodes_communityi = set()
        rp = 1
        flg_break = False
        for i in range(total):
            comm_total = self.getint(lines_read[rp])
            rp += 1
            rp_back = rp
            for j in range(comm_total):
                node = lines_read[rp].strip()
                rp += 1 
                if nodei == node:   # We are in nodei community now
                    rp = rp_back    # Point the read pointer at the 1st element in community
                    for k in range(comm_total):
                        node = lines_read[rp].strip()
                        rp += 1
                        nodes_communityi.add(node)
                    Flag_break = True 
                    break
            if flg_break: break
        nodes_communityi   = list(nodes_communityi)

        rp = 1
        for i in range(total):
            comm_total = self.getint(lines_read[rp])
            rp += 1
            for j in range(comm_total):
                 node = lines_read[rp].strip()
                 rp += 1
                 nodefile = 'PASS%d_%s' %(iter, node)
                 links = open(nodefile).readlines()
                 for link in links:
                     link = link.strip()
                     if nodei == node and link in nodes_communityi:  # If node is nodei and the link in file of nodei is a node from its community
                         mod.i_inci_c += 1
                         mod.c_inner += 1     #'''BUG IN ORIGINAL''''
                     elif link in nodes_communityi:
                         if node in nodes_communityi:  # If both node and link are from nodei community.
                             mod.c_inner += 1
                         else:                         # If node dont belong to community but link does.
                             mod.inci_c += 1
                     if link == nodei:                 # if link is nodei 
                         mod.inci_i += 1
                     mod.total += 1
        return mod.calculate()
             
    # Create a temp pass file by migrating nodei to nodej community.
    # Return -> True if node migrated, False if both nodes are in same community
    def create_tmp_community(self, communityFile, nodei, nodej):
        self.debugger("migrating %s -> %s" % (nodei, nodej))
        communityFile_tmp = communityFile + '_tmp' 
        foc = open(communityFile, 'r')
        ftc = open(communityFile_tmp, 'w')
        lines_read = foc.readlines()
        total = lines_read[0]
        lines_write = []
        lines_write.append(total)
        total = self.getint(total)
        rp = 1  # Read position
        wp = 1  # write position
        for i in range(total):
             comm_total = self.getint(lines_read[rp])
             rp += 1
             flag = 0
             buffer = []
             for j in range(comm_total):
                 node = lines_read[rp].strip()
                 rp += 1
                 buffer.append(node)
                 #print 'nodei %s \t node %s' %(nodei, node)
                 if nodei == node:  # nodei found
                     flag = flag + 1
                 elif nodej == node:
                     flag = flag + 2 # nodej found
             if flag == 1:  # nodei found
                 comm_total -= 1   #Decreasing no of nodes in community, as nodei is migrating
                 if comm_total == 0:
                     lines_write[0] = total - 1   # If no nodes in community, total number of  community will be decreased by 1
                     continue
                 lines_write.append(comm_total)
                 wp += 1
                 # Since nodei is removed from this community, add remaining element of community to except nodei to it.
                 for node in buffer:
                     node = node.strip()
                     if node == nodei: continue 
                     lines_write.append(node)
                     wp += 1 
             elif flag == 2: #nodej found
                 comm_total += 1  #Increasing no of nodes, as nodei is comming to this community
                 lines_write.append(comm_total)
                 wp += 1
                 for node in buffer:
                     lines_write.append(node)
                     wp += 1 
                 lines_write.append(nodei)  #nodei is now added to this community
                 wp += 1
             elif flag == 3:  # if both nodei and nodej are in same community then no need to transfer
                  ftc.close() # no need of temprary file, it is rejected
                  return False 
             else:
                 lines_write.append(comm_total)
                 wp += 1
                 for node in buffer:
                     lines_write.append(node)
                     wp += 1 
        for line in lines_write:
            ftc.write(self.format(line))
        foc.close()
        ftc.close() 
        return True

    # This migrate a node to its neighbours community and check in which migration it gain max modularity.
    # It max maodularity > 0 new Pass file is created else remain unaltered
    # Return Value -> True if migrated, False if not migrated
    def migrate_node(self, communityFile, nodei, iter):
        communityFile_tmp = '%s_tmp' % communityFile
        nodei_file = 'PASS%d_%s' %(iter, nodei)
        neighbours_nodei = open(nodei_file).readlines()   # Reading nodei file for its neighbours
        max_modularity = 0.0
        node_max= '';
        for nodej in neighbours_nodei:
            nodej = nodej.strip()
            if not self.create_tmp_community(communityFile, nodei, nodej):        # Create a tmp file for new community
                continue;
            modularity1 = self.find_modularity(communityFile, nodei, iter);     # Get modularity of nodei
            modularity2 = self.find_modularity(communityFile_tmp, nodei, iter); # Get modularity of nodei
            modularity = modularity2 - modularity1
            self.debugger('\tChange Modularity %f' % modularity)
            if (modularity > max_modularity):
                max_modularity = modularity
                node_max = nodej
        self.debugger('\tmax : %f' % max_modularity)
        if (max_modularity < 0.0000001):
            return False
        self.debugger('\tFinal Migration: %s -> %s' % (nodei ,node_max))
        #print communityFile_tmp
        self.create_tmp_community(communityFile, nodei, node_max);
        os.rename(communityFile_tmp, communityFile)
        return True

    # Create Main file for pass
    def createpassfile(self, pool1, iter):
        nec = pool1.no_of_nodes()  # No of elements in community
        communityFile = 'PASS%d' % iter 
        fw = open(communityFile, 'w')
        fw.write("%d\n" % nec)  # Total no of community
        for key in pool1.nodes.keys():
            node = pool1.nodes[key]
            fw.write("1\n")  # Total no of nodes in each community
            fw.write("%s\n" % node.node_name)
        fw.close()
        
    # Create initail tmp directory structure.
    def initial_onetimepass(self, pool1):
        nec = pool1.no_of_nodes()  # No of elements in community
        communityFile = 'PASS1' 

        '''
        keyset = set(pool1.nodes.keys())
        valueset = set()
        for node in pool1.nodes.values():
            for elem in node.elems:
                valueset.add(elem)
        print keyset
        print valueset  
        print valueset-keyset   # ELEMENTS which are not included in final tally -> needed to be fixed
        '''
        fw = open(communityFile, 'w')   
        fw.write("%d\n" % nec)  # Total no of community
        for key in pool1.nodes.keys():
            # Writing to new community file
            node = pool1.nodes[key]
            fw.write("1\n")  # Total no of nodes in each community
            fw.write("%s\n" % node.node_name)
            fn = open('PASS1_%s' % node.node_name, 'w')
            for elem in node.elems:
               fn.write('%s\n' % elem)
            fn.close()
        fw.close()
        self.phase1(iter=1, nep = -1) 

    def getposition(self, communityno):
        communityFile = 'PASS%d' % self.iter
        fr = open(communityFile, 'r')
        lines = fr.readlines()
        noc = self.getint(lines[0])
        line_pos = 1
        # For each community
        for i in range(noc):
            if (i == communityno):
                return line_pos
            non = self.getint(lines[line_pos])
            line_pos += 1 
            # For each node
            for j in range(non):
                node_name = lines[line_pos].strip()
                line_pos += 1

    # This phase detects which community are close, grouping together nodes into 1 community
    def phase1(self, iter, nep):
        self.iter = iter
        self.phase = 1
        if (self.nop > 0 and self.nop == iter - 1):  # return if no of passes exceeds the allowed limit
            self.getcommunity(self.nop)
            return
        communityFile = 'PASS%d' % iter
        fr = open(communityFile, 'r')
        lines = fr.readlines()
        nec = self.getint(lines[0])                  # no of community in current Pass
        if ( nep > 0 and nec == nep) :               # return if no of community in previous pass is same as for this pass
            self.getcommunity(iter - 1)
            return
        flag = 1
        # Every node is migrated to other community many times till no more migration become possible
        while flag:
            flag = 0 
            noc = self.getint(lines[0])
            line_pos = 1
            # For each community
            cuts = 0
            for i in range(noc):
                non = self.getint(lines[line_pos])
                line_pos += 1 
                # For each node
                for j in range(non):
                    node_name = lines[line_pos].strip()
                    line_pos += 1
                    # Check if node migrated
                    if self.migrate_node(communityFile, node_name, iter):
                        # If node is migrated we need to restart the process with while loop 
                        lines = open(communityFile, 'r').readlines()
                        noc = self.getint(lines[0])
                        line_pos = self.getposition(i - cuts) # get the position of ith commmunity
                        #self.debugger(open(communityFile).readlines())
                        cuts += 1
                        flag = 1
                        break
                #if flag: break   # breaks the 2nd for loop
        self.phase2(iter, nec)

    # This Phase build new community by grouping previous phase nodes into 1 community
    def phase2(self, iter, nec):
        self.phase = 2
        pool2 = wrapper.Pool()
        communityFile = 'PASS%d' % iter # Pass file for given iteration
        fc = open(communityFile, 'r')
        lines_read = fc.readlines()
        total = self.getint(lines_read[0])
        rp = 1
        local = 0
        dict_node2community = {}
        for i in range(total):
            comm_total = self.getint(lines_read[rp])
            rp += 1
            name_node = 'node%d' % local
            local += 1
            pool2.add_node(name_node)
            for j in range(comm_total):
                node = lines_read[rp].strip()
                rp += 1
                dict_node2community[node] = name_node
        #self.debugger("Nodes for next pass " %s ", ".join(dict_node2community))

        if not len(dict_node2community.keys()): return
        for key in dict_node2community:
            nodefile = 'PASS%d_%s' % (iter + 1, dict_node2community[key])
            fnp2 = open(nodefile, 'a')
            key = 'PASS%d_%s' % (iter, key)  # node files got given pass
            if os.path.exists(key):            
                fnp1 = open(key, 'r')
                for line in fnp1.readlines():
                    line = line.strip()
                    if not line in dict_node2community: continue
                    newlink = dict_node2community[line]
                    self.debugger('writing %s' % newlink)
                    if not newlink:
                        raise KeyError("%s not found in dict_node2community file for Phase2 iter %d" % (newlink, iter))
                    fnp2.write('%s\n' % newlink)
                fnp1.close()
            fnp2.close()
        iter = iter + 1  
        self.createpassfile(pool2, iter) 
        self.phase1(iter, nec)
 
    def start(self, pool1, nop, debug):
        self.nop = nop
        self.debug = debug
        self.debugger("No of Passes %d" % self.nop)
        self.initial_onetimepass(pool1)
        return self.getcommunity(self.iter) 
