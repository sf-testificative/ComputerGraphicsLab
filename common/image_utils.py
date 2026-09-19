import numpy as np
import cv2
from PIL import Image, ImageTk
import tkinter as tk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def to_tk_image(app, img_rgb, max_w=350, max_h=250):
    im = Image.fromarray(img_rgb)
    im.thumbnail((max_w, max_h), Image.LANCZOS)
    tkimg = ImageTk.PhotoImage(im)
    return app.register_tk_image(tkimg)


def gray_to_rgb(gray):
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)


def show_hist(container, data, title, color="steelblue",
              figsize=(3.2, 2.0), dpi=80):
    for w in container.winfo_children():
        w.destroy()
    fig = Figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)
    ax.hist(np.asarray(data).ravel(), bins=256, range=(0, 255), color=color)
    ax.set_title(title, fontsize=9)
    ax.set_xlim(0, 255)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=container)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)