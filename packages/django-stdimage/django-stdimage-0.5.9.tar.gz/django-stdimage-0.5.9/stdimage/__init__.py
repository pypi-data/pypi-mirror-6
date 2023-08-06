from __future__ import absolute_import

from .fields import StdImageField

try:
    from south.modelsinspector import add_introspection_rules
    rules = [
      (
        (StdImageField,),
        [],
        {
            "variations": ["variations", {"default": None}],
            "min_size": ["min_size", {"default": None}],
            "max_size": ["max_size", {"default": None}],
        },
      )
    ]
    add_introspection_rules(rules, ["^stdimage\.fields"])
except ImportError:
    pass
