# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision$
from Products.ZSQLMethods.SQL import SQL

# DATA RETRIEVERS
class SQLDB:
    """generic abstraction for using SQL adapters without ZSQL methods
    """
    
    def __init__(self, connection, encoding='latin-1'):
        self.connection = connection
        self.encoding = encoding
        
    def getSQLData(self, context, template, parameters={}):
        """ Generic table data retrieval
        """        
        parameters = self._escapeParameters(parameters)
        statement = template % parameters
        
        assert type(statement) == type(u'')
        statement = statement.encode(self.encoding)

        sql_method = SQL(
            'sqlmethod', 'sqlmethod', self.connection, None, 
            statement).__of__(context)
        # XXX: We're materializing all data in the resultset here which
        # hurts performance for large sets. Brains 'normally' lazily
        # retrieve the data, but then we need to decode to unicode in
        # the wrong - i.e. in the ZPT's - layer...
        #
        # We need a better way.
        #
        data_dicts = sql_method().dictionaries()
        return self._unicodeHelper(data_dicts)
        
    def getUniqueRecord(self, context, table, key, value):
        """ Get data dictionary for the one record in the _table_
        where the primairy _key_ has the given _value_
        """
        data = self.getSQLData(
                context, 
                u"""SELECT * FROM %(table)s WHERE %(key)s = %(value)s""",
                {'table':table, 'key':key, 'value':value})
        if not data:
            return None        
        return data[0] # Should be one row at max.

    def valuesCount(self, context, table, column, range=None):
        """Returns the number of column values returned within specified range
            
            XXX these are not the unique column values
        """
        select_clause = 'count(%s)' % column
        results = self._uniqueValuesFor(
            context, table, column, select_clause, range)
        return results[0]['count']

    def uniqueValuesFor(self, context, table, column, range=None):
        """Sort of resembles the Catalog's uniqueValuesFor for the DB tables
        """
        # XXX: why? is column heading used?
        select_clause = '%s AS %s' % (column, column.lower())
        return self._uniqueValuesFor(context, table, column, select_clause, range)

    def _uniqueValuesFor(self, context, table, column, select_clause, range=None):
        if range is not None:
            start, end = range
            data = self.getSQLData(
                context, 
                (u"""SELECT DISTINCT %(select_clause)s FROM %(table)s """
                    """WHERE lower(%(column)s) BETWEEN '%(start)s' AND """
                    """'%(end)s'"""),
                    {'column': column, 
                        'select_clause': select_clause, 
                        'table': table, 
                        'start': start, 
                        'end': end})
        else:
            data = self.getSQLData(
                context, 
                u"""SELECT DISTINCT %(select_clause)s FROM %(table)s""",
                {'select_clause': select_clause, 'table': table})
        return data

    # XXX copied from SilvaExternalSources.SQLSource
    def _unicodeHelper(self, dictionaries):
        for d in dictionaries:
            for key, value in d.items():
                # XXX: Aaargll, the DA's have inconsistent casing policies, 
                # so I have to explicitly make the keys lower case here...
                # (this might leave a 'duplicate' with different casing in
                # the dicts - i don't think this will hurt)
                key = key.lower()
                d[key] = value
                # Make non-unicode strings unicode
                if type(value) is type(''):
                    d[key] = unicode(value, self.encoding, 'replace')
        return dictionaries

    def _escapeParameters(self, parameters):
        escaped_parameters = {}
        for key, value in parameters.items():
            if type(value) == type(u''):
                # escape a single quote with a double single quote
                value = value.replace("'", "''")
            escaped_parameters[key] = value
        return escaped_parameters
