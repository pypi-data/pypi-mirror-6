"""
.. module:: client
   :platform: Unix
   :synopsis: Wrapper functions for ipython.parallel connections and queries.

.. moduleauthor:: Nathan Faggian <nathan.faggian@gmail.com>

"""

import collections

from IPython import parallel


def simple_job_query(conn):
    """
    Queries the hub to request job information.

    :param conn: IPython.parallel.Client, client connection.
    :return: OrderedDict, dictionary of job data.
    """

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


def form_client_connection(**kwargs):
    """
    Wrapper for IPython client connection.

    :return: IPython.parallel.Client, client connection.
    """

    return parallel.Client(**kwargs)
