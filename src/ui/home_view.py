# src/ui/home_view.py
import customtkinter as ctk

from src.ui import theme as T
from src.ui.widgets import AnvilLogo, GradientButton


class HomeView(ctk.CTkFrame):

    def __init__(self, master, controller, on_assistant, on_quiz, **kwargs):

        super().__init__(master, fg_color=T.BG_DEEP, **kwargs)
        
        self.controller = controller

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


        settings_frame = ctk.CTkFrame(center, fg_color="transparent")
        settings_frame.grid(row=3, column=0, pady=(60, 0))

        ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=T.TEXT_PRIMARY
        ).grid(row=0, column=0, pady=(0, 10))

        pdf_engine_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        pdf_engine_frame.grid(row=1, column=0)
        
        ctk.CTkLabel(
            pdf_engine_frame,
            text="PDF Parser:",
            font=T.FONT_BODY,
            text_color=T.TEXT_SECONDARY
        ).grid(row=0, column=0, padx=(0, 10))
        
        engine_var = ctk.StringVar(value=self.controller.pdf_engine)
        
        def on_engine_change(choice):
            engine_map = {
                "PyMuPDF (Fast)": "pymupdf",
                "Docling (Recommended)": "docling",
                "Marker (Complex)": "marker"
            }
            self.controller.set_pdf_engine(engine_map.get(choice, "pymupdf"))

        reverse_map = {
            "pymupdf": "PyMuPDF (Fast)",
            "docling": "Docling (Recommended)",
            "marker": "Marker (Complex)"
        }
        engine_var.set(reverse_map.get(self.controller.pdf_engine, "PyMuPDF (Fast)"))

        ctk.CTkOptionMenu(
            pdf_engine_frame,
            values=["PyMuPDF (Fast)", "Docling (Recommended)", "Marker (Complex)"],
            variable=engine_var,
            command=on_engine_change,
            fg_color=T.BG_SURFACE,
            button_color=T.ACCENT,
            button_hover_color=T.ACCENT_HOVER,
            dropdown_fg_color=T.BG_SURFACE,
        ).grid(row=0, column=1)
