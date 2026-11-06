"""Seasonal dressing: sky colours, surface decorations, sky animations and the miner's hat.
The mine itself never changes."""

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
Animate = Callable[["Canvas", "Scene", int], None]
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
    animate: Animate | None = field(default=None, repr=False)

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
FIREWORK_POP = [
    ".c.",
    "chc",
    ".c.",
]
FIREWORK_SPACING = 14
FIREWORK_STAGE_TICKS = 5
FIREWORK_RISE_STAGES = 3
FIREWORK_RISE_PER_STAGE = 3
FIREWORK_MIN_PERIOD = 12
CONFETTI = ["gold", "copper", "diamond_hi", "shirt", "purple_hi"]
BANNER_TOP = 2
BANNER_TEXT_SCALE = 2


@dataclass(frozen=True)
class Firework:
    sprite: list[str]
    x: int
    y: int
    core: str
    tip: str
    period: int
    offset: int

    @property
    def centre(self) -> tuple[int, int]:
        return self.x + len(self.sprite[0]) // 2, self.y + len(self.sprite) // 2


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


def _banner_box(scene: Scene, text: str) -> tuple[int, int, int]:
    """Left edge, width and height of the year sign, centred in the sky."""
    w = S.text_width(text) * BANNER_TEXT_SCALE + 6
    h = S.GLYPH_H * BANNER_TEXT_SCALE + 4
    return (scene.w - w) // 2, w, h


def _banner(c: Canvas, scene: Scene, text: str) -> None:
    """A red sign on two posts with the year in big gold digits."""
    x0, w, h = _banner_box(scene, text)
    c.rect(x0, BANNER_TOP, w, h, S.IDX["gold"])
    c.rect(x0 + 1, BANNER_TOP + 1, w - 2, h - 2, S.IDX["shirt"])
    _big_text(c, text, x0 + 3, BANNER_TOP + 2, "gold_hi")
    for post_x in (x0 + 2, x0 + w - 3):
        c.rect(post_x, BANNER_TOP + h, 1, GRASS_Y - BANNER_TOP - h, S.IDX["dirt_light"])


def _fireworks(scene: Scene) -> list[Firework]:
    """Where each firework bursts and when, the same for every frame of a GIF."""
    rng = random.Random(f"{scene.cal.login}:fireworks")
    left, w, _ = _banner_box(scene, str(_coming_year()))
    width = len(BIG_FIREWORK[0])
    out = []
    for x in range(SKY_DECORATION_MIN_X, scene.w - width - 4, FIREWORK_SPACING):
        if left - width - 2 <= x <= left + w + 2:
            continue
        big = len(out) % 2 == 0
        core, tip = FIREWORK_COLOURS[len(out) % len(FIREWORK_COLOURS)]
        period = FIREWORK_MIN_PERIOD + rng.randrange(7)
        out.append(
            Firework(
                sprite=BIG_FIREWORK if big else SMALL_FIREWORK,
                x=x + rng.randrange(3),
                y=(8 if big else 9) + rng.randrange(2 if big else 3),
                core=core,
                tip=tip,
                period=period,
                offset=rng.randrange(period),
            )
        )
    return out


def _draw_firework(c: Canvas, fw: Firework, stage: int) -> None:
    """Rise as a rocket, pop, burst, fade to sparks, then stay dark until the next launch."""
    cx, cy = fw.centre
    if stage < FIREWORK_RISE_STAGES:
        head = min(GRASS_Y - 2, cy + (FIREWORK_RISE_STAGES - stage) * FIREWORK_RISE_PER_STAGE)
        c.set(cx, head, S.IDX[fw.tip])
        c.set(cx, head + 1, S.IDX[fw.core])
    elif stage == FIREWORK_RISE_STAGES:
        c.blit(FIREWORK_POP, {"c": fw.core, "h": fw.tip}, cx - 1, cy - 1)
    elif stage <= FIREWORK_RISE_STAGES + 2:
        c.blit(fw.sprite, {"c": fw.core, "h": fw.tip}, fw.x, fw.y)
    elif stage == FIREWORK_RISE_STAGES + 3:
        sparks = [row.replace("c", ".") for row in fw.sprite]
        c.blit(sparks, {"h": fw.tip}, fw.x, fw.y)


def _new_year(c: Canvas, scene: Scene, rng: random.Random) -> None:
    year = str(_coming_year())
    _banner(c, scene, year)
    left, w, _ = _banner_box(scene, year)
    scene.stars = [star for star in scene.stars if not left <= star[0] < left + w]
    for x in range(scene.w):
        if rng.random() < 0.2:
            c.set(x, GRASS_Y + rng.randrange(2), S.IDX[rng.choice(CONFETTI)])


def _new_year_fireworks(c: Canvas, scene: Scene, tick: int) -> None:
    for fw in _fireworks(scene):
        _draw_firework(c, fw, (tick // FIREWORK_STAGE_TICKS + fw.offset) % fw.period)


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
        animate=_new_year_fireworks,
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
