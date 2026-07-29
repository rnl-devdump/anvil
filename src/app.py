# src/app.py
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]

if str(_ROOT) not in sys.path:

    sys.path.insert(0, str(_ROOT))

import customtkinter as ctk

from src.app_controller import AppController
from src.ui import theme as T
from src.ui.assistant_view import AssistantView
from src.ui.home_view import HomeView
from src.ui.quiz_view import QuizView


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        ctk.set_appearance_mode("dark")

        ctk.set_default_color_theme("dark-blue")


        self.controller = AppController()

        self.configure(fg_color=T.BG_DEEP)


        self.title("ANVIL")

        self.geometry("1024x720")

        self.minsize(900, 640)


        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)


        self.container = ctk.CTkFrame(self, fg_color=T.BG_DEEP)

        self.container.grid(row=0, column=0, sticky="nsew")

        self.container.grid_columnconfigure(0, weight=1)

        self.container.grid_rowconfigure(0, weight=1)


        self.views: dict[str, ctk.CTkFrame] = {}

        self._show_home()


    def _clear_views(self) -> None:

        for child in self.container.winfo_children():

            child.destroy()

        self.views.clear()


    def _show_home(self) -> None:

        self._clear_views()

        view = HomeView(
            self.container,
            controller=self.controller,
            on_assistant=self._show_assistant,
            on_quiz=self._show_quiz,
        )

        view.grid(row=0, column=0, sticky="nsew")

        self.views["home"] = view


    def _show_assistant(self) -> None:

        self._clear_views()

        view = AssistantView(
            self.container,
            controller=self.controller,
            on_back=self._show_home,
        )

        view.grid(row=0, column=0, sticky="nsew")

        self.views["assistant"] = view


    def _show_quiz(self) -> None:

        self._clear_views()

        view = QuizView(
            self.container,
            controller=self.controller,
            on_back=self._show_home,
        )

        view.grid(row=0, column=0, sticky="nsew")

        self.views["quiz"] = view


    def run(self) -> None:

        self.mainloop()


if __name__ == "__main__":

    App().run()
