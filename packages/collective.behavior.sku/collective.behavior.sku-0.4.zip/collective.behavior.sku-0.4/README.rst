=======================
collective.behavior.sku
=======================

collective.behavior.sku provides behavior add SKU field to dexterity content types.

Currently tested with
---------------------

* Plone-4.3.2 with Python-2.7.x [taito]

Behavior
--------

The behavior can be added through the web or directly through the file system to the dexterity content type xml file like::

  <property name="behaviors">
    ...
    <element value="collective.behavior.sku.interfaces.ISKU" />
    ...
  </property>
