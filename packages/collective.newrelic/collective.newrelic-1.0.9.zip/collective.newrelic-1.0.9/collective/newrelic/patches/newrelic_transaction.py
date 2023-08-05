from collective.newrelic.utils import logger
from newrelic.api.transaction import Transaction

original__init__ = Transaction.__init__
original__exit__ = Transaction.__exit__


def patched__init__(self, *args, **kwargs):
    original__init__(self, *args, **kwargs)

    self._transaction_id = id(self)
Transaction.__init__ = patched__init__
logger.info("Patched newrelic.api.transaction:Transaction.__init__ to add _transaction_id")


def patched__exit__(self, *args, **kwargs):

    if self._transaction_id != id(self):
        logger.exception("Checking my id: {0}  against {1}".format(self._transaction_id, id(self)))
        return

    original__exit__(self, *args, **kwargs)

Transaction.__exit__ = patched__exit__
logger.info("Patched newrelic.api.transaction:Transaction.__exit__ to check _transaction_id")
