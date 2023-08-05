
Changelog
=========

0.9
---

- The new_dexterity_type function no longer overwrites the 'klass' attribute.
  Fixes #1.

0.8
---

- Adds a safe_html function

- Fixes tools.get_parent returning a non-brain parent for brain input

0.7
---

- Adds a naive profiler function

- Adds a unicode collation sortkey

- Adds a DRY version of http://maurits.vanrees.org/weblog/archive/2009/12/catalog

0.6
---

- Fixes the schemafields from being unwritable by the supermodel

0.5
---

- Adds Email and Website fields for supermodel, schemaeditor, zope.schema

0.4
---

- New function to search for Dexterity FTI's that use a certain schema

- New translator function for translating text with the request language

0.3
---

- Renames utils.py to tools.py

0.2
---

- Adds commonly used javascripts

0.1
---

- Initial release