# src/ui/home_view.py
import customtkinter as ctk

from src.ui import theme as T
from src.ui.widgets import AnvilLogo, GradientButton


class HomeView(ctk.CTkFrame):

    def __init__(self, master, on_assistant, on_quiz, **kwargs):

        super().__init__(master, fg_color=T.BG_DEEP, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(2, weight=1)


        header = ctk.CTkFrame(self, fg_color="transparent")

        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(28, 0))

        AnvilLogo(header).pack(side="left")


        center = ctk.CTkFrame(self, fg_color="transparent")

        center.grid(row=2, column=0)

        center.grid_columnconfigure(0, weight=1)


        ctk.CTkLabel(
            center,
            text="Welcome to Anvil",
            font=T.FONT_HEADING,
            text_color=T.TEXT_PRIMARY,
        ).grid(row=0, column=0, pady=(0, 8))


        ctk.CTkLabel(
            center,
            text=(
                "Your study buddy where knowledge is forged through learning.\n"
                "Select a mode to begin — ask questions about your materials\n"
                "or test yourself with an AI-generated quiz."
            ),
            font=T.FONT_BODY,
            text_color=T.TEXT_SECONDARY,
            justify="center",
        ).grid(row=1, column=0, pady=(0, 36))


        btn_row = ctk.CTkFrame(center, fg_color="transparent")
        btn_row.grid(row=2, column=0)


        GradientButton(
            btn_row,
            text="Assistant",
            width=180,
            command=on_assistant,
        ).grid(row=0, column=0, padx=12)


        GradientButton(
            btn_row,
            text="Quiz Me!",
            width=180,
            command=on_quiz,
        ).grid(row=0, column=1, padx=12)
