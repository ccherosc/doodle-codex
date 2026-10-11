"""Build the Doodle Codex catalog site from a Krita Tile Factory checkout.

    python build.py <project root> [<tilekit demo dir>]

Reads <root>/game through its reference loader (tilekit.Kit) and writes, next
to this file: index.html, catalog.md, catalog.json, llms.txt, assets/ (the
strips the page animates) and sheets/ (static labelled contact sheets, which
are what a reader that cannot run JavaScript should look at).
"""
import html
import json
import re
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(sys.argv[1])
DEMO = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None
HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(ROOT, "game")
URL = "https://ccherosc.github.io/doodle-codex/"

sys.path.insert(0, os.path.join(ROOT, "tools"))
import tilekit                                              # noqa: E402
from tilelib import creatures, props, terrains              # noqa: E402

kit = tilekit.Kit(GAME)
F = kit.frames
PAPER = (243, 236, 220, 255)
INK = (43, 37, 32, 255)
esc = html.escape

for d in ("assets", "sheets"):
    shutil.rmtree(os.path.join(HERE, d), ignore_errors=True)
    os.makedirs(os.path.join(HERE, d))


def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def doc(table, name):
    fn = table.get(name)
    return " ".join(((fn.__doc__ or "") if fn else "").strip().split("\n\n")[0].split())


def put(rel_src, rel_dst):
    """Copy a file out of game/ into assets/, return the site-relative path."""
    dst = os.path.join(HERE, "assets", rel_dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(os.path.join(GAME, rel_src), dst)
    return "assets/" + rel_dst.replace("\\", "/")


def save(img, rel_dst):
    dst = os.path.join(HERE, rel_dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img.save(dst, optimize=True)
    return rel_dst.replace("\\", "/")


def copy_any(src, rel_dst):
    if not os.path.exists(src):
        print("  missing, skipped:", src)
        return None
    dst = os.path.join(HERE, rel_dst)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return rel_dst.replace("\\", "/")


def sheet(name, title, entries, cols, scale=2):
    """A static labelled contact sheet. entries: [(label, image)]."""
    cw = max(im.width for _l, im in entries) * scale
    ch = max(im.height for _l, im in entries) * scale
    f, ft = font(12), font(20)
    pad, lab, head = 10, 30, 40
    rows = -(-len(entries) // cols)
    W = cols * (cw + pad) + pad
    out = Image.new("RGBA", (W, head + rows * (ch + lab + pad) + pad), PAPER)
    d = ImageDraw.Draw(out)
    d.text((pad, 9), title, fill=INK, font=ft)
    for i, (label, im) in enumerate(entries):
        x = pad + (i % cols) * (cw + pad)
        y = head + (i // cols) * (ch + lab + pad)
        d.rectangle((x - 1, y - 1, x + cw, y + ch), outline=(225, 214, 188, 255))
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        out.alpha_composite(big, (x + (cw - big.width) // 2, y + ch - big.height))
        words, line, lines = re.findall(r"[^_ ]+[_ ]?", label), "", []
        for w in words:
            if d.textlength(line + w, font=f) > cw and line:
                lines.append(line)
                line = ""
            line += w
        lines.append(line)
        for k, ln in enumerate(lines[:2]):
            d.text((x, y + ch + 2 + k * 13), ln, fill=INK, font=f)
    path = save(out.convert("RGB"), "sheets/%s.png" % name)
    SHEETS.append((path, title, out.size))
    print("  sheet", path, out.size)
    return path


def person_strip(files):
    out = Image.new("RGBA", (kit.tile * F, kit.tile))
    for f in range(F):
        out.alpha_composite(kit.compose(files, f), (f * kit.tile, 0))
    return out


def frame0(rel, fw=None, fh=None):
    return kit.cell(rel, 0, 0, fw, fh) if fw else kit.cell(rel, 0)


SHEETS = []
CAT = {"schema": "doodle-codex.catalog/1", "site": URL, "tile": kit.tile,
       "animation": kit.catalog["animation"], "facings": kit.catalog["facings"]}
MD = []          # catalog.md lines
H = []           # index.html body


def canvas(src, fw, fh, rep=1, show=None):
    show = show or (fw * 2 if fw <= 64 else min(fw * 1.5, 264))
    return ('<canvas width="%d" height="%d" data-src="%s" data-fw="%d" data-fh="%d" data-rep="%d" '
            'style="width:%dpx"></canvas>' % (fw * rep, fh * rep, src, fw, fh, rep, show))


def card(media, label, sub="", note=""):
    return ('<figure>%s<figcaption>%s%s%s</figcaption></figure>'
            % (media, esc(label),
               '<span class="id">%s</span>' % esc(sub) if sub else "",
               '<span class="note">%s</span>' % esc(note) if note else ""))


def section(sid, title, count, intro):
    H.append('<section id="%s"><div class="sec-head"><h2>%s</h2><span class="count">%s</span></div>'
             '<p class="intro">%s</p>' % (sid, esc(title), esc(count), intro))
    MD.append("\n## %s (%s)\n" % (title, count))


def sheet_link(path, text):
    return '<a class="sheet" href="%s">static sheet: %s</a>' % (path, esc(text))


# --- terrain ---------------------------------------------------------------------
print("terrain")
T = kit.terrain
order = T["elevation_low_to_high"]
nvar = sum(len(b.get("variants", [])) for b in T["base"].values())
section("terrain", "Terrain", "%d terrains, %d variants" % (len(order), nvar),
        "Square, opaque, seamless 64&times;64 ground, six frames at 10 fps. Each base is shown 3&times;3 "
        "to prove the seam. A variant is its base plus one interior feature, and tiles against "
        "everything its base does; an engine picks one by a weighted hash on all-one-terrain cells. "
        "Listed low to high in draw order: the higher terrain owns the edge between two.")
MD.append("Seamless 64x64 tiles, 6 frames. Listed low to high in elevation (draw order).\n")
MD.append("| terrain | gameplay (suggested) | variants |\n| --- | --- | --- |")
ent, CAT["terrain"] = [], {}
H.append('<div class="grid">')
for t in order:
    b = T["base"][t]
    g = b.get("gameplay_suggested", {})
    gp = ", ".join(["walk x%s" % g.get("speed", 1.0) if g.get("walkable") else "not walkable"]
                   + ["%s %s" % (k, v) for k, v in g.items() if isinstance(v, str)]
                   + [k.replace("_", " ") for k, v in g.items() if v is True and k != "walkable"])
    src = put(b["file"], "terrain/%s.png" % t)
    H.append(card(canvas(src, 64, 64, 3, 144), t, gp, doc(terrains.RECIPES, t)))
    ent.append((t, frame0(b["file"])))
    vs = b.get("variants", [])
    MD.append("| %s | %s | %s |" % (t, gp, "; ".join("%s (%s)" % (v["name"], v["note"]) for v in vs)))
    CAT["terrain"][t] = {"gameplay_suggested": b.get("gameplay_suggested"),
                         "variants": {v["name"]: v["note"] for v in vs}}
H.append("</div><h3>Variants</h3><div class='grid'>")
for t in order:
    for v in T["base"][t].get("variants", []):
        src = put(v["file"], "terrain/%s__%s.png" % (t, v["name"]))
        H.append(card(canvas(src, 64, 64), v["name"], t, v["note"]))
        ent.append(("%s: %s" % (t, v["name"]), frame0(v["file"])))
H.append("</div>")
p = sheet("terrain", "Terrain: %d bases then %d variants (frame 0, 2x)" % (len(order), nvar), ent, 12)
H.append(sheet_link(p, "every terrain tile") + "</section>")

# --- transitions -----------------------------------------------------------------
print("transitions")
tt = T["transitions"]
section("transitions", "Transitions", "%d overlay, %d shore, %d scorch atlases"
        % (len(tt["overlay"]), len(tt["shore"]), len(tt["scorch"])),
        "Borders are a corner-Wang set drawn on a dual grid: 16 masks per terrain, six frames each. "
        "A cell with several terrains is the lowest as a base plus one overlay per higher terrain. "
        "<b>Shore</b> atlases replace the overlay when the lowest terrain is water (foam), "
        "<b>scorch</b> when it is lava (charred crust). Diagonal roads, rivers and trails stay "
        "connected by design. The pictures below are static proofs built from the shipped atlases.")
MD.append("Corner-Wang (16 masks) on a dual grid; overlay per higher terrain, `shore` over water, "
          "`scorch` over lava. Elevation: %s.\n" % " < ".join(order))
CAT["transitions"] = {"elevation_low_to_high": order, "overlay": sorted(tt["overlay"]),
                      "shore": sorted(tt["shore"]), "scorch": sorted(tt["scorch"])}
V = os.path.join(ROOT, "art", "validation")
H.append('<div class="grid proof">')
pics = [("transitions/map_0.png", "proof map 0: every terrain meeting its neighbours"),
        ("transitions/map_1.png", "proof map 1"), ("transitions/map_2.png", "proof map 2"),
        ("transitions/diagonals.png", "one-cell diagonal paths stay continuous"),
        ("transitions/pair_water__grass.png", "pair: grass over water, 16 masks (shore)"),
        ("transitions/pair_roads__grass.png", "pair: roads and grass"),
        ("transitions/pair_lava__grass.png", "pair: grass over lava (scorch)"),
        ("transitions/pair_ash__snow.png", "pair: ash and snow"),
        ("transitions/pair_grass__rock.png", "pair: rock over grass (dual-grid cliff)")]
for rel, cap in pics:
    q = copy_any(os.path.join(V, rel), "sheets/" + rel.replace("transitions/", "transition_"))
    if q:
        H.append(card('<a href="%s"><img loading="lazy" src="%s" alt="%s"></a>' % (q, q, esc(cap)), cap))
        SHEETS.append((q, "Transitions: " + cap, Image.open(os.path.join(HERE, q)).size))
H.append("</div></section>")

# --- walls -----------------------------------------------------------------------
print("walls")
W = kit.walls
section("walls", "Wall kit", "%d pieces, 1 material (rock)" % len(W["kinds"]["rock"]["pieces"]),
        "Hand-placeable cliff and wall pieces on the ordinary grid: one piece per cell, and the "
        "cell is what it blocks. The name says where the piece sits in a wall; a 256-entry lookup "
        "on the eight neighbours picks it automatically. Stone face is shown under every "
        "south-facing edge.")
MD.append(W["rule"] + "\n\nNaming: " + "; ".join("`%s` = %s" % kv for kv in W["naming"].items()) + "\n")
ent = []
H.append('<div class="grid">')
for name, rec in W["kinds"]["rock"]["pieces"].items():
    src = put(rec["file"], "walls/rock/%s.png" % name)
    H.append(card(canvas(src, 64, 64), name, "rock"))
    ent.append((name, frame0(rec["file"])))
H.append("</div>")
MD.append("Pieces: " + ", ".join("`%s`" % n for n in W["kinds"]["rock"]["pieces"]) + "\n")
CAT["walls"] = {"rock": {"pieces": list(W["kinds"]["rock"]["pieces"]), "naming": W["naming"],
                         "inset_px": W["kinds"]["rock"]["inset_px"], "face_px": W["kinds"]["rock"]["face_px"]}}
p = sheet("walls", "Rock wall kit: %d labelled pieces (2x)" % len(ent), ent, 10)
H.append(sheet_link(p, "all wall pieces"))
H.append('<div class="grid proof">')
for rel, cap in (("walls/rock_demo.png", "a yard, a maze and a cliff line built from the kit"),
                 ("walls/rock_pieces.png", "the pieces in place, labelled")):
    q = copy_any(os.path.join(V, rel), "sheets/" + rel.replace("walls/", "walls_"))
    if q:
        H.append(card('<a href="%s"><img loading="lazy" src="%s" alt="%s"></a>' % (q, q, esc(cap)), cap))
        SHEETS.append((q, "Walls: " + cap, Image.open(os.path.join(HERE, q)).size))
H.append("</div></section>")

# --- structures ------------------------------------------------------------------
print("structures")
S = kit.structures
nloc = sum(1 for r in S.values() if r["scale"] == "local")
section("structures", "Structures and props", "%d props, %d at a person's scale" % (len(S), nloc),
        "Cut-outs that stand on terrain, drawn in elevation with a ground shadow. <b>map</b> scale "
        "means a landmark for the world map (a castle two tiles wide); <b>local</b> scale means "
        "drawn to stand beside a person. Trees block only the trunk, so a person can walk behind "
        "the crown. Some have a second state (open, raided).")
MD.append("| name | tiles | scale | passable | states | description |\n| --- | --- | --- | --- | --- | --- |")
ent, CAT["structures"] = [], {}
H.append('<div class="grid wide">')
for name, r in S.items():
    fw, fh = r["frame_w"], r["frame_h"]
    d = doc(props.RECIPES, name)
    foot = "%dx%d" % tuple(r["footprint_tiles"])
    sub = "%s tiles, %s scale%s" % (foot, r["scale"], ", passable" if r.get("passable") else "")
    src = put(r["file"], "structures/%s.png" % name)
    H.append(card(canvas(src, fw, fh), name, sub, d))
    ent.append((name, frame0(r["file"], fw, fh)))
    st = r.get("states", {})
    for sname, sr in st.items():
        src = put(sr["file"], "structures/%s_%s.png" % (name, sname))
        H.append(card(canvas(src, sr["frame_w"], sr["frame_h"]), "%s: %s" % (name, sname), sub, sr.get("label", "")))
        ent.append(("%s: %s" % (name, sname), kit.cell(sr["file"], F - 1, 0, sr["frame_w"], sr["frame_h"])))
    MD.append("| %s | %s | %s | %s | %s | %s |" % (name, foot, r["scale"], "yes" if r.get("passable") else "",
                                                 ", ".join(st), d))
    CAT["structures"][name] = {"footprint_tiles": r["footprint_tiles"], "scale": r["scale"],
                               "passable": bool(r.get("passable")), "walk_behind": bool(r.get("walk_behind")),
                               "states": list(st), "description": d}
H.append("</div>")
p = sheet("structures", "Structures: %d props and their states (1x)" % len(S), ent, 8, 1)
H.append(sheet_link(p, "every structure") + "</section>")

# --- monsters --------------------------------------------------------------------
print("monsters")
M = kit.monsters
base = [n for n, r in M.items() if not r["elite"]]
elite = [n for n, r in M.items() if r["elite"]]
npair = sum(len(M[n]["states"]) for n in base)
section("monsters", "Monsters", "%d creatures, %d elites, %d states x 4 facings"
        % (len(base), len(elite), npair),
        "Cut-out actors. Every creature has idle, walk, attack, hurt, die and poof (the corpse "
        "vanishing in smoke) in four facings; some add a signature. Below: idle in all four "
        "facings, then every other state facing down. Tier is difficulty 1&ndash;5. An elite is "
        "its base creature in another palette with the same silhouette.")
MD.append("| creature | tier | rank | tiles | states | description |\n| --- | --- | --- | --- | --- | --- |")
ent, CAT["monsters"] = [], {}
for name in sorted(base, key=lambda n: (M[n]["tier"], base.index(n))):
    r = M[name]
    d = doc(creatures.RECIPES, name)
    foot = "%dx%d" % tuple(r["footprint_tiles"])
    states = list(r["states"])
    H.append('<article><h3>%s <span class="count">tier %d &middot; %s &middot; %s tiles</span></h3>'
             '<p class="intro">%s<br><span class="id">states: %s</span></p><div class="row">'
             % (esc(name), r["tier"], r["rank"], foot, esc(d), ", ".join(states)))
    for facing in kit.catalog["facings"]:
        f = r["states"]["idle"]["facings"][facing]
        src = put(f["file"], "monsters/%s/idle_%s.png" % (name, facing))
        H.append(card(canvas(src, f["frame_w"], f["frame_h"]), "idle", facing))
    for s in states:
        if s == "idle":
            continue
        f = r["states"][s]["facings"]["down"]
        src = put(f["file"], "monsters/%s/%s_down.png" % (name, s))
        H.append(card(canvas(src, f["frame_w"], f["frame_h"]), s, "down"))
    # the static sheet: every state, facing right, registered by anchor
    fs = {s: r["states"][s]["facings"]["right"] for s in states}
    ax, ay = max(f["anchor"][0] for f in fs.values()), max(f["anchor"][1] for f in fs.values())
    cw = max(ax - f["anchor"][0] + f["frame_w"] for f in fs.values())
    ch = max(ay - f["anchor"][1] + f["frame_h"] for f in fs.values())
    sc = 2 if cw <= 128 else 1
    lab = 70
    im = Image.new("RGBA", (lab + F * cw * sc, len(states) * ch * sc), PAPER)
    dr = ImageDraw.Draw(im)
    for j, s in enumerate(states):
        dr.text((6, j * ch * sc + 6), s, fill=INK, font=font(13))
        for i in range(F):
            fr = kit.cell(fs[s]["file"], i, 0, fs[s]["frame_w"], fs[s]["frame_h"])
            fr = fr.resize((fr.width * sc, fr.height * sc), Image.NEAREST)
            im.alpha_composite(fr, (lab + (i * cw + ax - fs[s]["anchor"][0]) * sc,
                                    (j * ch + ay - fs[s]["anchor"][1]) * sc))
    q = save(im.convert("RGB"), "sheets/monster_%s.png" % name)
    SHEETS.append((q, "Monster %s: every state x 6 frames, facing right" % name, im.size))
    H.append("</div>" + sheet_link(q, "%s, every state x 6 frames, facing right" % name) + "</article>")
    ent.append(("%s (tier %d)" % (name, r["tier"]), frame0(r["states"]["idle"]["facings"]["down"]["file"],
                                                         r["box"][0], r["box"][1])))
    MD.append("| %s | %d | %s | %s | %s | %s |" % (name, r["tier"], r["rank"], foot, ", ".join(states), d))
    CAT["monsters"][name] = {"tier": r["tier"], "rank": r["rank"], "footprint_tiles": r["footprint_tiles"],
                             "states": states, "description": d}
H.append('<h3>Elites</h3><div class="grid">')
for name in elite:
    r = M[name]
    f = r["states"]["idle"]["facings"]["down"]
    src = put(f["file"], "monsters/%s/idle_down.png" % name)
    H.append(card(canvas(src, f["frame_w"], f["frame_h"]), name, "tier %d" % r["tier"]))
    ent.append((name, frame0(f["file"], f["frame_w"], f["frame_h"])))
    CAT["monsters"][name] = {"tier": r["tier"], "rank": r["rank"], "elite": True, "states": list(r["states"])}
H.append("</div>")
MD.append("\nElites (palette swaps, same states as their base): " + ", ".join(elite) + "\n")
p = sheet("monsters", "Monsters: %d creatures by tier, then %d elites (idle, facing down, 2x)"
          % (len(base), len(elite)), ent, 7, 2)
H.append(sheet_link(p, "every monster") + "</section>")

# --- people ----------------------------------------------------------------------
print("people")
R = kit.rules
heroes, npcs = kit.heroes, kit.npcs
bodies = list(heroes) + [b for b in npcs if b not in heroes]
looks = list(next(iter(npcs.values()))["looks"])
hostile = set(R.get("hostile_looks_suggested", []))
section("people", "People: heroes and NPCs", "%d bodies, %d skins, %d hair colours, %d states"
        % (len(bodies), len(R["skins"]), len(R["hair_colors"]), len(R["states"])),
        "People are a paperdoll: a body in underwear plus wardrobe pieces the engine stacks, so any "
        "body can wear any item. Every piece exists for every body, state and facing. The strips "
        "below are composed from the shipped pieces exactly as an engine would.")
MD.append("Paperdoll: body + skin + hair + wardrobe items, stacked by the engine. "
          "Bodies: %s. Skins: %s. Hair colours: %s. States: %s.\n"
          % (", ".join(bodies), ", ".join(R["skins"]), ", ".join(R["hair_colors"]), ", ".join(R["states"])))
CAT["people"] = {"bodies": bodies, "skins": list(R["skins"]), "hair_colors": list(R["hair_colors"]),
                 "states": list(R["states"]), "hero_builds": {}, "npc_looks": {}}


def pcard(strip, rel, label, sub="", note=""):
    return card(canvas(save(strip, "assets/people/%s.png" % rel), 64, 64), label, sub, note)


ent = []
H.append('<h3>Bodies</h3><div class="grid">')
for b in bodies:
    st = person_strip(kit.person_layers(b, [], "down"))
    H.append(pcard(st, "body_" + b, b, "player" if b in heroes else "npc body"))
    ent.append(("body: " + b, st.crop((0, 0, 64, 64))))
H.append('</div><h3>Skins and hair colours</h3><div class="grid">')
for tone in R["skins"]:
    st = person_strip(kit.person_layers("m_burly", [], "down", tone=tone))
    H.append(pcard(st, "skin_" + tone, tone, "skin"))
    ent.append(("skin: " + tone, st.crop((0, 0, 64, 64))))
for col in R["hair_colors"]:
    st = person_strip(kit.person_layers("f_slender", [], "down", hair=col))
    H.append(pcard(st, "hair_" + col, col, "hair colour"))
    ent.append(("hair: " + col, st.crop((0, 0, 64, 64))))
H.append("</div>")
sheet("people_bodies", "People: %d bodies, %d skins, %d hair colours (2x)"
      % (len(bodies), len(R["skins"]), len(R["hair_colors"])), ent, 10)

ent = []
H.append('<h3>Hero builds</h3><div class="grid">')
MD.append("### Hero builds\n\n| build | items |\n| --- | --- |")
for hb in heroes:
    for build, rec in heroes[hb]["builds"].items():
        st = person_strip(kit.build_layers(hb, build, "down"))
        H.append(pcard(st, "%s_%s" % (hb, build), build, hb, ", ".join(rec["items"])))
        ent.append(("%s: %s" % (hb, build), st.crop((0, 0, 64, 64))))
        if hb == next(iter(heroes)):
            MD.append("| %s | %s |" % (build, ", ".join(rec["items"])))
            CAT["people"]["hero_builds"][build] = rec["items"]
H.append("</div>")
sheet("people_heroes", "Hero builds: 2 heroes x %d sets (2x)" % len(next(iter(heroes.values()))["builds"]), ent, 10)

PREF = {"king": "m_portly", "queen": "f_slender", "barmaid": "f_curvy", "guard": "m_burly",
        "wizard": "m_lanky", "necromancer": "m_elder", "hunter": "f_athletic", "farmer": "m_stocky",
        "blacksmith": "m_burly", "witch": "f_elder", "priest": "m_elder", "innkeeper": "m_portly"}
nb = list(npcs)
ent = []
H.append('<h3>NPC looks</h3><div class="grid">')
MD.append("\n### NPC looks (any look fits any body)\n\n| look | hostile | items |\n| --- | --- | --- |")
for i, look in enumerate(looks):
    b = PREF.get(look) if PREF.get(look) in npcs else nb[i % len(nb)]
    rec = npcs[b]["looks"][look]
    st = person_strip(kit.build_layers(b, look, "down"))
    hz = look in hostile or rec.get("hostile_suggested")
    H.append(pcard(st, "look_" + look, look, b + (" &middot; hostile" if hz else "").replace("&middot;", "-"),
                   ", ".join(rec["items"])))
    ent.append((look + (" (hostile)" if hz else ""), st.crop((0, 0, 64, 64))))
    MD.append("| %s | %s | %s |" % (look, "yes" if hz else "", ", ".join(rec["items"])))
    CAT["people"]["npc_looks"][look] = {"hostile": bool(hz), "items": rec["items"]}
H.append("</div>")
sheet("people_npcs", "NPC looks: %d (2x), each on one sample body" % len(looks), ent, 10)

# every state, on one armed hero and the two ranged looks
hb = next(iter(heroes))
builds = heroes[hb]["builds"]
armed = next((b for b, r in builds.items() if any(i.startswith(("sword", "longsword")) for i in r["items"])),
             list(builds)[len(builds) // 2])
ent = []
H.append('<h3>The %d states (hero in "%s", facing down)</h3><div class="grid">' % (len(R["states"]), armed))
for s in R["states"]:
    st = person_strip(kit.build_layers(hb, armed, "down", s))
    notes = []
    if s in R.get("cyclic_states", []):
        notes.append("cyclic")
    if s in R.get("hold_frames", {}):
        notes.append("hold frames %s" % R["hold_frames"][s])
    if not R["loops"].get(s, True):
        notes.append("holds last frame")
    H.append(pcard(st, "state_%s" % s, s, ", ".join(notes)))
    ent.append((s, st))
for look, s, b in (("hunter", "shoot", "f_athletic"), ("wizard", "cast", "m_lanky")):
    if look in looks:
        st = person_strip(kit.build_layers(b, look, "right", s))
        H.append(pcard(st, "state_%s_%s" % (look, s), "%s: %s" % (look, s), "right"))
        ent.append(("%s %s (right)" % (look, s), st))
H.append('</div><h3>Four facings (walk)</h3><div class="grid">')
for facing in kit.catalog["facings"]:
    st = person_strip(kit.build_layers(hb, armed, facing, "walk"))
    H.append(pcard(st, "walk_%s" % facing, "walk", facing))
    ent.append(("walk " + facing, st))
H.append("</div>")
sheet("people_states", "People: every state as a 6-frame strip (hero in %s, 1x)" % armed, ent, 3, 1)

# the wardrobe, each item alone on a body
print("wardrobe")
A = kit.accessories
ent, by_slot = [], {}
for it, rec in A.items():
    if it.startswith(("hair_", "beard_")) or it in ("hair", "beard"):
        continue
    by_slot.setdefault(rec["slot"], []).append(it)
    ent.append(("%s [%s]" % (it, rec["slot"]), kit.compose(kit.person_layers("hero", [it], "down"), 0)))
p = sheet("wardrobe", "Wardrobe: %d items, each alone on the hero body (2x) [slot]" % len(ent), ent, 12)
H.append('<h3>Wardrobe</h3><p class="intro">%d items across %d slots, each fitted to all %d bodies: %s.</p>'
         % (len(ent), len(by_slot), len(bodies),
            "; ".join("<b>%s</b>: %s" % (esc(s), esc(", ".join(v))) for s, v in by_slot.items())))
H.append('<a href="%s"><img class="full" loading="lazy" src="%s" alt="every wardrobe item on the hero body"></a>' % (p, p))
MD.append("\n### Wardrobe items by slot\n")
for s, v in by_slot.items():
    MD.append("- **%s**: %s" % (s, ", ".join(v)))
CAT["people"]["wardrobe_by_slot"] = by_slot
H.append("</section>")

# --- portraits and ui ------------------------------------------------------------
print("portraits, ui")
section("ui", "UI and portraits", "%d nine-slice pieces, portraits for %d bodies"
        % (len(kit.ui["pieces"]), len(kit.portraits["bodies"])),
        "Parchment UI as nine-slice pieces (corners fixed, edges tiled), and dialogue portraits "
        "layered from the same wardrobe as the sprite, so a portrait always matches what the "
        "person is wearing. Portraits are stills, facing the viewer.")
ent = []
H.append('<div class="grid wide">')
for i, look in enumerate(["king", "queen", "wizard", "guard", "barmaid", "farmer", "pirate",
                          "necromancer", "hunter", "jester", "sailor", "imperial_soldier"]):
    if look not in looks:
        continue
    b = PREF.get(look) if PREF.get(look) in npcs else nb[i % len(nb)]
    im = kit.portrait(b, npcs[b]["looks"][look]["items"])
    q = save(im, "assets/portraits/%s.png" % look)
    H.append(card('<img loading="lazy" src="%s" alt="portrait: %s" style="width:%dpx">' % (q, look, im.width), look, b))
    ent.append(("%s (%s)" % (look, b), im))
for hb2 in heroes:
    b0 = list(heroes[hb2]["builds"])[-1]
    im = kit.portrait(hb2, heroes[hb2]["builds"][b0]["items"])
    q = save(im, "assets/portraits/%s.png" % hb2)
    H.append(card('<img loading="lazy" src="%s" alt="portrait: %s" style="width:%dpx">' % (q, hb2, im.width), hb2, b0))
    ent.append(("%s (%s)" % (hb2, b0), im))
H.append("</div>")
sheet("portraits", "Dialogue portraits: a sample (1x). Any body x any outfit composes.", ent, 7, 1)
ent = []
H.append('<div class="grid wide">')
for name, prec in kit.ui["pieces"].items():
    q = put(prec["file"], "ui/%s.png" % name)
    im = kit.image(prec["file"])
    H.append(card('<img loading="lazy" src="%s" alt="ui: %s" style="width:%dpx">' % (q, name, im.width * 2), name,
                  "nine-slice, corner %d" % prec["corner"]))
    ent.append((name, im))
    ent.append((name + " as 160x64 box", kit.ui_box(name, 160, 64)))
H.append("</div>")
sheet("ui", "UI: nine-slice pieces and each one sliced to a box (2x)", ent, 5)
CAT["ui"] = list(kit.ui["pieces"])
MD.append("UI pieces: %s. Portraits compose for all %d bodies from the worn items.\n"
          % (", ".join(kit.ui["pieces"]), len(kit.portraits["bodies"])))
H.append("</section>")

# --- loot, fx, icons -------------------------------------------------------------
print("loot, fx, icons")
L, X, IC = kit.loot["loot"], kit.fx["fx"], kit.icons["icons"]
section("items", "Loot, effects and icons", "%d drops, %d effects, %d icons" % (len(L), len(X), len(IC)),
        "Loot is what a monster leaves when its smoke clears. Effects are projectiles the engine "
        "moves (drawn pointing right, shipped per facing) and a hit spark. Icons are still "
        "64&times;64 inventory pictures.")
ent = []
H.append('<div class="grid">')
for name, r in L.items():
    src = put(r["file"], "loot/%s.png" % name)
    H.append(card(canvas(src, r["frame_w"], r["frame_h"]), name, "loot: " + str(r.get("kind", ""))))
    ent.append(("loot: " + name, frame0(r["file"])))
for name, r in X.items():
    rel = r["files"].get("right") or r["files"]["any"]
    src = put(rel, "fx/%s.png" % name)
    H.append(card(canvas(src, 64, 64), name, "fx" + (", directional" if r.get("directional") else "")))
    ent.append(("fx: " + name, kit.cell(rel, 2)))
H.append('</div><h3>Icons</h3><div class="grid small">')
slots = {}
for name, r in IC.items():
    q = put(r["file"], "icons/%s.png" % name)
    H.append(card('<img loading="lazy" src="%s" alt="icon: %s" width="64" height="64">' % (q, name), name, str(r.get("slot") or "")))
    ent.append(("icon: " + name, kit.image(r["file"])))
    slots.setdefault(str(r.get("slot") or "other"), []).append(name)
H.append("</div>")
p = sheet("items", "Loot (%d), effects (%d), icons (%d) (2x)" % (len(L), len(X), len(IC)), ent, 12)
H.append(sheet_link(p, "loot, effects and every icon") + "</section>")
MD.append("Loot: %s. Effects: %s.\n\nIcons by slot:\n" % (", ".join(L), ", ".join(X)))
for s, v in slots.items():
    MD.append("- **%s**: %s" % (s, ", ".join(v)))
CAT["loot"], CAT["fx"], CAT["icons"] = list(L), list(X), slots

# --- scenes ----------------------------------------------------------------------
print("scenes")
SC = []
if DEMO:
    for fn, cap in (("demo_scene.png", "a local scene: walled yard, trees a person walks behind, chest, people"),
                    ("demo_map.png", "a map assembled by the reference loader: terrain, transitions, structures, monsters"),
                    ("demo_dialogue.png", "a dialogue box: nine-slice panel and a composed portrait"),
                    ("demo_scene.gif", "the local scene, animated")):
        q = copy_any(os.path.join(DEMO, fn), "sheets/" + fn)
        if q:
            SC.append((q, cap))
            SHEETS.append((q, "Scene: " + cap, Image.open(os.path.join(HERE, q)).size))

GAPS = [
    ("Local-scale buildings", "One hut is the only house a person can stand beside. A village scene needs a second house, an inn or shop front, and a door-in-a-wall piece for the rock kit (a cave or cellar entrance). Every other building is a world-map landmark."),
    ("Interiors", "No floorboards or flagstones as terrain, no interior wall kit, no furniture (table, bed, shelf, barrel, crate, hearth)."),
    ("Map landmarks named on the world map and not drawn", "The Tower of Legend, a lighthouse or sea tower, a mountain fortress, a temple or shrine."),
    ("Monsters by region", "No sea creature that fights (the sea serpent is a prop), no desert creature (scorpion or snake), nothing for the swamp beyond the frog, nothing for snow beyond the yeti, no elemental for ash."),
    ("Signatures, elites, portraits", "The imp and beastman have no signature state or elite; golem and treant have no signature; ogre, treant and dragon have no elite; the four boss lords have no dialogue portrait."),
    ("A second wall material", "The wall kit is rock only: no timber palisade or dressed stone, no gate or door piece, no second height."),
    ("UI", "Five parchment pieces only: no health or stamina bars, inventory slots, cursor or font."),
    ("Loot", "Gold, three gems, a sword and an axe. Potions and keys exist as icons but not as dropped loot."),
    ("Faces", "At 64 px a face is two eyes and a brow. Portraits carry the detail; sprites do not. More facial detail is under consideration, not built."),
    ("Terrain", "No cliffs within one terrain (a height step of grass over grass); farmland furrows only run east-west; edge textures have one seed each."),
    ("Gameplay data", "Only suggested data ships: walkability per terrain, blocked cells, idle hurtboxes, impact frames. No per-state hitboxes."),
]

# --- write -----------------------------------------------------------------------
counts = [("terrain tiles", len(order) + nvar), ("structures", len(S)), ("creatures", len(base)),
          ("elites", len(elite)), ("bodies", len(bodies)), ("wardrobe items", sum(map(len, by_slot.values()))),
          ("NPC looks", len(looks)), ("icons", len(IC)), ("wall pieces", len(W["kinds"]["rock"]["pieces"]))]
CAT["counts"] = dict(counts)
CAT["known_gaps"] = [{"title": a, "detail": b} for a, b in GAPS]
CAT["sheets"] = [{"url": URL + p, "title": t, "size": list(sz)} for p, t, sz in SHEETS]

game_md = copy_any(os.path.join(ROOT, "GAME_INTEGRATION.md"), "GAME_INTEGRATION.md")

head_md = [
    "# Doodle Codex: full asset catalog",
    "",
    "The art library for *Norfair Chronicles*, a real-time overhead action RPG (Godot 4, flat 2D, "
    "y-sorted): a world map for travel and local scenes for play. Everything is drawn in one "
    "pencil-doodle style on a 64x64 grid, animated as 6-frame horizontal strips at 10 fps, in "
    "four facings (down, left, right, up) where a thing can turn.",
    "",
    "This file is the text inventory. It is generated from the shipped game package, so the names "
    "here are the real asset names. Site: " + URL,
    "",
    "## How to look at the art without running the page",
    "",
    "Each of these is a static PNG with every asset labelled:",
    "",
] + ["- [%s](%s%s) (%dx%d)" % (t, URL, p, sz[0], sz[1]) for p, t, sz in SHEETS] + [
    "",
    "The engine contract (file layout, JSON fields, autotile rule, paperdoll composition): "
    "[GAME_INTEGRATION.md](%sGAME_INTEGRATION.md). Machine-readable summary: [catalog.json](%scatalog.json)." % (URL, URL),
    "",
    "## Counts",
    "",
] + ["- %s: %d" % c for c in counts] + [
    "",
    "## Known gaps (what the library does not have yet)",
    "",
] + ["%d. **%s.** %s" % (i + 1, a, b) for i, (a, b) in enumerate(GAPS)]
with open(os.path.join(HERE, "catalog.md"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(head_md + MD) + "\n")
with open(os.path.join(HERE, "catalog.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(CAT, fh, indent=1)
with open(os.path.join(HERE, "llms.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("# Doodle Codex\n\n> Animated pencil-doodle RPG art library for Norfair Chronicles. "
             "The page animates sprites with JavaScript; read these instead.\n\n"
             "- [Full text catalog](%scatalog.md)\n- [Summary JSON](%scatalog.json)\n"
             "- [Engine contract](%sGAME_INTEGRATION.md)\n\n## Labelled contact sheets\n\n" % (URL, URL, URL)
             + "\n".join("- [%s](%s%s)" % (t, URL, p) for p, t, _sz in SHEETS) + "\n")
open(os.path.join(HERE, ".nojekyll"), "w").close()

NAV = [("terrain", "Terrain"), ("transitions", "Transitions"), ("walls", "Walls"), ("structures", "Structures"),
       ("monsters", "Monsters"), ("people", "People"), ("ui", "UI"), ("items", "Items"), ("scenes", "Scenes"),
       ("gaps", "Gaps")]
page = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
ai = ('<section id="ai" class="ai"><div class="sec-head"><h2>Reading this without JavaScript</h2></div>'
      '<p class="intro">The sprites on this page are drawn onto canvases by a script. If you are a '
      'program, or the page looks empty, use these instead: '
      '<a href="catalog.md">catalog.md</a> (the full text inventory), '
      '<a href="catalog.json">catalog.json</a>, <a href="GAME_INTEGRATION.md">GAME_INTEGRATION.md</a> '
      '(the engine contract) and the static labelled contact sheets:</p><ul class="sheets">'
      + "".join('<li><a href="%s">%s</a> <span class="id">%dx%d</span></li>' % (p, esc(t), sz[0], sz[1])
                for p, t, sz in SHEETS) + "</ul></section>")
scenes = ('<section id="scenes"><div class="sec-head"><h2>Scenes</h2><span class="count">assembled from the '
          'shipped package</span></div><div class="grid proof">'
          + "".join(card('<a href="%s"><img loading="lazy" src="%s" alt="%s"></a>' % (q, q, esc(c)), c) for q, c in SC)
          + "</div></section>")
gaps = ('<section id="gaps"><div class="sec-head"><h2>Known gaps</h2><span class="count">what is not drawn yet'
        '</span></div><ol class="gaps">' + "".join("<li><b>%s.</b> %s</li>" % (esc(a), esc(b)) for a, b in GAPS)
        + "</ol></section>")
page = (page.replace("{{TAGS}}", "".join('<span class="tag">%d %s</span>' % (n, esc(l)) for l, n in counts))
        .replace("{{NAV}}", "".join('<a href="#%s">%s</a>' % n for n in NAV))
        .replace("{{BODY}}", ai + "\n".join(H) + scenes + gaps))
with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(page)

total = sum(os.path.getsize(os.path.join(r, f)) for r, _d, fs in os.walk(HERE) if ".git" not in r for f in fs)
print("done: %d sheets, site %.1f MB, index.html %d KB"
      % (len(SHEETS), total / 1e6, os.path.getsize(os.path.join(HERE, "index.html")) // 1024))
