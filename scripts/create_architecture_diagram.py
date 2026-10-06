from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUTPUT = Path("docs/architecture-diagram.png")

WIDTH = 1600
HEIGHT = 950

image = Image.new("RGB", (WIDTH, HEIGHT), "#f4f7fb")
draw = ImageDraw.Draw(image)


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)

    return ImageFont.load_default()


title_font = font(42, True)
subtitle_font = font(22)
box_title_font = font(24, True)
box_text_font = font(18)
small_font = font(17)


def centered_text(box, text, used_font, fill):
    x1, y1, x2, y2 = box
    bbox = draw.multiline_textbbox(
        (0, 0),
        text,
        font=used_font,
        spacing=6,
        align="center",
    )
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    draw.multiline_text(
        (
            x1 + (x2 - x1 - text_width) / 2,
            y1 + (y2 - y1 - text_height) / 2,
        ),
        text,
        font=used_font,
        fill=fill,
        spacing=6,
        align="center",
    )


def box(x, y, width, height, title, body, color):
    rectangle = (x, y, x + width, y + height)

    draw.rounded_rectangle(
        rectangle,
        radius=18,
        fill="#ffffff",
        outline=color,
        width=4,
    )

    draw.rectangle(
        (x, y, x + width, y + 12),
        fill=color,
    )

    centered_text(
        (x + 15, y + 25, x + width - 15, y + 72),
        title,
        box_title_font,
        "#0b2942",
    )

    centered_text(
        (x + 18, y + 78, x + width - 18, y + height - 18),
        body,
        box_text_font,
        "#415466",
    )


def arrow(start, end, color="#55758d", width=5):
    draw.line((start, end), fill=color, width=width)

    x1, y1 = start
    x2, y2 = end

    if abs(y2 - y1) > abs(x2 - x1):
        direction = 1 if y2 > y1 else -1
        points = [
            (x2, y2),
            (x2 - 12, y2 - direction * 22),
            (x2 + 12, y2 - direction * 22),
        ]
    else:
        direction = 1 if x2 > x1 else -1
        points = [
            (x2, y2),
            (x2 - direction * 22, y2 - 12),
            (x2 - direction * 22, y2 + 12),
        ]

    draw.polygon(points, fill=color)


centered_text(
    (80, 35, WIDTH - 80, 105),
    "ABB Alarm Intelligence Copilot",
    title_font,
    "#0b2942",
)

centered_text(
    (150, 105, WIDTH - 150, 145),
    "MCP integration + RAG evidence workflow",
    subtitle_font,
    "#637589",
)

# Main path
box(
    560,
    175,
    480,
    105,
    "Streamlit GUI",
    "Chat input | Results | Citations | Visualizations | MCP trace",
    "#168aad",
)

box(
    560,
    350,
    480,
    105,
    "Copilot Backend",
    "Intent extraction | Orchestration | Evidence composition",
    "#1261a0",
)

box(
    560,
    525,
    480,
    105,
    "MCP Client",
    "Tool discovery | Typed invocation | Multi-step chaining",
    "#6c63ff",
)

box(
    560,
    700,
    480,
    105,
    "Alarm MCP Server",
    "Validation | Auth | Retry | Timeout | Error mapping",
    "#20a464",
)

box(
    560,
    875,
    480,
    60,
    "Alarm API Simulator",
    "Synthetic enterprise alarm source system",
    "#e4a500",
)

arrow((800, 280), (800, 350))
arrow((800, 455), (800, 525))
arrow((800, 630), (800, 700))
arrow((800, 805), (800, 875))

# RAG path
box(
    80,
    350,
    350,
    120,
    "RAG Retrieval",
    "TF-IDF search | Ranking | Low-confidence filtering",
    "#6c63ff",
)

box(
    80,
    555,
    350,
    120,
    "Document Store",
    "Operating procedures\nMaintenance manuals\nSafety instructions",
    "#8b5cf6",
)

box(
    80,
    760,
    350,
    120,
    "Citations",
    "Document ID | Source path\nRelevance score | Text evidence",
    "#ec4899",
)

arrow((560, 400), (430, 410), "#8b5cf6")
arrow((255, 470), (255, 555), "#8b5cf6")
arrow((255, 675), (255, 760), "#ec4899")
arrow((430, 820), (560, 405), "#ec4899")

# Observability/security
box(
    1120,
    350,
    380,
    120,
    "Security Boundary",
    "Environment secrets\nBearer authentication\nRead-only operations",
    "#dc3545",
)

box(
    1120,
    555,
    380,
    120,
    "Observability",
    "Trace IDs | Tool duration\nStatus | Retrieval scores",
    "#64748b",
)

box(
    1120,
    760,
    380,
    120,
    "Deployment",
    "Local Python processes\nDocker Compose services",
    "#334155",
)

arrow((1040, 400), (1120, 410), "#dc3545")
arrow((1040, 580), (1120, 615), "#64748b")
arrow((1040, 750), (1120, 820), "#334155")

draw.text(
    (70, 915),
    "Synthetic demonstration environment | Recommendations require operator verification",
    font=small_font,
    fill="#718096",
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
image.save(OUTPUT, format="PNG", optimize=True)

print(f"Created: {OUTPUT}")
