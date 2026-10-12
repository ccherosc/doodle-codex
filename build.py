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
section("transitions", "Transitions", "%d overlay, %d shore, %d scorch, %d cliff atlases"
        % (len(tt["overlay"]), len(tt["shore"]), len(tt["scorch"]), len(tt.get("cliff", {}))),
        "Borders are a corner-Wang set drawn on a dual grid: 16 masks per terrain, six frames each. "
        "A cell with several terrains is the lowest as a base plus one overlay per higher terrain. "
        "<b>Shore</b> atlases replace the overlay when the lowest terrain is water (foam), "
        "<b>scorch</b> when it is lava (charred crust). Diagonal roads, rivers and trails stay "
        "connected by design. <b>Cliff</b> atlases draw a height step inside one terrain (grass over "
        "grass) from an integer height per cell: a bank on the south-facing edge and a drawn rim "
        "on the other three, with foam or a charred line at its foot where it stands in water or "
        "lava. Four stone stairs (see Structures) are the way up. Every overlay, shore and scorch "
        "atlas also has three <b>alternate</b> drawings that can be mixed in tile by tile without "
        "a seam, so a long border does not repeat. The pictures below are static proofs built "
        "from the shipped atlases.")
MD.append("Corner-Wang (16 masks) on a dual grid; overlay per higher terrain, `shore` over water, "
          "`scorch` over lava. Elevation: %s.\n" % " < ".join(order))
MD.append("Cliffs (a height step within one terrain, heights per cell; a bank on the south-facing "
          "edge, a rim on the others, a wash atlas where the step stands in water or lava; the "
          "stairs_* structures cross it): %s. Alternates: %d more drawings of every overlay, shore "
          "and scorch atlas, seam-safe in any mix.\n"
          % (", ".join(sorted(tt.get("cliff", {}))), tt.get("alternates", {}).get("count", 1)))
CAT["transitions"] = {"elevation_low_to_high": order, "overlay": sorted(tt["overlay"]),
                      "shore": sorted(tt["shore"]), "scorch": sorted(tt["scorch"]),
                      "cliff": sorted(tt.get("cliff", {})),
                      "cliff_shore": sorted(tt.get("cliff_shore", {})),
                      "cliff_scorch": sorted(tt.get("cliff_scorch", {})),
                      "alternates": {"count": tt.get("alternates", {}).get("count", 1),
                                     "suffixes": [s["suffix"] for s in tt.get("alternates", {}).get("sets", [])],
                                     "overlay": sorted(tt.get("alternates", {}).get("overlay", {})),
                                     "shore": sorted(tt.get("alternates", {}).get("shore", {})),
                                     "scorch": sorted(tt.get("alternates", {}).get("scorch", {}))}}
V = os.path.join(ROOT, "art", "validation")
H.append('<div class="grid proof">')
pics = [("transitions/map_0.png", "proof map 0: every terrain meeting its neighbours"),
        ("transitions/map_1.png", "proof map 1"), ("transitions/map_2.png", "proof map 2"),
        ("transitions/diagonals.png", "one-cell diagonal paths stay continuous"),
        ("transitions/pair_water__grass.png", "pair: grass over water, 16 masks (shore)"),
        ("transitions/pair_roads__grass.png", "pair: roads and grass"),
        ("transitions/pair_lava__grass.png", "pair: grass over lava (scorch)"),
        ("transitions/pair_ash__snow.png", "pair: ash and snow"),
        ("transitions/pair_grass__rock.png", "pair: rock over grass (dual-grid cliff)"),
        ("transitions/cliffs_sheet.png", "cliffs: a height step in each of six terrains"),
        ("transitions/cliff_grass.png", "cliff: grass plateaus over grass, dirt and sand"),
        ("transitions/cliff_wash_sheet.png", "cliff wash: a step standing in water (foam) and in lava (char)"),
        ("transitions/alternates.png", "alternates: the same border in each of its four drawings"),
        ("transitions/alternates_map.png", "alternates: one coast with the primary only, and with all four mixed")]
for rel, cap in pics:
    q = copy_any(os.path.join(V, rel), "sheets/" + rel.replace("transitions/", "transition_"))
    if q:
        H.append(card('<a href="%s"><img loading="lazy" src="%s" alt="%s"></a>' % (q, q, esc(cap)), cap))
        SHEETS.append((q, "Transitions: " + cap, Image.open(os.path.join(HERE, q)).size))
H.append("</div></section>")

# --- walls -----------------------------------------------------------------------
print("walls")
W = kit.walls
KINDS = W["kinds"]
ndoor = sum(len(k.get("doors", {})) for k in KINDS.values())
section("walls", "Wall kits", "%d materials x %d pieces, %d door and gate pieces"
        % (len(KINDS), len(next(iter(KINDS.values()))["pieces"]), ndoor),
        "Hand-placeable walls on the ordinary grid: one still piece per cell, and the cell is "
        "what it blocks. The name says where the piece sits in a wall; a 256-entry lookup on the "
        "eight neighbours picks it automatically. Walls do not animate. Kinds: " +
        "; ".join("<b>%s</b> (face %d px)" % (k, v["face_px"]) for k, v in KINDS.items()) +
        ". A door or gate replaces one straight piece of a run and ships closed and open. Kits "
        "join each other with a butt joint: %d small joint pieces per kit close the cut end where "
        "the neighbouring cell is a wall of another material." % len(next(iter(KINDS.values())).get("joints", {})))
MD.append(W["rule"] + "\n\n" + W.get("door_rule", "") + "\n\n" + W.get("join_rule", "") + "\n\nNaming: "
          + "; ".join("`%s` = %s" % kv for kv in W["naming"].items()) + "\n")
MD.append("Pieces (the same %d labels in every kind): " % len(KINDS["rock"]["pieces"])
          + ", ".join("`%s`" % n for n in KINDS["rock"]["pieces"]) + "\n")
CAT["walls"] = {"naming": W["naming"], "frames": 1, "kinds": {}}
SHOW = ("single", "straight_ew", "straight_ns", "corner_nw", "corner_se", "tee_s", "cross",
        "edge_s", "end_w", "inner_ne", "solid")
for kind, krec in KINDS.items():
    ent = []
    H.append("<h3>%s</h3><div class=\"grid\">" % esc(kind))
    for name, rec in krec["pieces"].items():
        ent.append((name, kit.image(rec["file"])))
        if name in SHOW:
            src_ = put(rec["file"], "walls/%s/%s.png" % (kind, name))
            H.append(card('<img loading="lazy" src="%s" alt="wall %s: %s" width="128" height="128">'
                          % (src_, kind, name), name, kind))
    for name, rec in krec.get("doors", {}).items():
        ent.append((name, kit.image(rec["file"])))
        src_ = put(rec["file"], "walls/%s/%s.png" % (kind, name))
        H.append(card('<img loading="lazy" src="%s" alt="wall %s: %s" width="128" height="128">'
                      % (src_, kind, name), name, kind + " door"))
    H.append("</div>")
    MD.append("- **%s**: face %d px; doors and gates: %s" % (
        kind, krec["face_px"], ", ".join("`%s`" % n for n in krec.get("doors", {})) or "none"))
    CAT["walls"]["kinds"][kind] = {"pieces": list(krec["pieces"]), "doors": list(krec.get("doors", {})),
                                   "joints": list(krec.get("joints", {})),
                                   "inset_px": krec["inset_px"], "face_px": krec["face_px"]}
    p = sheet("walls_" + kind, "%s wall kit: %d labelled pieces and doors (2x)" % (kind.capitalize(), len(ent)), ent, 10)
    H.append(sheet_link(p, "every %s piece" % kind))
    H.append('<div class="grid proof">')
    for rel, cap in (("walls/%s_demo.png" % kind, "%s: a yard, a maze and a line built from the kit" % kind),
                     ("walls/%s_pieces.png" % kind, "%s: the pieces in place, labelled" % kind)):
        q = copy_any(os.path.join(V, rel), "sheets/" + rel.replace("walls/", "walls_"))
        if q:
            H.append(card('<a href="%s"><img loading="lazy" src="%s" alt="%s"></a>' % (q, q, esc(cap)), cap))
            SHEETS.append((q, "Walls: " + cap, Image.open(os.path.join(HERE, q)).size))
    H.append("</div>")
q = copy_any(os.path.join(V, "walls/mixed_demo.png"), "sheets/walls_mixed_demo.png")
if q:
    cap = "all five kits in one building: a butt joint wherever two materials meet"
    H.append('<div class="grid proof">' + card(
        '<a href="%s"><img loading="lazy" src="%s" alt="%s"></a>' % (q, q, esc(cap)), cap) + "</div>")
    SHEETS.append((q, "Walls: " + cap, Image.open(os.path.join(HERE, q)).size))
H.append("</section>")

# --- structures ------------------------------------------------------------------
print("structures")
S = kit.structures
nloc = sum(1 for r in S.values() if r["scale"] == "local")
section("structures", "Structures and props", "%d props, %d at a person's scale" % (len(S), nloc),
        "Cut-outs that stand on terrain, drawn in elevation with a ground shadow. <b>map</b> scale "
        "means a landmark for the world map (a castle two tiles wide); <b>local</b> scale means "
        "drawn to stand beside a person. Trees block only the trunk, so a person can walk behind "
        "the crown. Some have a second state (open, raided). The four <b>stairs</b> stand across "
        "a cliff edge, one cell on the high ground and one on the low, and are where a unit climbs.")
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
    if r.get("climbs"):
        CAT["structures"][name]["climbs"] = r["climbs"]
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
        "vanishing in smoke) in four facings; most add a signature. Below: idle in all four "
        "facings, then every other state facing down. Tier is difficulty 1&ndash;5. An elite is "
        "its base creature in another palette with the same silhouette, and every creature has "
        "one. The seven big creatures (ogre, treant, dragon and the four lords) play their attack, "
        "walk and signature over <b>12 frames</b> instead of 6: a wind-up, the blow on frame 5, a "
        "follow-through and a recovery.")
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
    nfs = {s: kit.monster_frames(name, s) for s in states}
    wide = max(nfs.values())
    im = Image.new("RGBA", (lab + wide * cw * sc, len(states) * ch * sc), PAPER)
    dr = ImageDraw.Draw(im)
    for j, s in enumerate(states):
        dr.text((6, j * ch * sc + 6), s, fill=INK, font=font(13))
        for i in range(nfs[s]):
            fr = kit.cell(fs[s]["file"], i, 0, fs[s]["frame_w"], fs[s]["frame_h"])
            fr = fr.resize((fr.width * sc, fr.height * sc), Image.NEAREST)
            im.alpha_composite(fr, (lab + (i * cw + ax - fs[s]["anchor"][0]) * sc,
                                    (j * ch + ay - fs[s]["anchor"][1]) * sc))
    q = save(im.convert("RGB"), "sheets/monster_%s.png" % name)
    per = "6 frames" if wide == F else "6 or %d frames" % wide
    SHEETS.append((q, "Monster %s: every state x %s, facing right" % (name, per), im.size))
    H.append("</div>" + sheet_link(q, "%s, every state x %s, facing right" % (name, per)) + "</article>")
    ent.append(("%s (tier %d)" % (name, r["tier"]), frame0(r["states"]["idle"]["facings"]["down"]["file"],
                                                         r["box"][0], r["box"][1])))
    long_ = [s for s in states if nfs[s] != F]
    MD.append("| %s | %d | %s | %s | %s | %s |" % (
        name, r["tier"], r["rank"], foot,
        ", ".join(s + (" (%d frames)" % nfs[s] if s in long_ else "") for s in states), d))
    CAT["monsters"][name] = {"tier": r["tier"], "rank": r["rank"], "footprint_tiles": r["footprint_tiles"],
                             "states": states, "description": d}
    if long_:
        CAT["monsters"][name]["frames"] = {s: nfs[s] for s in long_}
H.append('<h3>Elites</h3><div class="grid">')
for name in elite:
    r = M[name]
    f = r["states"]["idle"]["facings"]["down"]
    src = put(f["file"], "monsters/%s/idle_down.png" % name)
    H.append(card(canvas(src, f["frame_w"], f["frame_h"]), name, "tier %d" % r["tier"]))
    ent.append((name, frame0(f["file"], f["frame_w"], f["frame_h"])))
    CAT["monsters"][name] = {"tier": r["tier"], "rank": r["rank"], "elite": True, "states": list(r["states"])}
H.append("</div>")
MD.append("\nElites (palette swaps, same states and frame counts as their base; what they throw is "
          "dyed from their own palette): " + ", ".join(elite) + "\n")
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
UI = kit.ui
section("ui", "UI and portraits", "%d nine-slice pieces, %d bar fills, %d cursors, %d fonts, portraits for %d bodies and %d lords"
        % (len(UI["pieces"]), len(UI["bars"]["fills"]), len(UI["cursors"]["cursors"]),
           len(UI["fonts"]["fonts"]), len(kit.portraits["bodies"]), len(kit.portraits.get("monsters", {}))),
        "Parchment UI as nine-slice pieces (corners fixed, edges tiled), inventory slots, bars "
        "whose fill tiles, cursors, and two handwritten bitmap fonts, each in two sizes and two "
        "pencils (ink and chalk): <b>hand</b>, the game's own printed pencil, and <b>cute</b>, a "
        "middle-schooler's rounder, friendlier writing. Both cover Western and Central European "
        "accents, and both also ship as a .ttf. Dialogue "
        "portraits are layered from the same wardrobe as the sprite, so a portrait always matches "
        "what the person is wearing, and carry the face detail a 64 px sprite cannot: irises, "
        "lids, nose, mouth, wrinkles, freckles, scars. Portraits are stills, facing the viewer.")
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
for name, prec in kit.portraits.get("monsters", {}).items():
    q = put(prec["file"], "portraits/%s.png" % name)
    im = kit.image(prec["file"])
    H.append(card('<img loading="lazy" src="%s" alt="portrait: %s" style="width:%dpx">' % (q, name, im.width), name, "lord"))
    ent.append(("%s (lord)" % name, im))
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
H.append('<div class="grid wide">')
for fill in UI["bars"]["fills"]:
    im = kit.bar(fill, 0.65, 180)
    q = save(im, "assets/ui/bar_%s.png" % fill)
    H.append(card('<img loading="lazy" src="%s" alt="bar: %s" style="width:%dpx">' % (q, fill, im.width * 2), "bar: " + fill, "track + tiled fill at 65%"))
    ent.append(("bar " + fill, im))
for name, crec in UI["cursors"]["cursors"].items():
    q = put(crec["file"], "ui/%s.png" % name)
    im = kit.image(crec["file"])
    H.append(card('<img loading="lazy" src="%s" alt="cursor: %s" style="width:%dpx">' % (q, name, im.width * 2), name, "hotspot %s" % crec["hotspot"]))
    ent.append((name, im))
for i, icon in enumerate(("sword", "potion_health", None)):
    im = kit.slot(icon, selected=i == 1)
    q = save(im, "assets/ui/slot_demo_%d.png" % i)
    H.append(card('<img loading="lazy" src="%s" alt="inventory slot" style="width:%dpx">' % (q, im.width * 2),
                  "slot_selected" if i == 1 else "slot", "with icon %s" % icon if icon else "empty"))
H.append("</div>")
sheet("ui", "UI: nine-slice pieces sliced to a box, bars, cursors (2x)", ent, 5)
ent = []
H.append('<h3>Handwriting</h3><div class="grid proof">')
PANGRAM = "The quick brown fox jumps over the lazy dog. 0123456789 ?! Zażółć gęślą jaźń, où est l'été? ♥ ★"
for fname, frec in UI["fonts"]["fonts"].items():
    for colour in frec["files"]:
        t = kit.text(kit.wrap(PANGRAM, 520, fname), fname, colour)
        bg = Image.new("RGBA", (t.width + 24, t.height + 20), PAPER if colour == "ink" else (58, 52, 48, 255))
        bg.alpha_composite(t, (12, 10))
        q = save(bg.convert("RGB"), "assets/ui/font_%s_%s.png" % (fname, colour))
        cap = "%s, %s: cell %dx%d, line %d" % (fname, colour, frec["cell_w"], frec["cell_h"], frec["line_height"])
        H.append(card('<img loading="lazy" src="%s" alt="%s">' % (q, esc(cap)), cap))
        ent.append(("%s %s" % (fname, colour), bg))
H.append("</div>")
sheet("font", "Handwriting: two faces (hand, cute), two sizes, ink and chalk (1x)", ent, 2, 1)
for face, frec in UI["fonts"].get("faces", {}).items():
    if frec.get("ttf"):
        put(frec["ttf"], "ui/%s.ttf" % face)
CAT["ui"] = {"pieces": list(UI["pieces"]), "bar_fills": list(UI["bars"]["fills"]),
             "cursors": list(UI["cursors"]["cursors"]), "fonts": list(UI["fonts"]["fonts"]),
             "font_faces": {f: {"ttf": URL + "assets/ui/%s.ttf" % f, "use": r.get("use", "")}
                            for f, r in UI["fonts"].get("faces", {}).items()},
             "font_chars": UI["fonts"]["chars"],
             "monster_portraits": list(kit.portraits.get("monsters", {}))}
MD.append("UI pieces: %s. Bar fills: %s. Cursors: %s. Fonts (handwriting, %d characters: ASCII, Latin-1, "
          "Latin Extended-A, typographic marks and nine symbols; ink and chalk; faces %s, each also a .ttf): %s. "
          "Portraits compose for all %d bodies from the worn items; the lords %s have one still each.\n"
          % (", ".join(UI["pieces"]), ", ".join(UI["bars"]["fills"]), ", ".join(UI["cursors"]["cursors"]),
             len(UI["fonts"]["chars"]), ", ".join(UI["fonts"].get("faces", {})),
             ", ".join(UI["fonts"]["fonts"]), len(kit.portraits["bodies"]),
             ", ".join(kit.portraits.get("monsters", {}))))
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
                    ("demo_dialogue.png", "a dialogue box: nine-slice panel, composed portraits, handwritten text"),
                    ("demo_hud.png", "a HUD: bars, inventory slots, cursors, all from the package"),
                    ("demo_cliff.png", "a grass plateau with a knoll and two flights of stairs: heights per cell, cliff atlases, alternates on"),
                    ("demo_cliff_wash.png", "the same step standing in water and in lava: foam and char at its foot"),
                    ("demo_walls_mixed.png", "five wall kits in one plan, joined where they meet"),
                    ("demo_handwriting.png", "both handwriting faces, with accents and symbols"),
                    ("demo_map.gif", "the map, animated: the ogre's blow takes twelve frames"),
                    ("demo_scene.gif", "the local scene, animated")):
        q = copy_any(os.path.join(DEMO, fn), "sheets/" + fn)
        if q:
            SC.append((q, cap))
            SHEETS.append((q, "Scene: " + cap, Image.open(os.path.join(HERE, q)).size))

GAPS = [
    ("Local scenes are still thin", "Two houses, an inn, six pieces of furniture, two floors, five wall kits and four flights of stone stairs. No windows as pieces, rugs, signs, market stalls or street lamps at a person's scale. Wall kits meet in a butt joint: one material stops and the next starts, with no bonded corner."),
    ("Cliffs and stairs", "A height step has a drawn bank on its south-facing edge only; the north, west and east edges are a lit lip, a rim line and a shade. Stairs are one material and climb one level (16 px): no ramp, no wooden flight, nothing that climbs a wall. Only six terrains have a cliff."),
    ("Landmarks", "One design and no state each (no ruined, raided or lit variant) for the great landmarks."),
    ("Monsters", "Eight creatures have no signature state: rat, goblin, wolf, orc, ogre and three of the lords. Twelve-frame animation covers the attack, walk and signature of the seven creatures bigger than a tile; their hurt and die, and every smaller creature and every person, are six frames. Three elite effects keep the base's colours by nature (a web, a tongue, a war-cry). Monster portraits exist for the lords only."),
    ("Portraits", "Stills, facing the viewer, one expression per body. No talking or blinking frames."),
    ("UI", "No icons for status effects, no minimap frame, no scroll bar. The two handwriting faces are Latin only (303 characters; no Greek, Cyrillic or CJK) and have no kerning pairs."),
    ("Faces", "Sprites keep two eyes and a brow at 64 px by design; all face detail is in the portraits."),
    ("Terrain", "Farmland runs east-west or north-south, not diagonally. Borders come in four interchangeable looks; within 10 px of the drawn contour any two differ on 11 to 45 percent of pixels (mean 24), and where a border crosses the tile edge is fixed, so a border is varied, not unique. Cliff and pair atlases have one look."),
    ("Gameplay data", "Only suggested data ships: walkability per terrain, blocked cells, idle hurtboxes, impact frames. No per-state hitboxes."),
]

# --- write -----------------------------------------------------------------------
counts = [("terrain tiles", len(order) + nvar), ("structures", len(S)), ("creatures", len(base)),
          ("elites", len(elite)), ("bodies", len(bodies)), ("wardrobe items", sum(map(len, by_slot.values()))),
          ("NPC looks", len(looks)), ("icons", len(IC)), ("wall pieces", sum(len(k["pieces"]) + len(k.get("doors", {})) for k in KINDS.values()))]
CAT["counts"] = dict(counts)
CAT["known_gaps"] = [{"title": a, "detail": b} for a, b in GAPS]
CAT["sheets"] = [{"url": URL + p, "title": t, "size": list(sz)} for p, t, sz in SHEETS]

game_md = copy_any(os.path.join(ROOT, "GAME_INTEGRATION.md"), "GAME_INTEGRATION.md")

head_md = [
    "# Doodle Codex: full asset catalog",
    "",
    "The art library for *Norfair Chronicles*, a real-time overhead action RPG (Godot 4, flat 2D, "
    "y-sorted): a world map for travel and local scenes for play. Everything is drawn in one "
    "pencil-doodle style on a 64x64 grid, animated as 6-frame horizontal strips at 10 fps (12 "
    "frames for a big creature's attack, walk and signature: read `frames` per state), in "
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
