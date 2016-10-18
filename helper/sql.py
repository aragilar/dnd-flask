import sys
import sqlite3

class DB:
    r"""
    A database manager class for sqlite3
    """

    def __init__(self, db=None, commit=True):
        r"""
        db is the file to open the database from
        commit is whether to commit changes before closing
        """
        if db is None:
            db = "data.db"
        self.file = db
        self.will_commit = commit
        self.conn = None
        self.curs = None

    def __call__(self, commit=None):
        r"""
        Creates a new instance of this class with the same parameters
        Useful for multithreading

        e.x.

        database = DB('file.db', commit=True)
        with database() as db:
            db.select('table')
        """
        if commit is None:
            commit = self.will_commit
        return type(self)(db=self.file, commit=commit)

    def connect(self):
        r"""
        Opens the database connection and sets the row factory
        """
        self.conn = sqlite3.connect(self.file)
        self.conn.row_factory = self._to_dict # sqlite3.Row
        self.curs = self.conn.cursor()
        return self

    __enter__ = connect

    def close(self, exception_type=None, exception_value=None, traceback=None):
        r"""
        Closes the connections and commits changes if requested
            when the DB was created
        """
        if self.will_commit:
            self.conn.commit()
        self.conn.close()
        self.conn = None
        self.curs = None

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
        return {desc[0].lower(): value for desc, value in zip(curs.description, row)}

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

    def create_table(self, table, fields={}, ignore_existing=True):
        r"""
        Creates a table with the give fields
        The fields are specified with a dictionary mapping the name to a type
        The type can be a string or the actual Python type desired

        Returns if the creation was successful
        """
        types = {
            None: "NULL",
            str: "TEXT",
            int: "INTEGER",
            float: "REAL",
        }

        if sys.version_info[0] < 3:
            types[unicode] = "TEXT"
        else:
            types[bytes] = "BLOB",

        ret = False
        if self.curs:
            for key, value in fields.items():
                if value is None or isinstance(value, type):
                    value = types[value]
                fields[key] = "{} {}".format(key, value)
            statement = "CREATE TABLE "
            if ignore_existing:
                statement += "IF NOT EXISTS "
            statement += "{} ({})".format(table, ", ".join(fields.values()))
            statement += ";"
            try:
                self.curs.execute(statement)
            except:
                sys.stderr.write("%s\n" % statement)
                raise
            ret = True
        return ret

    def insert(self, table, fields={}):
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
                sys.stderr.write("%s\n" % statement)
                raise
            ret = self.curs.fetchall()
        return ret
