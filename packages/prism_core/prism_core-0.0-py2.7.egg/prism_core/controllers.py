#
# Copyright (c) Elliot Peele <elliot@bentlogic.net>
#
# This program is distributed under the terms of the MIT License as found
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any warrenty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
#

"""
Core Controller.
"""

import logging

log = logging.getLogger('prism.core.controllers')

class CoreController(object):
    """
    Root manager class for managing all other controllers.
    """

    _db = None
    _controller_classes = {}

    def __init__(self, notify=None):
        self.notify = notify
        for name, cls in self._controller_classes.iteritems():
            setattr(self, name, cls(self, notify))

    @classmethod
    def _set_db(cls, session):
        if cls._db is None:
            cls._db = session

    @classmethod
    def _get_db(cls):
        return cls._db

    db = property(_get_db, _set_db)

    @classmethod
    def register(cls, ctrlcls):
        assert ctrlcls.name != BaseController.name, 'Must set controller name'
        cls._controller_classes[ctrlcls.name] = ctrlcls
        return ctrlcls

register_controller = CoreController.register


class BaseController(object):
    """
    Base class for all controllers to inherit from.
    """

    # name to use for this manager.
    name = 'base'

    def __init__(self, core, notify):
        self.core = core
        self.notify = notify

    def _set_db(self, value):
        self.core.db = value

    def _get_db(self):
        return self.core.db

    db = property(_get_db, _set_db)

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def getById(self, resource_id):
        raise NotImplementedError

    def delete(self, resource_id):
        raise NotImplementedError
