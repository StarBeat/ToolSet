#coding:utf-8
import re
import sys
import os
import time as ti
import matplotlib.pyplot as plt
import networkx as nx
import time as ti

def ReplaceEndCRLF(str):
    return str.replace(" ", '').replace('\r', '').replace('\n', '')
        
class ClassesParser(object):
    #cpp
    patt_cpp_extend = re.compile(r'class(\s+[\w_\d]+\s+)?(\s*[\w_][\w_\d<,\s]+>?\s*):\s*((public|protected|private)\s+[\w_\d<,\s]+>?\s*)((\s*,\s*(public|protected|private)?(\s+[\w_\d<,\s]+>?\s*))*)?')
    patt_cpp_nobase = re.compile(r'class(\s+[\w_\d]+\s+)?(\s*[\w_][\w_\d<,\s]+>?\s*)[^:^,]{', flags = re.M)
    getbase_from_res = re.compile(r'(public|protected|private)(\s+[\w_\d]+[^<]\s*|\s+[\w_\d<,\s]+>\s*)')
    #c#
    patt_cs_extend = re.compile(r'')
    patt_cs_nobase = re.compile(r'')

    #parse resault
    nobaseclass_set = set()
    classes_extend_map = dict()
    visitied = set()

    class ExtendPair():
        def __init__(self, name, ext, file_name):
            self.name = name
            self.ext = ext
            self.file_name = file_name

    def __init__(self):
        super(ClassesParser, self).__init__()
        self.files = []
        self.parsed = False

    def RecursiveTraversal(self, path):
        filels = os.listdir(path)
        for fi in filels:
            if os.path.isdir(fi):
                self.RecursiveTraversal(fi)
            else:
                self.files.append(os.path.join(path, f))

    def Walk(self, path):
        for fpath, dirs, fs in os.walk(path):
            for f in fs:
                self.files.append(os.path.join(fpath, f))

    def Parse(self):
        if self.parsed:
            return
        if len(self.files) == 0: 
            print("Err can not find files.")
            return
        for f in self.files:
            if os.path.getsize(f) == 0:
                continue
            if f.endswith(".h") or f.endswith(".hpp") or f.endswith(".cpp") or f.endswith(".cxx"):
                with open(f, 'rb') as f:
                    #print(chardet.detect(f.read())['encoding'])
                    try:
                        str = f.read().decode(encoding = "UTF-8", errors = 'ignore')
                    except Exception as e:
                        str = f.read().decode(encoding = "GBK", errors = 'ignore')
                    else:
                        pass
                    tempbase = self.patt_cpp_nobase.findall(str)
                    tempclasses = self.patt_cpp_extend.findall(str)
                    for x in tempbase:
                        self.nobaseclass_set.add(ReplaceEndCRLF(x[1]))
                    for x in tempclasses:
                        tmpbase1 = self.getbase_from_res.findall(x[2])
                        tmpbase2 = self.getbase_from_res.findall(x[4])
                        basels = []
                        if len(tmpbase1) != 0:
                            basels.append(ClassesParser.ExtendPair(ReplaceEndCRLF(tmpbase1[0][1]), ReplaceEndCRLF(tmpbase1[0][0]), ReplaceEndCRLF(f.name)))
                        for z in tmpbase2:
                            basels.append(ClassesParser.ExtendPair(ReplaceEndCRLF(z[1]), ReplaceEndCRLF(z[0]), ReplaceEndCRLF(f.name)))
                        self.classes_extend_map[ReplaceEndCRLF(x[1])] = basels
            elif f.endswith(".cs"):
                pass

        self.parsed = True

    def CreateBranch(self, key, graphs):
        if key in self.nobaseclass_set:
            print("class " + key + " has not base class")
            return
        print("!--------------")
        print(key)
        if key in self.visitied:
            return
        extls = []
        if not self.classes_extend_map.has_key(key):
            return
        for x in self.classes_extend_map[key]:
            print(x.ext + " " + x.name)
            graphs.add_edge(key, x.name, weight = 1 if x.ext == 'public' else 0.5 if x.ext == 'protected' else 0)
            extls.append(x.name)
            self.visitied.add(key)
        print("--------------!")
        for x in extls:
            self.CreateBranch(x, graphs)

    def Treed(self, graphs):
        for k, v in self.classes_extend_map.items():
            self.CreateBranch(k, graphs)

    def OneTree(self, graphs, key):
        self.CreateBranch(key, graphs)

    def CreateAllNetMap(self):
        graphs = nx.generators.directed.random_k_out_graph(0, 3, 0.5)
        self.Parse()
        #print(self.nobaseclass_set)
        self.Treed(graphs)
        self.CreatePic(graphs)
    
    def CreateNetMap(self):
        patt = re.compile(r'[\w_\d]+[^<]?')
        self.Parse()
        for k, v in self.classes_extend_map.items():
            graphs = nx.generators.directed.random_k_out_graph(0, 3, 0.5)
            self.OneTree(graphs, k)
            print( k)
            print( patt.findall(k))
            name = patt.findall(k)[0] + ".eps"
            self.CreatePic(graphs, name)

    def CreatePic(self, graphs, name = "pic.eps"):
        epublic = [(k, v) for (k, v, x) in graphs.edges(data = True) if x['weight'] == 1]
        eprotected = [(k, v) for (k, v, x) in graphs.edges(data = True) if x['weight'] == 0.5]
        eprivate = [(k, v) for (k, v, x) in graphs.edges(data = True) if x['weight'] == 0]
        enums = (len(epublic) + len(eprotected) + len(eprivate)) * 2
        pos = nx.random_layout(graphs)

        plt.tight_layout()
        fig = plt.gcf()
        if enums < 50:
            #fig.set_size_inches(10, 10)
            nodesize = 300
            edgesize = 3
            arrowsize1 = 0.2
            arrowsize2 = 0.1
            font_size = 12
        elif enums < 100:
            fig.set_size_inches(10, 10)
            nodesize = 200
            edgesize = 1
            arrowsize1 = 0.2
            arrowsize2 = 0.1
            font_size = 5
        else:
            fig.set_size_inches(100, 100)
            nodesize = 20
            edgesize = 0.01
            arrowsize1 = 0.002
            arrowsize2 = 0.001
            font_size = 0.05
        nodes = nx.draw_networkx_nodes(graphs, pos, node_size = nodesize)

        nx.draw_networkx_edges(graphs, pos, node_size = nodesize, edgelist = epublic, width = edgesize, alpha = 0.5, edge_color = 'green')
        nx.draw_networkx_edges(graphs, pos, node_size = nodesize, edgelist = eprotected, width = edgesize, alpha = 0.5, edge_color = 'blue')
        nx.draw_networkx_edges(graphs, pos, node_size = nodesize, edgelist = eprivate, width = edgesize, alpha = 0.5, edge_color = 'red')
        nx.draw_networkx_edges(graphs, pos, node_size = nodesize, width = arrowsize1, alpha = 0.1, 
            edge_color = 'yellow', arrowstyle = "->", arrowsize = arrowsize2, edge_cmap = plt.cm.Blues,style = 'dashed')
        #labels
        nx.draw_networkx_labels(graphs, pos, font_size = font_size, font_family = "sans-serif")

        plt.axis('off')
        fig.savefig("./map/" + name, format = 'eps', dpi = 100000)
        #plt.show()


if __name__ == '__main__':
    sys.setrecursionlimit(1000000)
    cp = ClassesParser()
    exe_full_path = sys.argv[0]
    exe_folder_path = exe_full_path[0: exe_full_path.rfind("\\")]
    if len(sys.argv) > 1:
        cp.Walk(sys.argv[1])
    else:
        cp.Walk(exe_folder_path)
    print("file num:", len(cp.files).__str__())
    cp.CreateNetMap()
