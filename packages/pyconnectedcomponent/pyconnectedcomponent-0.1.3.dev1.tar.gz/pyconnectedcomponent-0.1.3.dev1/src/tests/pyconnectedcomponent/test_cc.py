
from pyconnectedcomponent import Node, connected_components

def test_cc():

    # The first group, let's make a tree.
    a = Node("a")
    b = Node("b")
    c = Node("c")
    d = Node("d")
    e = Node("e")
    f = Node("f")
    a.add_link(b)    #      a
    a.add_link(c)    #     / \
    b.add_link(d)    #    b   c
    c.add_link(e)    #   /   / \
    c.add_link(f)    #  d   e   f

    # The second group, let's leave a single, isolated node.
    g = Node("g")

    # The third group, let's make a cycle.
    h = Node("h")
    i = Node("i")
    j = Node("j")
    k = Node("k")
    h.add_link(i)    #    h----i
    i.add_link(j)    #    |    |
    j.add_link(k)    #    |    |
    k.add_link(h)    #    k----j

    # The third group, let's make a clique.
    l = Node("l")
    m = Node("m")
    n = Node("n")
    o = Node("o")
    clique = [l, m, n, o]
    from itertools import combinations
    for n1, n2 in combinations(clique, 2):
        n1.add_link(n2)
        n2.add_link(n1)

    # Put all the nodes together in one big set.
    nodes = {a, b, c, d, e, f, g, h, i, j, k, l, m, n, o}

    # Find all the connected components.
    number = 1
    for components in connected_components(nodes):
        names = sorted(node.name for node in components)
        names = ", ".join(names)
        print "Group #%i: %s" % (number, names)
        number += 1

    # You should now see the following output:
    # Group #1: l, m, n, o
    # Group #2: h, i, j, k
    # Group #3: a, b, c, d, e, f
    # Group #4: g

    assert len(connected_components(nodes)) == 4
    assert set(map(len, connected_components(nodes))) == set([4,4,1,6])
