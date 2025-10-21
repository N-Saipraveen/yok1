import reflex as rx
from app.states.state import State


def _table_selector() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            "Select Table", class_name="block text-sm font-medium text-gray-700 mb-1.5"
        ),
        rx.el.select(
            rx.el.option("Select a table", value="", disabled=True),
            rx.foreach(
                State.sql_tables, lambda table: rx.el.option(table, value=table)
            ),
            on_change=State.on_table_select,
            value=State.selected_table,
            class_name="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200",
        ),
        class_name="w-full",
    )


def _collection_selector() -> rx.Component:
    return rx.el.div(
        rx.el.label(
            "Select Collection",
            class_name="block text-sm font-medium text-gray-700 mb-1.5",
        ),
        rx.el.select(
            rx.el.option("Select a collection", value="", disabled=True),
            rx.foreach(
                State.mongo_collections, lambda coll: rx.el.option(coll, value=coll)
            ),
            on_change=State.on_collection_select,
            value=State.selected_collection,
            class_name="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200",
        ),
        class_name="w-full",
    )


def _conversion_controls_section() -> rx.Component:
    """Section with conversion and download buttons."""
    return rx.el.div(
        rx.el.h3(
            "3. Convert & Download",
            class_name="text-lg font-semibold text-gray-900 mb-2",
        ),
        rx.el.div(
            rx.el.p(
                "Your data is ready for conversion.",
                class_name="text-sm text-gray-500 mb-4",
            ),
            rx.cond(
                State.download_ready,
                rx.el.button(
                    rx.icon("cloud_download", class_name="mr-2"),
                    "Download ",
                    rx.el.span(
                        State.download_filename, class_name="font-semibold ml-1"
                    ),
                    on_click=State.download_converted_file,
                    class_name="w-full flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-green-600 rounded-lg shadow-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200",
                ),
                rx.el.button(
                    rx.icon("wand-sparkles", class_name="mr-2"),
                    "Convert & Prepare Download",
                    on_click=State.execute_conversion,
                    class_name="w-full flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200",
                ),
            ),
            class_name="p-6 bg-white border border-gray-200 rounded-xl shadow-sm",
        ),
        class_name="w-full mt-8",
    )


def data_preview_section() -> rx.Component:
    show_selector = (
        (State.active_tab == "sql_to_nosql") | (State.active_tab == "nosql_to_sql")
    ) & (State.connection_status == "success")
    return rx.el.div(
        rx.cond(
            show_selector,
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "2. Select Source & Preview Data",
                        class_name="text-lg font-semibold text-gray-900",
                    ),
                    rx.el.p(
                        "Choose a table or collection to preview its contents.",
                        class_name="text-sm text-gray-500 mt-1",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.match(
                        State.active_tab,
                        ("sql_to_nosql", _table_selector()),
                        ("nosql_to_sql", _collection_selector()),
                    ),
                    class_name="w-full p-6 bg-white border border-gray-200 rounded-xl shadow-sm",
                ),
                class_name="w-full mt-8",
            ),
            None,
        ),
        rx.cond(State.preview_data.length() > 0, _conversion_controls_section(), None),
    )