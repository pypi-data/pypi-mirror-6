import re

from collections import defaultdict


class BaseCirculator(object):
    """
    Base circulator. Allows you to register distributors with regex. Extend this if you need a custom circulator.
    """

    def __init__(self, mapping={}, *args, **kwargs):
        """
        Initalize a curculator

        :type mapping: dict
        :param mapping: Keys are a regex to match against the verb of an activity. Values are a single distributor or a list of distributors.
        """
        self._registry = defaultdict(list)
        for key, value in mapping.items():
            distributors = []
            try:
                for distributor in value:
                    distributors.append(self._init_distributor(distributor))
            except:
                #possibly just  single distributor?
                distributors.append(self._init_distributor(value))

            self._registry[key].extend(distributors)

    def register(self, identifier, distributor):
        """
        Registers a new verb-distributor(s) pair with the circulator. If the key already exists,
        the distributors will be appended to the list of current distributors.

        :type identifier: string
        :param identifier: a regex to match match the verb of the activity against
        :type distributor: Distributor or list of Distributor
        :param distributor: distributor(s) to run when the verb of the activity matches the identifier
        """
        distributor = self._init_distributor(distributor)
        self._registry.setdefault(identifier, []).append(distributor)

    def circulate(self, activity, *args, **kwargs):
        """
        Run the circulate funcion of the distributors matching ``activity``

        :type activity: dict
        :param activity: a dictionary representing an activity
        """
        raise NotImplementedError()

    def uncirculate(self, activity, *args, **kwargs):
        """
        Run the uncirculate funcion of the distributors matching ``activity``

        :type activity: dict
        :param activity: a dictionary representing an activity
        """
        raise NotImplementedError()

    def _init_distributor(self, distributor):
        """
        Initializes the distributor class if it already hasn't.
        """
        if callable(distributor):
            distributor = distributor()
        return distributor


class Circulator(BaseCirculator):
    """
    This is a helper class that will allow you to index your activities over indexes.

    Meant to use in conjuction with ``sunspear.utils.distributors.Distributor``.

    By registering verbs with certain distributors, you can control which activities are processed by which distributors:

    ```
    circulator = Circulator({
        r'post': [PostFeedDistributor, PostNotificationDistributor, PostEmailNotificationDistributor],
        r'like': LikeNotificationDistributor,
        r'reply': [ReplyStreamDistributor, ReplyNotificationDistributor, ReplyEmailNotificationDistributor],
    })
    ```
    """
    def circulate(self, activity, *args, **kwargs):
        """
        Run the circulate funcion of the distributors matching ``activity``

        :type activity: dict
        :param activity: a dictionary representing an activity
        """
        self._perform_action(activity, action='add', *args, **kwargs)

    def uncirculate(self, activity, *args, **kwargs):
        """
        Run the uncirculate funcion of the distributors matching ``activity``

        :type activity: dict
        :param activity: a dictionary representing an activity
        """
        self._perform_action(activity, action='remove', *args, **kwargs)

    def _perform_action(self, activity, action='add', *args, **kwargs):
        for pattern, distributors in self._registry.items():
            if re.match(pattern, self.get_comparable_value(activity)) is not None:
                for distributor in distributors:
                    distributor.distribute(activity, action=action)

    def get_comparable_value(self, activity):
        """
        Get the value from the activity to compare to the regex

        :type activity: dict
        :param activity: a dictionary representing an activity        
        """
        return activity.get('verb')
