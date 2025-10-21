import reflex as rx
import logging
from typing import Literal
from bson import ObjectId

ConversionType = Literal["sql_to_nosql", "nosql_to_sql", "json_to_sql", "json_to_nosql"]


def _convert_mongo_types(doc):
    if isinstance(doc, dict):
        return {key: _convert_mongo_types(value) for key, value in doc.items()}
    elif isinstance(doc, list):
        return [_convert_mongo_types(item) for item in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    return doc


class State(rx.State):
    """Manages the state for the DataBridge application."""

    active_tab: ConversionType = "sql_to_nosql"
    uploaded_files: list[str] = []
    is_uploading: bool = False
    connection_status: str = ""
    is_connecting: bool = False
    sql_tables: list[str] = []
    mongo_collections: list[str] = []
    preview_data: list[dict] = []
    selected_table: str = ""
    selected_collection: str = ""
    download_ready: bool = False
    download_filename: str = ""
    download_content: str = ""
    sql_host: str = "localhost"
    sql_port: int = 3306
    sql_user: str = ""
    sql_password: str = ""
    sql_database: str = ""
    mongo_conn_string: str = ""
    mongo_database: str = ""
    mongo_collection: str = ""

    def _reset_download_state(self):
        self.download_ready = False
        self.download_filename = ""
        self.download_content = ""

    def _reset_preview(self):
        self.preview_data = []
        self._reset_download_state()

    @rx.event
    def set_active_tab(self, tab_name: ConversionType):
        """Sets the currently active conversion tab."""
        self.active_tab = tab_name
        self.connection_status = ""
        self.sql_tables = []
        self.mongo_collections = []
        self._reset_preview()

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handles the JSON file upload."""
        self.is_uploading = True
        yield
        for file in files:
            upload_data = await file.read()
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / file.filename
            with file_path.open("wb") as f:
                f.write(upload_data)
            self.uploaded_files.append(file.filename)
        self.is_uploading = False
        return

    @rx.event(background=True)
    async def test_sql_connection(self):
        """Tests the SQL database connection and fetches table names."""
        async with self:
            self.is_connecting = True
            self.connection_status = ""
            self.sql_tables = []
            self._reset_preview()
        yield
        try:
            import mysql.connector

            conn = mysql.connector.connect(
                host=self.sql_host,
                port=self.sql_port,
                user=self.sql_user,
                password=self.sql_password,
                database=self.sql_database,
                connect_timeout=5,
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            conn.close()
            async with self:
                self.connection_status = "success"
                self.sql_tables = tables
            yield rx.toast.success("SQL Connection Successful!")
        except mysql.connector.Error as e:
            logging.exception(f"SQL connection error: {e}")
            async with self:
                self.connection_status = "error"
            yield rx.toast.error(f"SQL Error: {e}")
        finally:
            async with self:
                self.is_connecting = False

    @rx.event(background=True)
    async def on_table_select(self, table: str):
        """Fetches preview data when a SQL table is selected."""
        async with self:
            self.selected_table = table
            self._reset_preview()
        yield
        if not table:
            return
        try:
            import mysql.connector
            import json

            conn = mysql.connector.connect(
                host=self.sql_host,
                port=self.sql_port,
                user=self.sql_user,
                password=self.sql_password,
                database=self.sql_database,
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table} LIMIT 20")
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            for row in data:
                for key, value in row.items():
                    if hasattr(value, "isoformat"):
                        row[key] = value.isoformat()
            async with self:
                self.preview_data = data
        except Exception as e:
            logging.exception(f"Error fetching SQL preview: {e}")
            yield rx.toast.error(f"Preview Error: {e}")

    @rx.event(background=True)
    async def on_collection_select(self, collection: str):
        """Fetches preview data when a MongoDB collection is selected."""
        async with self:
            self.selected_collection = collection
            self._reset_preview()
        yield
        if not collection:
            return
        try:
            import pymongo
            from bson import ObjectId
            import json

            client = pymongo.MongoClient(self.mongo_conn_string)
            db = client[self.mongo_database]
            coll = db[collection]
            data = list(coll.find().limit(20))
            client.close()
            processed_data = _convert_mongo_types(data)
            async with self:
                self.preview_data = processed_data
        except Exception as e:
            logging.exception(f"Error fetching Mongo preview: {e}")
            yield rx.toast.error(f"Preview Error: {e}")

    @rx.event(background=True)
    async def execute_conversion(self):
        """Executes the selected conversion and prepares the download."""
        async with self:
            self._reset_download_state()
        converter = self._get_converter()
        if not converter:
            yield rx.toast.error("Invalid conversion type.")
            return
        try:
            filename, content = await converter()
            async with self:
                self.download_filename = filename
                self.download_content = content
                self.download_ready = True
            yield rx.toast.success("Conversion successful! Your download is ready.")
        except Exception as e:
            logging.exception(f"Conversion failed: {e}")
            yield rx.toast.error(f"Conversion Error: {e}")

    def _get_converter(self):
        """Returns the appropriate conversion function based on the active tab."""
        if self.active_tab == "sql_to_nosql":
            return self._convert_sql_to_nosql
        elif self.active_tab == "nosql_to_sql":
            return self._convert_nosql_to_sql
        elif self.active_tab == "json_to_sql":
            return self._convert_json_to_sql
        elif self.active_tab == "json_to_nosql":
            return self._convert_json_to_nosql
        return None

    async def _convert_sql_to_nosql(self):
        """Converts SQL table data to a JSON string for NoSQL."""
        import json

        return (f"{self.selected_table}.json", json.dumps(self.preview_data, indent=2))

    async def _convert_nosql_to_sql(self):
        """Converts MongoDB collection data to SQL INSERT statements."""
        if not self.preview_data:
            return (f"{self.selected_collection}.sql", "-- No data to convert.")
        table_name = self.selected_collection
        columns = list(self.preview_data[0].keys())
        create_statement = f"CREATE TABLE `{table_name}` (\n"
        for col in columns:
            sample_val = self.preview_data[0][col]
            sql_type = "VARCHAR(255)"
            if isinstance(sample_val, int):
                sql_type = "INT"
            elif isinstance(sample_val, float):
                sql_type = "FLOAT"
            elif isinstance(sample_val, bool):
                sql_type = "BOOLEAN"
            elif col == "_id":
                sql_type = "VARCHAR(24)"
            create_statement += f"  `{col}` {sql_type},\n"
        create_statement = (
            create_statement.rstrip(""",
""")
            + """
);

"""
        )
        insert_statements = ""
        for row in self.preview_data:
            values = []
            for col in columns:
                val = row.get(col)
                if val is None:
                    values.append("NULL")
                elif isinstance(val, bool):
                    values.append(str(val).upper())
                elif isinstance(val, (int, float)):
                    values.append(val)
                else:
                    values.append(f"""'{str(val).replace("'", "''")}'""")
            insert_statements += f"INSERT INTO `{table_name}` (`{'`, `'.join(columns)}`) VALUES ({', '.join(map(str, values))});\n"
        return (f"{table_name}.sql", create_statement + insert_statements)

    async def _convert_json_to_sql(self):
        """Converts uploaded JSON to SQL."""
        if not self.uploaded_files:
            raise ValueError("No JSON file uploaded.")
        import json
        import os

        filename = self.uploaded_files[-1]
        self.selected_collection = os.path.splitext(filename)[0]
        filepath = rx.get_upload_dir() / filename
        with open(filepath, "r") as f:
            data = json.load(f)
        self.preview_data = data if isinstance(data, list) else [data]
        return await self._convert_nosql_to_sql()

    async def _convert_json_to_nosql(self):
        """Converts uploaded JSON to a formatted JSON string."""
        if not self.uploaded_files:
            raise ValueError("No JSON file uploaded.")
        import json

        filepath = rx.get_upload_dir() / self.uploaded_files[-1]
        with open(filepath, "r") as f:
            data = json.load(f)
        return (f"{self.uploaded_files[-1]}", json.dumps(data, indent=2))

    @rx.event
    def download_converted_file(self):
        """Serves the converted file for download."""
        return rx.download(data=self.download_content, filename=self.download_filename)

    @rx.event(background=True)
    async def test_mongo_connection(self):
        """Tests the MongoDB connection and fetches collection names."""
        async with self:
            self.is_connecting = True
            self.connection_status = ""
            self.mongo_collections = []
            self._reset_preview()
        yield
        try:
            import pymongo

            client = pymongo.MongoClient(
                self.mongo_conn_string, serverSelectionTimeoutMS=5000
            )
            client.server_info()
            db = client[self.mongo_database]
            collections = db.list_collection_names()
            client.close()
            async with self:
                self.connection_status = "success"
                self.mongo_collections = collections
            yield rx.toast.success("MongoDB Connection Successful!")
        except Exception as e:
            logging.exception(f"Mongo connection error: {e}")
            async with self:
                self.connection_status = "error"
            yield rx.toast.error(f"Mongo Error: {e}")
        finally:
            async with self:
                self.is_connecting = False