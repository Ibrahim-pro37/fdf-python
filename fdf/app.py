"""Окно Tkinter для просмотра каркасной карты."""

from __future__ import annotations

import tkinter as tk

from fdf.errors import FdfError
from fdf.model import Map
from fdf.projection import Camera


class App:
    """Отобразить карту и обработать события окна."""

    def __init__(self, height_map: Map, map_name: str = "") -> None:
        self.height_map = height_map
        self.camera = Camera()
        self._redraw_id: str | None = None
        try:
            self._root = tk.Tk()
        except tk.TclError as error:
            raise FdfError(f"не удалось открыть графическое окно: {error}") from error

        self._root.title(f"FdF — {map_name}" if map_name else "FdF — карта высот")
        self._root.geometry("960x640")
        self._canvas = tk.Canvas(self._root, background="#101827", highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)
        self._canvas.bind("<Configure>", self._on_resize)
        self._root.bind("<Escape>", self._on_escape)
        self._root.protocol("WM_DELETE_WINDOW", self._close)

    def run(self) -> None:
        """Запустить цикл обработки событий окна."""
        self._root.mainloop()

    def _on_escape(self, _event: tk.Event[tk.Misc]) -> None:
        self._close()

    def _close(self) -> None:
        if self._redraw_id is not None:
            self._root.after_cancel(self._redraw_id)
        self._root.destroy()

    def _on_resize(self, _event: tk.Event[tk.Canvas]) -> None:
        if self._redraw_id is not None:
            self._root.after_cancel(self._redraw_id)
        self._redraw_id = self._root.after(25, self._draw)

    def _draw(self) -> None:
        self._redraw_id = None
        self.camera.fit(self.height_map, self._canvas.winfo_width(), self._canvas.winfo_height())
        self._canvas.delete("all")
        points = [self.camera.project(point) for point in self.height_map]
        if len(points) == 1:
            x, y = points[0]
            self._canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#528DF6", outline="")

        columns = self.height_map.width
        for index, point in enumerate(self.height_map):
            for neighbor in self.height_map.neighbors(point):
                target = neighbor.y * columns + neighbor.x
                self._canvas.create_line(*points[index], *points[target], fill="#528DF6")
