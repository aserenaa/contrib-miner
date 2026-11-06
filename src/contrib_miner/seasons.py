"""Seasonal dressing: sky colours, surface decorations and the miner's hat. The mine itself never changes."""

from __future__ import annotations

import datetime
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from . import sprites as S
from .layout import GRASS_Y, SKY_DECORATION_MIN_X

if TYPE_CHECKING:
    from .render import Canvas, Scene

Decorate = Callable[["Canvas", "Scene", random.Random], None]
MonthDay = tuple[int, int]


@dataclass(frozen=True)
class Season:
    name: str
    first_day: MonthDay
    last_day: MonthDay
    palette_by_theme: dict[str, dict[str, str]]
    hat_colours: dict[str, str]
    card_border: str
    decorate: Decorate = field(repr=False)

    def active_on(self, day: datetime.date) -> bool:
        return self.first_day <= (day.month, day.day) <= self.last_day


def _surface_spots(scene: Scene, rng: random.Random, count: int, width: int) -> list[int]:
    lo, hi = SKY_DECORATION_MIN_X, scene.w - width - 4
    slot = (hi - lo) // count
    return [lo + i * slot + rng.randrange(max(1, slot - width)) for i in range(count)]


MOON = [
    "..mmm..",
    ".mmmMm.",
    "mmMmmmm",
    "mmmmmMm",
    "mMmmmmm",
    ".mmmMm.",
    "..mmm..",
]
MOON_KEY = {"m": "gold_hi", "M": "gold"}

BAT = [
    "b.....b",
    "bb.b.bb",
    ".bbbbb.",
    "...b...",
]

PUMPKIN = [
    "...s...",
    ".oOoOo.",
    "oeoOoeo",
    "oOoOoOo",
    "ommmmmo",
    ".oOoOo.",
]
PUMPKIN_KEY = {"s": "grass_dark", "o": "copper", "O": "copper_hi", "e": "gold_hi", "m": "gold_hi"}


def _halloween(c: Canvas, scene: Scene, rng: random.Random) -> None:
    mx = scene.w * 3 // 5
    c.blit(MOON, MOON_KEY, mx, 7)
    bat = {"b": "purple_hi" if scene.theme == "dark" else "coal"}
    for dx, dy in ((-30, 9), (12, 5), (40, 11)):
        c.blit(BAT, bat, mx + dx, dy)
    pumpkin_top = GRASS_Y - len(PUMPKIN) + 1
    for x in _surface_spots(scene, rng, 7, len(PUMPKIN[0])):
        c.blit(PUMPKIN, PUMPKIN_KEY, x, pumpkin_top)


TREE = [
    "...*...",
    "...g...",
    "..gGg..",
    "..gog..",
    ".gGgGg.",
    ".ggogg.",
    "gGgGgGg",
    "gogggog",
    "...t...",
]
TREE_KEY = {"*": "gold", "g": "grass_dark", "G": "grass", "o": "shirt", "t": "dirt_light"}


def _snow_on_grass(c: Canvas, scene: Scene, rng: random.Random) -> None:
    c.rect(0, GRASS_Y, scene.w, 1, S.IDX["spark"])
    for x in range(scene.w):
        if rng.random() < 0.35:
            c.set(x, GRASS_Y + 1, S.IDX["spark"])


def _christmas(c: Canvas, scene: Scene, rng: random.Random) -> None:
    _snow_on_grass(c, scene, rng)
    for x in _surface_spots(scene, rng, 7, len(TREE[0])):
        c.blit(TREE, TREE_KEY, x, GRASS_Y - len(TREE))


FLAG = [
    "k.......",
    "pbwbwbwb",
    "pbbbwbbb",
    "pwwwwwww",
    "pbbbwbbb",
    "pbwbwbwb",
    "p.......",
    "p.......",
    "p.......",
]
FLAG_KEY = {"k": "gold", "p": "stone_light", "b": "pants", "w": "spark"}

BONFIRE = [
    "...f...",
    "..fgf..",
    ".fgygf.",
    ".fgyyf.",
    "ldfgfdl",
    "dl...ld",
]
BONFIRE_KEY = {"f": "copper", "g": "gold", "y": "gold_hi", "l": "dirt_light", "d": "dirt_dark"}

FIREWORK = [
    "x.x.x",
    ".xxx.",
    "xxoxx",
    ".xxx.",
    "x.x.x",
]


def _quebec(c: Canvas, scene: Scene, rng: random.Random) -> None:
    burst = {"x": "spark" if scene.theme == "dark" else "pants", "o": "diamond"}
    mx = scene.w // 2
    for dx, dy in ((-40, 2), (-6, 5), (30, 1)):
        c.blit(FIREWORK, burst, mx + dx, dy)
    for i, x in enumerate(_surface_spots(scene, rng, 7, len(FLAG[0]))):
        sprite, key = (FLAG, FLAG_KEY) if i % 2 == 0 else (BONFIRE, BONFIRE_KEY)
        c.blit(sprite, key, x, GRASS_Y - len(sprite))


PAPEL_PICADO = [
    "fffff",
    "f.f.f",
    "ff.ff",
    ".f.f.",
]
PAPEL_PICADO_COLOURS = ["purple_hi", "copper", "grass_hi", "diamond", "gold", "shirt"]
PAPEL_PICADO_Y = 9

OFRENDA = [
    "....f..sss..f....",
    ".O..w.seses.w..O.",
    "OoO.w.ssnss.w.OoO",
    ".g..w..s.s..w..g.",
]
OFRENDA_KEY = {"f": "gold", "w": "spark", "s": "spark", "n": "coal", "O": "copper", "o": "gold", "g": "grass_dark"}
SKULL_EYE_COLOURS = ["diamond", "shirt", "purple_hi", "grass"]


def _dia_de_muertos(c: Canvas, scene: Scene, rng: random.Random) -> None:
    flag_w = len(PAPEL_PICADO[0])
    left, right = SKY_DECORATION_MIN_X, scene.w - 4
    c.rect(left, PAPEL_PICADO_Y, right - left, 1, S.IDX["text_dim"])
    for i, x in enumerate(range(left + 1, right - flag_w, flag_w + 2)):
        colour = PAPEL_PICADO_COLOURS[i % len(PAPEL_PICADO_COLOURS)]
        c.blit(PAPEL_PICADO, {"f": colour}, x, PAPEL_PICADO_Y + 1)
    for x in range(scene.w):
        if rng.random() < 0.3:
            c.set(x, GRASS_Y, S.IDX[rng.choice(("copper", "gold"))])
    for x in _surface_spots(scene, rng, 5, len(OFRENDA[0])):
        eyes = rng.choice(SKULL_EYE_COLOURS)
        c.blit(OFRENDA, {**OFRENDA_KEY, "e": eyes}, x, GRASS_Y - len(OFRENDA))


SEASONS: dict[str, Season] = {
    "quebec": Season(
        name="quebec",
        first_day=(6, 17),
        last_day=(6, 24),
        palette_by_theme={
            "dark": {"bg": "#0b1a3a", "star": "#3b5dc9", "star_hi": "#ffffff", "accent": "#ffffff"},
            "light": {"bg": "#cfe3ff", "star": "#ffffff", "star_hi": "#eaf2ff", "accent": "#003da5"},
        },
        hat_colours={"y": "pants", "w": "spark"},
        card_border="pants",
        decorate=_quebec,
    ),
    "halloween": Season(
        name="halloween",
        first_day=(10, 15),
        last_day=(10, 31),
        palette_by_theme={
            "dark": {"bg": "#1f1030", "star": "#5d275d", "star_hi": "#8e478c", "accent": "#ef7d57"},
            "light": {"bg": "#f4a261", "star": "#ffd6a5", "star_hi": "#f8c08a", "accent": "#5d275d"},
        },
        hat_colours={"y": "purple", "w": "gold_hi"},
        card_border="copper",
        decorate=_halloween,
    ),
    "dia-de-muertos": Season(
        name="dia-de-muertos",
        first_day=(11, 1),
        last_day=(11, 2),
        palette_by_theme={
            "dark": {
                "bg": "#24122e",
                "star": "#6b3a6b",
                "star_hi": "#ffcd75",
                "accent": "#ff9f1c",
                "purple_hi": "#e4007c",
            },
            "light": {
                "bg": "#f3c4dc",
                "star": "#ffffff",
                "star_hi": "#fbe3ef",
                "accent": "#5d275d",
                "purple_hi": "#e4007c",
            },
        },
        hat_colours={"y": "purple_hi", "w": "gold"},
        card_border="purple_hi",
        decorate=_dia_de_muertos,
    ),
    "christmas": Season(
        name="christmas",
        first_day=(12, 1),
        last_day=(12, 26),
        palette_by_theme={
            "dark": {"bg": "#10213b", "star": "#94b0c2", "star_hi": "#ffffff", "accent": "#ffffff"},
            "light": {"bg": "#d6ecf7", "star": "#ffffff", "star_hi": "#eaf4fb", "accent": "#b13e53"},
        },
        hat_colours={"y": "shirt", "w": "spark"},
        card_border="shirt",
        decorate=_christmas,
    ),
}

SEASON_CHOICES = ["none", "auto", *SEASONS]


def resolve(choice: str | None, today: datetime.date | None = None) -> Season | None:
    """Turn a --season choice into a Season. "auto" picks whichever is active today."""
    if choice in (None, "", "none"):
        return None
    if choice == "auto":
        today = today or datetime.datetime.now(datetime.timezone.utc).date()
        return next((s for s in SEASONS.values() if s.active_on(today)), None)
    if choice not in SEASONS:
        raise ValueError(f"unknown season {choice!r}; choose from {', '.join(SEASON_CHOICES)}")
    return SEASONS[choice]
