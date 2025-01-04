import sqlite3
import inspect


class Database:
    def __init__(self, path):
        self.conn = sqlite3.Connection(path)

    @property
    def tables(self):
        SELECT_TABLE_SQL = "SELECT name FROM sqlite_master WHERE type = 'table' ;"
        return [row[0] for row in self.conn.execute(SELECT_TABLE_SQL).fetchall()]

    def create(self, table):
        self.conn.execute(table._get_create_sql())

    def save(self, instance):
        sql, values = instance._get_insert_sql()
        curser = self.conn.execute(sql, values)
        self.conn.commit()
        instance._data["id"] = curser.lastrowid


class Table:
    def __init__(self, **kwargs):
        self._data = {
            "id": None

        }

        for key, value in kwargs.items():
            self._data[key] = value

    @classmethod
    def _get_create_sql(cls):
        CREATE_TABLE_SQL = "CREATE TABLE IF NOT EXISTS {name} ({fields});"
        fields = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT"

        ]

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(f"{name} {col.sql_type}")

            elif isinstance(col, ForeignKey):
                fields.append(f"{name}_id INTEGER")

        fields = ', '.join(fields)
        name = cls.__name__.lower()

        return CREATE_TABLE_SQL.format(name=name, fields=fields)

    def __getattribute__(self, attr_name):
        _data = super().__getattribute__("_data")

        if attr_name in _data:
            return _data[attr_name]

        return super().__getattribute__(attr_name)

    def _get_insert_sql(self):
        INSERT_SQL = "INSERT INTO {name} ({fields}) VALUES ({placeholders});"
        cls = self.__class__
        fields = []
        placeholders = []
        values = []

        for name, col in inspect.getmembers(cls):
            if isinstance(col, Column):
                fields.append(name)
                values.append(getattr(self, name))
                placeholders.append("?")
            elif isinstance(col, ForeignKey):
                fields.append(name)
                values.append(getattr(self, name).id)
                placeholders.append("?")

        fields = ", ".join(fields)
        placeholders = ", ".join(placeholders)

        sql = INSERT_SQL.format(name=cls.__name__.lower(), fields=fields, placeholders=placeholders)

        return sql, values


class Column:
    def __init__(self, column_type):
        self.type = column_type

    @property
    def sql_type(self):
        SQLITE_TYPE_MAP = {
            int: "INTEGER",
            str: "TEXT",
            bool: "INTEGER",  # 0 OR 1
            float: "REAL",
            bytes: "BLOB"

        }
        return SQLITE_TYPE_MAP[self.type]


class ForeignKey:
    def __init__(self, table):
        self.table = table
