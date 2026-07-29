# src/ui/import_dialog.py
import threading
import customtkinter as ctk
from tkinter import messagebox

from src.ui import theme as T
from src.ui.widgets import GradientButton, LoadingDots


class ImportDialog(ctk.CTkToplevel):

    def __init__(self, master, controller, on_complete, **kwargs):

        super().__init__(master, **kwargs)

        self.controller = controller

        self.on_complete = on_complete

        self._generating = False


        self.title("Import Materials")

        self.geometry("520x480")

        self.configure(fg_color=T.BG_DEEP)

        self.resizable(False, False)

        self.transient(master)

        self.grab_set()


        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)


        ctk.CTkLabel(
            self,
            text="Import Study Materials",
            font=T.FONT_HEADING,
            text_color=T.TEXT_PRIMARY,
        ).grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")


        ctk.CTkLabel(
            self,
            text="Upload a PDF/TXT file or paste plain text to generate a quiz.",
            font=T.FONT_SMALL,
            text_color=T.TEXT_SECONDARY,
        ).grid(row=1, column=0, padx=24, sticky="w")


        self.paste_box = ctk.CTkTextbox(
            self,
            fg_color=T.BG_CARD,
            border_color=T.BORDER,
            border_width=1,
            text_color=T.TEXT_PRIMARY,
            font=T.FONT_BODY,
            corner_radius=T.CORNER_RADIUS_SM,
        )
        self.paste_box.grid(row=2, column=0, sticky="nsew", padx=24, pady=12)

        self.pref_entry = ctk.CTkEntry(
            self,
            placeholder_text="Preferences (e.g. I prefer multiple choice...)",
            font=T.FONT_BODY,
            fg_color=T.BG_CARD,
            border_color=T.BORDER,
            text_color=T.TEXT_PRIMARY,
        )
        self.pref_entry.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 12))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Browse PDF / TXT",
            fg_color=T.BG_OPTION,
            hover_color=T.BG_CARD,
            text_color=T.TEXT_PRIMARY,
            command=self._browse,
        ).pack(side="left", padx=(0, 8))

        self.status = ctk.CTkLabel(
            self,
            text="",
            font=T.FONT_SMALL,
            text_color=T.TEXT_SECONDARY,
        )
        self.status.grid(row=5, column=0, padx=24, sticky="w")

        self.loader = LoadingDots(self, text="Generating quiz")
        self.loader.grid(row=6, column=0, padx=24, sticky="w")

        self.gen_btn = GradientButton(
            self,
            text="Import & Generate Quiz",
            command=self._import_and_generate,
        )
        self.gen_btn.grid(row=7, column=0, padx=24, pady=(8, 24), sticky="ew")

        self._loaded_path: str | None = None

    def _browse(self) -> None:
        path = self.controller.open_file()
        if path:
            self._loaded_path = path
            self.paste_box.delete("1.0", "end")
            self.status.configure(text=f"Loaded: {path}")

    def _import_and_generate(self) -> None:
        if self._generating:
            return

        pasted = self.paste_box.get("1.0", "end").strip()
        prefs = self.pref_entry.get().strip()

        def load():
            if pasted:
                self.controller.load_pasted_text(pasted)
                return "Pasted text"
            if self._loaded_path:
                return self._loaded_path
            raise ValueError("Select a file or paste text first.")

        def generate():
            source = load()
            total_holder = [0]

            def progress(current, total, preview):
                total_holder[0] = total
                self.after(
                    0,
                    lambda: self.status.configure(
                        text=f"Chunk {current}/{total}: {preview[:50]}…"
                    ),
                )

            questions = self.controller.generate_quiz(on_progress=progress, preferences=prefs)
            record = self.controller.save_quiz_to_history(questions)
            return record, total_holder[0]


        self._generating = True
        self.gen_btn.configure(state="disabled")
        self.loader.start()


        def runner():
            try:

                result = generate()

                self.after(0, self._done, result)
            except Exception as e:

                self.after(0, self._fail, e)


        threading.Thread(target=runner, daemon=True).start()


    def _done(self, result) -> None:

        record, chunks = result

        self._generating = False
        self.loader.stop()
        self.gen_btn.configure(state="normal")

        self.on_complete(record)

        messagebox.showinfo(
            "Quiz ready",
            f"Generated {record['question_count']} questions from {chunks} chunks.",
        )

        self.destroy()


    def _fail(self, exc) -> None:

        self._generating = False
        self.loader.stop()
        self.gen_btn.configure(state="normal")

        messagebox.showerror("Import failed", str(exc))
