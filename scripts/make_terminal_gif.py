from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "assets" / "terminal.gif"

IMAGE_WIDTH = 820
IMAGE_HEIGHT = 270
LINE_HEIGHT = 30
TEXT_LEFT = 28
TEXT_TOP = 62

BACKGROUND = (13, 17, 23)
TOP_BAR = (22, 27, 34)
BORDER = (48, 54, 61)
TEXT_COLOR = (230, 237, 243)
MUTED_COLOR = (125, 133, 144)
GREEN = (63, 185, 80)
BLUE = (88, 166, 255)

COMMAND_TEXT = 'python automate.py --task "boring work"'
STEPS = ["scraping data", "calling APIs", "sending report"]
FINAL_TEXT = "6 hours of manual work  ->  0 seconds"


def load_fonts():
    return ImageFont.truetype(FONT_PATH, 17), ImageFont.truetype(FONT_PATH, 13)


def draw_window(draw, small_font):
    draw.rounded_rectangle((0, 0, IMAGE_WIDTH - 1, IMAGE_HEIGHT - 1), 14, fill=BACKGROUND, outline=BORDER)
    draw.rounded_rectangle((1, 1, IMAGE_WIDTH - 2, 40), 14, fill=TOP_BAR)
    draw.rectangle((1, 26, IMAGE_WIDTH - 2, 40), fill=TOP_BAR)
    for index, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        center_x = 26 + index * 22
        draw.ellipse((center_x - 6, 14, center_x + 6, 26), fill=color)
    draw.text((IMAGE_WIDTH // 2 - 70, 14), "anhafdev  --  zsh", font=small_font, fill=MUTED_COLOR)


def draw_line(draw, font, row, parts):
    position_x = TEXT_LEFT
    position_y = TEXT_TOP + row * LINE_HEIGHT
    for text, color in parts:
        draw.text((position_x, position_y), text, font=font, fill=color)
        position_x += draw.textlength(text, font=font)


def build_frame(font, small_font, command_chars, finished_steps, step_dots, show_final, cursor_on):
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw_window(draw, small_font)
    cursor = "█" if cursor_on else " "
    command_done = command_chars >= len(COMMAND_TEXT)
    typed = COMMAND_TEXT[:command_chars]
    draw_line(draw, font, 0, [("$ ", GREEN), (typed, TEXT_COLOR), ("" if command_done else cursor, BLUE)])
    for index in range(len(STEPS)):
        if index < finished_steps:
            draw_line(draw, font, index + 1, [(f"[{index + 1}/3] {STEPS[index]} ", TEXT_COLOR), ("." * 8 + " ", MUTED_COLOR), ("done", GREEN)])
        elif index == finished_steps and command_done and step_dots > 0:
            draw_line(draw, font, index + 1, [(f"[{index + 1}/3] {STEPS[index]} ", TEXT_COLOR), ("." * step_dots, MUTED_COLOR)])
    if show_final:
        draw_line(draw, font, 4, [("✔ ", GREEN), (FINAL_TEXT, BLUE)])
        draw_line(draw, font, 5, [("$ ", GREEN), (cursor, BLUE)])
    return image


def build_all_frames(font, small_font):
    frames = []
    durations = []

    def add(command_chars=0, finished=0, dots=0, final=False, cursor=True, duration=70):
        frames.append(build_frame(font, small_font, command_chars, finished, dots, final, cursor))
        durations.append(duration)

    add(duration=700)
    for count in range(1, len(COMMAND_TEXT) + 1, 2):
        add(command_chars=count, duration=55)
    full = len(COMMAND_TEXT)
    add(command_chars=full, cursor=False, duration=400)
    for step_index in range(len(STEPS)):
        for dots in range(1, 9):
            add(command_chars=full, finished=step_index, dots=dots, duration=60)
        add(command_chars=full, finished=step_index + 1, duration=260)
    for blink in range(6):
        add(command_chars=full, finished=3, final=True, cursor=blink % 2 == 0, duration=450)
    return frames, durations


def main():
    font, small_font = load_fonts()
    frames, durations = build_all_frames(font, small_font)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUTPUT_FILE, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print("Saved", OUTPUT_FILE, len(frames), "frames")


if __name__ == "__main__":
    main()
