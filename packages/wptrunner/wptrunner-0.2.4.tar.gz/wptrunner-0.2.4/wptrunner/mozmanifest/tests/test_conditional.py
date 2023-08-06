import unittest

import sys
import os

from ..backends import conditional

# There aren't many tests here because it turns out to be way more convenient to
# use test_serializer for the majority of cases

class TestConditional(unittest.TestCase):
    def compile(self, input_text):
        return conditional.compile(input_text)

    def test_0(self):
        data = """
key: value

[Heading 1]
  other_key:
    if a == 1: value_1
    if a == 2: value_2
    value_3
"""

        manifest = self.compile(data)

        self.assertEquals(manifest.get("key")(), "value")

        children = list(item for item in manifest.iterchildren())
        self.assertEquals(len(children), 1)
        section = children[0]
        self.assertEquals(section.name, "Heading 1")

        self.assertEquals(section.get("other_key")({"a":1}), "value_1")
        self.assertEquals(section.get("other_key")({"a":2}), "value_2")
        self.assertEquals(section.get("other_key")({"a":3}), "value_3")
        self.assertEquals(section.get("key")(), "value")

#     def test_1(self):
#         data = """
# key: value

# [Heading 1]
#   other_key:
#     if a == 1: value_1
#     if a == 2: value_2
#     value_3
# """
#         manifest = self.compile(data, {"a":3})

#         children = list(item for item in manifest.iterchildren())
#         section = children[0]
#         self.assertEquals(section.get("other_key"), "value_3")

#     def test_2(self):
#         data = """key:
#   if a == 1.5: value_1
#   value_2
# key_1: other_value
# """
#         manifest = self.compile(data, {"a":1.5})

#         self.assertFalse(manifest.is_empty)
#         self.assertEquals(manifest.root, manifest)
#         self.assertTrue(manifest.has_key("key_1"))
#         self.assertFalse(manifest.has_key("key_2"))

#         self.assertEquals(set(manifest.iterkeys()), set(["key", "key_1"]))
#         self.assertEquals(set(manifest.itervalues()), set(["value_1", "other_value"]))
