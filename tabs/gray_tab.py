import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2

from .base_tab import BaseTab
from common.image_utils import to_tk_image, gray_to_rgb, show_hist

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class GrayTab(BaseTab):

    def _build(self):
        ctrl = ttk.LabelFrame(self, text="Формулы серого", padding=5)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl,
                  text="Вариант 1 (0.299R + 0.587G + 0.114B, Rec.601)"
                  ).grid(row=0, column=0, sticky="w")
        ttk.Label(ctrl,
                  text="Вариант 2 (0.2126R + 0.7152G + 0.0722B, Rec.709)"
                  ).grid(row=1, column=0, sticky="w")

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, pady=5)

        top_row = ttk.Frame(body)
        top_row.grid(row=0, column=0, sticky="nsew")

        self.lbl_gray1 = self.make_image_cell(top_row, "Серое #1", 0, 0)
        self.lbl_gray2 = self.make_image_cell(top_row, "Серое #2", 0, 1)
        self.lbl_diff  = self.make_image_cell(top_row, "Разность |#1 − #2|", 0, 2)

        for i in range(3):
            top_row.columnconfigure(i, weight=1)
        top_row.rowconfigure(0, weight=1)

        self.hist_frame = ttk.LabelFrame(body, text="Гистограммы")
        self.hist_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=3)
        body.rowconfigure(1, weight=2)

        self.gray1 = None
        self.gray2 = None

    def on_image_loaded(self):
        self.run_gray()

    def reset(self):
        for lbl in (self.lbl_gray1, self.lbl_gray2, self.lbl_diff):
            lbl.config(image="")
        self.clear_children(self.hist_frame)
        self.gray1 = None
        self.gray2 = None

    def run_gray(self):
        rgb = self.app.original_rgb
        if rgb is None:
            return

        R = rgb[:, :, 0].astype(np.float32)
        G = rgb[:, :, 1].astype(np.float32)
        B = rgb[:, :, 2].astype(np.float32)

        g1 = 0.299 * R + 0.587 * G + 0.114 * B
        g2 = 0.2126 * R + 0.7152 * G + 0.0722 * B

        self.gray1 = np.clip(g1, 0, 255).astype(np.uint8)
        self.gray2 = np.clip(g2, 0, 255).astype(np.uint8)

        self.lbl_gray1.config(image=to_tk_image(self.app, gray_to_rgb(self.gray1)))
        self.lbl_gray2.config(image=to_tk_image(self.app, gray_to_rgb(self.gray2)))

        self.show_gray_diff()
        self._show_hist_both()

    def _show_hist_both(self):
        self.clear_children(self.hist_frame)

        fig = Figure(figsize=(6.4, 2.3), dpi=80)
        ax1 = fig.add_subplot(121)
        ax1.hist(self.gray1.ravel(), bins=256, range=(0, 255), color="gray")
        ax1.set_title("Гистограмма серого #1", fontsize=9)
        ax1.set_xlim(0, 255)
        ax1.tick_params(labelsize=7)

        ax2 = fig.add_subplot(122)
        ax2.hist(self.gray2.ravel(), bins=256, range=(0, 255), color="dimgray")
        ax2.set_title("Гистограмма серого #2", fontsize=9)
        ax2.set_xlim(0, 255)
        ax2.tick_params(labelsize=7)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.hist_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_gray_diff(self):
        if self.gray1 is None or self.gray2 is None:
            return

        diff = cv2.absdiff(self.gray1, self.gray2)
        self.lbl_diff.config(image=to_tk_image(self.app, gray_to_rgb(diff)))

        self.app.current_result = gray_to_rgb(diff)

        show_hist(self.hist_frame, diff,
                  "Гистограмма разности |#1 − #2|",
                  color="crimson", figsize=(6.4, 2.3))