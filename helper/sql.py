import sys
import sqlite3
import re
from collections import OrderedDict

class DB:
    r"""
    A database manager class for sqlite3
    """
    data_types = {
        None: "NULL",
        str: "TEXT",
        int: "INTEGER",
        float: "REAL",
    }
    if sys.version_info[0] < 3:
        data_types[unicode] = "TEXT"
    else:
        data_types[bytes] = "BLOB"

    def __init__(self, db=None, commit=True, debug=True):
        r"""
        db is the file to open the database from
        commit is whether to commit changes before closing
        """
        if db is None:
            db = "data.db"
        self.file = db
        self.will_commit = commit
        self.debug = debug
        self.conn = None
        self.curs = None

    def __call__(self, commit=None):
        r"""
        Creates a new instance of this class with the same parameters
        Useful for multithreading (if you need separate instances)

        e.x.

        database = DB('file.db', commit=False)
        with database() as db:
            db.select('table')
        """
        if commit is None:
            commit = self.will_commit
        return type(self)(db=self.file, commit=commit, debug=debug)

    def connect(self):
        r"""
        Opens the database connection and sets the row factory
        """
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = self._to_dict # sqlite3.Row
        self.curs = self.conn.cursor()
        self.curs.execute("PRAGMA journal_mode = MEMORY;")
        self.curs.execute("PRAGMA foreign_keys = ON;")
        return self

    __enter__ = connect

    def close(self, exception_type=None, exception_value=None, traceback=None):
        r"""
        Closes the connections and commits changes if requested
            when the DB was created
        """
        if self.curs:
            self.curs.close()
        self.curs = None
        if self.conn:
            if self.will_commit:
                self.conn.commit()
            self.conn.close()
        self.conn = None

    __exit__ = close

    def commit(self):
        r"""
        Commits any recent changes
        """
        self.conn.commit()

    def rollback(self):
        r"""
        Rolls backany changes to the last commit
        """
        self.conn.rollback()

    @staticmethod
    def _to_dict(curs, row):
        r"""
        A simple method for use with the Connection's row_factory

        Returns a dictionary of the columns
        """
        return OrderedDict((desc[0].lower(), value) for desc, value in zip(curs.description, row))

    def switch_schema(self, schema):
        pass # for now

    def has_table(self, table):
        r"""
        Returns whether the given table exists in the database
        """
        ret = False
        if self.curs:
            ret = self.select("sqlite_master", columns="count(*)", conditions=["type='table'", "name='{}'".format(table)])
            ret = bool(ret)
        return ret

    def create_table(self, table, fields={}, constraints={}, adtl_constraints=[], ignore_existing=True):
        r"""
        Creates a table with the give fields
        The fields are specified with a dictionary mapping the name to a type
        The type can be a string or the actual Python type desired

        constraints is currently ignored

        Returns if the creation was successful
        """
        ret = False
        if self.curs:
            for key, value in fields.items():
                value = self.data_types.get(value, value)
                if key in constraints:
                    constraint = constraints[key]
                    fields[key] = "{} {} {}".format(key, value, constraint)
                else:
                    fields[key] = "{} {}".format(key, value)
            statement = "CREATE TABLE "
            if ignore_existing:
                statement += "IF NOT EXISTS "
            cols = list(fields.values())
            cols += adtl_constraints
            statement += "{} ({})".format(table, ", ".join(cols))
            statement += ";"
            try:
                self.curs.execute(statement)
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % statement)
                raise
            ret = True
        return ret

    def insert(self, table, fields):
        r"""
        Inserts data into the given table
        The values are a dictionary with fields as the keys
            and the value to insert as the values

        Returns if the insertion was successful
        """
        ret = None
        if self.curs:
            f = []
            p = []
            for key, value in fields.items():
                f.append(key)
                p.append(value)
            fields = ", ".join(f)
            params = ",".join(["?"] * len(p))
            statement = "INSERT INTO {} ({}) VALUES ({})".format(table, fields, params)
            statement += ";"
            try:
                self.curs.execute(statement, p)
            except:
                if self.debug:
                    sys.stderr.write("%s\n%s\n" % (statement, " | ".join(map(repr, p))))
                raise
        return ret

    def select(self, tables, columns=["*"], conditions=[], order=[], distinct=False, params=[]):
        r"""
        Retireves data from the database in the form of a list of dictionaries
        The keys to the dictionary are the columns requested in lowercase

        tables: a list of the tables to pull data from (may be aliased),
            may use a string for a single table

        columns: a list of the columns to retrieve,
            may use a string for a single column
            defaults to * (all columns)

        conditions: a list of the conditions for the WHERE statement,
            may use a string for a single column

        order: the columns to sort the output by

        distinct: returns only distinct columns if True

        params: values to be filled in with ? substitution,
            much safer than using %s or {} to fill values
        """
        ret = None
        if self.curs:
            if isinstance(tables, list):
                tables = ", ".join(tables)
            if isinstance(columns, list):
                columns = ", ".join(columns)
            if isinstance(conditions, list):
                conditions = " AND ".join(conditions)
            if isinstance(order, list):
                order = ", ".join(order)

            statement = "SELECT {} FROM {}".format(columns, tables)
            if conditions:
                statement += " WHERE {}".format(conditions)
            if order:
                statement += " ORDER BY {}".format(order)
            statement += ";"

            try:
                self.curs.execute(statement, params)
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % statement)
                raise
            ret = self.curs.fetchall()
        return ret

    def update(self, table, fields, conditions=[], params=[]):
        r"""
        Updates data in the given table

        fields: a dictionary with fields as the keys
            and the value to insert as the values

        conditions: a list of the conditions for the WHERE statement,
            may use a string for a single column

        params: values to be filled in with ? substitution,
            much safer than using %s or {} to fill values

        Returns the number of updated rows
        """
        ret = -1
        if self.curs:
            if isinstance(table, list):
                table = ", ".join(table)
            if isinstance(conditions, list):
                conditions = " AND ".join(conditions)

            data = []
            newparams = []
            for key, value in fields.items():
                data.append('%s=?' % key)
                newparams.append(value)
            data = ','.join(data)
            newparams.extend(params)
            params = newparams

            statement = "UPDATE {} SET {}".format(table, data)
            if conditions:
                statement += " WHERE {}".format(conditions)
            statement += ";"

            try:
                self.curs.execute(statement, params)
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % statement)
                raise
            ret = self.curs.rowcount
        return ret

    def delete(self, table, conditions=[], params=[]):
        r"""
        Deletes the rows with the given conditions
        Deletes all rows if conditions omitted

        table: the name of the tables to delete data from

        conditions: a list of the conditions of which rows to delete,
            may use a string for a single column

        params: values to be filled in with ? substitution,
            much safer than using %s or {} to fill values
        """
        ret = -1
        if self.curs:
            if isinstance(conditions, list):
                conditions = " AND ".join(conditions)

            statement = "DELETE FROM {}".format(table)
            if conditions:
                statement += " WHERE {}".format(conditions)
            statement += ";"

            try:
                self.curs.execute(statement, params)
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % statement)
                raise
            ret = self.curs.rowcount
        return ret

    def drop_table(self, table):
        r"""
        Drops the given table

        Returns if the operation was successful
        """
        ret = False
        if self.curs:
            statement = "DROP TABLE {}".format(table)
            statement += ';'
            try:
                self.curs.execute(statement, params)
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % statement)
                raise
            ret = True
        return ret

    def dump(self):
        r"""
        Output an iterator that yeilds SQL sattements to build the database.
        A very hacked together implementation, may need to be fixed.
        """
        conn = sqlite3.connect(self.file)
        for item in conn.iterdump():
            yield item
        conn.close()

    def list_tables(self):
        r"""
        Returns a list of tables in the database
        """
        ret = []
        if self.curs:
            try:
                self.curs.execute("SELECT name FROM sqlite_master WHERE type='table';")
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % "SELECT * FROM dbname.sqlite_master WHERE type='table';")
                raise
            ret = self.curs.fetchall()
            ret = list(map(lambda a: a['name'], ret))
        return ret

    def list_columns(self, table):
        r"""
        Returns a list of columns for the given table
        """
        ret = []
        if self.curs:
            try:
                self.curs.execute("SELECT sql FROM sqlite_master WHERE tbl_name=? AND type = 'table';", [table])
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % "SELECT sql FROM sqlite_master WHERE tbl_name=? AND type='table';")
                raise
            ret = self.curs.fetchall()
            ret = map(lambda a: a['sql'], ret)
            ret = ''.join(ret)
            ret = re.findall(r'\(?(\S+) \S+[,)]', ret)
        return ret

    def drop_columns(self, table, columns=[]):
        ret = False
        if self.curs:
            if isinstance(columns, str):
                columns = [columns]
            cols = filter(lambda a: a not in columns, self.list_columns(table))
            cols = ','.join(cols)
            for statement in [
                "CREATE TEMPORARY TABLE {0}_backup({1});",
                "INSERT INTO {0}_backup SELECT {1} FROM {0};",
                "DROP TABLE {0};",
                "CREATE TABLE {0}({1});",
                "INSERT INTO {0} SELECT {1} FROM {0}_backup;",
                "DROP TABLE {0}_backup",
            ]:
                statement = statement.format(table, cols)
                try:
                    self.curs.execute(statement)
                except:
                    if self.debug:
                        sys.stderr.write("%s\n" % statement)
                    self.rollback()
                    raise
            ret = True
        return ret

    def add_column(self, table, column, type):
        ret = False
        if self.curs:
            type = self.data_types.get(type, type)
            statement = "ALTER TABLE %s ADD %s %s;" % (table, column, type)
            try:
                self.curs.execute(statement)
            except:
                if self.debug:
                    sys.stderr.write("%s\n" % statement)
                self.rollback()
                raise
            ret = True
        return ret
