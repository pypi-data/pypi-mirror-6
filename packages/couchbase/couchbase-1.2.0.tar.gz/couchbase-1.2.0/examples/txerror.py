from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from couchbase import experimental
experimental.enable()

from txcouchbase.connection import Connection as TxCouchbase

cb = TxCouchbase(bucket='defauaalt')

@inlineCallbacks
def runme():
#    yield cb.connect()
    yield cb.set("key", "value")
#    yield cb.get("key")

runme()
reactor.run()
