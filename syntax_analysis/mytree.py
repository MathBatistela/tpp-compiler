from anytree import Node, RenderTree, AsciiStyle, PreOrderIter
from anytree.exporter import DotExporter
from anytree import NodeMixin, RenderTree


node_sequence = 0


class MyNode(NodeMixin):
    def __init__(
        self, name, parent=None, id=None, type=None, label=None, children=None, line=None, scope="global"
    ):
        super(MyNode, self).__init__()
        global node_sequence

        if id:
            self.id = id
        else:
            self.id = str(node_sequence) + ": " + str(name)

        self.label = name

        self.scope = scope

        self.line = line

        self.name = name
        node_sequence = node_sequence + 1
        self.type = type
        self.parent = parent
        if children:
            self.children = children

    @staticmethod
    def nodenamefunc(node):
        return "%s" % (node.name)

    @staticmethod
    def nodeattrfunc(node):
        return "%s" % (node.name)

    @staticmethod
    def edgeattrfunc(node, child):
        return ""

    @staticmethod
    def edgetypefunc(node, child):
        return "--"

    def child(self,count=0,name=None):
        if name:
            try:
                return next(filter(lambda node: node.name == name, self.children))
            except:
                return None
        else:
            if self.children:
                temp = list(self.children)
                try:
                    return temp[count]
                except IndexError:
                    return None

    def __str__(self):
        return f"*{self.name}*"
