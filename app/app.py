import reflex as rx
from app.states.state import State
from app.components.forms import (
    sql_connection_form,
    mongo_connection_form,
    json_upload_form,
)
from app.components.previews import data_preview_section


def _tab_button(label: str, tab_name: str) -> rx.Component:
    """Helper to create a styled tab button."""
    is_active = State.active_tab == tab_name
    return rx.el.button(
        label,
        on_click=State.set_active_tab(tab_name),
        class_name=rx.cond(
            is_active,
            "px-4 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-lg shadow-md transition-all duration-200",
            "px-4 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-800 rounded-lg transition-all duration-200",
        ),
    )


def _form_section(
    title: str, subtitle: str, form_component: rx.Component
) -> rx.Component:
    """Helper to create a form section with title and subtitle."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(title, class_name="text-lg font-semibold text-gray-900"),
            rx.el.p(subtitle, class_name="text-sm text-gray-500 mt-1"),
            class_name="mb-4",
        ),
        form_component,
        class_name="w-full",
    )


def index() -> rx.Component:
    """The main page of the DataBridge application."""
    return rx.el.main(
        rx.el.div(
            rx.el.div(
                rx.icon("database-zap", size=36, class_name="text-indigo-600"),
                rx.el.div(
                    rx.el.h1(
                        "DataBridge", class_name="text-3xl font-bold text-gray-900"
                    ),
                    rx.el.p(
                        "Seamless Database & JSON Conversion",
                        class_name="text-md text-gray-600 mt-1",
                    ),
                    class_name="ml-4",
                ),
                class_name="flex items-center justify-center mb-10",
            ),
            rx.el.div(
                rx.el.div(
                    _tab_button("SQL → NoSQL", "sql_to_nosql"),
                    _tab_button("NoSQL → SQL", "nosql_to_sql"),
                    _tab_button("JSON → SQL", "json_to_sql"),
                    _tab_button("JSON → NoSQL", "json_to_nosql"),
                    class_name="flex space-x-2 p-1.5 bg-gray-100 rounded-xl",
                ),
                rx.el.div(
                    rx.match(
                        State.active_tab,
                        (
                            "sql_to_nosql",
                            _form_section(
                                "1. Connect to SQL Source",
                                "Provide credentials for your MySQL database.",
                                sql_connection_form(),
                            ),
                        ),
                        (
                            "nosql_to_sql",
                            _form_section(
                                "1. Connect to MongoDB Source",
                                "Provide details for your MongoDB instance.",
                                mongo_connection_form(),
                            ),
                        ),
                        (
                            "json_to_sql",
                            _form_section(
                                "1. Upload JSON Source",
                                "Upload a JSON file (array of objects or single object).",
                                json_upload_form(),
                            ),
                        ),
                        (
                            "json_to_nosql",
                            _form_section(
                                "1. Upload JSON Source",
                                "Upload a JSON file to be converted.",
                                json_upload_form(),
                            ),
                        ),
                        rx.el.div("Select a conversion type."),
                    ),
                    data_preview_section(),
                    class_name="mt-8 w-full",
                ),
                class_name="w-full max-w-4xl p-6 md:p-8 bg-white border border-gray-200/80 rounded-2xl shadow-lg",
            ),
            class_name="flex flex-col items-center w-full px-4",
        ),
        class_name="font-['Poppins'] bg-gray-50 min-h-screen py-12 md:py-20",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)