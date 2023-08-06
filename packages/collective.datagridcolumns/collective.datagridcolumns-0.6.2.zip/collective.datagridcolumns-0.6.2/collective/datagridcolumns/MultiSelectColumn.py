# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.Archetypes import atapi
from Products.DataGridField.Column import Column
from collective.datagridcolumns.SelectColumn import SelectColumn
from zope import schema
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError


class MultiSelectColumn(SelectColumn):
    """ Defines column with a set or checkboxes """

    security = ClassSecurityInfo()

    def __init__(self, label, col_description=None, vocabulary=None, vocabulary_factory=None, default=None,
                 default_method=None, required=False):
        """ Create a SelectColumn

        @param vocabulary Vocabulary method name. This method is called
               from Archetypes instance to get values for dropdown list.
        @param vocabulary_factory Vocabulary utility.
        """
        # do not call base SelectColumn constructor
        if required or col_description:
            # sorry for this trick, but we are using this product with a custom DataGridField 1.6.4
            # see https://github.com/RedTurtle/Products.DataGridField/tree/1.6
            Column.__init__(self, label, col_description=col_description, default=default,
                            default_method=default_method, required=required)
        else:
            Column.__init__(self, label, default=default, default_method=default_method)
        self.vocabulary = vocabulary
        self.vocabulary_factory = vocabulary_factory

    security.declarePublic('getMacro')
    def getMacro(self):
        """ Return macro used to render this column in view/edit """
        return "datagrid_multiselect_cell"

    security.declarePublic('processCellData')
    def processCellData(self, form, value, context, field, columnId):
        """ Read cell values from raw form data

        Read special table for radio button columns from form data.
        The selected radio button cell id is placed as a cell value.
        """

        newValue = []

        #print "form value:" + str(form)

        for row in value:

            # we must clone row since
            # row is readonly ZPublished.HTTPRequest.record object
            newRow = {}
            for key in row.keys():
                newRow[key] = row[key]

            orderIndex = row["orderindex_"]
            # pageColumns.options.required.64

            newRow[columnId] = []
            for vitem in self.getVocabulary(context).keys():    
                cellId = "%s.%s.%s.%s" % (field.getName(), columnId, vitem, orderIndex)
                if form.has_key(cellId):
                    # If radio button is set in HTML form
                    # it's id appears in form of field.column.orderIndex
                    newRow[columnId].append(vitem)
    
            newValue.append(newRow)
        return newValue

# Initializes class security
InitializeClass(MultiSelectColumn)
