import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2

from .base_tab import BaseTab
from common.image_utils import to_tk_image


class HsvTab(BaseTab):

    def _build(self):
        ctrl = ttk.LabelFrame(self, text="HSV-коррекция", padding=5)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        self.hue_var = tk.IntVar(value=0)
        self.sat_var = tk.IntVar(value=100)
        self.val_var = tk.IntVar(value=100)

        ttk.Label(
            ctrl,
            text="Оттенок (сдвиг, -180..180)"
        ).grid(row=0, column=0, sticky="w")

        ttk.Scale(
            ctrl,
            from_=-180,
            to=180,
            orient=tk.HORIZONTAL,
            variable=self.hue_var,
            command=lambda e: self.update_hsv(),
            length=300
        ).grid(row=0, column=1, padx=10)

        ttk.Label(
            ctrl,
            textvariable=self.hue_var
        ).grid(row=0, column=2)

        ttk.Label(
            ctrl,
            text="Насыщенность (%, 0..200)"
        ).grid(row=1, column=0, sticky="w")

        ttk.Scale(
            ctrl,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.sat_var,
            command=lambda e: self.update_hsv(),
            length=300
        ).grid(row=1, column=1, padx=10)

        ttk.Label(
            ctrl,
            textvariable=self.sat_var
        ).grid(row=1, column=2)

        ttk.Label(
            ctrl,
            text="Яркость (%, 0..200)"
        ).grid(row=2, column=0, sticky="w")

        ttk.Scale(
            ctrl,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.val_var,
            command=lambda e: self.update_hsv(),
            length=300
        ).grid(row=2, column=1, padx=10)

        ttk.Label(
            ctrl,
            textvariable=self.val_var
        ).grid(row=2, column=2)

        ttk.Button(
            ctrl,
            text="Сбросить",
            command=self.reset_sliders
        ).grid(row=0, column=3, rowspan=3, padx=10)

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, pady=5)

        self.lbl_hsv_orig = self.make_image_cell(
            body,
            "Исходное (RGB)",
            0,
            0
        )

        self.lbl_hsv_res = self.make_image_cell(
            body,
            "После HSV-коррекции",
            0,
            1
        )

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

    def reset(self):
        self.lbl_hsv_orig.config(
            image=to_tk_image(
                self.app,
                self.app.original_rgb
            )
            if self.app.original_rgb is not None
            else ""
        )

        self.lbl_hsv_res.config(image="")

    def reset_sliders(self):
        self.hue_var.set(0)
        self.sat_var.set(100)
        self.val_var.set(100)

        self.update_hsv()

    def update_hsv(self):
        if self.app.original_rgb is None:
            return

        hsv = cv2.cvtColor(
            self.app.original_rgb,
            cv2.COLOR_RGB2HSV
        ).astype(np.float32)

        H = hsv[:, :, 0]
        S = hsv[:, :, 1]
        V = hsv[:, :, 2]

        # Изменение оттенка
        H = np.mod(
            H + self.hue_var.get() / 2.0,
            180
        )

        S = np.clip(
            S * self.sat_var.get() / 100.0,
            0,
            255
        )

        V = np.clip(
            V * self.val_var.get() / 100.0,
            0,
            255
        )

        hsv_result = np.dstack(
            (H, S, V)
        ).astype(np.uint8)

        rgb_result = cv2.cvtColor(
            hsv_result,
            cv2.COLOR_HSV2RGB
        )

        self.app.current_result = rgb_result

        self.lbl_hsv_res.config(
            image=to_tk_image(
                self.app,
                rgb_result
            )
        )