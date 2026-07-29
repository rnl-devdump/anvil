# src/ui/quiz_view.py
import random
import threading
import customtkinter as ctk
from tkinter import messagebox

from src.ui import theme as T
from src.ui.import_dialog import ImportDialog
from src.ui.widgets import AnvilLogo, GradientButton


class QuizView(ctk.CTkFrame):

    LETTERS = ("A", "B", "C", "D")


    def __init__(self, master, controller, on_back, **kwargs):

        super().__init__(master, fg_color=T.BG_DEEP, **kwargs)

        self.controller = controller

        self.on_back = on_back


        self.questions: list[dict] = []

        self.current_index = 0

        self.selected_choice: str | None = None

        self._evaluating = False


        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(1, weight=1)


        self._build_header()
        self._build_sidebar()
        self._build_quiz_panel()


    def _build_header(self) -> None:

        header = ctk.CTkFrame(self, fg_color="transparent")

        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(20, 8))

        header.grid_columnconfigure(1, weight=1)


        AnvilLogo(header).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Quiz",
            font=T.FONT_HEADING,
            text_color=T.TEXT_PRIMARY,
        ).grid(row=0, column=1)

        ctk.CTkButton(
            header,
            text="← Home",
            width=80,
            fg_color="transparent",
            hover_color=T.BG_CARD,
            text_color=T.TEXT_SECONDARY,
            command=self.on_back,
        ).grid(row=0, column=2, sticky="e")


    def _build_sidebar(self) -> None:

        sidebar = ctk.CTkFrame(
            self,
            fg_color=T.BG_SIDEBAR,
            corner_radius=T.CORNER_RADIUS_SM,
            width=240,
        )

        sidebar.grid(row=1, column=0, sticky="nsew", padx=(24, 8), pady=(0, 24))

        sidebar.grid_propagate(False)

        sidebar.grid_rowconfigure(1, weight=1)

        sidebar.grid_columnconfigure(0, weight=1)


        ctk.CTkLabel(
            sidebar,
            text="Quiz History",
            font=T.FONT_BODY,
            text_color=T.TEXT_SECONDARY,
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")


        self.history_list = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            scrollbar_button_color=T.BG_CARD,
        )

        self.history_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=4)

        self.history_list.grid_columnconfigure(0, weight=1)


        GradientButton(
            sidebar,
            text="Import",
            command=self._open_import,
        ).grid(row=2, column=0, padx=16, pady=16, sticky="ew")


        self.refresh_history()


    def _build_quiz_panel(self) -> None:

        panel = ctk.CTkFrame(
            self,
            fg_color=T.BG_CARD,
            corner_radius=T.CORNER_RADIUS,
            border_width=1,
            border_color=T.BORDER,
        )

        panel.grid(row=1, column=1, sticky="nsew", padx=(8, 24), pady=(0, 24))

        panel.grid_columnconfigure(0, weight=1)

        panel.grid_rowconfigure(3, weight=1)


        top = ctk.CTkFrame(panel, fg_color="transparent")

        top.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 8))

        top.grid_columnconfigure(0, weight=1)


        self.q_label = ctk.CTkLabel(
            top,
            text="Question 0 of 0",
            font=T.FONT_SMALL,
            text_color=T.TEXT_SECONDARY,
        )
        self.q_label.grid(row=0, column=0, sticky="w")


        self.pct_label = ctk.CTkLabel(
            top,
            text="0% done",
            font=T.FONT_SMALL,
            text_color=T.ACCENT_PURPLE,
        )
        self.pct_label.grid(row=0, column=1, sticky="e")


        self.progress = ctk.CTkProgressBar(
            panel,
            progress_color=T.ACCENT_BLUE,
            fg_color=T.BG_OPTION,
            height=6,
            corner_radius=3,
        )

        self.progress.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 16))

        self.progress.set(0)


        self.question_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.question_frame.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 12))
        self.question_frame.grid_columnconfigure(1, weight=1)


        self.num_badge = ctk.CTkLabel(
            self.question_frame,
            text="1",
            width=36,
            height=36,
            fg_color=T.ACCENT_BLUE,
            corner_radius=8,
            font=T.FONT_BODY,
            text_color=T.TEXT_PRIMARY,
        )
        self.num_badge.grid(row=0, column=0, padx=(0, 16), sticky="nw")


        self.question_text = ctk.CTkLabel(
            self.question_frame,
            text="Import materials to generate your first quiz.",
            font=T.FONT_QUESTION,
            text_color=T.TEXT_PRIMARY,
            wraplength=520,
            justify="left",
            anchor="w",
        )
        self.question_text.grid(row=0, column=1, sticky="ew")


        self.answer_frame = ctk.CTkScrollableFrame(
            panel,
            fg_color="transparent",
            height=280,
        )
        self.answer_frame.grid(row=3, column=0, sticky="nsew", padx=28, pady=(0, 12))
        self.answer_frame.grid_columnconfigure(0, weight=1)


        self.feedback = ctk.CTkLabel(
            panel,
            text="",
            font=T.FONT_BODY,
            text_color=T.TEXT_SECONDARY,
            wraplength=560,
            justify="left",
        )
        self.feedback.grid(row=4, column=0, sticky="ew", padx=28, pady=(0, 8))


        nav = ctk.CTkFrame(panel, fg_color="transparent")
        nav.grid(row=5, column=0, sticky="ew", padx=28, pady=(0, 24))

        nav.grid_columnconfigure(0, weight=1)


        self.submit_btn = GradientButton(
            nav,
            text="Submit",
            width=120,
            command=self._submit,
        )
        self.submit_btn.grid(row=0, column=1, padx=(0, 8))


        ctk.CTkButton(
            nav,
            text="Next →",
            width=100,
            fg_color=T.BG_OPTION,
            hover_color=T.BORDER,
            text_color=T.TEXT_PRIMARY,
            command=self._next_question,
        ).grid(row=0, column=2)


    def refresh_history(self) -> None:

        for w in self.history_list.winfo_children():
            w.destroy()


        records = self.controller.quiz_store.all

        if not records:

            ctk.CTkLabel(
                self.history_list,
                text="No quizzes yet",
                font=T.FONT_SMALL,
                text_color=T.TEXT_MUTED,
            ).grid(row=0, column=0, pady=12, padx=8, sticky="w")
            return


        for i, record in enumerate(records):

            btn = ctk.CTkButton(
                self.history_list,
                text=f"{record['title']}\n{record['question_count']} questions",
                font=T.FONT_SMALL,

                fg_color=T.BG_OPTION if record["id"] != self.controller.active_quiz_id else T.ACCENT_BLUE,
                hover_color=T.BG_CARD,
                text_color=T.TEXT_PRIMARY,
                anchor="w",
                height=56,

                command=lambda rid=record["id"]: self.load_quiz(rid),
            )

            btn.grid(row=i, column=0, sticky="ew", pady=4, padx=4)


    def _open_import(self) -> None:

        ImportDialog(self.winfo_toplevel(), self.controller, self._on_import_complete)


    def _on_import_complete(self, record: dict) -> None:

        self.refresh_history()

        self.load_quiz(record["id"])


    def load_quiz(self, quiz_id: str) -> None:
        try:

            self.questions = self.controller.load_quiz_from_history(quiz_id)
        except ValueError as e:

            messagebox.showerror("Error", str(e))
            return

        self.current_index = 0

        self.refresh_history()

        self._render_question()


    def _render_question(self) -> None:

        for w in self.answer_frame.winfo_children():
            w.destroy()


        self.feedback.configure(text="")

        self.selected_choice = None


        total = len(self.questions)

        if total == 0:

            self.q_label.configure(text="Question 0 of 0")
            self.pct_label.configure(text="0% done")
            self.progress.set(0)
            return


        idx = self.current_index
        q = self.questions[idx]
        qtype = q["type"]


        self.q_label.configure(text=f"Question {idx + 1} of {total}")
        pct = int(((idx) / total) * 100)
        self.pct_label.configure(text=f"{pct}% done")
        self.progress.set(idx / total)


        self.num_badge.configure(text=str(idx + 1))
        self.question_text.configure(text=q["question"])


        if qtype == "MULTIPLE_CHOICE":
            self._render_mc(q)
        elif qtype == "IDENTIFICATION":
            self._render_identification()
        elif qtype == "ENUMERATION":
            self._render_enumeration()
        elif qtype == "PARAGRAPH":
            self._render_paragraph()
        elif qtype == "TRUE_FALSE":
            self._render_tf(q)
        elif qtype == "MATCHING":
            self._render_matching(q)
        else:
            ctk.CTkLabel(
                self.answer_frame,
                text=f"Unsupported type: {qtype}",
                text_color=T.ERROR,
            ).grid(row=0, column=0, sticky="w")


    def _render_mc(self, q: dict) -> None:

        for i, choice in enumerate(q["choices"]):

            letter = self.LETTERS[i]

            row = ctk.CTkFrame(self.answer_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=6)
            row.grid_columnconfigure(1, weight=1)


            badge = ctk.CTkLabel(
                row,
                text=letter,
                width=32,
                height=32,
                fg_color=T.BG_DEEP,
                corner_radius=8,
                text_color=T.ACCENT_PURPLE,
                font=T.FONT_BODY,
            )
            badge.grid(row=0, column=0, padx=(0, 12))


            btn = ctk.CTkButton(
                row,
                text=choice,
                anchor="w",
                fg_color=T.BG_OPTION,
                hover_color=T.BORDER,
                text_color=T.TEXT_SECONDARY,
                font=T.FONT_BODY,
                height=48,

                command=lambda c=choice, b=None: self._select_mc(c),
            )
            btn.grid(row=0, column=1, sticky="ew")

            btn.configure(command=lambda c=choice, b=btn: self._select_mc(c, b))

            btn._choice = choice


    def _select_mc(self, choice: str, btn=None) -> None:

        self.selected_choice = choice

        for w in self.answer_frame.winfo_children():
            if isinstance(w, ctk.CTkFrame):
                for child in w.winfo_children():

                    if isinstance(child, ctk.CTkButton) and hasattr(child, "_choice"):

                        child.configure(
                            fg_color=T.ACCENT_BLUE if child._choice == choice else T.BG_OPTION
                        )


    def _render_identification(self) -> None:

        self.answer_entry = ctk.CTkEntry(
            self.answer_frame,
            placeholder_text="Type your answer…",
            fg_color=T.BG_OPTION,
            border_color=T.BORDER,
            text_color=T.TEXT_PRIMARY,
            font=T.FONT_BODY,
            height=44,
        )
        self.answer_entry.grid(row=0, column=0, sticky="ew", pady=8)


    def _render_enumeration(self) -> None:

        ctk.CTkLabel(
            self.answer_frame,
            text="Enter items separated by commas or new lines:",
            font=T.FONT_SMALL,
            text_color=T.TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))


        self.answer_text = ctk.CTkTextbox(
            self.answer_frame,
            fg_color=T.BG_OPTION,
            text_color=T.TEXT_PRIMARY,
            font=T.FONT_BODY,
            height=120,
        )
        self.answer_text.grid(row=1, column=0, sticky="ew")


    def _render_paragraph(self) -> None:
        ctk.CTkLabel(
            self.answer_frame,
            text="Write your answer in a short paragraph:",
            font=T.FONT_SMALL,
            text_color=T.TEXT_MUTED,
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.answer_text = ctk.CTkTextbox(
            self.answer_frame,
            fg_color=T.BG_OPTION,
            text_color=T.TEXT_PRIMARY,
            font=T.FONT_BODY,
            height=160,
        )
        self.answer_text.grid(row=1, column=0, sticky="ew")

    def _render_tf(self, q: dict) -> None:
        choices = ["True", "False"]
        for i, choice in enumerate(choices):
            row = ctk.CTkFrame(self.answer_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=6)
            row.grid_columnconfigure(1, weight=1)

            btn = ctk.CTkButton(
                row,
                text=choice,
                anchor="w",
                fg_color=T.BG_OPTION,
                hover_color=T.BORDER,
                text_color=T.TEXT_SECONDARY,
                font=T.FONT_BODY,
                height=48,
                command=lambda c=choice, b=None: self._select_mc(c),
            )
            btn.grid(row=0, column=1, sticky="ew")
            btn.configure(command=lambda c=choice, b=btn: self._select_mc(c, b))
            btn._choice = choice

    def _render_matching(self, q: dict) -> None:
        self.matching_vars = {}
        pairs = q["pairs"]
        responses = [p["response"] for p in pairs]
        
        shuffled = list(responses)
        random.shuffle(shuffled)
        options = ["Select..."] + shuffled
        
        for i, pair in enumerate(pairs):
            premise = pair["premise"]
            
            row = ctk.CTkFrame(self.answer_frame, fg_color="transparent")
            row.grid(row=i, column=0, sticky="ew", pady=6)
            row.grid_columnconfigure(1, weight=1)

            lbl = ctk.CTkLabel(
                row,
                text=premise,
                font=T.FONT_BODY,
                text_color=T.TEXT_PRIMARY,
                wraplength=360,
                justify="left",
                anchor="w",
            )
            lbl.grid(row=0, column=0, padx=(0, 16), sticky="w")

            var = ctk.StringVar(value="Select...")
            dropdown = ctk.CTkOptionMenu(
                row,
                values=options,
                variable=var,
                fg_color=T.BG_OPTION,
                button_color=T.BG_CARD,
                button_hover_color=T.BORDER,
                text_color=T.TEXT_SECONDARY,
                dropdown_fg_color=T.BG_CARD,
                dropdown_text_color=T.TEXT_PRIMARY,
            )
            dropdown.grid(row=0, column=1, sticky="e")
            self.matching_vars[premise] = var


    def _get_user_answer(self) -> any:
        q = self.questions[self.current_index]
        qtype = q["type"]

        if qtype == "MULTIPLE_CHOICE":
            return self.selected_choice or ""
        
        if qtype == "TRUE_FALSE":
            if not self.selected_choice:
                return None
            return self.selected_choice == "True"
            
        if qtype == "MATCHING":
            ans = {premise: var.get() for premise, var in self.matching_vars.items()}
            if any(val == "Select..." for val in ans.values()):
                return None
            return ans

        if qtype == "IDENTIFICATION":
            return self.answer_entry.get().strip()

        if qtype in ("ENUMERATION", "PARAGRAPH"):
            return self.answer_text.get("1.0", "end").strip()

        return ""


    def _submit(self) -> None:
        if not self.questions or self._evaluating:
            return

        q = self.questions[self.current_index]
        qtype = q["type"]
        user = self._get_user_answer()

        if user is None or (isinstance(user, str) and not user):
            messagebox.showwarning("Answer required", "Please provide a complete answer first.")
            return

        if qtype == "PARAGRAPH":
            self._submit_paragraph(q, user)
            return

        if qtype == "MULTIPLE_CHOICE":
            correct = user == q["answer"]
            self._show_result(correct, q["answer"])

        elif qtype == "TRUE_FALSE":
            correct = user == q["answer"]
            self._show_result(correct, str(q["answer"]))

        elif qtype == "MATCHING":
            expected = {p["premise"]: p["response"] for p in q["pairs"]}
            correct_count = sum(1 for p, r in user.items() if r == expected[p])
            total = len(expected)
            correct = correct_count == total
            self._show_result(
                correct,
                "All pairs matched correctly",
                extra=f"Matched {correct_count}/{total} pairs.",
            )

        elif qtype == "IDENTIFICATION":
            correct = user.lower().strip() == q["answer"].lower().strip()
            self._show_result(correct, q["answer"])

        elif qtype == "ENUMERATION":
            expected = [a.lower().strip() for a in q["answer"]]
            given = [p.strip().lower() for p in user.replace("\n", ",").split(",") if p.strip()]
            matches = sum(1 for g in given if any(g in e or e in g for e in expected))
            correct = matches >= len(expected) * 0.6
            self._show_result(
                correct,
                ", ".join(q["answer"]),
                extra=f"Matched {matches}/{len(expected)} expected items.",
            )


    def _submit_paragraph(self, q: dict, user: str) -> None:

        self._evaluating = True

        self.submit_btn.configure(state="disabled")

        self.feedback.configure(text="Evaluating your answer…", text_color=T.TEXT_SECONDARY)


        def work():

            return self.controller.evaluate_paragraph(q["question"], q["answer"], user)


        def done(result):

            self._evaluating = False

            self.submit_btn.configure(state="normal")

            status = "Correct" if result.is_correct else ("Relevant" if result.is_relevant else "Needs work")

            color = T.SUCCESS if result.is_correct else (T.WARNING if result.is_relevant else T.ERROR)

            self.feedback.configure(
                text=f"{status} · Score {result.score}/100\n{result.feedback}",
                text_color=color,
            )


        def fail(exc):

            self._evaluating = False

            self.submit_btn.configure(state="normal")

            self.feedback.configure(text=str(exc), text_color=T.ERROR)


        def runner():
            try:

                r = work()

                self.after(0, done, r)
            except Exception as e:

                self.after(0, fail, e)


        threading.Thread(target=runner, daemon=True).start()


    def _show_result(self, correct: bool, expected: str, extra: str = "") -> None:

        if correct:

            msg = f"✓ Correct! {extra}".strip()

            color = T.SUCCESS

        else:

            msg = f"✗ Incorrect. Expected: {expected}. {extra}".strip()

            color = T.ERROR

        self.feedback.configure(text=msg, text_color=color)


    def _next_question(self) -> None:

        if not self.questions:
            return

        if self.current_index < len(self.questions) - 1:

            self.current_index += 1

            self._render_question()

        else:

            self.pct_label.configure(text="100% done")
            self.progress.set(1.0)

            self.feedback.configure(
                text="Quiz complete! Select another from history or import new materials.",
                text_color=T.ACCENT_PURPLE,
            )
