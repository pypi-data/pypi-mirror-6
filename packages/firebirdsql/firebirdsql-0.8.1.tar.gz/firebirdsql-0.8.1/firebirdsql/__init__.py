##############################################################################
# Copyright (c) 2009-2013 Hajime Nakagami<nakagami@gmail.com>
# All rights reserved.
# Licensed under the New BSD License
# (http://www.freebsd.org/copyright/freebsd-license.html)
#
# Python DB-API 2.0 module for Firebird. 
##############################################################################

from firebirdsql.consts import *

class Error(Exception):
    def __init__(self, message, gds_codes=0, sql_code=0):
        self._message = message
        self.gds_codes = gds_codes
        self.sql_code = sql_code
        self.args = [message, sql_code]
    def __str__(self):
        return self._message

class Warning(Exception):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class DisconnectByPeer(Warning):
    pass

class InternalError(DatabaseError):
    def __init__(self):
        DatabaseError.__init__(self, 'InternalError')

class OperationalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class DataError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    def __init__(self):
        DatabaseError.__init__(self, 'NotSupportedError')

from firebirdsql.fbcore import ( __version__, apilevel, threadsafety, 
    paramstyle, Transaction, Cursor, Connection,
    ISOLATION_LEVEL_READ_UNCOMMITTED, ISOLATION_LEVEL_READ_COMMITED,
    ISOLATION_LEVEL_REPEATABLE_READ, ISOLATION_LEVEL_SERIALIZABLE,
    ISOLATION_LEVEL_READ_COMMITED_READ_ONLY
)

import firebirdsql.services

def connect(dsn=None, user=None, password=None, role=None, host=None, 
            database=None, charset=DEFAULT_CHARSET, port=3050,
            timeout=None, isolation_level=None, use_unicode=None):
    return Connection(dsn=dsn, user=user, password=password,
                role=role, host=host, 
                database=database, charset=charset, port=port,
                timeout=timeout, isolation_level=isolation_level,
                use_unicode=use_unicode)

def create_database(dsn=None, user=None, password=None, host=None, role=None,
            database=None, charset=DEFAULT_CHARSET, port=3050, page_size=4096,
            timeout=None, isolation_level=None, use_unicode=None):
    return Connection(dsn=dsn, user=user, password=password,
                role=role, host=host, 
                database=database, charset=charset, port=port, 
                page_size=page_size, timeout=timeout,
                isolation_level=isolation_level, use_unicode=use_unicode)
