from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt


class TreeNode(object):
    def __init__(self, parent, row):
        self.parent = parent
        self.row = row
        self.subnodes = self._getChildren()

    def _getChildren(self):
        raise NotImplementedError()


class TreeModel(QAbstractItemModel):
    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.rootNodes = self._getRootNodes()

    def _getRootNodes(self):
        raise NotImplementedError()

    def index(self, row, column, parent):
        if not parent.isValid():
            return self.createIndex(row, column, self.rootNodes[row])
        parentNode = parent.internalPointer()
        return self.createIndex(row, column, parentNode.subnodes[row])

    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        return self.rootNodes[0]

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        node = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        else:
            return self.createIndex(node.parent.row, 0, node.parent)

    def reset(self):
        self.rootNodes = self._getRootNodes()
        QAbstractItemModel.reset(self)

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.rootNodes)
        node = parent.internalPointer()
        return len(node.subnodes)

    def removeRows(self, position=0, count=1,  parent=QModelIndex()):
        node = self.nodeFromIndex(parent)
        self.beginRemoveRows(parent, position, position + count - 1)
        node.subnodes.pop(position)
        self.endRemoveRows()
        return True


class NamedElement(object): # your internal structure
    def __init__(self, name, msgid, subelements):
        self.name = name
        self.msgid = msgid
        self.subelements = subelements


class NamedNode(TreeNode):
    def __init__(self, ref, parent, row):
        self.ref = ref
        TreeNode.__init__(self, parent, row)

    def _getChildren(self):
        return [NamedNode(elem, self, index)
            for index, elem in enumerate(self.ref.subelements)]


class NamesModel(TreeModel):
    def __init__(self, rootElements):
        self.rootElements = rootElements
        TreeModel.__init__(self)

    def _getRootNodes(self):
        return [NamedNode(elem, None, index)
            for index, elem in enumerate(self.rootElements)]

    def columnCount(self, parent=None):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == Qt.DisplayRole and index.column() == 0:
            return node.ref.name

        if role == Qt.DisplayRole and index.column() == 1:
            return node.ref.msgid
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole \
            and section == 0:
            return 'Queues'

        if orientation == Qt.Horizontal and role == Qt.DisplayRole \
            and section == 1:
            return 'Identifier'
        return None

