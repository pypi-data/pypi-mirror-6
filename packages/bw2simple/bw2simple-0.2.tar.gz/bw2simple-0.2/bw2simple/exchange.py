# -*- coding: utf-8 -*
from .activity import Activity
from stats_arrays import uncertainty_choices
import copy


class Exchange(object):
    """
Simple proxy for an exchange between activity datasets. Makes manipulation and use in command line more convenient.

.. warning:: This proxy is read only! To save changes to a dataset, you will need to work with the raw database data.

Usually these proxies are created by the :ref:`activity`, but you can instantiate one with the dictionary of exchange data and an Activity proxy of the consuming activity:

.. code-block:: python

    exchange = Exchange({"my exchange data": "goes here"}, my_activity_proxy)

Properties:

* ``input``: Returns :ref:`activity`
* ``to``: Returns :ref:`activity`
* ``amount``
* ``uncertainty``: Returns dictionary of uncertainty data
* ``uncertainty_type``: Returns ``stats_arrays`` uncertainty type
* ``unit``

    """
    def __init__(self, exc, activity):
        self.raw = copy.deepcopy(exc)
        self.input = Activity(self.raw['input'])
        self.to = activity
        self.amount = self.raw['amount']

    def __str__(self):
        return "%s %s to %s" % (self.amount, str(self.input), str(self.to))

    def __unicode__(self):
        return u"%.2g %s from %s to %s" % (self.amount, self.unit, self.input, self.to)

    def __repr__(self):
        return unicode(self).encode('utf-8')

    @property
    def unit(self):
        return self.input.unit

    @property
    def uncertainty(self):
        KEYS = {
            'uncertainty type',
            'loc',
            'scale',
            'shape',
            'minimum',
            'maximum'
        }
        return {k: v for k,v in self.raw.iteritems() if k in KEYS}

    @property
    def uncertainty_type(self):
        return uncertainty_choices[self.raw.get("uncertainty type", 0)]

    def random_sample(self, n=100):
        """Draw a random sample from this exchange."""
        ut = self.uncertainty_type
        array = ut.from_dicts(self.uncertainty)
        return ut.bounded_random_variables(array, n).ravel()
