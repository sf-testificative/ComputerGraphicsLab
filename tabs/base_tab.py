import tkinter as tk
from tkinter import ttk


class BaseTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=5)
        self.app = app
        self._build()

    def _build(self):
        raise NotImplementedError

    def reset(self):
        pass

    @staticmethod
    def make_image_cell(parent, title, r, c):
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
        lbl = ttk.Label(frame, anchor="center")
        lbl.pack(fill=tk.BOTH, expand=True)
        return lbl

    @staticmethod
    def clear_children(widget):
        for w in widget.winfo_children():
            w.destroy()