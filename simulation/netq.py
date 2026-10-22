import re,sys,collections
txt=open(sys.argv[1],encoding="utf-8").read()
nets=collections.OrderedDict()
for m in re.finditer(r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]*)"\)(.*?)(?=\(net\s+\(code|\Z)', txt, re.S):
    name=m.group(1); body=m.group(2)
    nodes=re.findall(r'\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)', body)
    nets[name]=nodes
want=sys.argv[2].split(",")
for n,nodes in nets.items():
    refs=set(r for r,_ in nodes)
    if refs & set(want):
        hit=[ "%s.%s"%(r,p) for r,p in nodes ]
        print("%-22s : %s" % (n, "  ".join(hit)))
