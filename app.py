import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np

from tabs.gray_tab import GrayTab
from tabs.channels_tab import ChannelsTab
from tabs.hsv_tab import HsvTab


class ImageApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Обработка изображений")
        self.root.geometry("1200x800")
        self.original_bgr = None      
        self.original_rgb = None      
        self.hsv = None               
        self.current_result = None   
        self._tk_images = []

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.root, padding=5)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(top, text="Открыть изображение",
                   command=self.open_image).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Сохранить результат",
                   command=self.save_result).pack(side=tk.LEFT, padx=3)

        self.status = ttk.Label(top, text="Изображение не загружено",
                                foreground="gray")
        self.status.pack(side=tk.LEFT, padx=15)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.gray_tab = GrayTab(self.nb, self)
        self.channels_tab = ChannelsTab(self.nb, self)
        self.hsv_tab = HsvTab(self.nb, self)

        self.nb.add(self.gray_tab, text="1) Оттенки серого и разность")
        self.nb.add(self.channels_tab, text="2) Каналы R, G, B")
        self.nb.add(self.hsv_tab, text="3) HSV")


    def register_tk_image(self, tkimg):
        self._tk_images.append(tkimg)
        return tkimg

    def set_status(self, text, color="black"):
        self.status.config(text=text, foreground=color)

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Изображения",
                        "*.png *.jpg *.jpeg *.bmp"),
                       ("Все файлы", "*.*")])
        if not path:
            return

        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img is None:
            messagebox.showerror("Ошибка", "Не удалось открыть изображение")
            return

        self.original_bgr = img
        self.original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.current_result = None
        self.set_status(f"Загружено: {path}", "black")

        self.channels_tab.reset()
        self.gray_tab.reset()

        self.channels_tab.run_channels()
        self.gray_tab.run_gray()

    def save_result(self):
        if self.current_result is None:
            messagebox.showwarning("Ошибка", "Файл не выбран")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
        if not path:
            return
        rgb = self.current_result
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        ext = "." + path.split(".")[-1]
        ok, buf = cv2.imencode(ext, bgr)
        if ok:
            buf.tofile(path)
            self.set_status(f"Сохранено: {path}", "green")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить файл")