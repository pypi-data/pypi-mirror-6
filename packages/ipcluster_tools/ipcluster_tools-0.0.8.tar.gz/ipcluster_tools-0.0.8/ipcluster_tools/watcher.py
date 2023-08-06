import collections
import itertools
import sys

from IPython import parallel
from functools import partial

from PyQt4 import QtGui, QtCore, Qt
from ipcluster_tools.tree_model import NamesModel, NamedElement


def processed_jobs(conn):
    data = conn.queue_status(verbose=True)
    queue, completed, tasks = set([]), set([]), set([])
    queue |= set(data['unassigned'])

    for d, v in data.items():
        if d == 'unassigned':
            continue
        queue |= set(v['queue'])
        completed |= set(v['completed'])
        tasks |= set(v['tasks'])

    return collections.OrderedDict((
        ('Processing', tasks),
        ('Waiting', queue),
        ('Completed', completed)))


def tree_from_jobs(job_data):
    def form_children(data):
        return [NamedElement('-', x, []) for x in data]
    return [NamedElement(x, '', form_children(job_data[x])) for x in job_data.keys()]


def equal_tree(treeA, treeB):
    for rootNodeA, rootNodeB in zip(treeA, treeB):
        if set(x.msgid for x in rootNodeA.subelements) != set(x.msgid for x in rootNodeB.subelements):
            return False
    return True


class TreeModelView(QtGui.QTreeView):

    def __init__(self, updateFn, parent=None):
        super(TreeModelView, self).__init__(parent)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateModel)
        self.timer.start(1000)
        self.updateFn = updateFn
        self.setStyleSheet('font-size: 12pt; font-family: Courier;')

    def updateModel(self):

        data = self.updateFn()
        data_tree = tree_from_jobs(data)

        if equal_tree(self.model().rootElements, data_tree):
            return

        # Keep track of expanded state
        root_indices = [self.model().index(x, 0, QtCore.QModelIndex()) for x in
                            range(len(self.model().rootNodes))]
        roots_expanded = [self.isExpanded(x) for x in root_indices]

        # Update model data
        self.model().rootElements = tree_from_jobs(data)
        self.model().reset()

        # Restore expanded state
        root_indices = [self.model().index(x, 0, QtCore.QModelIndex()) for x in
                            range(len(self.model().rootNodes))]
        for expand, index in zip(roots_expanded, root_indices):
            self.setExpanded(index, expand)


def main():
    """
    Watch the connection.
    """

    conn = parallel.Client()

    update_callback = partial(processed_jobs, conn)

    job_data = processed_jobs(conn)
    data = tree_from_jobs(job_data)

    app = QtGui.QApplication(sys.argv)

    model = NamesModel(data)

    treeView = TreeModelView(update_callback)
    treeView.setModel(model)
    treeView.setWindowTitle("IPcluster status")
    treeView.show()

    sys.exit(app.exec_())


if __name__ == '__main__':

    main()
