An additional set of **column types** for `DatagridField`__ Plone product.

__ http://plone.org/products/datagridfield

.. contents::

New columns
===========

TextAreaColumn
--------------

Like the base *Column* type, just display a ``textarea`` HTML element.

Additional parameters:

``rows``
    Default: 3. Number of rows of the textarea.
``cols``
    Default: 0. Number of columns of the textarea. If not provided the
    html ``cols`` attribute is omitted and an inline style "*width: 100%*"
    wil be used instead.

Example::

    ...
    DataGridField('foo',
              columns=("type", "description"),
              widget = DataGridWidget(
                        columns={
                             'type' : Column(_(u"Type")),
                             'description' : TextAreaColumn(_(u"Description"),
                                                            rows=10,
                                                            cols=20),
                        },
             ),
    ),
    ...

SelectColumn
------------

Like the default *SelectColumn* from DataGridField product, but explicitly support the
``vocabulary_factory`` way to provide vocabularies.

Additional parameters:

``vocabulary_factory``
    Provide the name of a registered vocabulary using a Zope Component Utility. See the
    Archetypes Develop Manual for more.
``vocabulary``
    As default SelectColumn, required only if you don't provide ``vocabulary_factory``.
    Use this to call a method on the context to obtain the vocabulary.

Example::

    ...
    DataGridField('foo',
              columns=("type", "description"),
              widget = DataGridWidget(
                        columns={
                             'type' : SelectColumn(_(u"Type"),
                                                   vocabulary_factory='plone.app.vocabularies.PortalTypes'),
                             'description' : Column(_(u"Description"),),
                        },
             ),
    ),
    ...

.. note:: The base *SelectColumn* of DataGridField 1.8 already have some kind of support for Zope-3-like
          vocabularies, however the use of that feature is not clear (and *this* version also works on Plone 3).

ReferenceColumn
---------------

This is a complex column type that store an unique object "*UID*". The default view rendering of this column
will display a proper link to the referenced object.

You can use this is different ways. In the simpler example, just use it as a textual column::

    ...
    DataGridField('foo',
              columns=("uid", "comment"),
              widget = DataGridWidget(
                        columns={
                             'uid' : ReferenceColumn(_(u"Reference")),
                             'comment' : Column(_(u"Comment")),
                        },
             ),
    ),
    ...

So you are on your own to store a propert UID in the field (not very interesting, isn't it?).

If you want something more, you can enable an additional JavaScript module and you'll get an
**autocomplete feature** of referenced objects::

    ...
    DataGridField('foo',
              columns=("uid", "comment"),
              widget = DataGridWidget(
                        helper_js= ('datagridwidget.js', 'datagridautocomplete.js'),
                        columns={
                             'uid' : ReferenceColumn(_(u"Reference")),
                             'comment' : Column(_(u"Comment")),
                        },
             ),
    ),
    ...

So you will add to the default ``datagridwidget.js`` (automatically provided by the widget) a new
``datagridautocomplete.js`` ones.
This will also required `jQueryUI autocomplete`__. Please, read also the "Dependencies" section below.

__ http://jqueryui.com/demos/autocomplete/

When using autocomplete, you can query Plone in two different way:

* starting a query with the "``/``" character will query documents by *path*, so you can manually
  surf the whole site.
* starting as query with other character will perform a full-text query on titles.

Additional parameters:

``object_provides``
    When using the full-text query, only return results of objects that provide those interfaces.
    Default is an empty list (no filter).
``surf_site``
    Choose to be able to surf the site tree using a "/dir/dir/..." term.
    Default to True (allowed).
``search_site``
    Choose to be able to search items in the site by full-text query or not.
    Default to True (allowed).

DateColumn
----------

A simple column field that allows to insert some dates. This field use `jQuery UI datepicker plugin`__.

__ http://jqueryui.com/datepicker/

To use datepicker plugin you need to enable datepicker plugin of jQuery UI (see above for infos) and add an
helper_js named ``datagriddatepicker.js`` in the widget. See the example below.

Additional parameters:

``date_format``
    Default: yy/mm/dd. The date format to store in the field.

Example::

    ...
    DataGridField('foo',
              columns=("name", "birthday"),
              widget = DataGridWidget(
                        helper_js= ('datagridwidget.js', 'datagriddatepicker.js'),
                        columns={
                             'name' : Column(_(u"Name")),
                             'birthday' : DateColumn(_(u"Birthday"),
                                                     date_format="dd/mm/yy"),
                        },
             ),
    ),
    ...

MultiSelectColumn
-----------------

Based on the *SelectColumn* from (from this package, not the original ones, so it support the 
``vocabulary_factory`` parameter), show a list of checkboxes and store a list of selected entries.

Additional parameters: see all parameter from *SelectColumn*.

Example::

    ...
    DataGridField('foo',
              columns=("recipe_name", "recipe_options"),
              widget = DataGridWidget(
                        helper_js= ('datagridwidget.js', 'datagridwidget_patches.js', 'datagridmultiselect.js'),
                        columns={
                             'recipe_name' : Column(_(u"Name of the recipe"),),
                             'recipe_options' : MultiSelectColumn(_(u"Type"),
                                                                  vocabulary_factory='your.vocabulary',
                                                                  ),
                        },
             ),
    ),
    ...

.. warning:: This column suffer of the same limitations of *RadioColumn* and
             *CheckboxColumn* columns (from original DataGridField).
             
             If you get a validation error when saving, **post data will not be reloaded** on the form itself.

Dependencies
============

This product has been tested on:

* *Plone 3.3* and *DataGridField 1.6*
* *Plone 4.2 and 4.3* and *DataGridField 1.9*

jQuery version (for Plone 3)
----------------------------

Both *ReferenceColumn*, *DateColumn* and *MultiSelectColumn* need jQuery 1.4.2 or better to work.
Plone 3.3 is shipped with jQuery 1.3. You can fix this dependency by your how, or using a 3rd party library.

An alternative Generic Setup import step ("*DataGridField: register jQuery 1.4*") is provided
with the product. Run this and the default Plone jQuery version will be disabled, then a
1.4.4 version of jQuery will be registered.

**Do not run this** on Plone 4! 

jQueryUI
--------

ReferenceColumn and DateColumn needs that Plone provide jQueryUI library. This product *will not* cover this
requirement, even by dependency.

If you have already jQueryUI (autocomplete or datepicker) behaviour in your Plone site, you are already ok.
If you don't, take a look at `collective.jqueryui.autocomplete`__ (or read it's documentation page
to understand how cover this need).

__ http://plone.org/products/collective.jqueryui.autocomplete

Keep in mind that the standard way of providing jQueryUI support to Plone is by using `collective.js.jqueryui`__

__ http://plone.org/products/collective.js.jqueryui

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

Credits
=======

Developed with the support of:


* `Regione Emilia Romagna`__
* `Azienda USL Ferrara`__
  
  .. image:: http://www.ausl.fe.it/logo_ausl.gif
     :alt: Azienda USL's logo
  
* `S. Anna Hospital, Ferrara`__

  .. image:: http://www.ospfe.it/ospfe-logo.jpg 
     :alt: S. Anna Hospital logo

All of them supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.ausl.fe.it/
__ http://www.ospfe.it/
__ http://www.plonegov.it/
