"""Окно Tkinter для просмотра каркасной карты."""

from __future__ import annotations

import tkinter as tk
from math import ceil

from fdf.errors import FdfError
from fdf.model import Map
from fdf.projection import Camera, height_color, lerp_color

ScreenPoint = tuple[float, float]
BACKGROUND = "#101827"
PANEL = "#1A2638"
TEXT = "#E2EBFA"
HINT = "#A9BCD7"
PAN_STEPS = {"left": (-24, 0), "right": (24, 0), "up": (0, -24), "down": (0, 24)}
RUSSIAN_SHORTCUTS = {"е": "t", "й": "q", "у": "e", "к": "r"}
WINDOWS_SHORTCUTS = {ord(key.upper()): key for key in "tqer"}


class App:
    """Владеть окном, камерой и обработчиками событий."""

    def __init__(self, height_map: Map, map_name: str = "") -> None:
        self.height_map = height_map
        self.camera = Camera()
        self._min_height = min(point.z for point in height_map)
        self._max_height = max(point.z for point in height_map)
        self._colors = [
            point.color or height_color(point.z, self._min_height, self._max_height)
            for point in height_map
        ]
        self._fit_scale = 1.0
        self._model_center: ScreenPoint = (0.0, 0.0)
        self._fit_needed = True
        self._redraw_id: str | None = None
        self._render_error: FdfError | None = None

        try:
            self._root = tk.Tk()
        except tk.TclError as error:
            raise FdfError(f"не удалось открыть графическое окно: {error}") from error

        self._windows = self._root.tk.call("tk", "windowingsystem") == "win32"
        self._root.title(f"FdF — {map_name}" if map_name else "FdF — карта высот")
        self._root.geometry("960x640")
        self._root.minsize(550, 340)
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)

        self._canvas = tk.Canvas(self._root, background=BACKGROUND, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._status = tk.Label(
            self._root,
            anchor="w",
            background=PANEL,
            foreground=TEXT,
            padx=16,
            pady=6,
            font=("TkDefaultFont", 10),
        )
        self._status.grid(row=1, column=0, sticky="ew")
        controls = tk.Label(
            self._root,
            text="Колесо  масштаб   Стрелки  сдвиг   + / −  высота   "
            "T  вид   Q / E  угол   R  сброс   Esc  выход",
            anchor="w",
            background=PANEL,
            foreground=HINT,
            padx=16,
            pady=3,
        )
        controls.grid(row=2, column=0, sticky="ew")

        self._canvas.bind("<Configure>", self._on_resize)
        self._canvas.bind("<MouseWheel>", self._on_wheel)
        self._canvas.bind("<Button-4>", self._on_wheel)
        self._canvas.bind("<Button-5>", self._on_wheel)
        self._root.bind("<KeyPress>", self._on_key)
        self._root.protocol("WM_DELETE_WINDOW", self._close)

    def run(self) -> None:
        """Запустить цикл обработки событий окна."""
        self._root.mainloop()
        if self._render_error is not None:
            raise self._render_error

    def _close(self) -> None:
        if self._redraw_id is not None:
            self._root.after_cancel(self._redraw_id)
        self._root.destroy()

    def _on_resize(self, _event: tk.Event[tk.Canvas]) -> None:
        self._request_redraw(refit=True)

    def _on_wheel(self, event: tk.Event[tk.Canvas]) -> None:
        if event.num == 4:
            steps = 1.0
        elif event.num == 5:
            steps = -1.0
        else:
            steps = min(4.0, max(-4.0, event.delta / 120))

        old_scale = self.camera.scale
        new_scale = min(self._fit_scale * 8, max(self._fit_scale * 0.2, old_scale * 1.18**steps))
        ratio = new_scale / old_scale
        center_x, center_y = self._model_center
        self.camera.offset_x = center_x + (self.camera.offset_x - center_x) * ratio
        self.camera.offset_y = center_y + (self.camera.offset_y - center_y) * ratio
        self.camera.scale = new_scale
        self._request_redraw()

    def _on_key(self, event: tk.Event[tk.Misc]) -> None:
        key = RUSSIAN_SHORTCUTS.get(event.char.lower(), event.keysym.lower())
        if self._windows and key == "??":
            key = WINDOWS_SHORTCUTS.get(event.keycode, key)
        if key == "escape":
            self._close()
        elif key in PAN_STEPS:
            dx, dy = PAN_STEPS[key]
            self.camera.offset_x += dx
            self.camera.offset_y += dy
            center_x, center_y = self._model_center
            self._model_center = center_x + dx, center_y + dy
            self._request_redraw()
        elif key in {"plus", "equal", "kp_add"}:
            self.camera.z_scale = min(8.0, self.camera.z_scale + 0.2)
            self._request_redraw(refit=True)
        elif key in {"minus", "underscore", "kp_subtract"}:
            self.camera.z_scale = max(0.0, self.camera.z_scale - 0.2)
            self._request_redraw(refit=True)
        elif key == "t":
            self.camera.top_view = not self.camera.top_view
            self._request_redraw(refit=True)
        elif key == "q":
            self.camera.angle = max(0.0, self.camera.angle - 5)
            self._request_redraw(refit=True)
        elif key == "e":
            self.camera.angle = min(85.0, self.camera.angle + 5)
            self._request_redraw(refit=True)
        elif key == "r":
            self.camera = Camera()
            self._request_redraw(refit=True)

    def _request_redraw(self, *, refit: bool = False) -> None:
        self._fit_needed = self._fit_needed or refit
        if self._redraw_id is not None:
            self._root.after_cancel(self._redraw_id)
        self._redraw_id = self._root.after(25, self._draw)

    def _draw(self) -> None:
        self._redraw_id = None
        try:
            self._draw_map()
        except (ArithmeticError, ValueError, tk.TclError):
            self._render_error = FdfError("не удалось спроецировать карту с указанными высотами")
            self._close()

    def _draw_map(self) -> None:
        width = self._canvas.winfo_width()
        height = self._canvas.winfo_height()
        if self._fit_needed:
            self.camera.fit(self.height_map, width, height)
            self._fit_scale = self.camera.scale
            self._model_center = width / 2, height / 2
            self._fit_needed = False

        self._canvas.delete("all")
        points = [self.camera.project(point) for point in self.height_map]
        if len(points) == 1:
            x, y = points[0]
            self._canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=self._colors[0], outline="")

        columns = self.height_map.width
        for index, point in enumerate(self.height_map):
            x0, y0 = points[index]
            for neighbor in self.height_map.neighbors(point):
                target = neighbor.y * columns + neighbor.x
                x1, y1 = points[target]
                if max(x0, x1) < 0 or min(x0, x1) > width:
                    continue
                if max(y0, y1) < 0 or min(y0, y1) > height:
                    continue
                self._draw_edge((x0, y0), (x1, y1), self._colors[index], self._colors[target])

        mode = "Вид сверху" if self.camera.top_view else "Изометрия"
        zoom = self.camera.scale / self._fit_scale
        self._status.configure(
            text=f"{mode}   ·   {columns} × {self.height_map.height}   ·   "
            f"z {self._min_height}…{self._max_height}   ·   "
            f"Масштаб ×{zoom:.2f}   ·   Высота ×{self.camera.z_scale:.1f}   ·   "
            f"Угол {self.camera.angle:g}°"
        )

    def _draw_edge(
        self, start: ScreenPoint, end: ScreenPoint, color_a: str, color_b: str
    ) -> None:
        if color_a == color_b:
            self._canvas.create_line(*start, *end, fill=color_a)
            return

        dx, dy = end[0] - start[0], end[1] - start[1]
        segments = min(16, max(1, ceil(max(abs(dx), abs(dy)) / 3)))
        x0, y0 = start
        for index in range(segments):
            position = (index + 1) / segments
            x1, y1 = start[0] + dx * position, start[1] + dy * position
            mix = index / (segments - 1) if segments > 1 else 0.5
            color = lerp_color(color_a, color_b, mix)
            self._canvas.create_line(x0, y0, x1, y1, fill=color)
            x0, y0 = x1, y1
