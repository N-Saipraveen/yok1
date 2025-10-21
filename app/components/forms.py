import reflex as rx
from app.states.state import State


def _input_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    type: str = "text",
) -> rx.Component:
    """Helper to create a styled input field."""
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1.5"),
        rx.el.input(
            placeholder=placeholder,
            default_value=value,
            on_change=on_change,
            type=type,
            class_name="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200",
        ),
        class_name="w-full",
    )


def _connection_status() -> rx.Component:
    """Displays the current connection status."""
    return rx.cond(
        State.connection_status != "",
        rx.el.div(
            rx.cond(
                State.connection_status == "success",
                rx.icon("square_check", class_name="text-green-500"),
                rx.icon("circle_x", class_name="text-red-500"),
            ),
            rx.el.p(
                rx.cond(
                    State.connection_status == "success",
                    "Connection successful!",
                    "Connection failed.",
                ),
                class_name="ml-2 text-sm font-medium",
            ),
            class_name=rx.cond(
                State.connection_status == "success",
                "flex items-center p-3 rounded-lg bg-green-50 text-green-700",
                "flex items-center p-3 rounded-lg bg-red-50 text-red-700",
            ),
        ),
        None,
    )


def sql_connection_form() -> rx.Component:
    """Form for SQL database connection details."""
    return rx.el.div(
        rx.el.div(
            _input_field("Host", "e.g., 127.0.0.1", State.sql_host, State.set_sql_host),
            _input_field(
                "Port",
                "e.g., 3306",
                State.sql_port.to_string(),
                State.set_sql_port,
                type="number",
            ),
            _input_field("Username", "e.g., root", State.sql_user, State.set_sql_user),
            _input_field(
                "Password",
                "Enter password",
                State.sql_password,
                State.set_sql_password,
                type="password",
            ),
            _input_field(
                "Database", "e.g., my_db", State.sql_database, State.set_sql_database
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4",
        ),
        _connection_status(),
        rx.el.button(
            rx.cond(
                State.is_connecting,
                rx.spinner(class_name="mr-2"),
                rx.icon("plug-zap", class_name="mr-2"),
            ),
            rx.cond(State.is_connecting, "Connecting...", "Test Connection"),
            on_click=State.test_sql_connection,
            disabled=State.is_connecting,
            class_name="mt-4 flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-all duration-200",
        ),
        class_name="space-y-4 p-6 bg-white border border-gray-200 rounded-xl shadow-sm",
    )


def mongo_connection_form() -> rx.Component:
    """Form for MongoDB connection details."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                _input_field(
                    "Connection String",
                    "mongodb://...",
                    State.mongo_conn_string,
                    State.set_mongo_conn_string,
                ),
                class_name="md:col-span-2",
            ),
            _input_field(
                "Database",
                "e.g., my_app_db",
                State.mongo_database,
                State.set_mongo_database,
            ),
            _input_field(
                "Collection",
                "e.g., users",
                State.mongo_collection,
                State.set_mongo_collection,
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4",
        ),
        _connection_status(),
        rx.el.button(
            rx.cond(
                State.is_connecting,
                rx.spinner(class_name="mr-2"),
                rx.icon("plug-zap", class_name="mr-2"),
            ),
            rx.cond(State.is_connecting, "Connecting...", "Test Connection"),
            on_click=State.test_mongo_connection,
            disabled=State.is_connecting,
            class_name="mt-4 flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 transition-all duration-200",
        ),
        class_name="space-y-4 p-6 bg-white border border-gray-200 rounded-xl shadow-sm",
    )


def json_upload_form() -> rx.Component:
    """Component for uploading JSON files."""
    return rx.upload.root(
        rx.el.div(
            rx.el.div(
                rx.icon("cloud_upload", size=48, class_name="text-gray-400 mx-auto"),
                rx.el.p(
                    "Drag & drop files here, or ",
                    rx.el.span(
                        "click to browse", class_name="text-indigo-600 font-semibold"
                    ),
                    class_name="mt-4 text-sm text-gray-600",
                ),
                rx.cond(
                    State.is_uploading,
                    rx.el.div(
                        rx.spinner(class_name="text-indigo-500"),
                        rx.el.p(
                            "Uploading...", class_name="text-sm text-gray-500 ml-2"
                        ),
                        class_name="flex items-center justify-center mt-2",
                    ),
                    None,
                ),
                rx.foreach(
                    State.uploaded_files,
                    lambda filename: rx.el.div(
                        rx.icon("file-text", class_name="text-indigo-500"),
                        rx.el.span(
                            filename,
                            class_name="ml-2 text-sm font-medium text-gray-700",
                        ),
                        class_name="mt-2 flex items-center bg-gray-100 px-3 py-1.5 rounded-md",
                    ),
                ),
                class_name="text-center",
            ),
            class_name="flex flex-col items-center justify-center w-full h-64 p-6 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:bg-gray-50 transition-colors duration-200",
        ),
        id="upload-json",
        on_drop=State.handle_upload(rx.upload_files(upload_id="upload-json")),
    )