import tkinter as tk
from tkinter import ttk
import numpy as np

from .base_tab import BaseTab
from common.image_utils import to_tk_image, show_hist


class ChannelsTab(BaseTab): 
    def _build(self):
        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, pady=5)

        self.lbl_R = self.make_image_cell(body, "Канал R", 0, 0)
        self.lbl_G = self.make_image_cell(body, "Канал G", 0, 1)
        self.lbl_B = self.make_image_cell(body, "Канал B", 0, 2)

        self.hist_R_frame = ttk.LabelFrame(body, text="Гистограмма R")
        self.hist_G_frame = ttk.LabelFrame(body, text="Гистограмма G")
        self.hist_B_frame = ttk.LabelFrame(body, text="Гистограмма B")
        self.hist_R_frame.grid(row=1, column=0, sticky="nsew")
        self.hist_G_frame.grid(row=1, column=1, sticky="nsew")
        self.hist_B_frame.grid(row=1, column=2, sticky="nsew")

        for c in range(3):
            body.columnconfigure(c, weight=1)
        body.rowconfigure(0, weight=2)
        body.rowconfigure(1, weight=2)

    def reset(self):
        for lbl in (self.lbl_R, self.lbl_G, self.lbl_B):
            lbl.config(image="")
        for f in (self.hist_R_frame, self.hist_G_frame, self.hist_B_frame):
            self.clear_children(f)

    def run_channels(self):
        rgb = self.app.original_rgb
        if rgb is None:
            return

        R = rgb[:, :, 0]
        G = rgb[:, :, 1]
        B = rgb[:, :, 2]
        zero = np.zeros_like(R)

        rgb_R = np.dstack([R, zero, zero])
        rgb_G = np.dstack([zero, G, zero])
        rgb_B = np.dstack([zero, zero, B])

        self.lbl_R.config(image=to_tk_image(self.app, rgb_R))
        self.lbl_G.config(image=to_tk_image(self.app, rgb_G))
        self.lbl_B.config(image=to_tk_image(self.app, rgb_B))

        show_hist(self.hist_R_frame, R, "R", color="red")
        show_hist(self.hist_G_frame, G, "G", color="green")
        show_hist(self.hist_B_frame, B, "B", color="blue")