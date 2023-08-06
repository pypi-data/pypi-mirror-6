# -*- coding: utf-8 -*
from bw2calc import LCA
from bw2data import Database
from bw2data.utils import open_activity_in_webbrowser


class Activity(object):
    """
Simple proxy for an activity dataset. Makes manipulation and use in command line more convenient.

.. warning:: This proxy is read only! To save changes to a dataset, you will need to work with the raw database data.

Instantiate a activity proxy with its key, e.g. ``("foo", "bar")``:

.. code-block:: python

    activity = Activity(("foo", "bar"))

Properties:

* ``categories``
* ``code``
* ``database``
* ``location``
* ``name``
* ``unit``

``activity.exchanges`` returns a list of :ref:`exchange` objects.

See also the descriptions of each method below.

    """
    def __init__(self, key):
        self.key = key
        self.raw = self._load()

    # Magic methods to make Activity have the same behavior in dictionaries
    # as the normal ("foo", "bar") key

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other

    def __str__(self):
        return str(self.key)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        try:
            return u"'%s' (%s, %s, %s)" % (self.name, self.unit, self.location,
            self.categories)
        except:
            return u"Error with key %s" % (self.key, )

    def __getitem__(self, key):
        if key == 0:
            return self.database
        elif key == 1:
            return self.code
        else:
            return self.raw[key]

    def __contains__(self, key):
        return key in self.raw

    @property
    def database(self):
        return self.key[0]

    @property
    def code(self):
        return self.key[1]

    @property
    def categories(self):
        return self.raw.get('categories', [])

    @property
    def location(self):
        return self.raw.get('location', [])

    @property
    def name(self):
        return self.raw.get('name', [])

    @property
    def unit(self):
        return self.raw.get('unit', [])

    @property
    def exchanges(self):
        from .exchange import Exchange
        return [Exchange(exc, self) for exc in self.raw.get('exchanges', [])]

    def open_in_webbrowser(self):
        """Open this activity in the web UI.

        Requires `bw2-web.py` to be running."""
        open_activity_in_webbrowser(self)

    # TODO: Complete
    # def create_system_process(self, database):
    #     """Create a SimaPro `system` process, i.e. one that has no technosphere inputs, only biosphere flows."""
    #     lca = LCA({self: 1})
    #     lca.lci()
    #     lca.fix_dictionaries()

    def lca(self, method=None, amount=1.):
        """Shortcut to construct an LCA object for this activity."""
        lca = LCA({self: amount}, method=method)
        lca.lci()
        lca.fix_dictionaries()
        if method is not None:
            lca.lcia()
        return lca

    # Methods not normally needed in public API

    def _load(self):
        return Database(self.key[0]).load()[self]
