#This file is part of flask_tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from functools import wraps

from flask import request

from trytond.config import CONFIG
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.cache import Cache
from trytond import backend

__version__ = '0.1'


class Tryton(object):
    "Control the Tryton integration to one or more Flask applications."
    def __init__(self, app=None):
        self.context_callback = None
        if app is not None:
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        "Initialize an application for the use with this Tryton setup."
        self.app = app
        database = app.config.setdefault('TRYTON_DATABASE', None)
        user = app.config.setdefault('TRYTON_USER', 0)
        configfile = app.config.setdefault('TRYTON_CONFIG', None)

        CONFIG.update_etc(configfile)

        # 3.0 compatibility
        if hasattr(CONFIG, 'set_timezone'):
            CONFIG.set_timezone()

        self.pool = Pool(database)
        with Transaction().start(database, user, readonly=True):
            self.pool.init()

    def default_context(self, callback):
        "Set the callback for the default transaction context"
        self.context_callback = callback
        return callback

    def _readonly(self):
        return not (request
            and request.method in ('PUT', 'POST', 'DELETE', 'PATCH'))

    def transaction(self, readonly=None, user=None, context=None):
        """Decorator to run inside a Tryton transaction.
        The decorated method could be run multiple times in case of
        database operational error.

        If readonly is None then the transaction will be readonly except for
        PUT, POST, DELETE and PATCH request methods.

        If user is None then TRYTON_USER will be used.

        readonly, user and context can also be callable.
        """
        database = self.app.config['TRYTON_DATABASE']
        DatabaseOperationalError = backend.get('DatabaseOperationalError')
        if readonly is None:
            readonly = self._readonly
        if user is None:
            user = int(self.app.config['TRYTON_USER'])

        def get_value(value):
            return value() if callable(value) else value

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                Cache.clean(database)
                transaction_user = get_value(user)
                is_readonly = get_value(readonly)

                transaction_context = {}
                if self.context_callback or context:
                    with Transaction().start(database, transaction_user,
                            readonly=True):
                        if self.context_callback:
                            transaction_context = self.context_callback()
                        transaction_context.update(get_value(context) or {})

                for count in range(int(CONFIG['retry']), -1, -1):
                    with Transaction().start(database, transaction_user,
                            readonly=is_readonly,
                            context=transaction_context) as transaction:
                        cursor = transaction.cursor
                        try:
                            result = func(*args, **kwargs)
                            if not is_readonly:
                                cursor.commit()
                        except DatabaseOperationalError:
                            cursor.rollback()
                            if count and not is_readonly:
                                continue
                            raise
                        except Exception:
                            cursor.rollback()
                            raise
                    Cache.resets(database)
                    return result
            return wrapper
        return decorator
