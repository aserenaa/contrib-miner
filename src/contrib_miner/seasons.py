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
        today = (day.month, day.day)
        if self.first_day <= self.last_day:
            return self.first_day <= today <= self.last_day
        return today >= self.first_day or today <= self.last_day


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


BIG_FIREWORK = [
    "...h...",
    ".h.c.h.",
    "..ccc..",
    "hcc.cch",
    "..ccc..",
    ".h.c.h.",
    "...h...",
]
SMALL_FIREWORK = [
    "h.h.h",
    ".ccc.",
    "hc.ch",
    ".ccc.",
    "h.h.h",
]
FIREWORK_COLOURS = [
    ("copper", "copper_hi"),
    ("diamond", "diamond_hi"),
    ("shirt", "gold_hi"),
    ("purple_hi", "spark"),
    ("grass", "grass_hi"),
    ("gold", "spark"),
]
FIREWORK_SPACING = 14
CONFETTI = ["gold", "copper", "diamond_hi", "shirt", "purple_hi"]
BANNER_TOP = 2
BANNER_TEXT_SCALE = 2


def _coming_year(today: datetime.date | None = None) -> int:
    """The year being welcomed: next year from July on, this year until then."""
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    return today.year + 1 if today.month >= 7 else today.year


def _big_text(c: Canvas, text: str, x: int, y: int, colour: str) -> None:
    k = BANNER_TEXT_SCALE
    for i, ch in enumerate(text):
        for dy, row in enumerate(S.FONT[ch]):
            for dx, bit in enumerate(row):
                if bit == "#":
                    c.rect(x + (i * S.GLYPH_ADVANCE + dx) * k, y + dy * k, k, k, S.IDX[colour])


def _banner(c: Canvas, scene: Scene, year: int) -> tuple[int, int]:
    """A red sign on two posts with the year in big gold digits. Returns its left and right edges."""
    text = str(year)
    text_w = S.text_width(text) * BANNER_TEXT_SCALE
    text_h = S.GLYPH_H * BANNER_TEXT_SCALE
    w, h = text_w + 6, text_h + 4
    x0 = (scene.w - w) // 2
    c.rect(x0, BANNER_TOP, w, h, S.IDX["gold"])
    c.rect(x0 + 1, BANNER_TOP + 1, w - 2, h - 2, S.IDX["shirt"])
    _big_text(c, text, x0 + 3, BANNER_TOP + 2, "gold_hi")
    for post_x in (x0 + 2, x0 + w - 3):
        c.rect(post_x, BANNER_TOP + h, 1, GRASS_Y - BANNER_TOP - h, S.IDX["dirt_light"])
    return x0, x0 + w


def _new_year(c: Canvas, scene: Scene, rng: random.Random) -> None:
    left, right = _banner(c, scene, _coming_year())
    scene.stars = [star for star in scene.stars if not left <= star[0] < right]
    x, i = SKY_DECORATION_MIN_X, 0
    while x < scene.w - len(BIG_FIREWORK[0]) - 4:
        if x + len(BIG_FIREWORK[0]) + 2 < left or x > right + 2:
            big = i % 2 == 0
            sprite = BIG_FIREWORK if big else SMALL_FIREWORK
            core, tip = FIREWORK_COLOURS[i % len(FIREWORK_COLOURS)]
            y = (8 if big else 9) + rng.randrange(2 if big else 3)
            c.blit(sprite, {"c": core, "h": tip}, x + rng.randrange(3), y)
            i += 1
        x += FIREWORK_SPACING
    for x in range(scene.w):
        if rng.random() < 0.2:
            c.set(x, GRASS_Y + rng.randrange(2), S.IDX[rng.choice(CONFETTI)])


SEASONS: dict[str, Season] = {
    "halloween": Season(
        name="halloween",
        first_day=(10, 15),
        last_day=(11, 1),
        palette_by_theme={
            "dark": {"bg": "#1f1030", "star": "#5d275d", "star_hi": "#8e478c", "accent": "#ef7d57"},
            "light": {"bg": "#f4a261", "star": "#ffd6a5", "star_hi": "#f8c08a", "accent": "#5d275d"},
        },
        hat_colours={"y": "purple", "w": "gold_hi"},
        card_border="copper",
        decorate=_halloween,
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
    "new-year": Season(
        name="new-year",
        first_day=(12, 27),
        last_day=(1, 2),
        palette_by_theme={
            "dark": {"bg": "#0b0e24", "star": "#566c86", "star_hi": "#ffffff", "accent": "#ffcd75"},
            "light": {"bg": "#f3d9e6", "star": "#ffffff", "star_hi": "#fbeef4", "accent": "#5d275d"},
        },
        hat_colours={"y": "diamond", "w": "gold_hi"},
        card_border="diamond",
        decorate=_new_year,
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
