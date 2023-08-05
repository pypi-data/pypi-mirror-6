__title__ = 'werewolf.base'
__version__ = '0.5'
__build__ = 0x000005
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('WerewolfConf',)

def namify(model):
    return "{0}.{1}".format(model.__module__, model.__name__)


class WerewolfConf(object):
    """
    Model settings for werewolf.

    :example:
    >>> from werewolf.base import WerewolfConf
    >>> 
    """
    status_choices = None
    status_published = None
    default_status = None


class WerewolfConfRegistry(object):
    """
    Registry of werewolf configuration settings for separate models.
    """
    def __init__(self):
        self._registry = {}
        self._forced = []

    def register(self, cls, model, force=False):
        """
        Registers the plugin in the registry.

        :param mixed.
        """
        if not issubclass(cls, WerewolfConf):
            raise InvalidRegistryItemType("Invalid item type `{0}` for registry `{1}`".format(cls, self.__class__))

        uid = namify(model)

        # If item has not been forced yet, add/replace its' value in the registry
        if force:

            if not cls.uid in self._forced:
                self._registry[uid] = cls
                self._forced.append(uid)
                return True
            else:
                return False

        else:

            if uid in self._registry:
                return False
            else:
                self._registry[uid] = cls
                return True

    def unregister(self, model):
        # Only non-forced items are allowed to be unregistered.
        uid = namify(model)
        if uid in self._registry and not uid in self._forced:
            self._registry.pop(uid)
            return True
        else:
            return False

    def get(self, uid, default=None):
        """
        Gets the given entry from the registry.

        :param str uid:
        :return mixed.
        """
        item = self._registry.get(uid, default)
        if not item:
            logger.debug("Can't find item with uid `{0}` in `{1}` registry".format(uid, self.__class__))
        return item

