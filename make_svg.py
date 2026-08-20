import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from content import PALETTE, ROWS, LAYOUT

REGULAR = "fonts/JetBrainsMono-Regular.ttf"
BOLD = "fonts/JetBrainsMono-Bold.ttf"


class FontFace:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upem = self.font["head"].unitsPerEm
        self.cache = {}

    def advance(self, size):
        name = self.cmap[ord("M")]
        return self.glyphs[name].width * size / self.upem

    def path_for(self, character):
        if character in self.cache:
            return self.cache[character]
        name = self.cmap.get(ord(character))
        if name is None:
            self.cache[character] = ""
            return ""
        pen = SVGPathPen(self.glyphs)
        self.glyphs[name].draw(pen)
        data = pen.getCommands()
        self.cache[character] = data
        return data


regular = FontFace(REGULAR)
bold = FontFace(BOLD)


def draw_word(face, word, x, baseline, size, color, delay):
    scale = size / face.upem
    step = face.advance(size)
    pieces = []
    cursor = x
    for character in word:
        data = face.path_for(character)
        if data and character != " ":
            pieces.append(
                '<path d="%s" transform="translate(%.2f %.2f) scale(%.5f %.5f)"/>'
                % (data, cursor, baseline, scale, -scale)
            )
        cursor += step
    if not pieces:
        return "", cursor
    group = '<g class="w" fill="%s" style="animation-delay:%.3fs">%s</g>' % (
        color,
        delay,
        "".join(pieces),
    )
    return group, cursor


def dotted_leader(start_x, end_x, baseline, step):
    dots = []
    position = start_x
    while position < end_x - step:
        dots.append('<circle cx="%.2f" cy="%.2f" r="1.1"/>' % (position + step / 2, baseline - 5))
        position += step
    return '<g fill="%s" opacity="0.85">%s</g>' % (PALETTE["dots"], "".join(dots))


def build():
    size = LAYOUT["font_size"]
    heading_size = LAYOUT["heading_size"]
    step = regular.advance(size)
    line_height = LAYOUT["line_height"]
    baseline = LAYOUT["top_padding"] + size
    clock = 0.25
    body = []
    stops = []

    for row in ROWS:
        kind = row["kind"]

        if kind == "rule":
            y = baseline - size + LAYOUT["rule_gap"]
            body.append(
                '<line class="r" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                'stroke-width="1" style="animation-delay:%.3fs"/>'
                % (LAYOUT["text_x"], y, LAYOUT["width"] - 30, y, PALETTE["rule"], clock)
            )
            clock += 0.07
            baseline += line_height
            continue

        if kind == "heading":
            piece, cursor = draw_word(
                bold, row["text"], LAYOUT["text_x"], baseline, heading_size, PALETTE["label"], clock
            )
            body.append(piece)
            stops.append((cursor, baseline, clock))
            clock += LAYOUT["word_delay"] * 2 + LAYOUT["line_pause"]
            baseline += line_height
            continue

        if kind == "bullet":
            start = LAYOUT["value_x"] - LAYOUT["bullet_indent"]
            body.append(
                '<g class="w" fill="%s" style="animation-delay:%.3fs">'
                '<circle cx="%.2f" cy="%.2f" r="2.4"/></g>'
                % (PALETTE["label"], clock, start, baseline - 5)
            )
            cursor = start + step * 2
            for word in row["text"].split(" "):
                piece, cursor = draw_word(
                    regular, word + " ", cursor, baseline, size, PALETTE["value"], clock
                )
                body.append(piece)
                stops.append((cursor - step, baseline, clock))
                clock += LAYOUT["word_delay"]
            clock += LAYOUT["line_pause"]
            baseline += line_height
            continue

        label = row["label"]
        tone = PALETTE[row.get("tone", "value")]

        if label:
            piece, cursor = draw_word(
                bold, label, LAYOUT["text_x"], baseline, size, PALETTE["label"], clock
            )
            body.append(piece)
            stops.append((cursor, baseline, clock))
            clock += LAYOUT["word_delay"]
            body.append(dotted_leader(cursor + step, LAYOUT["value_x"] - step, baseline, step))

        cursor = LAYOUT["value_x"]
        for word in row["value"].split(" "):
            piece, cursor = draw_word(regular, word + " ", cursor, baseline, size, tone, clock)
            if piece:
                body.append(piece)
                stops.append((cursor - step, baseline, clock))
                clock += LAYOUT["word_delay"]
        clock += LAYOUT["line_pause"]
        baseline += line_height

    height = baseline - size + LAYOUT["bottom_padding"]
    total = clock + 0.2

    moves = []
    times = []
    for x, y, at in stops:
        moves.append("%.1f,%.1f" % (x, y))
        times.append(max(0.0, min(1.0, at / total)))
    times[0] = 0.0
    times[-1] = 1.0

    caret = (
        '<g opacity="0"><animate attributeName="opacity" values="0;1" begin="0.3s" dur="0.01s" '
        'fill="freeze"/>'
        '<rect width="%.1f" height="%.1f" y="%.1f" fill="%s" opacity="0.9">'
        '<animate attributeName="opacity" values="0.9;0.1;0.9" dur="1.05s" '
        'repeatCount="indefinite"/></rect>'
        '<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
        'values="%s" keyTimes="%s" dur="%.2fs" fill="freeze"/></g>'
        % (
            step,
            size + 4,
            -size,
            PALETTE["bar"],
            ";".join(moves),
            ";".join("%.5f" % t for t in times),
            total,
        )
    )

    style = (
        "<style>"
        ".w{opacity:0;animation:reveal .2s ease-out forwards}"
        ".r{opacity:0;animation:reveal .3s ease-out forwards}"
        "@keyframes reveal{from{opacity:0}to{opacity:1}}"
        "@media(prefers-reduced-motion:reduce){"
        ".w,.r{opacity:1;animation:none}}"
        "</style>"
    )

    frame = (
        '<rect width="%.1f" height="%.1f" rx="10" fill="%s"/>'
        '<rect x="%.1f" y="18" width="3" height="%.1f" rx="1.5" fill="%s" opacity="0.9"/>'
        % (LAYOUT["width"], height, PALETTE["background"], LAYOUT["bar_x"], height - 36, PALETTE["bar"])
    )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f %.0f" width="%.0f" '
        'height="%.0f" role="img" aria-label="ANHAF profile card">%s%s%s%s</svg>'
        % (LAYOUT["width"], height, LAYOUT["width"], height, style, frame, "".join(body), caret)
    )


if __name__ == "__main__":
    target = sys.argv[1]
    with open(target, "w") as handle:
        handle.write(build())
    print("written", target)