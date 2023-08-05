"""
    polaris.ext.database
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 Eleme, http://polaris.eleme.io
    :license: MIT

    Database extension, we use sqlalchemy engine to interact with databases, so
    this extension support all databases which sqlalchemy support.
"""

import datetime
import collections

import pandas as pd

from sqlalchemy import create_engine

from polaris.ext import (
    PolarisExtension,
    ext_cache
)

from polaris.exc import (
    InvalidValueError,
    PolarisError,
)


class DataFramePivotError(PolarisError):
    """Raised when try to reshape datafram failed."""


class Database(PolarisExtension):
    """Get DataFrame from relational database.
    """

    def __init__(self, url, options=None, **kwargs):
        super(Database, self).__init__(**kwargs)

        self.name = "database"
        self.url = url
        self.options = options or {}
        self.engine = create_engine(self.url, **self.options)

    @ext_cache
    def get(self, sql, index=None, unstack=None, fillna=0,
            cf=None, **filters):
        """Get DataFrame by args.

        `cf` will make a `cross_filter` and add it to the `filters` list,
        if an 'cross_filter' already exists in filters, it'll be overwritten.
        """
        if cf:
            tmpl = "AND {cf_col} >= '{cf_gte}' AND {cf_col} < '{cf_lte}'"
            cf_col, cf_gte, cf_lte = cf.split("|")
            cross_filter = tmpl.format(cf_col=cf_col, cf_gte=cf_gte,
                                       cf_lte=cf_lte)
            filters["cross_filter"] = cross_filter
        sql = self._format_sql(sql, filters)
        self._validate_sql(sql)

        with self.engine.contextual_connect() as conn:
            cur = conn.execute(sql)
            df = pd.DataFrame.from_records(cur.fetchall(),
                                           columns=cur.keys(),
                                           coerce_float=True)

        index = index or df.columns[0]
        if unstack:
            if unstack not in df.columns:
                raise DataFramePivotError("Pivot column do not exists!")
            if len(df.columns) != 3:
                raise DataFramePivotError("Can only pivot 1 dimension data!")

            value_column = list(set(df.columns) - set([index, unstack]))[0]
            df = df.pivot(index, unstack, value_column).fillna(fillna)
        else:
            df = df.set_index(index).fillna(fillna)

        if isinstance(df.index[0], (datetime.date, datetime.datetime)):
            df.index = df.index.to_datetime()

        return df

    def _format_sql(self, sql, filters):
        """This method will try to format sql with additional filters.

        If a filter variable don't exists, it'll be replaced by a space.
        """
        kwargs = collections.defaultdict(lambda: " ")
        kwargs.update(filters)
        sql = sql.format(**kwargs)
        return ' '.join(sql.split())

    def _validate_sql(self, sql):
        if not sql:
            raise InvalidValueError("sql can't be empty!")

        # TODO this is just a simple sql safe check.
        # Need to make it more strict later.
        blacklist = ["delete", "drop", "truncate", "alter"]
        if not all(w not in sql for w in blacklist):
            raise InvalidValueError("sql not safe!")
