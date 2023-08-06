#-*- coding: utf-8 -*-

from contextlib import contextmanager
from logging import getLogger

logger = getLogger(__name__)


@contextmanager
def conn(conn_):
    try:
        yield conn_
    except Exception as e:
        logger.error("Error: {0}".format(e))
        conn_.rollback()
        raise
    else:
        conn_.commit()
    finally:
        conn_.close()


@contextmanager
def cursor(cursor_):
    try:
        yield cursor_
    except Exception as e:
        logger.error("Error: {0}".format(e))
        raise
    finally:
        cursor_.close()
