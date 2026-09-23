import tkinter as tk
from tkinter import ttk
import numpy as np

from .base_tab import BaseTab
from common.image_utils import to_tk_image


class HsvTab(BaseTab):

    def _build(self):
        ctrl = ttk.LabelFrame(self, text="HSV-коррекция", padding=5)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        self.hue_var = tk.IntVar(value=0)
        self.sat_var = tk.IntVar(value=100)
        self.val_var = tk.IntVar(value=100)

        ttk.Label(ctrl, text="Оттенок (сдвиг, -180..180)").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Scale(
            ctrl,
            from_=-180,
            to=180,
            orient=tk.HORIZONTAL,
            variable=self.hue_var,
            command=lambda e: self.update_hsv(),
            length=300,
        ).grid(row=0, column=1, padx=10)
        ttk.Label(ctrl, textvariable=self.hue_var).grid(row=0, column=2)

        ttk.Label(ctrl, text="Насыщенность (%, 0..200)").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Scale(
            ctrl,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.sat_var,
            command=lambda e: self.update_hsv(),
            length=300,
        ).grid(row=1, column=1, padx=10)
        ttk.Label(ctrl, textvariable=self.sat_var).grid(row=1, column=2)

        ttk.Label(ctrl, text="Яркость (%, 0..200)").grid(
            row=2, column=0, sticky="w"
        )
        ttk.Scale(
            ctrl,
            from_=0,
            to=200,
            orient=tk.HORIZONTAL,
            variable=self.val_var,
            command=lambda e: self.update_hsv(),
            length=300,
        ).grid(row=2, column=1, padx=10)
        ttk.Label(ctrl, textvariable=self.val_var).grid(row=2, column=2)

        ttk.Button(
            ctrl,
            text="Сбросить",
            command=self.reset_sliders,
        ).grid(row=0, column=3, rowspan=3, padx=10)

        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, pady=5)

        self.lbl_hsv_orig = self.make_image_cell(
            body, "Исходное (RGB)", 0, 0
        )
        self.lbl_hsv_res = self.make_image_cell(
            body, "После HSV-коррекции", 0, 1
        )

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

    @staticmethod
    def rgb_to_hsv(rgb):
        rgb = rgb.astype(np.float32) / 255.0

        R = rgb[:, :, 0]
        G = rgb[:, :, 1]
        B = rgb[:, :, 2]

        MAX = np.max(rgb, axis=2)
        MIN = np.min(rgb, axis=2)
        delta = MAX - MIN

        H = np.zeros_like(MAX)

        not_gray = MAX != MIN

        mask = not_gray & (MAX == R) & (G >= B)
        H[mask] = 60.0 * (G[mask] - B[mask]) / delta[mask]

        mask = not_gray & (MAX == R) & (G < B)
        H[mask] = 60.0 * (G[mask] - B[mask]) / delta[mask] + 360.0

        mask = not_gray & (MAX != R) & (MAX == G)
        H[mask] = 60.0 * (B[mask] - R[mask]) / delta[mask] + 120.0

        mask = not_gray & (MAX != R) & (MAX != G) & (MAX == B)
        H[mask] = 60.0 * (R[mask] - G[mask]) / delta[mask] + 240.0

        S = np.zeros_like(MAX)
        non_black = MAX != 0
        S[non_black] = 1.0 - MIN[non_black] / MAX[non_black]

        V = MAX

        return np.dstack((H, S, V))

    @staticmethod
    def hsv_to_rgb(hsv):
        H = hsv[:, :, 0] % 360.0
        S = np.clip(hsv[:, :, 1], 0.0, 1.0)
        V = np.clip(hsv[:, :, 2], 0.0, 1.0)

        H_div_60 = H / 60.0
        H_floor = np.floor(H_div_60)

        Hi = H_floor.astype(np.int32) % 6
        f = H_div_60 - H_floor

        p = V * (1.0 - S)
        q = V * (1.0 - f * S)
        t = V * (1.0 - (1.0 - f) * S)

        R = np.zeros_like(V)
        G = np.zeros_like(V)
        B = np.zeros_like(V)

        mask = Hi == 0
        R[mask] = V[mask]
        G[mask] = t[mask]
        B[mask] = p[mask]

        mask = Hi == 1
        R[mask] = q[mask]
        G[mask] = V[mask]
        B[mask] = p[mask]

        mask = Hi == 2
        R[mask] = p[mask]
        G[mask] = V[mask]
        B[mask] = t[mask]

        mask = Hi == 3
        R[mask] = p[mask]
        G[mask] = q[mask]
        B[mask] = V[mask]

        mask = Hi == 4
        R[mask] = t[mask]
        G[mask] = p[mask]
        B[mask] = V[mask]

        mask = Hi == 5
        R[mask] = V[mask]
        G[mask] = p[mask]
        B[mask] = q[mask]

        rgb = np.dstack((R, G, B))
        return np.rint(np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)

    def reset(self):
        if self.app.original_rgb is None:
            self.app.hsv = None
            self.lbl_hsv_orig.config(image="")
            self.lbl_hsv_res.config(image="")
            return

        self.app.hsv = self.rgb_to_hsv(self.app.original_rgb)

        self.lbl_hsv_orig.config(
            image=to_tk_image(self.app, self.app.original_rgb)
        )
        self.lbl_hsv_res.config(image="")

    def reset_sliders(self):
        self.hue_var.set(0)
        self.sat_var.set(100)
        self.val_var.set(100)
        self.update_hsv()

    def update_hsv(self):
        if self.app.hsv is None:
            return

        hsv = self.app.hsv.copy()

        H = hsv[:, :, 0]
        S = hsv[:, :, 1]
        V = hsv[:, :, 2]

        H = (H + self.hue_var.get()) % 360.0
        S = np.clip(S * self.sat_var.get() / 100.0, 0.0, 1.0)
        V = np.clip(V * self.val_var.get() / 100.0, 0.0, 1.0)

        hsv_result = np.dstack((H, S, V))
        rgb_result = self.hsv_to_rgb(hsv_result)

        self.app.current_result = rgb_result
        self.lbl_hsv_res.config(
            image=to_tk_image(self.app, rgb_result)
        )
