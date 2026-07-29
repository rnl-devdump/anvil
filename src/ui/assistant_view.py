# src/ui/assistant_view.py
import threading
import customtkinter as ctk

from src.ui import theme as T
from src.ui.widgets import AnvilLogo, ChatBubble, GradientButton, LoadingDots


class AssistantView(ctk.CTkFrame):

    def __init__(self, master, controller, on_back, **kwargs):

        super().__init__(master, fg_color=T.BG_DEEP, **kwargs)

        self.controller = controller

        self.on_back = on_back

        self._busy = False

        self._chat_row = 0


        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(1, weight=1)


        self._build_header()
        self._build_chat()
        self._build_input()


    def _build_header(self) -> None:

        header = ctk.CTkFrame(self, fg_color="transparent")

        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))

        header.grid_columnconfigure(1, weight=1)


        AnvilLogo(header).grid(row=0, column=0, sticky="w")


        ctk.CTkButton(
            header,
            text="← Home",
            width=80,
            fg_color="transparent",
            hover_color=T.BG_CARD,
            text_color=T.TEXT_SECONDARY,
            command=self.on_back,
        ).grid(row=0, column=2, sticky="e")


        ctk.CTkLabel(
            header,
            text="Assistant",
            font=T.FONT_HEADING,
            text_color=T.TEXT_PRIMARY,
        ).grid(row=0, column=1)


    def _build_chat(self) -> None:

        self.chat_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=T.BG_DEEP,
            scrollbar_button_color=T.BG_CARD,
            scrollbar_button_hover_color=T.ACCENT_BLUE,
        )

        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=8)

        self.chat_scroll.grid_columnconfigure(0, weight=1)


        self._add_ai_message(
            "Hello! Ask me anything about your uploaded document.\n"
            "Import materials from the Quiz section if you haven't yet."
        )


        self.loader = LoadingDots(self.chat_scroll, text="Generating")

        self.loader.grid(row=999, column=0, sticky="w", pady=8)

        self.loader.grid_remove()


    def _build_input(self) -> None:

        bar = ctk.CTkFrame(self, fg_color="transparent")

        bar.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))

        bar.grid_columnconfigure(0, weight=1)


        input_shell = ctk.CTkFrame(
            bar,
            fg_color=T.BG_INPUT,
            corner_radius=T.CORNER_RADIUS_PILL,
            border_width=1,
            border_color=T.BORDER_SUBTLE,
        )

        input_shell.grid(row=0, column=0, sticky="ew")

        input_shell.grid_columnconfigure(0, weight=1)


        self.input_field = ctk.CTkEntry(
            input_shell,
            placeholder_text="Ask Anvil…",
            fg_color="transparent",
            border_width=0,
            text_color=T.TEXT_PRIMARY,
            placeholder_text_color=T.TEXT_MUTED,
            font=T.FONT_BODY,
            height=48,
        )

        self.input_field.grid(row=0, column=0, sticky="ew", padx=(20, 8), pady=4)

        self.input_field.bind("<Return>", lambda _e: self._send())


        GradientButton(
            input_shell,
            text="Send",
            width=90,
            height=36,
            corner_radius=18,
            command=self._send,
        ).grid(row=0, column=1, padx=(0, 8), pady=6)


    def _next_row(self) -> int:

        row = self._chat_row

        self._chat_row += 1

        return row


    def _add_user_message(self, text: str) -> None:

        row = self._next_row()

        bubble = ChatBubble(self.chat_scroll, text, is_user=True)

        bubble.grid(row=row, column=0, sticky="e", pady=6, padx=4)


    def _add_ai_message(self, text: str) -> None:

        row = self._next_row()

        bubble = ChatBubble(self.chat_scroll, text, is_user=False)

        bubble.grid(row=row, column=0, sticky="w", pady=6, padx=4)


    def _show_loader(self, show: bool) -> None:

        if show:

            self.loader.grid(row=999, column=0, sticky="w", pady=8)

            self.loader.start()

        else:

            self.loader.stop()

            self.loader.grid_remove()


    def _send(self) -> None:

        if self._busy:
            return

        question = self.input_field.get().strip()

        if not question:
            return


        self.input_field.delete(0, "end")

        self._add_user_message(question)

        self._busy = True

        self._show_loader(True)


        def work():

            return self.controller.ask(question)


        def on_success(result):

            answer, _sources = result

            self._show_loader(False)

            self._add_ai_message(answer)

            self._busy = False


        def on_error(exc):

            self._show_loader(False)

            self._add_ai_message(f"Sorry — {exc}")

            self._busy = False


        def runner():
            try:

                result = work()

                self.after(0, on_success, result)
            except Exception as e:

                self.after(0, on_error, e)


        threading.Thread(target=runner, daemon=True).start()
