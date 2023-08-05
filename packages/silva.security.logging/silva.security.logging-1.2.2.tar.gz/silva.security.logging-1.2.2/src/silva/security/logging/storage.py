# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from five import grok
from zeam.form import silva as silvaforms

from silva.security.logging.interfaces import (
    ILoggingStorage, ISQLStorageConfiguration, ILogger)

logger = logging.getLogger("silva.security.logging")


class PythonLogger(grok.GlobalUtility):
    grok.implements(ILoggingStorage, ILogger)
    grok.provides(ILoggingStorage)
    grok.name('Python Logger')

    storage_conf = silvaforms.Fields()

    def log(self, event):
        msg = u'%r did %s on %s'
        info = [event.username, event.action, event.content_path]
        if event.detail:
            msg += u' (%s)'
            info.append(event.detail)
        logger.info(msg % tuple(info))

    def configure(self, context):
        return self


class ZopeSQLLogger(object):
    """Log in a Zope SQL connection.
    """
    grok.implements(ILogger)

    def __init__(self, connection, table='log'):
        self.connection = connection
        self.table = table

    def log(self, event):
        db = self.connection()
        query = """insert into %s
                        (username, action, time, content, content_intid, info)
                        values (%r, %r, now(), %r, %d, %r)""" % (
                self.table, event.username, event.action,
                event.content_path, event.content_id,
                event.detail or "")
        db.query(query)


class ZopeSQLStorage(grok.GlobalUtility):
    grok.implements(ILoggingStorage)
    grok.provides(ILoggingStorage)
    grok.name('Zope SQL')

    storage_conf = silvaforms.Fields(ISQLStorageConfiguration)

    def configure(self, context):
        if 'sql_connection_id' not in context.storage_conf:
            logger.error('SQL logger not properly configured')
            return None
        connection_id = context.storage_conf['sql_connection_id']
        table = str(context.storage_conf.get('sql_table', 'log'))
        try:
            connection = getattr(context, connection_id)
        except AttributeError:
            logger.error('SQL connection %s no longer exists' % connection_id)
            return None
        return ZopeSQLLogger(connection, table)


class MemoryLogger(grok.GlobalUtility):
    grok.implements(ILoggingStorage, ILogger)
    grok.provides(ILoggingStorage)
    grok.name('Memory Logger (for testing)')

    storage_conf = silvaforms.Fields()
    records = []                # Records will be stored on the class

    def log(self, event):
        info = [event.username, event.action, event.content_path]
        if event.detail:
            info.append(event.detail)
        self.records.append(info)

    def purge(self):
        del self.records[:]

    def configure(self, context):
        return self
