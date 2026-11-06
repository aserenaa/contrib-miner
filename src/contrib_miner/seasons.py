"""Seasonal dressing: sky colours, surface decorations and the miner's hat. The mine itself never changes.

A Sky recolours the background for the time of year. A Season is a holiday on top of it, and its colours win.
"""

from __future__ import annotations

import datetime
import itertools
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


@dataclass(frozen=True)
class Sky:
    name: str
    months: tuple[int, ...]
    palette_by_theme: dict[str, dict[str, str]]
    decorate: Decorate = field(repr=False)


def _today() -> datetime.date:
    return datetime.datetime.now(datetime.timezone.utc).date()


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


MEXICAN_FLAG = [
    "k......",
    "|ggwwrr",
    "|ggeerr",
    "|ggwwrr",
    "|......",
    "|......",
    "|......",
    "|......",
    "|......",
]
MEXICAN_FLAG_KEY = {"k": "gold", "|": "stone_light", "g": "grass", "w": "spark", "r": "shirt", "e": "copper"}

PENNANT = [
    "ccc",
    "c.c",
    ".c.",
]
PENNANT_COLOURS = ("grass", "spark", "shirt")
PENNANT_SPACING = 4
GARLAND_SAG = 3


def _garland(c: Canvas, x0: int, x1: int, y: int, first_colour: int) -> int:
    """A sagging string of papel picado between two poles. Returns the next pennant colour."""
    span = x1 - x0
    colour = first_colour
    for x in range(x0, x1 + 1):
        t = (x - x0) / span
        sag = round(GARLAND_SAG * 4 * t * (1 - t))
        c.set(x, y + sag, S.IDX["stone_light"])
        if x - x0 >= 2 and x1 - x >= 4 and (x - x0) % PENNANT_SPACING == 2:
            c.blit(PENNANT, {"c": PENNANT_COLOURS[colour % len(PENNANT_COLOURS)]}, x, y + sag + 1)
            colour += 1
    return colour


def _independence(c: Canvas, scene: Scene, rng: random.Random) -> None:
    flag_top = GRASS_Y - len(MEXICAN_FLAG)
    poles = _surface_spots(scene, rng, 7, len(MEXICAN_FLAG[0]))
    colour = 0
    for left, right in itertools.pairwise(poles):
        colour = _garland(c, left + len(MEXICAN_FLAG[0]), right, flag_top + 1, colour)
    for x in poles:
        c.blit(MEXICAN_FLAG, MEXICAN_FLAG_KEY, x, flag_top)


FLAG = [
    "prrrwwwrwwwrrr",
    "prrrwrwrwrwrrr",
    "prrrwrrrrrwrrr",
    "prrrwwrrrwwrrr",
    "prrrwwwrwwwrrr",
    "p.............",
    "p.............",
    "p.............",
    "p.............",
]
FLAG_KEY = {"p": "stone_light", "r": "shirt", "w": "spark"}

FIREWORK = [
    "...x...",
    ".x...x.",
    "...h...",
    "x.hHh.x",
    "...h...",
    ".x...x.",
    "...x...",
]


def _canada_day(c: Canvas, scene: Scene, rng: random.Random) -> None:
    mx = scene.w * 3 // 5
    second = "spark" if scene.theme == "dark" else "gold"
    for dx, dy, colour in ((-34, 2, "shirt"), (0, 6, second), (30, 1, "shirt"), (58, 7, second)):
        c.blit(FIREWORK, {"x": colour, "h": colour, "H": "gold_hi"}, mx + dx, dy)
    for x in _surface_spots(scene, rng, 6, len(FLAG[0])):
        c.blit(FLAG, FLAG_KEY, x, GRASS_Y - len(FLAG))


QUEBEC_FLAG = [
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
QUEBEC_FLAG_KEY = {"k": "gold", "p": "stone_light", "b": "pants", "w": "spark"}

BONFIRE = [
    "...f...",
    "..fgf..",
    ".fgygf.",
    ".fgyyf.",
    "ldfgfdl",
    "dl...ld",
]
BONFIRE_KEY = {"f": "copper", "g": "gold", "y": "gold_hi", "l": "dirt_light", "d": "dirt_dark"}

QUEBEC_FIREWORK = [
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
        c.blit(QUEBEC_FIREWORK, burst, mx + dx, dy)
    for i, x in enumerate(_surface_spots(scene, rng, 7, len(QUEBEC_FLAG[0]))):
        sprite, key = (QUEBEC_FLAG, QUEBEC_FLAG_KEY) if i % 2 == 0 else (BONFIRE, BONFIRE_KEY)
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


SNOWY_PINE = [
    "...w...",
    "..wgw..",
    "..ggg..",
    ".wwgww.",
    ".ggGgg.",
    "wwgggww",
    "gggGggg",
    "...t...",
    "...t...",
]
SNOWY_PINE_KEY = {"w": "spark", "g": "grass_dark", "G": "grass", "t": "dirt_light"}

SNOWMAN = [
    "..kkk..",
    "..kkk..",
    ".kkkkk.",
    "..wcw..",
    "..wwoo.",
    "s.www.s",
    ".swcws.",
    "..www..",
    ".wwcww.",
    ".wwwww.",
    "..www..",
]
SNOWMAN_KEY = {"k": "shirt", "w": "spark", "c": "coal", "o": "copper", "s": "dirt_light"}


def _winter(c: Canvas, scene: Scene, rng: random.Random) -> None:
    _snow_on_grass(c, scene, rng)
    for i, x in enumerate(_surface_spots(scene, rng, 7, len(SNOWY_PINE[0]))):
        sprite, key = (SNOWMAN, SNOWMAN_KEY) if i % 3 == 1 else (SNOWY_PINE, SNOWY_PINE_KEY)
        c.blit(sprite, key, x, GRASS_Y - len(sprite))


FLOWER = [
    ".p.",
    "pcp",
    ".p.",
    ".s.",
]
FLOWER_COLOURS = ("shirt", "gold", "purple_hi", "diamond", "spark")

BLOSSOM_TREE = [
    "..pPpp...",
    ".pPpPpPp.",
    "pPpwpPpPp",
    "pPpPpPwpp",
    ".pPpPpPp.",
    "...pttp..",
    "....t....",
    "....t....",
    "....t....",
]
BLOSSOM_TREE_KEY = {"p": "copper_hi", "P": "spark", "w": "purple_hi", "t": "dirt_light"}


def _spring(c: Canvas, scene: Scene, rng: random.Random) -> None:
    for i, x in enumerate(_surface_spots(scene, rng, 5, len(BLOSSOM_TREE[0]))):
        if i % 2 == 0:
            c.blit(BLOSSOM_TREE, BLOSSOM_TREE_KEY, x, GRASS_Y - len(BLOSSOM_TREE))
    for x in _surface_spots(scene, rng, 18, len(FLOWER[0])):
        key = {"p": rng.choice(FLOWER_COLOURS), "c": "gold_hi", "s": "grass_dark"}
        c.blit(FLOWER, key, x, GRASS_Y - len(FLOWER) + 1)


PALM = [
    ".gg...gg.",
    "gGgg.ggGg",
    "g..gGg..g",
    "...cGc...",
    "....t....",
    "....t....",
    "...t.....",
    "...t.....",
    "...t.....",
    "....t....",
]
PALM_KEY = {"g": "grass_dark", "G": "grass", "c": "dirt_dark", "t": "dirt_light"}

UMBRELLA = [
    "...r...",
    ".rwrwr.",
    "rwrwrwr",
    "...p...",
    "...p...",
    "...p...",
    "...p...",
]
UMBRELLA_KEY = {"r": "shirt", "w": "spark", "p": "stone_light"}

VOLLEYBALL_NET = [
    "..........wb...",
    ".........wbww..",
    ".........wwbw..",
    "p.........bw..p",
    "pwwwwwwwwwwwwwp",
    "pw.w.w.w.w.w.wp",
    "p.w.w.w.w.w.w.p",
    "pwwwwwwwwwwwwwp",
    "p.............p",
    "p.............p",
]
VOLLEYBALL_NET_KEY = {"p": "stone_light", "w": "spark", "b": "diamond"}

SUN = [
    "..g.g..",
    ".gGGGg.",
    "gGGGGGg",
    ".GGGGG.",
    "gGGGGGg",
    ".gGGGg.",
    "..g.g..",
]
SUN_KEY = {"g": "gold", "G": "gold_hi"}


def _summer(c: Canvas, scene: Scene, rng: random.Random) -> None:
    c.rect(0, GRASS_Y, scene.w, 2, S.IDX["gold"])
    c.rect(0, GRASS_Y + 2, scene.w, 1, S.IDX["dirt_light"])
    for x in range(scene.w):
        if rng.random() < 0.25:
            c.set(x, GRASS_Y + rng.randrange(2), S.IDX["gold_hi"])
    if scene.theme == "light":
        c.blit(SUN, SUN_KEY, scene.w * 3 // 5, 7)
    items = ((PALM, PALM_KEY), (VOLLEYBALL_NET, VOLLEYBALL_NET_KEY), (UMBRELLA, UMBRELLA_KEY))
    for i, x in enumerate(_surface_spots(scene, rng, 6, len(VOLLEYBALL_NET[0]))):
        sprite, key = items[i % len(items)]
        c.blit(sprite, key, x, GRASS_Y - len(sprite))


AUTUMN_TREE = [
    "...oOo...",
    ".ooOroOo.",
    "oOrooOroo",
    "ooOoOooOo",
    ".oorOoOo.",
    "..ooOoo..",
    "....t....",
    "....t....",
    "....t....",
]
AUTUMN_TREE_KEY = {"o": "copper", "O": "gold", "r": "shirt", "t": "dirt_light"}
LEAF_COLOURS = ("copper", "gold", "shirt")


def _autumn(c: Canvas, scene: Scene, rng: random.Random) -> None:
    tree_w, tree_h = len(AUTUMN_TREE[0]), len(AUTUMN_TREE)
    for x in _surface_spots(scene, rng, 6, tree_w):
        c.blit(AUTUMN_TREE, AUTUMN_TREE_KEY, x, GRASS_Y - tree_h)
        for _ in range(5):
            c.set(
                x + rng.randrange(-4, tree_w + 6),
                rng.randrange(GRASS_Y - tree_h + 4, GRASS_Y),
                S.IDX[rng.choice(LEAF_COLOURS)],
            )
    for x in range(scene.w):
        if rng.random() < 0.3:
            c.set(x, GRASS_Y, S.IDX[rng.choice(LEAF_COLOURS)])


SEASONS: dict[str, Season] = {
    # Mexican Independence Day: the Grito on the night of September 15, the holiday on the 16th.
    "independence": Season(
        name="independence",
        first_day=(9, 1),
        last_day=(9, 16),
        palette_by_theme={
            "dark": {"bg": "#101b33", "accent": "#38b764"},
            "light": {"bg": "#fde4c4", "star": "#ffffff", "star_hi": "#fff3e3"},
        },
        hat_colours={"y": "grass", "w": "spark"},
        card_border="grass",
        decorate=_independence,
    ),
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
    "canada-day": Season(
        name="canada-day",
        first_day=(6, 25),
        last_day=(7, 2),
        palette_by_theme={
            "dark": {"bg": "#0e1630", "star": "#3b4a6b", "star_hi": "#94b0c2", "accent": "#ef5b5b"},
            "light": {"bg": "#bfe6fb", "star": "#ffffff", "star_hi": "#e3f4fd", "accent": "#b13e53"},
        },
        hat_colours={"y": "shirt", "w": "spark"},
        card_border="shirt",
        decorate=_canada_day,
    ),
}

# Meteorological seasons, northern hemisphere. In the light theme "star" and "star_hi" colour the clouds.
SKIES: dict[str, Sky] = {
    "winter": Sky(
        name="winter",
        months=(12, 1, 2),
        palette_by_theme={
            "dark": {"bg": "#121a30", "star": "#6d8bb0", "star_hi": "#e0f0ff"},
            "light": {"bg": "#d3e2ee", "star": "#ffffff", "star_hi": "#eef5fa"},
        },
        decorate=_winter,
    ),
    "spring": Sky(
        name="spring",
        months=(3, 4, 5),
        palette_by_theme={
            "dark": {"bg": "#14262e", "star": "#5a8a7a", "star_hi": "#c8f0d8"},
            "light": {"bg": "#b4e6ec", "star": "#ffffff", "star_hi": "#e4f6f8"},
        },
        decorate=_spring,
    ),
    "summer": Sky(
        name="summer",
        months=(6, 7, 8),
        palette_by_theme={
            "dark": {"bg": "#1c1838", "star": "#6c5ca8", "star_hi": "#ffe9a8"},
            "light": {"bg": "#7ccaf5", "star": "#ffffff", "star_hi": "#d4eefc"},
        },
        decorate=_summer,
    ),
    "autumn": Sky(
        name="autumn",
        months=(9, 10, 11),
        palette_by_theme={
            "dark": {"bg": "#26181c", "star": "#8a6656", "star_hi": "#ffcd9a"},
            "light": {"bg": "#f0d4ae", "star": "#fff7ea", "star_hi": "#fbe8cf"},
        },
        decorate=_autumn,
    ),
}

SKY_CHOICES = ["none", "auto", *SKIES]


def resolve_sky(choice: str | None, today: datetime.date | None = None) -> Sky | None:
    """Turn a --sky choice into a Sky. "auto" picks the season of the year today falls in."""
    if choice in (None, "", "none"):
        return None
    if choice == "auto":
        month = (today or _today()).month
        return next(s for s in SKIES.values() if month in s.months)
    if choice not in SKIES:
        raise ValueError(f"unknown sky {choice!r}; choose from {', '.join(SKY_CHOICES)}")
    return SKIES[choice]


SEASON_CHOICES = ["none", "auto", *SEASONS]


def resolve(choice: str | None, today: datetime.date | None = None) -> Season | None:
    """Turn a --season choice into a Season. "auto" picks whichever is active today."""
    if choice in (None, "", "none"):
        return None
    if choice == "auto":
        today = today or _today()
        return next((s for s in SEASONS.values() if s.active_on(today)), None)
    if choice not in SEASONS:
        raise ValueError(f"unknown season {choice!r}; choose from {', '.join(SEASON_CHOICES)}")
    return SEASONS[choice]
