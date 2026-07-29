# src/ui/widgets.py
import customtkinter as ctk

from src.ui import theme as T


class AnvilLogo(ctk.CTkFrame):

    def __init__(self, master, **kwargs):

        super().__init__(master, fg_color="transparent", **kwargs)

        ctk.CTkLabel(
            self,
            text="ANVIL",
            font=T.FONT_LOGO,
            text_color=T.ACCENT_BLUE,
        ).pack(side="left")


class LoadingDots(ctk.CTkFrame):
    """Animated three-dot loader for async operations."""


    FRAMES = ["   ", ".  ", ".. ", "..."]


    def __init__(self, master, text: str = "Thinking", **kwargs):

        super().__init__(master, fg_color="transparent", **kwargs)

        self._text = text

        self._frame_idx = 0

        self._job = None

        self.label = ctk.CTkLabel(
            self,
            text=f"{text}{self.FRAMES[0]}",
            font=T.FONT_SMALL,
            text_color=T.TEXT_SECONDARY,
            anchor="w",
        )

        self.label.pack(anchor="w")


    def start(self) -> None:

        self._tick()


    def stop(self) -> None:

        if self._job:

            self.after_cancel(self._job)

            self._job = None

        self.label.configure(text="")


    def _tick(self) -> None:

        self._frame_idx = (self._frame_idx + 1) % len(self.FRAMES)

        self.label.configure(text=f"{self._text}{self.FRAMES[self._frame_idx]}")

        self._job = self.after(400, self._tick)


class GradientButton(ctk.CTkButton):

    def __init__(self, master, **kwargs):

        defaults = dict(
            fg_color=T.ACCENT_BLUE,
            hover_color=T.ACCENT_PURPLE,
            text_color=T.TEXT_PRIMARY,
            font=T.FONT_BODY,
            corner_radius=T.CORNER_RADIUS_SM,
            height=44,
        )

        defaults.update(kwargs)

        super().__init__(master, **defaults)


class ChatBubble(ctk.CTkFrame):

    def __init__(self, master, text: str, is_user: bool = False, **kwargs):

        bg = T.BG_USER_BUBBLE if is_user else "transparent"

        anchor = "e" if is_user else "w"

        super().__init__(master, fg_color="transparent", **kwargs)


        bubble = ctk.CTkFrame(
            self,
            fg_color=bg,
            corner_radius=T.CORNER_RADIUS,
        )

        side = "right" if is_user else "left"

        bubble.pack(side=side, padx=(80 if is_user else 0, 0 if is_user else 80))


        ctk.CTkLabel(
            bubble,
            text=text,
            font=T.FONT_BODY,
            text_color=T.TEXT_PRIMARY,
            wraplength=520,
            justify="left" if not is_user else "right",
        ).pack(padx=16, pady=12, anchor=anchor)
