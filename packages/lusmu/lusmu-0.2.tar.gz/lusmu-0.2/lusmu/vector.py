# -*- encoding: utf-8 -*-

"""The lazy evaluation graph adapted for numpy arrays and pandas Series

Copyright 2013 Eniram Ltd. See the LICENSE file at the top-level directory of
this distribution and at https://github.com/akaihola/lusmu/blob/master/LICENSE

"""

# pylint: disable=W0611
#         update_inputs is provided as a convenience for importing it from the
#         same place as the Input and Node classes
# pylint: disable=R0903
#         mixins have few public methods, that's ok

import logging
from lusmu.core import (DIRTY,
                        Input as LusmuInput,
                        Node as LusmuNode,
                        update_inputs)
import numexpr as ne
import numpy as np
import pandas as pd


_LOGGER = logging.getLogger('lusmu.vector')


def vector_eq(a, b):
    """Return True if vectors are equal, comparing NaNs correctly too

    Arguments
    ---------
    a, b: numpy.array
                The vectors to compare

    """
    # pylint: disable=C0103
    #         allow one-letter function arguments

    if len(a) != len(b):
        # comparing np.array([]) to np.array([1]) only works this way
        return False
    # Consider NaNs equal; see http://stackoverflow.com/a/10821267
    return np.all(ne.evaluate('(a==b)|((a!=a)&(b!=b))'))


class VectorEquality(object):
    """Mixin for extending Lusmu Inputs and Nodes to work with vector values"""
    def _value_eq(self, other_value):
        """Replace the equality test of Input/Node values

        Lusmu uses the ``==`` operator by default.  It doesn't work correctly
        with vectors which have more than one value – ``bool(vec1 == vec2)``
        raises an exception.

        """
        # pylint: disable=E1101
        #         (Instance of VectorEquality has no _value member)
        #         This class will be mixed into ones that have _value

        if not vector_eq(self._value, other_value):
            return False
        if hasattr(self._value, 'index') and hasattr(other_value, 'index'):
            # The values are Pandas Series with time indices. Compare time
            # indices, too.
            return vector_eq(self._value.index.values.astype(float),
                             other_value.index.values.astype(float))
        return True


class NodePickleMixin(object):
    """Mixin defining the attributes to pickle for all node types"""
    _state_attributes = 'name', '_dependents', '_value'

    def __getstate__(self):
        return {key: getattr(self, key)
                for key in self._state_attributes}


class Input(NodePickleMixin, VectorEquality, LusmuInput):
    """Vector compatible Lusmu Input

    The value of the input node is always set dirty when unpickling.

    """
    _state_attributes = NodePickleMixin._state_attributes + ('last_timestamp',)

    def __init__(self, name=None, value=DIRTY):
        super(Input, self).__init__(name=name, value=value)
        self.last_timestamp = self._get_max_timestamp(value)

    @staticmethod
    def _get_max_timestamp(value):
        """Return the latest timestamp in the Series

        Arguments
        ---------
        value: pandas.Series with a timestamp index

        """
        if isinstance(value, pd.Series) and len(value):
            return value.index[-1]

    def _set_value(self, value, make_cache=True):
        """Keep track of latest timestamp processed"""
        new_last_timestamp = self._get_max_timestamp(value)
        if new_last_timestamp:
            self.last_timestamp = new_last_timestamp
        return super(Input, self)._set_value(value, make_cache=make_cache)


class Node(NodePickleMixin, VectorEquality, LusmuNode):
    """Vector compatible Lusmu Node"""
    _state_attributes = (NodePickleMixin._state_attributes +
                         ('_action',
                          'triggered',
                          '_positional_inputs',
                          '_keyword_inputs'))

    def _evaluate(self):
        """Log a message when evaluating a node"""
        # pylint: disable=E1101
        #         self.name comes from lusmu
        _LOGGER.debug('[%s]._evaluate()', self.name)
        return super(Node, self)._evaluate()
