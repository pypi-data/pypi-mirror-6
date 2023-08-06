"""
.. module:: watcher
   :platform: Unix
   :synopsis: PyQt4 IPython cluster monitor.

.. moduleauthor:: Nathan Faggian <nathan.faggian@gmail.com>

"""

import time
import itertools
import sys

from functools import partial
from PyQt4 import QtGui, QtCore, Qt

from ipcluster_tools.tree_model import NamesModel, NamedElement
from ipcluster_tools import client, progressbar


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


def gui_watcher():
    """
    Polls job information to update a tree view.
    """

    # Connect to the server and retrieve status.
    conn = client.form_client_connection()
    job_data = client.simple_job_query(conn)

    # Form a callback for tree updates.
    update_callback = partial(client.simple_job_query, conn)

    app = QtGui.QApplication(sys.argv)

    # Form a model and view.
    data = tree_from_jobs(job_data)
    model = NamesModel(data)

    view = TreeModelView(update_callback)
    view.setModel(model)
    view.setWindowTitle("IPcluster status")
    view.show()

    sys.exit(app.exec_())


def waiting_progress(delay=0.5, **kwargs):
    """
    Polls the waiting queue and updates progress bar.
    """

    # Connect to the server and retrieve status.
    conn = client.form_client_connection(**kwargs)

    job_data = client.simple_job_query(conn)
    job_count = len(job_data['Waiting'])

    if not job_count:
        return

    progress = progressbar.progress_bar(job_count)

    # Watch the state of the waiting queue.
    while True:
        # Poll every half second.
        time.sleep(delay)
        job_data = client.simple_job_query(conn)
        job_count = len(job_data['Waiting'])
        progress.update(job_count)

        # Stop reporting when it reduces to zero.
        if not job_count:
            return

if __name__ == '__main__':

    gui_watcher()
