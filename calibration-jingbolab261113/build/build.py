"""Assemble index.html: CoBRA deck head/CSS + JS tail, new slides from slides.src.html,
reused CoBRA slides pulled by {{REUSE:n}} with speaker notes from Speaking_draft."""
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
COBRA = HERE.parent.parent / "cobra-chi260414"  # sibling folder in the talk repo

src = (COBRA / "index.html").read_text()
s = (HERE / "slides.src.html").read_text()

DECK_OPEN = '<div class="deck" id="deck" tabindex="-1">'
BODY = src.index(DECK_OPEN)

# ---- speaker notes from the CoBRA speaking draft ----
draft = (COBRA / "Speaking_draft").read_text()
pages = {int(m.group(1)): m.group(2) for m in re.finditer(r"Page (\d+):\s*(.*?)(?=Page \d+:|\Z)", draft, re.S)}
notes = {k: re.sub(r"\s+", " ", v.replace("￼", "")).strip() for k, v in pages.items()}
notes[1] = ("So here is one example of closing this loop. " + notes[1].replace("Hi! I’m so happy to be here to share our work,", "This is our work,")
            .replace("I’m Xuan Liu, and this is joint work", "This is joint work"))
notes[3] = notes[3].replace("John Lin is a xxx", '"John Lin is a pharmacy shopkeeper who loves to help people..."')
notes[10] = (notes[10].split("衔接")[0].replace("multiple-choicse quesntiosn", "multiple-choice questions")
             .replace(" xxx", ""))
notes[14] = notes[14].replace(" xxx", "") + " Reproducibility, controllability, and generalization."


def block(n: str) -> str:
    """Return the first top-level slide div with data-slide=n inside the deck body."""
    pos = src.index(f'data-slide="{n}"', BODY)
    i = src.rfind('<div class="slide', 0, pos)
    depth = 0
    for m in re.finditer(r"<div\b|</div>", src[i:]):
        depth += 1 if m.group() == "<div" else -1
        if depth == 0:
            b = src[i : i + m.end()]
            break
    k = int(n)
    if notes.get(k):
        b = re.sub(r'data-notes="[^"]*"', 'data-notes="%s"' % html.escape(notes[k], quote=True), b, count=1)
    return b


# OPENING: CoBRA title slide (same layout + demo), only the title text swapped
OPEN_NOTES = ("Hi everyone, I'm Xuan Liu from UC San Diego. Today I want to talk about building closed-loop calibration for behavior simulation: "
              "how we can close the loop for agents that simulate people, using classic social science experiments. "
              "What you see here is a quick demo: the same agents, with their follow-the-crowd bias dialed to different levels.")
opening = block("1").replace('data-slide="1"', 'data-slide="opening"', 1)
opening = re.sub(r'data-notes="[^"]*"', 'data-notes="%s"' % html.escape(OPEN_NOTES, quote=True), opening, count=1)
OLD_T = ('<span style="font-size: 44px; color: var(--cobra-dark);" class="">CoBRA:</span> '
         '<span style="color: var(--g800); font-size: 38px;" class="">Programming Cognitive Bias in Social Agents<br>Using Classic Social Science Experiments</span>')
NEW_T = '<span style="font-size: 42px; color: #000; white-space: nowrap;" class="">Building <span style="color: var(--cobra-dark);">Closed-Loop Calibration</span> for Behavior Simulation</span>'
assert OLD_T in opening
opening = opening.replace(OLD_T, NEW_T)
DEMO_OLD = "width:calc(100% + 156px); margin-left:-78px; margin-top:0;"
assert DEMO_OLD in opening
opening = opening.replace(DEMO_OLD, "width:calc(100% + 156px); margin-left:-78px; margin-top:34px;")
TITLE_OLD = "text-align:center; flex-shrink:0; margin-top:-6px;"
assert TITLE_OLD in opening
opening = opening.replace(TITLE_OLD, "text-align:center; flex-shrink:0; margin-top:8px;")
opening, n_snake = re.subn(r'<img src="co_website/public/snake.svg"[^>]*>', "", opening, count=1)
assert n_snake == 1
# HOME link, bottom-left. Slide content is wrapped in .slide-zoom-wrap (inset 64px left / 40px bottom), hence negative offsets.
HOME = ('<a href="https://xuanl17.github.io" target="_blank" style="position:absolute; left:-40px; bottom:-11px; '
        'font-size:22px; color:var(--cobra-dark); text-decoration:none; z-index:5;">xuanl17.github.io</a>')
opening = opening[: opening.rfind("</div>")] + HOME + "\n</div>"
s = s.replace("{{OPENING}}", opening)

s = re.sub(r"\{\{SVG:([^}]+)\}\}", lambda m: (HERE.parent / m.group(1)).read_text(), s)
s = re.sub(r"\{\{REUSE:(\d+)\}\}", lambda m: block(m.group(1)), s)



head = src[: BODY + len(DECK_OPEN)]
head = head.replace("CoBRA — CHI 2026 Presentation", "Building Closed-Loop Calibration for Behavior Simulation — Xuan Liu")
head = re.sub(r'\s*<(?:link rel="canonical"|meta property="og:(?:url|image[^"]*)"|meta name="twitter:(?:url|image)")[^>]*>', "", head)

# TABLE_FONT_FIX: let table cells inherit the font-size set on their <table>
head = head.replace("</style></head>", "  .slide table[style*='font-size'] th, .slide table[style*='font-size'] td { font-size: inherit; }\n  </style></head>", 1)

progress = src.index('<div class="progress"')
tail = src[src.rfind("</div>", 0, progress):]

# BRANDING: opening slide shows avatar + "Xuan Liu"; CoBRA title/end slides keep the original co-author branding
SOLO = ("const soloBrandingHtml='<img src=\"cute-me.png\" alt=\"\" style=\"height:52px;width:46px;object-fit:cover;border-radius:4px;vertical-align:-16px;margin-right:10px;\">"
        "<span style=\"color:#000;font-weight:700;font-size:22px;\">Xuan Liu</span><span style=\"color:#000;font-size:22px;\">&nbsp;·&nbsp;</span>"
        "<img src=\"ucsd.png\" alt=\"\" style=\"height:48px;vertical-align:-10px;margin-right:8px;\"><span style=\"font-size:32px;font-weight:700;color:#00629B;text-decoration:underline;text-decoration-color:#FFCD00;text-decoration-thickness:3px;text-underline-offset:4px;\">UC San Diego</span>';\n")
tail = tail.replace("  const pageNumBrandingHtml=", "  " + SOLO + "  const pageNumBrandingHtml=", 1)
OLD_COND = "if(i===0||s.classList.contains('slide-end')){pn.innerHTML=pageNumBrandingHtml;}"
NEW_COND = "if(i===0){pn.innerHTML=soloBrandingHtml;}else if(s.classList.contains('slide-title')||s.classList.contains('slide-end')){pn.innerHTML=pageNumBrandingHtml;}"
assert tail.count(OLD_COND) == 2
tail = tail.replace(OLD_COND, NEW_COND)
out = head + "\n\n" + s + "\n" + tail
(HERE.parent / "index.html").write_text(out)
print("slides:", re.findall(r'<div class="slide[^"]*" data-slide="([^"]+)"', s))
