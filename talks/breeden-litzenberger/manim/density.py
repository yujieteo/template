"""Native animation for the frame labelled `density` (replaces its slide image).

The closed-form density draws itself on the first sentence; the second
differences of the call prices then land on it point by point, and the value
at K0 appears on the second sentence. Data: data/curves.csv and numbers.tex.
"""
import csv
import re
from pathlib import Path

from manim import (
    Create, Dot, FadeIn, LaggedStart, Line, UP, DOWN, LEFT, RIGHT, VGroup, VMobject, Write, config,
)
from talkscene import PALETTE, SLIDE_SCALE, text

TALK = Path(__file__).resolve().parents[1]


def load():
    rows = list(csv.DictReader((TALK / "data" / "curves.csv").open()))
    numbers = dict(re.findall(r"\\newcommand\{\\(\w+)\}\{([^}]*)\}", (TALK / "data" / "numbers.tex").read_text()))
    return rows, numbers


def animate(scene, frame):
    rows, numbers = load()
    k0, p0 = float(numbers["blKzero"]), float(numbers["blPzero"])
    fg, muted, accent = PALETTE["foreground"], PALETTE["secondary"], PALETTE["accent"]

    # Plot box in the area the slide image would occupy.
    top = config.frame_height / 2 - 0.12
    bottom = top - config.frame_height * SLIDE_SCALE
    left, right = -config.frame_width / 2 + 1.6, config.frame_width / 2 - 1.0
    x0, y0, x1, y1 = left + 0.6, bottom + 1.1, right - 0.4, top - 2.1
    kmin, kmax, pmax = 60.0, 160.0, 0.021
    X = lambda k: x0 + (k - kmin) / (kmax - kmin) * (x1 - x0)
    Y = lambda p: y0 + p / pmax * (y1 - y0)

    title = text(frame["title"], 40)
    title.scale_to_fit_width(min(title.width, config.frame_width - 1.4)).to_corner(UP + LEFT, buff=0.6)
    axes = VGroup(Line([x0, y0, 0], [x1, y0, 0], color=muted, stroke_width=2),
                  Line([x0, y0, 0], [x0, y1, 0], color=muted, stroke_width=2))
    ticks = VGroup(*[text(str(k), 20, muted).next_to([X(k), y0, 0], DOWN, buff=0.15) for k in range(60, 161, 20)])
    xlabel = text("strike K", 22, muted).next_to([(x0 + x1) / 2, y0, 0], DOWN, buff=0.6)
    ylabel = text("density p(K)", 22, muted).rotate(1.5708).next_to([x0, (y0 + y1) / 2, 0], LEFT, buff=0.3)

    closed = VMobject(stroke_color=muted, stroke_width=10, stroke_opacity=0.45)
    closed.set_points_smoothly([[X(float(r["K"])), Y(float(r["density"])), 0] for r in rows[::4]])
    fd = [r for r in rows[1:-1:6]]
    dots = VGroup(*[Dot([X(float(r["K"])), Y(float(r["fd"])), 0], radius=0.045, color=accent) for r in fd])
    marker = Dot([X(k0), Y(p0), 0], radius=0.09, color=accent)
    value = text(f"p({numbers['blKzero']}) = {numbers['blPzero']}", 28, accent).next_to(marker, UP, buff=0.2)
    legend = VGroup(text("closed form", 22, muted), text("from call prices", 22, accent)) \
        .arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    legend.move_to([X(129), Y(0.0160), 0], aligned_edge=UP + LEFT)

    group = VGroup(title, axes, ticks, xlabel, ylabel)
    scene.swap_to(group)
    scene.play(Create(closed), FadeIn(legend[0]), run_time=min(2.0, scene.budget(scene.span(0)[1])))
    scene.at(0, 0.45)
    scene.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.08), FadeIn(legend[1]),
               run_time=min(2.4, scene.budget(scene.span(0)[1] + 1)))
    scene.at(1, 0.2)
    scene.play(FadeIn(marker, scale=0.3), Write(value), run_time=0.8)
