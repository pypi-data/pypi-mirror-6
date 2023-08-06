from nose.plugins.attrib import attr
from nose.tools import nottest

from rexpro.tests.base import BaseRexProTestCase, multi_graph
from rexpro._compat import print_

import gevent


def slow_start_simulation(ref):
    gevent.sleep(1)
    conn = ref.get_connection()
    return conn


def spawn_slow_network_and_query_slow_response(ref, script, sleep_time, data):
    conn = slow_start_simulation(ref)
    return conn.execute(script=script, params={'sleep_length': sleep_time, 'data': data})


@attr('unit', 'concurrency')
class TestConcurrency(BaseRexProTestCase):

    NUM_ITER = 10
    SLOW_NETWORK_QUERY = """def test_slow_query(sleep_length, data) {
    sleep sleep_length
    return data
    }
    """

    def test_start_many_connections(self):
        """ Test starting up many connections """

        gevent.joinall([gevent.spawn(self.get_connection) for _ in xrange(self.NUM_ITER)], timeout=3)

    def test_start_many_slow_connections(self):
        """ Test starting many slow connections """

        gevent.joinall([gevent.spawn(slow_start_simulation, self) for _ in xrange(self.NUM_ITER)], timeout=3)

    def test_many_network_calls(self):
        """ Test known responses on a network that should be slow, we should get them all asynchronously """

        threads = []

        for i in xrange(self.NUM_ITER):
            threads.append(gevent.spawn(spawn_slow_network_and_query_slow_response,
                                        self,
                                        self.SLOW_NETWORK_QUERY,
                                        1,
                                        {'value': i, i: 'value'}
                                        )
                           )

        gevent.joinall(threads, timeout=5)