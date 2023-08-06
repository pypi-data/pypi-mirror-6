# vim: fileencoding=utf-8 et ts=4 sts=4 sw=4 tw=0 fdm=marker fmr=#{,#}

from netcall.utils     import get_zmq_classes
from netcall.threading import ThreadPool, ThreadingRPCService
from netcall.sync      import SyncRPCClient

from .base          import BaseCase
from .client_mixins import ClientBindConnectMixIn
from .rpc_mixins    import RPCCallsMixIn


class SyncBase(BaseCase):

    def setUp(self):
        Context, _ = get_zmq_classes()

        self.context = Context()
        self.pool    = ThreadPool(24)
        self.client  = SyncRPCClient(context=self.context)
        self.service = ThreadingRPCService(context=self.context, pool=self.pool)

        super(SyncBase, self).setUp()

    def tearDown(self):
        self.client.shutdown()
        self.service.shutdown()
        self.context.term()
        self.pool.close()
        self.pool.stop()
        self.pool.join()

        super(SyncBase, self).tearDown()


class SyncClientBindConnectTest(ClientBindConnectMixIn, SyncBase):
    pass

class SyncRPCCallsTest(RPCCallsMixIn, SyncBase):
    pass

