import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BOLD_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
REGULAR_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "assets" / "hero.gif"

BANNER_WIDTH = 820
BANNER_HEIGHT = 300
SCENE_LEFT = 420
SCENE_GRID_WIDTH = 100
SCENE_GRID_HEIGHT = 75
PIXEL_SIZE = 4
FRAME_COUNT = 16
FRAME_DURATION = 110

BACKGROUND = "#0d1117"
BORDER = "#30363d"
PANEL = "#161b22"
BLUE = "#58a6ff"
GREEN = "#3fb950"
PURPLE = "#d2a8ff"
ORANGE = "#f0883e"
RED = "#ff7b72"
WHITE = "#e6edf3"
MUTED = "#8b949e"

GLYPHS = {
    "{": ["..##.", ".#...", ".#...", "##...", ".#...", ".#...", "..##."],
    "}": [".##..", "...#.", "...#.", "...##", "...#.", "...#.", ".##.."],
    "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
}

FLOATING_GLYPHS = [
    ("{", 8, 22, BLUE, 0.0),
    ("}", 86, 20, PURPLE, 0.3),
    ("<", 12, 42, GREEN, 0.6),
    (">", 82, 38, ORANGE, 0.9),
    ("/", 90, 6, BLUE, 0.5),
]

CODE_LINES = [
    (2, [(6, RED), (10, WHITE)]),
    (6, [(8, PURPLE), (14, WHITE)]),
    (6, [(5, GREEN), (18, BLUE)]),
    (2, [(12, BLUE), (6, ORANGE)]),
]


def draw_glyph(draw, glyph, left, top, color):
    for row_index, row in enumerate(GLYPHS[glyph]):
        for column_index, cell in enumerate(row):
            if cell == "#":
                draw.point((left + column_index, top + row_index), fill=color)


def build_star_positions():
    generator = random.Random(7)
    return [(generator.randint(2, 97), generator.randint(2, 40), generator.randint(0, 7)) for _ in range(16)]


def draw_stars(draw, star_positions, frame_index):
    for star_x, star_y, phase in star_positions:
        bright = (frame_index // 2 + phase) % 8 < 4
        draw.point((star_x, star_y), fill=WHITE if bright else BORDER)


def draw_screen_code(frame_index):
    screen = Image.new("RGB", (42, 38), "#0b1a33")
    screen_draw = ImageDraw.Draw(screen)
    shift = frame_index % 4
    first_line = frame_index // 4
    for slot in range(-1, 11):
        indent, segments = CODE_LINES[(slot + first_line) % len(CODE_LINES)]
        position_x = 3 + indent
        position_y = slot * 4 - shift + 2
        for width, color in segments:
            screen_draw.rectangle((position_x, position_y, position_x + width - 1, position_y + 1), fill=color)
            position_x += width + 2
    return screen


def draw_steam(draw, frame_index):
    for dot_index in range(3):
        height = (frame_index + dot_index * 5) % 14
        sway = 1 if (height // 3) % 2 == 0 else 0
        color = MUTED if height < 7 else BORDER
        draw.point((85 + sway, 50 - height), fill=color)


def draw_scene(star_positions, frame_index):
    scene = Image.new("RGB", (SCENE_GRID_WIDTH, SCENE_GRID_HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(scene)
    draw_stars(draw, star_positions, frame_index)
    draw.rectangle((0, 62, 99, 74), fill=PANEL)
    draw.line((0, 62, 99, 62), fill=BORDER)
    draw.rectangle((24, 13, 76, 60), fill="#0f2a55")
    draw.rectangle((22, 58, 78, 61), fill="#484f58")
    draw.line((22, 58, 78, 58), fill="#6e7681")
    draw.rectangle((27, 16, 73, 58), fill=BORDER)
    scene.paste(draw_screen_code(frame_index), (29, 18))
    draw.rectangle((82, 52, 90, 61), fill=ORANGE)
    draw.rectangle((91, 54, 92, 58), outline=ORANGE)
    draw_steam(draw, frame_index)
    led_color = GREEN if frame_index % 8 < 5 else "#1a4d2a"
    draw.point((76, 59), fill=led_color)
    for glyph, glyph_x, glyph_y, color, phase in FLOATING_GLYPHS:
        bob = round(math.sin(2 * math.pi * (frame_index / FRAME_COUNT + phase)) * 2)
        draw_glyph(draw, glyph, glyph_x, glyph_y + bob, color)
    return scene.resize((SCENE_GRID_WIDTH * PIXEL_SIZE, SCENE_GRID_HEIGHT * PIXEL_SIZE), Image.NEAREST)


def draw_text_side(draw, frame_index):
    title_font = ImageFont.truetype(BOLD_FONT, 50)
    subtitle_font = ImageFont.truetype(REGULAR_FONT, 18)
    small_font = ImageFont.truetype(REGULAR_FONT, 15)
    draw.text((40, 38), "~/anhafdev $ whoami", font=small_font, fill=GREEN)
    draw.text((40, 76), "ANHAFDEV", font=title_font, fill=WHITE)
    draw.rectangle((42, 142, 182, 145), fill=BLUE)
    draw.text((40, 166), "Python Automation Engineer", font=subtitle_font, fill=BLUE)
    cursor = "█" if frame_index % 8 < 5 else " "
    draw.text((40, 194), "Backend & Full-Stack Developer" + cursor, font=subtitle_font, fill=MUTED)
    dot_color = GREEN if frame_index % 8 < 5 else "#1a4d2a"
    draw.ellipse((42, 252, 52, 262), fill=dot_color)
    draw.text((64, 249), "Open for freelance", font=small_font, fill=WHITE)


def build_frame(star_positions, frame_index):
    banner = Image.new("RGB", (BANNER_WIDTH, BANNER_HEIGHT), BACKGROUND)
    banner.paste(draw_scene(star_positions, frame_index), (SCENE_LEFT, 0))
    draw = ImageDraw.Draw(banner)
    draw.rounded_rectangle((0, 0, BANNER_WIDTH - 1, BANNER_HEIGHT - 1), 14, outline=BORDER)
    draw_text_side(draw, frame_index)
    return banner


def main():
    star_positions = build_star_positions()
    frames = [build_frame(star_positions, index) for index in range(FRAME_COUNT)]
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUTPUT_FILE, save_all=True, append_images=frames[1:], duration=FRAME_DURATION, loop=0, optimize=True)
    print("Saved", OUTPUT_FILE)


if __name__ == "__main__":
    main()
