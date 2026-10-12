# GAME_INTEGRATION.md

Audience: an AI agent or programmer wiring this art into a game engine.
Everything the engine needs is in `game/`. Nothing outside `game/` is needed at
runtime. `game/reference/tilekit.py` (Pillow only) implements every rule below;
when porting to an engine, port that file and the behaviour is right by
construction. Run `python game/reference/tilekit.py --demo OUT` to see a
rendered map with terrain, transitions, a structure, a monster and two heroes,
`demo_scene.png`: a walled yard built from the wall kit, a chest and two trees
with a person behind one crown and in front of the other trunk, and `demo_dialogue.png`: a nine-sliced panel, three framed portraits and the buttons.
It also writes `demo_cliff.png` (a plateau, a knoll and four flights up it:
stone, wood and a ramp), `demo_cliff_wash.png` (the same step standing in
water and in lava), `demo_cliff_alternates.png` (that step in its four looks),
`demo_walls_mixed.png` and `demo_walls_bonded.png` (five wall kits joined in
one plan, butted and bonded), `demo_hud.png` (bars, slots, status icons, a
minimap and a scroll bar) and `demo_handwriting.png` (both handwriting faces,
with accents, Greek and Cyrillic), and four for a street and a map that
changes: `demo_street.png` (a stone front and a timber one built from the wall
kits with a door and three windows, lamps lit and dark, four trade signs, two
stalls, a mat under the hero), `demo_room.png` (the interior kit's windows, a
rug under a table), `demo_waterfall.png` (a river going over a step) and
`demo_landmark_states.png` (every map structure's states beside its idle).

Maintained by: `tools/package_game.py` builds `game/`, and this file is copied
there. **Whoever changes the package layout, a JSON schema, or a rule the engine
must follow updates this file in the same change** (see CLAUDE.md).

---

## 0. Invariants (true for every sprite)

| fact | value | source |
| --- | --- | --- |
| tile | 64 px, square | `catalog.json:tile` |
| frames per animation | 6, except the **12-frame** long states of the seven big creatures (§3) | `catalog.json:animation.frames`; `monsters.json` per-state `frames` |
| playback | 10 fps (100 ms/frame) | `catalog.json:animation.fps` |
| strip layout | horizontal: frame `i` at `x = i*frame_w`, `y = 0` | all `*.png` except atlases |
| atlas layout | row = autotile mask 0..15, column = frame 0..5; 384×1024 | `terrain/transitions/**` |
| facings | `down`, `left`, `right`, `up` — every facing is its own file | `catalog.json:facings` |
| filtering | nearest-neighbour only; integer scale only | the pencil grain dies under bilinear |
| format | PNG RGBA, straight (non-premultiplied) alpha | |

**One global clock.** `frame = floor(seconds * 10) % 6`, the same value for
every sprite on screen: terrain, overlays, structures, monsters and every
paperdoll layer. (A monster state that says `frames: 12` takes the same clock
`% 12`; nothing else has a length of its own.) Never give a tile or a layer its own phase. Transition overlays
are drawn to line up frame-for-frame with the base tiles underneath. Paperdoll
layers breathe with the body under them. Both break under per-sprite offsets.

**Never mirror at runtime.** `left` is shipped as its own file. Anchors differ per
facing.

---

## 1. Directory map

```
game/
  catalog.json            index: counts, names, where each category's JSON lives
  GAME_INTEGRATION.md     this file
  characters.json         paperdoll rules: slots, bands, z order, hides, skins, hair colours
  terrain/terrain.json    base tiles + transition atlases + the autotile rule
  terrain/base/<terrain>.png                      384x64 seamless strip
  terrain/variants/<terrain>/<variant>.png        384x64, drop-in for an all-<terrain> tile
  terrain/transitions/overlay/<upper>.png         16x6 atlas, RGBA overlay
  terrain/transitions/shore/<upper>.png           16x6 atlas, RGBA overlay over water
  terrain/transitions/scorch/<upper>.png          16x6 atlas, RGBA overlay over lava (not for lava itself)
  terrain/transitions/pair/<lower>__<upper>.png   16x6 atlas, opaque, pre-composited
  terrain/transitions/cliff/<terrain>.png         16x6 atlas, RGBA: a height step of one terrain (15 terrains)
  terrain/transitions/cliff_shore/<terrain>.png   16x6 atlas, RGBA: the foam at the foot of a step that stands in water
  terrain/transitions/cliff_scorch/<terrain>.png  16x6 atlas, RGBA: the charred line at the foot of a step that stands in lava
  terrain/transitions/overlay_b|_c|_d/<upper>.png three more drawings of every overlay atlas (alternates)
  terrain/transitions/shore_b|_c|_d/<upper>.png   the same for shore
  terrain/transitions/scorch_b|_c|_d/<upper>.png  the same for scorch
  terrain/transitions/cliff_b|_c|_d/<terrain>.png             three more drawings of every cliff atlas
  terrain/transitions/cliff_shore_b|_c|_d/<terrain>.png       the same for a step's foam
  terrain/transitions/cliff_scorch_b|_c|_d/<terrain>.png      the same for a step's charred foot
  terrain/walls/walls.json                        the hand-placeable wall kits: pieces, doors, joints, lookup, rules
  terrain/walls/<kind>/<label>.png                one still 64x64 cut-out: 47 labelled pieces per kind
  terrain/walls/<kind>/<door|gate>_<where>_<state>.png   a door or gate piece, closed and open
  terrain/walls/<kind>/window_<where>_<dark|lit>.png     a window piece (stone, timber, interior)
  terrain/walls/<kind>/joint_<side>[_<corner>...].png    a butt joint against another kind: 16 per kind
  terrain/walls/<kind>/bond_<other>_<side>[_<corner>].png  the joint with teeth, against kind <other>: 16 per kind
  structures/structures.json
  structures/<name>.png                           cut-out strip, frame = footprint*64
  structures/<name>_<state>.png                   the same frame in another state (open, raided, dark, erupt, ...)
                                                  (structures.json: `scale` = map landmark or person-scale)
  monsters/monsters.json
  monsters/<creature>/<state>_<facing>.png        cut-out strip, frame may be padded; 6 frames, or 12 (the state's `frames`)
  monsters/<creature>_elite/<state>_<facing>.png  the same creature in its elite palette
  heroes/heroes.json                              player bodies (hero, hero2) + 10 builds
  heroes/<body>/<piece>_<facing>.png              skins (body_<tone>[-near]), hair[_<colour>][-back], beard[_<colour>]
  npcs/npcs.json                                  10 NPC bodies + 39 looks
  npcs/<body>/<piece>_<facing>.png
  accessories/accessories.json                    119 wearable items
  accessories/<slot>/<item>/<body>/<band>_<facing>.png
  loot/loot.json                                  drops + a suggested drop table
  loot/<item>.png                                 gold, gem_ruby|sapphire|emerald, drop_sword|axe,
                                                  potion_health|mana, key
  fx/fx.json                                      projectiles and the hit spark
  fx/<effect>_<facing>.png                        arrow|bolt|firebolt per facing; spark_any
  icons/icons.json                                124 inventory icons: wardrobe slot per icon
  icons/<name>.png                                one still 64x64 frame; no facing, no state
  ui/ui.json                                      parchment, slots, bars, scroll bar, status icons, minimap, cursors, fonts: every rule
  ui/<piece>.png                                  panel, button[_hover|_pressed], frame, slot[_selected] (nine-slice stills)
  ui/bar.png, ui/bar_fill_<what>.png              a bar's track and its health|stamina|mana fills
  ui/cursor_<name>.png                            32x32 pointers, with a hotspot
  ui/scroll.png, ui/scroll_thumb.png              a vertical scroll bar: track and thumb, three slices each
  ui/minimap.png, ui/marker_<name>.png            the minimap's hollow nine-slice frame and its player|quest pins
  ui/status_<effect>.png                          twelve 24x24 status-effect icons
  ui/font/<font>_<ink|chalk>.png, <font>.fnt      the handwriting: fixed-cell atlases + BMFont files (two faces x two sizes)
  ui/font/<face>.ttf                              the same two hands as TrueType outlines, kerned
  portraits/portraits.json                        dialogue portraits: layered like the paperdoll
  portraits/<body>/<piece>.png                    one still 160x160 per piece, facing down
  portraits/monsters/<name>.png                   one still 160x160 for a monster that speaks (the lords)
  reference/tilekit.py                            reference implementation
```

Every path inside any JSON is relative to `game/`.

---

## 2. Terrain

### 2.1 Base tiles

`terrain.json:base[<terrain>]` → `{file, frame_w:64, frame_h:64, loops, seamless, elevation, gameplay_suggested, weight, variants}`.
The 20 terrains are `water, lava, ice, cave, ash, sand, desert, swamp,
flagstones, floorboards, dirt, farmland, farmland_ns, snow, roads, grass,
forest, mountain, peaks, rock` (that is also their elevation order, low to
high). Each tiles
seamlessly with itself, so fill a region by repeating the strip's current frame.

`gameplay_suggested` = `{walkable, speed, blocks_projectiles, blocks_sight}`
(plus `slippery` on ice and `hazard` on lava), a
prototyping default and not part of the art:

| terrain | walkable | speed | blocks_projectiles | blocks_sight |
| --- | --- | --- | --- | --- |
| water | no | 0 | no | no |
| dirt | yes | 1.0 | no | no |
| roads | yes | 1.25 | no | no |
| grass | yes | 1.0 | no | no |
| forest | yes | 0.7 | no | yes |
| mountain | no | 0 | yes | yes |
| swamp | yes | 0.6 | no | no |
| ice | yes | 1.0, `slippery: true` | no | no |
| peaks | no | 0 | yes | yes |
| sand | yes | 0.85 | no | no |
| desert | yes | 0.8 | no | no |
| farmland | yes | 0.9 | no | no |
| cave | yes | 1.0 | no | no |
| lava | no | 0, `hazard: "burn"` | no | no |
| rock | no | 0 | yes | yes |
| ash | yes | 0.9 | no | no |
| snow | yes | 0.75 | no | no |
| flagstones | yes | 1.0 | no | no |
| floorboards | yes | 1.0 | no | no |
| farmland_ns | yes | 0.9 | no | no |

`mountain` and `peaks` are **map-scale** pictures: a whole range in one tile.
`rock` is the **local-scale** wall: one tile of solid boulder face, for a cave
or cliff a person stands next to. Build a walk-around cave from `cave` floor
and `rock` walls; keep `mountain` for the overworld. For a wall you place by
hand, cell by cell, with ends and corners, use the wall kit (§2.5) instead of
the `rock` terrain.

`ash` is burnt ground, grey with ember flecks: the land around a volcano and
the floor of a ruined, cursed country. `snow` is deep lying snow, the walkable
ground of the cold regions (`ice` is a frozen lake, `peaks` a range).

`flagstones` and `floorboards` are **indoor floors**: a cellar, a hall, a
room. Both hold almost still. Wall a room with the `interior` wall kit (§2.5)
and furnish it with the local-scale structures (§2.4). `farmland_ns` is
`farmland` with its furrows running north-south, so a field can follow
either road; the two are separate terrains with their own variants.

Gameplay reads the **logical cell's** terrain, never the display tile's pixels.

**Variants.** `base[T].variants` is a list of `{name, file, weight, note}`.
Each is the base tile with something added in the middle: flower patches,
pines, a higher peak, lily pads, a mossy cobble. Every terrain has at least
four; six terrains have one or two more, the *incidents* of a world map (a
wreck, a ring of standing stones, a ruin in the dunes), at weight 1 so the
hash scatters them thinly. Read the list from `terrain.json`; do not assume a
count.
Two terrains carry an extra gameplay key, and an engine that ignores either
loses nothing: `ice` has `slippery: true` (momentum carries), and `lava` has
`hazard: "burn"` (it is not walkable; anything pushed or flying over it should
take damage). `cave` is an ordinary floor: build its walls from `rock` in a
scene people walk through, or from `mountain` on a map.

| terrain | variants (weight) | base weight |
| --- | --- | --- |
| grass | meadow_flowers (2), meadow_wild (1), meadow_rocks (1), meadow_stump (1), meadow_stones (1) | 6 |
| forest | canopy_pines (2), canopy_autumn (1), canopy_clearing (1), canopy_pond (1), canopy_deadwood (1), canopy_ruin (1) | 6 |
| mountain | crags_high (1), crags_twin (1), crags_boulders (1), crags_cave (1), crags_tarn (1) | 6 |
| water | shallows_lilies (1), shallows_rocks (1), shallows_reeds (1), shallows_sandbar (1), shallows_wreck (1) | 6 |
| dirt | packed_rocks (1), packed_puddle (1), packed_ruts (1), packed_scrub (1) | 6 |
| roads | cobble_moss (1), cobble_worn (1), cobble_puddle (1), cobble_leaves (1) | 6 |
| swamp | bog_cattails (2), bog_snag (1), bog_lilies (1), bog_toadstools (1) | 6 |
| ice | floe_drifts (2), floe_hole (1), floe_rocks (1), floe_ridge (1) | 6 |
| peaks | summit_spire (1), summit_glacier (1), summit_cairn (1), summit_pines (1) | 6 |
| sand | beach_shells (1), beach_driftwood (1), beach_tidepool (1), beach_grass (2) | 6 |
| desert | dunes_cactus (2), dunes_bones (1), dunes_rocks (1), dunes_oasis (1), dunes_ruin (1) | 6 |
| farmland | furrows_wheat (2), furrows_pumpkins (1), furrows_scarecrow (1), furrows_cabbages (1) | 6 |
| cave | cavern_crystals (1), cavern_stalagmites (2), cavern_pool (1), cavern_mushrooms (1) | 6 |
| lava | magma_crust (2), magma_vent (1), magma_rocks (1), magma_whirl (1), magma_obsidian (1), magma_bones (1) | 6 |
| rock | wall_moss (2), wall_ore (1), wall_crack (1), wall_crystals (1) | 6 |
| ash | cinders_stumps (2), cinders_fissure (1), cinders_stones (1), cinders_vent (1) | 6 |
| snow | snowfield_pines (2), snowfield_rocks (1), snowfield_tracks (1), snowfield_snowman (1) | 6 |

- **Use a variant only on a display tile whose four corners are all `T`**
  (one terrain present). Transition tiles always start from `base[T]`.
- **Every variant's outer 6 px are the base tile's pixels, in every frame**
  (measured: max difference 0 on all 76). So a variant seams against the base,
  other variants and every transition tile with no extra rule. Hand-place them
  freely.
- **Default pick**, deterministic per display tile `(x, y)` (`terrain.json:variants_rule`):

  ```python
  h = ((x * 73856093) ^ (y * 19349663)) & 0xFFFFFFFF
  h = ((h ^ (h >> 13)) * 0x5BD1E995) & 0xFFFFFFFF
  h ^= h >> 15
  choices = [base[T]] + base[T]["variants"]          # file order
  r = h % sum(c["weight"] for c in choices)
  for c in choices:                                  # first c with r < weight
      if r < c["weight"]: break
      r -= c["weight"]
  ```

- A variant is cosmetic. Its gameplay is `base[T].gameplay_suggested`, even
  where it draws a rock or a puddle.
- Cache by the chosen file, not by the corner tuple (`tilekit.Kit.render_map`).

### 2.2 Transitions (autotiling): corner / dual-grid Wang, 16 masks

Terrain is stored **per logical map cell**. Tiles are drawn on a **display grid
offset by half a tile** (up-left), so each display tile straddles four logical
cells, and those four cells are its corners:

```
display tile (x, y), for x in 0..W, y in 0..H   (display grid is (W+1) x (H+1))
  TL = cell(x-1, y-1)   TR = cell(x, y-1)
  BL = cell(x-1, y)     BR = cell(x, y)        (clamp coordinates at map edges)
  drawn at pixel (x*64 - 32, y*64 - 32)
```

**Mask bits:** `TL=1, TR=2, BL=4, BR=8` (`terrain.json:transitions.mask_bits`).
An atlas cell is at `x = frame*64, y = mask*64`.

**Elevation order** (low → high): `water < lava < ice < cave < ash < sand < desert < swamp < flagstones < floorboards < dirt < farmland < farmland_ns < snow < roads < grass < forest < mountain < peaks < rock`
(`terrain.json:elevation_low_to_high`). The higher terrain always draws *over*
the lower one and owns the edge: its fringe, its rim line, its cast shadow, a
cliff face for mountains, peaks and rock (rock's is the tallest, 26 px, shaded
with ledges and a lit lip: it is a wall seen from in front, and it stands only
under edges that face the viewer), a low ice shelf for ice, and a kerb for roads. `lava` is the second liquid and sits just above water, so every
land terrain banks over it; `farmland` furrows run east-west and are not
rotated at an edge.

**Algorithm for one display tile (any number of distinct corner terrains, 1–4):**

```python
present = sorted(set([TL, TR, BL, BR]), key=elevation)      # low first
draw base[present[0]] frame                                  # opaque, full tile
for i, T in enumerate(present[1:]):
    mask = sum(bit for bit, c in zip((1,2,4,8), (TL,TR,BL,BR)) if elevation[c] >= elevation[T])
    if i == 0 and present[0] == "water": atlas = shore[T]
    elif i == 0 and present[0] == "lava": atlas = scorch[T]
    else: atlas = overlay[T]
    draw atlas cell (row=mask, col=frame), alpha-blended
```

Note `>=`: when T is drawn, every corner that is T *or higher* is in its mask,
so the higher overlays drawn later sit on a T surface, not a hole.
`overlay/<T>` row 15 equals the base tile of T exactly, and row 0 is empty.
Cache by the tuple `(TL, TR, BL, BR, frame)`: there are few distinct tuples.
(An all-one-terrain tile may instead be a variant; see §2.1.)
`terrain.json:transitions.rule` is this algorithm as a list of sentences.

**Diagonal masks 6 and 9** (two opposite corners of the upper terrain) join
the *lower* terrain's two corners through the tile centre. The exception is
when the upper terrain is `roads`, where the road's corners join. The result is
that a one-cell-wide diagonal road, river or trail stays connected whichever
side of it is higher: a road on grass, grass through mountains, a river
through anything. Paint diagonal paths freely.

**Shore:** when the lowest terrain in a tile is water, the first overlay comes
from `shore/<T>.png`. That is the same edge plus a foam band and a wet line on
the water side. There is no water overlay (water is lowest) and no shore for
water. Lava meeting water uses `shore/lava`, where the foam reads as steam;
land meeting lava uses the plain `overlay/<T>`.

**Scorch:** when the lowest terrain in a tile is lava, the first overlay comes
from `scorch/<T>.png` instead of `overlay/<T>.png` — the same edge plus a
charred crust and a glow along its cracks on the lava side, the lava-side twin
of shore's foam. There is no scorch for lava itself (lava is never the
terrain drawn over lava). Lava meeting water still uses `shore/lava`, not
scorch — scorch only applies when lava is the *lower* terrain of the pair.

**Pair atlases** (`pair/<lower>__<upper>.png`, all 190 pairs): opaque, already
composited `base[lower] + (shore, scorch or overlay)[upper]`. Use them when a
tile never mixes more than two terrains, which is what editor terrain systems
want. Row 0 = all lower, row 15 = all upper.

**Cliffs: a height step** (`transitions.cliff`, `cliff_rule`). Optional. A map
may give each logical cell an integer height beside its terrain; without
heights nothing changes. `cliff/<T>.png` exists for **fifteen terrains, every
one a unit walks on**: grass, dirt, sand, desert, snow, ash, forest, swamp,
ice, cave, farmland, farmland_ns, roads, flagstones and floorboards. Mountain,
peaks and rock are already high ground and have none; water and lava have
none either (see the waterfall, below). It is laid out like an overlay (row =
mask, where a set bit is a corner on the *upper* level). It draws the upper level's ground,
its edge and its cast shadow; the lower side is transparent, so a grass
plateau stands on dirt or sand as readily as on grass. Where the edge faces
**south** it is a bank `cliff_face_px` (16) tall. A **north, west or east**
edge has no face to show from this camera and is a rim instead: a pale lip on
the top surface, a heavier line, and a soft shade on the low ground against
it. Per display tile:

1. `levels` = the distinct heights of the four corners, low first. One level:
   draw as above and stop.
2. Ground: `under` = the lowest-elevation terrain among the corners on
   `levels[0]`. Treat every higher corner as `under` and draw the tile by the
   ordinary rule (shore and scorch included).
3. For each level `L` above the lowest: `on` = corners with height >= `L`,
   `T` = the lowest-elevation terrain among them; draw `cliff[T]` at row
   `mask(on)`. Then for each other terrain `U` among the `on` corners, low
   first, draw `overlay[U]` at the mask of corners that are `on` *and* at or
   above `U`.
4. **A step that stands in water or lava has a wash.** If `under` is `water`,
   draw `cliff_shore[T]` for the *first* level above the ground (`levels[1]`),
   at that level's mask, straight after the base strip and before every other
   layer of the tile; if `under` is `lava`, `cliff_scorch[T]` the same way. It
   is the foam (or the charred, glowing line) at the foot of the step and
   nothing else: rows 0 and 15 are empty. Both exist for the same fifteen
   terrains as `cliff`.

**Stairs and ramps** are the way up. The terrain art draws none; twelve
structures do (§2.4), each named for the side it comes **down** on:
`stairs_s|n|e|w` (a stone flight), `stairs_wood_s|n|e|w` (planks on two
stringers, for a village or a dock) and `ramp_s|n|e|w` (a trodden earth
slope, for open country). Each is two cells, one on the high ground and one
on the low (`structures.json:climbs`), and the border between them is the one
place a unit may cross that step. The three are the same crossing in three
materials: choose by what the place is built of. Any of them stands on any of
the fifteen stepping terrains.

**A river goes over a step as a waterfall.** Water has no cliff atlas: a step
is a contour a whole plateau follows, and a fall is one cell of it. So give
the river's cells the **lower** height on both sides of the step. The banks'
cliffs then stop at the river, each with its `cliff_shore` wash where it
stands in the water, and the `waterfall` structure (§2.4, `falls`) is laid
over the two river cells that straddle the step. Lava works the same way with
`cliff_scorch`, and has no fall drawn for it.

Limits: only a south-facing edge has a drawn face; the other three are the
rim, which is correct for the camera. Every flight climbs one level, 16 px. A
terrain not in `transitions.cliff` has no step (`tilekit` raises); for rock,
build with the wall kit (§2.5), whose own flight is `stairs_wall_*` (§2.4).
On masks 6 and 9 the lower level joins, like every other terrain. Cliff
atlases have alternates (below). A waterfall exists for a south-facing step
only, and is one cell wide.
`tilekit.Kit.render_map(grid, frame, heights=...)` is the reference.

**Alternates: four drawings of every edge** (`transitions.alternates`).
Optional. Each `overlay`, `shore` and `scorch` atlas has three more drawings,
under `overlay_b/`, `_c/`, `_d/` (and `shore_…`, `scorch_…`): other strokes
and another contour between the same edge crossings, so a long border does
not repeat every 64 px. `alternates.sets` lists them, each
`{suffix, overlay, shore, scorch}` with the same keys as the primary maps,
and `alternates.count` is how many there are (3).

- Choose per display tile by a stable hash of its (x, y):
  `pick = hash % (count + 1)`; 0 draws the primary atlases, `k` draws
  `sets[k - 1]`. The reference uses the variant hash of §2.1
  (`tilekit.alt_pick(x, y)`). Make **one** choice per tile and use it for
  every layer of that tile.
- Any mix is seamless: an alternate's outer 2 px ring is its primary's pixels
  in every mask and frame, so any two looks meet exactly as the primary meets
  itself.
- `alternates.overlay`, `.shore` and `.scorch` at the top level are `sets[0]`
  (the `_b` set), kept for a loader written when there was one. Using only
  those with `hash & 1` is still correct.
- How different they are, measured on the shipped atlases: within 10 px of
  the drawn contour any two of the four looks differ on 11–45% of pixels
  (mean 24%; `forest` most, `farmland` least), and over a whole tile on
  6–29% of its busiest mask. With four looks two neighbouring tiles share one
  a quarter of the time, where two looks shared one half of the time.
- What it cannot do: an alternate changes the contour and the strokes
  *between* the edge crossings. The crossings themselves are fixed (that is
  what makes any mix seamless), and the ground inside a terrain is the base
  tile and its variants (§2.1), not this.
- **A height step has alternates on the same terms.** Each set also carries
  `cliff`, `cliff_shore` and `cliff_scorch` (folders `cliff_b/` … and
  `cliff_shore_b/` …), three more drawings of every cliff atlas for the same
  fifteen terrains. Use the tile's one choice for them with every other layer of
  that tile. Measured on the shipped atlases through the reference renderer:
  the difference on display-tile seams between any mix and the primary is 0.
- Pair atlases have no alternate: they are pre-composited for editors. A map
  that wants the alternates draws layers.

`render_map(..., alternates=True)` is the reference.

### 2.3 Engine recipes

**Custom renderer (recommended; handles 3–4 terrains per tile):** implement
§2.2 directly. `tilekit.Kit.render_map(grid, frame)` is the reference.

**Godot 4:**
- Put the display TileMapLayer at offset (-32, -32) relative to the logic grid,
  or use a dual-grid addon. Base strips and pair atlases load as
  `TileSetAtlasSource` with `texture_region_size = 64x64`.
- For each atlas, create the tile at atlas coords `(0, mask)` with
  `animation_frames_count = 6`, `animation_columns = 6`,
  `animation_separation = (0,0)`, and each frame duration 0.1 s. The frames run
  horizontally, which is exactly how the atlas is laid out.
- Godot animates every tile off one engine clock, so frame sync is automatic.
- For terrain painting, create a terrain set in mode *Match Corners* with one
  terrain per name. On each pair atlas, set the peering bits of tile
  `(0, mask)`: `top_left_corner` = upper if `mask & 1`, else lower;
  `top_right_corner` = `mask & 2`; `bottom_left_corner` = `mask & 4`;
  `bottom_right_corner` = `mask & 8`.
- Godot's matcher can only pick existing tiles, so a display tile with 3+
  terrains finds no match. Either keep maps two-terrain per display tile, or
  draw layers: one TileMapLayer per elevation using the `overlay/` atlases,
  applying §2.2 per layer.

**Tiled:** one tileset per pair atlas (64×64, 6 columns × 16 rows).
- Add a *corner* Wang set with two colours (lower, upper). Assign Wang IDs per
  row from the mask.
- Give column 0 of each row a 6-frame animation of that row's columns at
  100 ms each.
- Base strips are 6-frame animated single tiles.

**Unity:** one Tile per (atlas, mask) as an AnimatedTile (6 sprites, 10 fps),
using a RuleTile or custom corner rule. Or run §2.2 in a script into Tilemap
layers ordered by elevation.

### 2.4 Structures (props)

`structures.json:structures[name]` -> `{file, footprint_tiles:[cols,rows], blocked_cells_suggested, passable, scale, frame_w, frame_h, loops, variant_of?, ground_suggested?, perch?, states?, solid_px_suggested?, sort_y_px?, walk_behind?, climbs?, layer?, falls?}`.

Seventy-eight structures:

| group | names |
| --- | --- |
| landmarks | `castle`, `tower`, `dungeon` |
| second designs | `castle_citadel`, `tower_wizard`, `dungeon_crypt`, `city_timber` (3x2, of `city`) |
| towns | `town_hamlet`, `town_crossroads`, `town_market`, `town_village` |
| wayside | `windmill`, `ruins`, `graveyard`, `mine`, `camp`, `well`, `signpost`, `fence` |
| crossings | `bridge` (2x1, east-west), `bridge_ns` (1x2, north-south), `dock` (2x1) |
| great landmarks, 3x2 | `volcano`, `stronghold`, `city`, `castle_ruin` |
| great landmarks, 2x2 | `palace`, `bastion`, `fort`, `great_tree` |
| great landmarks, 2x1 and 1x2 | `ship`, `cave_mouth`, `sea_serpent`, `stilt_village` (2x1), `spires` (1x2) |
| great landmarks, added | `tower_legend`, `lighthouse` (1x2), `temple` (2x2), `mountain_fortress` (3x2) |
| local scale, outdoors | `tree_oak`, `tree_pine`, `tree_birch` (1x2), `chest` (1x1), `hut`, `house` (2x2), `inn` (3x2) |
| local scale, furniture | `table`, `shelf`, `barrel`, `crate`, `hearth` (1x1), `bed` (1x2) |
| local scale, stairs up a step | `stairs_s`, `stairs_n` (1x2), `stairs_e`, `stairs_w` (2x1): stone |
| | `stairs_wood_s`, `stairs_wood_n` (1x2), `stairs_wood_e`, `stairs_wood_w` (2x1): planks |
| | `ramp_s`, `ramp_n` (1x2), `ramp_e`, `ramp_w` (2x1): trodden earth |
| local scale, stairs up a wall | `stairs_wall_s`, `stairs_wall_n` (1x2), `stairs_wall_e`, `stairs_wall_w` (2x1): stone, onto the `stone` wall kit |
| local scale, the street | `lamp`, `sign_inn`, `sign_smith`, `sign_shop`, `sign_healer` (1x2), `stall`, `stall_wares` (2x2) |
| local scale, on the floor | `rug` (2x1), `mat` (1x1) |
| local scale, water | `waterfall` (1x2) |

- **`scale` is `"map"` or `"local"`.** A map structure is a landmark on an
  overworld: a whole castle is two tiles wide and a person beside it is a
  marker. A local structure is drawn at a person's own scale (the hut's door is
  as tall as the people who use it) for a scene people walk around in. The
  thirty-nine in the last nine rows are local; the other thirty-nine are map. Do
  not put a map building and a local building in one scene.
- **The street: a lamp, four trade signs and two stalls.** All seven stand
  up, are walked behind and carry `walk_behind`, `solid_px_suggested` and
  `sort_y_px`, like the trees.
  - `lamp` is an iron post with a lantern on a crook, two cells tall so the
    light hangs above the heads under it. It blocks its foot cell `[0, 1]`
    (`solid_px_suggested` `[18, 104, 14, 10]`, `sort_y_px` 113). Idle is lit;
    the state `dark` is the same lamp with the light out, for day.
  - `sign_inn` (a tankard), `sign_smith` (an anvil), `sign_shop` (a purse and
    a coin) and `sign_healer` (a red flask) are a board hanging from a post,
    1x2, blocking the foot cell (`[11, 106, 9, 8]`, 113). They name a trade
    without a word, so they need no font and no translation. Stand one beside
    the door it belongs to. (`signpost`, the wayside fingerpost, points down a
    road; these mark a door.)
  - `stall` (a greengrocer's, red awning) and `stall_wares` (a pedlar's pots
    and cloth, blue awning; `variant_of` `stall`) are 2x2 and block their
    bottom row (`[20, 98, 88, 14]`, `sort_y_px` 112): a buyer stands south of
    the counter, and whoever stands north of it is behind the awning.
- **`layer: "floor"` marks a structure that lies flat** (`rug`, `mat`), seen
  from straight above: no height, no ground shadow, no collider. Draw it over
  the terrain and **under** every unit and every other structure, and never
  y-sort it. It is `passable`, blocks nothing and changes nothing about the
  ground under it. Absent means the structure stands up and is y-sorted.
  `tilekit.structure_is_floor(name)` is the reference.
- **`falls` is on `waterfall` only**: `{descends: "s", high_cell: [0, 0],
  low_cell: [0, 1], rise_px: 16}`, the same shape as a flight's `climbs`. It
  is laid over the two river cells that straddle a south-facing step (§2.2):
  `high_cell` on the river cell upstream of the step and `low_cell` on the
  one below it. Both cells are blocked and `ground_suggested` is `"water"`.
  It is one cell wide and falls 16 px, a cascade and not a cataract; a wider
  river takes one per cell, side by side. It loops on the global clock.
- **`house` and `inn` are buildings a person walks behind.** They block only
  their bottom row of cells (`blocked_cells_suggested`), and like the trees
  they carry `walk_behind`, `solid_px_suggested` (`[19, 89, 90, 24]` for the
  house, `[37, 89, 138, 24]` for the inn) and `sort_y_px` (`112`): someone
  standing north of that line is hidden by the roof. The inn has a shop front
  and a hanging sign; both have `open` (the door).
- **Furniture** blocks its footprint and also carries `solid_px_suggested`
  and `sort_y_px`, so a free-moving person can step close to a table and be
  sorted against it properly. `hearth` loops a fire; the rest only boil.
  `lighthouse` loops its lamp. Furniture is drawn for `flagstones` or
  `floorboards` but is an ordinary cut-out and stands anywhere.

- A structure is a cut-out (transparent background) that stands **on** terrain.
  The frame is exactly its footprint. Draw it with the frame's top-left at the
  footprint's top-left cell, on the logical grid.
- The bottom edge is the ground line, and the structure's ground shadow is in
  the art.
- Y-sort by the footprint's bottom edge together with monsters and people.
- `blocked_cells_suggested` lists the blocking footprint cells as `[col, row]`
  from the top-left: every cell, except that a tree blocks only its trunk cell
  `[0, 1]`. A person may stand in the crown's cell and the y-sort draws the
  leaves over them. It is a default: carve out a gate cell if the game lets
  units enter.
- **Trees: walk behind the crown, not through the trunk.** The three trees
  carry `walk_behind: true` and two pixel fields, both in frame pixels from the
  frame's top-left (measured on the shipped strips):
  - `solid_px_suggested` = `[x, y, w, h]`, the trunk's base: `[25, 106, 14, 11]`
    for the oak, `[26, 106, 12, 11]` for the pine and the birch. In a
    free-moving (not cell-stepped) game use this rectangle as the tree's only
    collider, in place of the trunk cell. Everything else in the 64x128 frame
    is walkable.
  - `sort_y_px` = `116`, the row where the trunk meets the ground. Y-sort the
    tree by `frame_top + sort_y_px`, not by the frame's bottom edge (the last
    12 rows are ground shadow). A person whose feet are above that line is
    drawn first and the crown covers them; one whose feet are below it is
    drawn over the trunk.
  `tilekit.structure_sort_y(name, top_px)` is the reference; it falls back to
  the frame's bottom edge for structures without the field.
- `passable` is `true` for a structure units walk **over**: `bridge`,
  `bridge_ns` and `dock`, the sixteen flights below, and the two floor pieces
  `rug` and `mat` (twenty-one in all). Their `blocked_cells_suggested` is `[]`. Lay a bridge
  over water cells (`bridge` for a crossing that runs east-west, `bridge_ns`
  for one that runs north-south) and treat those cells as walkable; a `dock`
  runs out from a shore over water the same way. Draw a passable structure
  *under* the units on it rather than y-sorting it. The sixteen flights
  below are passable too.
- **A flight crosses a height.** `climbs` is on the sixteen stairs and ramps
  only: `{descends, high_cell, low_cell, rise_px, material, onto}`, plus
  `wall_kind` on a wall flight. `descends` is the side the flight comes down
  on (`"s"`, `"n"`, `"e"`, `"w"`); `high_cell` and `low_cell` are `[col, row]`
  in the footprint, like `blocked_cells_suggested`; `material` is `"stone"`,
  `"wood"` or `"earth"`; `onto` says what the top of the flight stands on.
  - **`onto: "step"`** (`stairs_*`, `stairs_wood_*`, `ramp_*`): one level of
    stepped ground (§2.2, cliffs), `rise_px` 16. Place it with `high_cell` on
    the last cell of the upper level and `low_cell` on the first cell of the
    lower one, so the frame straddles the step: the `_s` flight on a
    south-facing bank (treads and risers toward the viewer), `_n` on a north
    edge (seen from above: treads going away), `_e` and `_w` on the flanks.
    Let a unit pass between those two cells and nowhere else along the step.
    The art does not move the unit: if the game shows height, ease the
    unit's y by `rise_px` across the frame. One flight climbs one level; a
    two-level bank needs a landing between two.
  - The three materials are the same crossing. Stone and wood have treads
    and read as built; the ramp is a bare slope with no risers, and it reads
    best where it comes toward the viewer (`ramp_s`). On a flank (`ramp_e`,
    `ramp_w`) it is drawn from the side: one sheet of trodden earth falling
    from the landing to the ground, with the bank showing in section under
    its near edge. It still has no treads to count, so prefer the stairs on a
    flank if the crossing has to be found at a glance.
  - **`onto: "wall"`** (`stairs_wall_*`): the top of a wall kit, and
    `wall_kind` names the kit, `"stone"`. `rise_px` is 30, that kit's face.
    Put `high_cell` **on a wall cell** (the flight is drawn over that piece's
    top and down its face) and `low_cell` on the open ground beside it. This
    is the only way a unit gets onto a wall: let it pass between those two
    cells, and from the wall cell along the wall's own cells, and nowhere
    else. The wall's top is drawn `rise_px` above the wall cell's foot, so
    lift a unit standing on the wall by `rise_px` and ease it across the
    flight; while it is on the wall draw it **after** the wall pieces it
    stands on (a wall is otherwise never sorted against a person, §2.5).
    Only the `stone` kit has a flight. None is drawn for `rock`, `stone_low`,
    `timber` or `interior`, whose faces and insets are other sizes
    (`walls.json:kinds[kind].face_px`, `inset_px_by_side`): do not stand this
    one against them.
- `variant_of` names the structure this one is a second design of
  (`castle_citadel` -> `castle`, `tower_wizard` -> `tower`, `dungeon_crypt` ->
  `dungeon`, `city_timber` -> `city`, `stall_wares` -> `stall`). The
  footprint, the blocked cells and the states match, so a map can swap one
  for the other, by hand or by a hash of the cell. `city_timber` is a walled
  town of timber and thatch on the capital's ground plan (a palisade, a
  roofed gate, a thatched hall, a lookout on legs), for the northern and
  border towns the pale stone capital does not suit.
- **The great landmarks are the named places of a world map**, two, four and
  six tiles each, for the zoomed-in map layer: one per place, not scattered.
  A six-tile one is 192x128 and stands on a 3x2 block of cells. They block
  their whole footprint. Sixteen of the seventeen have a state (below);
  `castle_ruin` has none, because what changes there is the dragon on its
  `perch`.
- `ground_suggested` names the terrain a structure is drawn to stand in when
  that is not dry land: `ship` and `sea_serpent` are `"water"` (a waterline
  and wake, no ground shadow: on grass they float), `stilt_village` is
  `"swamp"`. Absent means any land. `ship` does not move; if the game sails
  it, the engine translates the sprite.
- `perch` is `[x, y]` in frame pixels from the frame's top-left: where the
  feet of something standing **on** the structure go. Only `castle_ruin` has
  one, the flat roof of its great tower, drawn for a `dragon`: put the
  dragon's box bottom-centre there and draw it after the structure.
- `windmill` turns its sails 90 degrees per loop (four sails, so the loop
  closes); `camp` has a fire and `graveyard` a wisp, both looping.

**Structure states.** `states` is present on twenty-eight structures (thirty-one
state strips) and maps a state name to `{file, frame_w, frame_h, loops,
label}`. `file` at the top level is idle. A state's frame has the same size
and position as idle's. There are two kinds, and `loops` says which:

- **`loops: false`: play once, hold the last frame, play backwards to undo.**
  Frame 0 is idle's frame 0, pixel for pixel (measured on all fifteen shipped
  strips), so the change starts on any idle frame boundary without a jump.
- **`loops: true`: a condition.** Swap it in for idle for as long as it
  lasts, on the global clock, and cut between the two on any frame.

| state | on | loops | how to play it |
| --- | --- | --- | --- |
| `open` | `castle`, `castle_citadel` | `false` | Frame 0 is the closed gate: idle's frame 0, pixel for pixel (measured on both castles). Play 0->5 once and **hold frame 5**: the gate stays up. To close it, play the strip backwards. |
| `open` | `chest`, `hut`, `house`, `inn` | `false` | The same contract (frame 0 measured identical to idle's on each): the chest's lid tilts back on its rear hinge, one connected shape in every frame, onto gold; the door swings in. Hold frame 5; play backwards to close. An opened chest stays on frame 5. |
| `open` | `city`, `city_timber`, `stronghold`, `bastion`, `fort`, `mountain_fortress` | `false` | The same contract on a great landmark: the gate goes up, or the doors swing in, and stays. |
| `moored` | `ship` | `false` | The sails are furled and she rides at anchor. Hold frame 5 while she is in port; play backwards to make sail. |
| `dive` | `sea_serpent` | `false` | The serpent goes under. Frame 5 is open water with a ripple on it: hold it, or remove the structure. Play backwards for it to surface. |
| `sealed` | `cave_mouth` | `false` | A rockfall closes the mouth. Hold frame 5 while the way is shut; play backwards to clear it. |
| `raided` | the four `town_*`; `city`, `city_timber`, `palace`, `fort`, `great_tree`, `stilt_village` | `true` | The place on fire. Swap it in for idle for as long as the raid lasts. |
| `erupt` | `volcano` | `true` | The volcano in eruption, for as long as the story says. |
| `dark` | `lamp`, `lighthouse`, `temple`, `tower_legend` | `true` | The lights are out: a lamp or a lighthouse by day, a temple or a tower abandoned. |
| `awake` | `spires` | `true` | The obsidian spires lit from within. |

Two things an engine should know about them, measured on the shipped strips.
`sea_serpent`'s `dive` changes more per frame than any other structure strip
(mean step 45.5, against 1.6-8.6 for the other landmark states): the whole
animal leaves the frame, which is the point. And `ship`'s `moored` is 24.3
for the same reason, three sails coming down. Neither is a looping state, so
neither flickers; both simply should not be played faster than the clock.

`tilekit.structure_frame(name, frame, state)` is the reference.

### 2.5 Walls: the hand-placeable kits (47 labelled pieces each)

`terrain/walls/walls.json`. A wall here is **a cell that is wall**, on the
logical grid, not the dual grid: the `rock` *terrain* (§2.2) grows a cliff
edge between cells and is right for a painted cave or a mountainside; a
*kit* is for walls a designer places cell by cell, one tile wide if wanted,
with proper ends, corners, tees and crossings.

**Walls do not animate.** Every piece is one still 64x64 PNG, not a strip
(`frames: 1`). Do not put walls on the global frame clock.

```json
{ "frames": 1, "still": "...", "grid": "primary",
  "neighbour_bits": {"n":1,"ne":2,"e":4,"se":8,"s":16,"sw":32,"w":64,"nw":128},
  "rule": "...", "door_rule": "...", "window_rule": "...", "join_rule": "...", "bond_rule": "...",
  "bond_rank": ["interior","timber","stone_low","stone","rock"],
  "naming": {...}, "blocks": "...", "draw": "...",
  "kinds": { "<kind>": {
      "note", "inset_px": 8, "inset_px_by_side": {"n","s","e","w"}, "face_px",
      "gameplay_suggested": {...},
      "pieces": { "<label>": { "file", "wall_neighbours": [...], "open_sides": [...], "has_face": bool,
                               "joints": {"n","e","s","w": "<joint name>"} } },
      "doors":  { "<name>":  { "file", "replaces", "what", "state", "passable", "opening_px": [x0,y0,x1,y1] } },
      "windows": { "<name>": { "file", "replaces", "state", "passable": false, "seen_from", "glass_px": [x0,y0,x1,y1] } },
      "joints": { "<joint name>": { "file", "side", "wall_at_corners": [...] } },
      "bonds":  { "<other kind>": { "<joint name>": { "file", "against", "replaces", "teeth_of" } } },
      "lookup": [ 256 labels ] } } }
```

- **Five kinds**, the same 47 labels and the same `lookup` in each, so a map
  can change material by changing one string:

  | kind | what it is | face_px | doors |
  | --- | --- | --- | --- |
  | `rock` | living rock: a cliff or cave wall placed by hand | 24 | door (a cave or cellar mouth) |
  | `stone` | dressed stone in courses: a keep, a town wall, a cellar | 30 | door, gate |
  | `stone_low` | the same stone at half height: a garden wall, a parapet | 12 | none |
  | `timber` | a palisade of upright logs, one log thick | 28 | door, gate |
  | `interior` | a room's wall, cut away: hatched top, plaster over a wainscot | 36 | door |

  `stone_low` and `timber` stand further in from their open sides than the
  rest (`inset_px_by_side`); they still block the whole cell.
- **Kinds join each other with a butt joint** (`join_rule`). A wall cell of
  *any* kind counts as a neighbour when a piece is chosen, so each kit runs to
  the edge of its own cell. Then, on each of the four sides where the
  neighbour is a wall of **another** kind, draw this kind's joint over the
  piece: `pieces[piece].joints[side]` names it and `kinds[kind].joints[name]`
  has the file (a door cell uses its `replaces` piece's). Both cells of a
  boundary do this, each from its own kit. A joint is one still 64x64 cut-out
  that lies inside its own cell and inside its own piece's ink: it closes the
  cut end with the kit's own outline and a shade, and draws nothing on the
  neighbour. Sixteen per kind: four sides, times which of the two diagonal
  neighbours beside that side are wall (`joint_e`, `joint_e_ne`,
  `joint_e_ne_se`…). Where both neighbours are the same kind no joint is
  drawn and nothing changes: a one-kind map renders exactly as before.
- **Or with a bond** (`bond_rule`), for two kinds built as one wall. A bond
  is the joint with teeth: in the face, the stronger kind's blocks run 4-5 px
  into the weaker one, each outlined, and the line between the kinds is left
  open behind them. `bond_rank` is the order, weakest first: rock keys into
  everything, stone into timber, a palisade's two rails into a room's plaster.
  To use it, wherever the join rule says to draw joint `J` on a side whose
  neighbour is of kind `K`, draw `kinds[kind].bonds[K][J]` instead **if it
  exists**, and the joint if it does not. Both cells do this, each from its own
  kit; the weaker kind's file holds the teeth, the stronger kind's is its
  joint with the gaps (`teeth_of` names the kind whose blocks they are).
  - A bond exists only for an **east or west** side that shows face: the
    profiles `joint_e`, `joint_e_ne`, `joint_w`, `joint_w_nw`. A north or
    south side, and a side with wall at its south corner, keeps its joint: two
    tops meet there at different heights and widths, and nothing keys across.
    So 16 files a kind (4 other kinds x 4 profiles), 80 in all.
  - A bond is a still 64x64 cut-out inside its own cell, within 7 px of its
    side and on solid wall in every piece it can be laid over, a closed or
    open gate included. Outside the teeth it is the joint, pixel for pixel.
  - Choose per wall, not per cell: a boundary whose two cells disagree shows
    teeth with a line across their roots.
- **Automatic placement.** For a wall cell, OR together `neighbour_bits` of the
  eight neighbours that are also wall (of any kind), and draw
  `lookup[bits]`. All 256 combinations are in the table; a diagonal neighbour
  only changes the piece when both orthogonal neighbours beside it are wall,
  and the table already folds that in. Cells off the map count as not-wall (or
  as wall, if the map edge should read as solid).
- **Hand placement.** The labels say what a piece is:

  | label | what it is |
  | --- | --- |
  | `single` | a lone pillar |
  | `end_n`, `end_e`, `end_s`, `end_w` | that end of a one-cell-wide wall |
  | `straight_ns`, `straight_ew` | a one-cell-wide run |
  | `bend_ne`, `bend_se`, `bend_sw`, `bend_nw` | a one-cell-wide wall turning; the corner named is the outside of the turn |
  | `tee_n`, `tee_e`, `tee_s`, `tee_w` | a one-cell-wide T; the side named has no branch |
  | `cross` | a one-cell-wide crossing |
  | `corner_ne`, `corner_se`, `corner_sw`, `corner_nw` | that corner of a solid block |
  | `edge_n`, `edge_e`, `edge_s`, `edge_w` | that edge of a solid block (`edge_s` shows the face) |
  | `inner_ne`, `inner_se`, `inner_sw`, `inner_nw` | solid, with that diagonal neighbour missing: an inside corner |
  | `solid` | interior: the top, no edge |
  | `<piece>_notch_<diagonals>` | the same piece with inside corners at those diagonals |

  `pieces[label].wall_neighbours` lists the neighbours the piece expects and
  `open_sides` the sides it faces open ground on, so an editor can check a
  hand-placed piece.
- **Doors and gates are wall cells with the piece swapped.** A door is an
  18 px opening in a south face, a gate 38 px. Each comes in two places and
  two states: `door_ew_closed`, `door_ew_open`, `door_edge_s_closed`,
  `door_edge_s_open` (and `gate_...` the same). Mark a wall cell as a door;
  where `lookup` answers the door's `replaces` (`straight_ew` for `_ew`,
  `edge_s` for `_edge_s`), draw the door piece instead. Anywhere else the
  cell cannot hold a door: fall back to the plain piece. The neighbours see a
  door cell as wall, so nothing around it changes.
  - **Closed** (`passable: false`) blocks like any wall.
  - **Open** (`passable: true`): the cell is walkable. There is no opening
    strip; swap the picture. `opening_px` is the hole in the piece, so an
    engine can limit walking to it.
  - An `_ew` door leads through a one-cell-wide wall, north to south. An
    `_edge_s` door leads *into* a solid block: it is the mouth of a cave or
    cellar, and what is behind it is another scene.
- **Windows are wall cells with the piece swapped, as doors are**
  (`window_rule`). Three kits have them, `stone`, `timber` and `interior`
  (`kinds[kind].windows`; `rock` and `stone_low` have an empty table), four
  pieces each: `window_ew_dark`, `window_ew_lit`, `window_edge_s_dark`,
  `window_edge_s_lit`. Mark a wall cell as a window; where `lookup` answers
  the window's `replaces` (`straight_ew` or `edge_s`), draw the window
  instead, and anywhere else fall back to the plain piece. The neighbours see
  a window cell as wall, so nothing around it changes.
  - A window **always blocks** (`passable: false`), like the wall it is in.
  - `state` is whether light comes through the glass at the viewer, and
    `seen_from` says which way that is. `"outside"` (stone, timber): `lit` is
    a lamp indoors, for night, and `dark` is the day. `"inside"` (interior):
    `lit` is daylight and `dark` is the night sky. There is no strip: swap
    the picture.
  - `glass_px` is the pane in cell pixels, `[25, 33, 39, 48]` for stone,
    `[25, 32, 39, 45]` for timber, `[25, 24, 39, 38]` for interior, for an
    engine that adds its own glow.
  - A window is in the south face, so only a wall the viewer sees the face of
    has one. Corner pieces and north, east and west edges have none.
- **Any piece fits any neighbour the table would give it**, exactly: a map
  rendered whole and the same map assembled from pieces differ by 0
  (`make_walls.py`'s `wallcheck`, per kind).
- **Collision is the cell.** A wall cell blocks all of its 64x64. The art
  stands `inset_px_by_side` in from each open side and shows `face_px` of face
  under every south-facing edge, all inside the cell, with a short cast shadow
  that also stays inside it.
- **Draw walls over the terrain and before anything y-sorted.** Because the
  face is inside the wall's own blocked cell, a wall never needs to hide a
  person. The one exception is an **open** door or gate: draw that piece after
  (over) whoever stands in its cell, so the lintel covers their head. Put any
  terrain under a wall; it is a cut-out.
- **Walking on a wall** is possible on the `stone` kit only, by way of a
  `stairs_wall_*` flight (§2.4, `climbs.onto: "wall"`). A unit on a wall cell
  is drawn after the wall pieces, lifted by the flight's `rise_px` (30).
- `tilekit.wall_piece(wall, x, y, kind)`, `door_piece(piece, what, state, kind)`,
  `window_piece(piece, state, kind)`,
  `wall_joints(kinds, x, y)`, `wall_overlays(kinds, x, y, bonded)` and
  `render_walls(img, cells, kind, doors, bonded, windows)` are the reference
  (`windows` maps a wall cell to `"dark"` or `"lit"`; `demo_street.png` and
  `demo_room.png`);
  `render_walls` takes a set of cells of one kind, or a dict `{(x, y): kind}`
  for a plan of several (`demo_walls_mixed.png`, and the same plan with
  `bonded=True` in `demo_walls_bonded.png`).

---

## 3. Monsters

`monsters.json:monsters[creature]`:

```json
{ "tier": 1..5,                        // int: 1-3 regular, 4 miniboss (ogre, treant), 5 boss (dragon and the four lords)
                                        // 1: slime rat bat frog crab imp serpent;
                                        // 2: goblin skeleton wolf boar zombie harpy beastman scorpion merrow;
                                        // 3: orc spider wraith yeti golem frostshard ashfiend
  "rank": "normal" | "miniboss" | "boss",
  "footprint_tiles": [cols, rows],      // ogre, treant and the four lords [1,2], dragon [2,2], others [1,1]
  "box": [w_px, h_px],                  // footprint * 64: the idle box
  "elite": bool, "elite_of": "<creature>",   // elite_of only when elite is true
  "states": { "<state>": {
      "frames": 6 | 12,                 // this state's length; 12 only for a big creature's long states (below)
      "loops": bool, "follows": null | "<state>", "cyclic": bool, "hover_px": number,
      "impact_frame": int,              // offensive states only (attack, cast, web, tongue, split, fire_breath,
                                        //   bubble, charge, spew, roar, ember, warcry, slam, roots,
                                        //   spit, venom, tide, nova, cinders, pounce, bomb, howl, cleave, hurl)
      "facings": { "<facing>": { "file", "frame_w", "frame_h", "anchor": [ax, ay],
                                 "body_bbox": [x0, y0, x1, y1],            // idle only
                                 "bbox_frames": [[x0, y0, x1, y1] | null, ...],   // one per frame
                                 "hit_bbox": [x0, y0, x1, y1] | null } } } } }    // states with an impact_frame
```

There are thirty creatures and thirty elites, 60 entries in all. Every
one has `idle, walk, attack, hurt, die, poof`, and **every one has a
signature state** (`bat` and `harpy`'s is `fly`):
- `slime` has `split`;
- `frog` has `tongue`, a lash that reaches 33 px past its body facing left or right and 24 px
  facing up, but only 6 px below its feet facing down (measured);
- `crab` has `bubble`, a stream of bubbles; `zombie` has `spew`, a gout of bile;
  `yeti` has `roar`, a cone of frost. All three are effects thrown ahead of the
  body, like `web`;
- `boar` has `charge`: the body itself lunges a long way forward, trailing dust;
- `imp` has `ember`, a coal thrown from its fork; `beastman` has `warcry`, a
  bellow that shakes the air in front of it; `golem` has `slam`, both fists
  into the ground and a shock ring along it; `treant` has `roots`, thorns
  breaking out of the ground ahead. All four are effects like `web`; the
  first three have impact frame 3, and `roots` is a twelve-frame state with
  impact frame 6. Measured reach past the idle ink, facing right: 20, 14, 26 and
  35 px. Facing down or up the `slam` and `roots` spread sideways across the
  whole 64 px frame instead (9-11 px and 5-6 px past the body each side);
- the five regional monsters each throw something of a different shape, all
  effects like `web` (the body holds its pose), impact frame 3. Reach past the
  idle ink, measured on the shipped strips:
  - `serpent` has `spit`, a jet of venom: 24 px facing right, 18 px upward
    facing up; facing down the body covers it (4 px above the head);
  - `scorpion` has `venom`, flung off the raised barb: 17 px facing right,
    13 px facing up, 5 px below the body facing down;
  - `merrow` has `tide`, a wave called up with the trident: 23 px facing
    right; facing up it spreads 10-11 px to each side, facing down 3-5 px all
    round;
  - `frostshard` has `nova`, a ring of splinters burst outward: 8-12 px on
    every side in every facing. It is the one signature with no direction, so
    hit everything around it;
  - `ashfiend` has `cinders`, a breathed cloud of ash: 21 px facing right,
    9 px upward facing up, 4-5 px to each side facing down;
- `bat` and `harpy` have `fly`;
- `skeleton`, `wraith` and `darkhorn` have `cast`;
- `spider` has `web`;
- `dragon` has `fly` and `fire_breath`;
- the five that had only a bite or a blade, all six frames, impact frame 3.
  Reach is `hit_bbox` past `body_bbox`, measured on the shipped strips:
  - `rat` has `pounce`: it crouches and springs, and is off the ground on
    the impact frame. The one six-frame state that leaves the ground. 19 px
    forward facing right, 10 px upward facing up;
  - `goblin` has `bomb`: it lights a bomb and lobs it. The bomb is an effect
    like `web`; it bursts 34 px in front facing right (a 26 x 24 px burst),
    25 px below the feet facing down, 27 px above the head facing up;
  - `wolf` has `howl`: muzzle to the sky. Nothing travels: it is a call, for
    a buff, a summons or a fear effect, not a hit. Its `hit_bbox` is the
    raised head and the sound lines above it, 16-19 px over the body;
  - `orc` has `cleave`: one flat sweep of the axe that strikes like an
    attack and trails an arc. 14 px to the front facing right, 11 px to one
    side facing down or up. The sweep crosses the whole front over frames
    2-4, so hit everything in front of it, not only inside the box;
  - `ogre` has `hurl`, a **twelve-frame** state: it tears a boulder out of
    the ground (a hand on it by frame 2), has it overhead by frame 4, lets
    go on frame 6, and the boulder **lands on frame 8**, the impact frame,
    61 px in front facing right, 27 px below the feet facing down, 50 px
    above the head facing up;
- three of the lords, each a **twelve-frame** state under a name a small
  creature also uses. `monsters.json` is per creature, so nothing collides:
  - `ghorakhar` has `charge`: horns down and a run of 33 px forward facing
    right, impact frame 6. The body itself travels, like the boar's;
  - `rangoskhar` has `slam`: a leap (off the ground on frames 2-5) and a
    landing on both hooves on frame 6, the impact frame, with a shock ring
    10-19 px past the body on every side in every facing. Like `nova`, it
    has no direction: hit everything around it;
  - `ramulos` has `roar`: a drawn breath and a roar, impact frame 5, 21 px
    in front facing right. Facing down or up the body covers it
    (`hit_bbox` is null).

**Elites.** Every creature has an elite, the four lords included:
`<creature>_elite`, with `elite: true` and `elite_of: "<creature>"`. It is the
same drawing in another palette, shipped as its own strips, so no runtime
recolouring is needed. Its states, `frames`, frame sizes, anchors,
`impact_frame`s and tier are its base's, so it can stand in for its base
anywhere; what makes it stronger is the engine's business. An elite's
*effects* are in its own colours too: what it throws, breathes or bursts into
is dyed from the elite's palette, so an elite imp's coal is not the base's
orange one. The shapes are still the base's.

**Regional rank and file.** `imp` (tier 1) is a small red horned devil with
bat wings, a coal-tipped tail and a fork, for volcanic and ashen ground;
`beastman` (tier 2) is a bull-headed, hooved soldier with a two-handed axe,
the foot soldier of the horned lords. Five more belong to a region each:
`serpent` (tier 1, a coiled desert snake) and `scorpion` (tier 2) for sand and
desert; `merrow` (tier 2), a fish-man with a trident who comes ashore, for
coasts and swamp; `frostshard` (tier 3), a hovering ice crystal, for snow and
ice; `ashfiend` (tier 3), an elemental of cinders, for ash and lava banks.
All seven are ordinary 1x1 creatures, each with a signature (above).

**The lords.** `ghorakhar` (a horned warlord in black plate, spear),
`rangoskhar` (his horned reaver, poleaxe), `ramulos` (the lion lord,
greatsword) and `darkhorn` (a horned sorcerer, staff; `cast` is his ranged
attack, impact frame as listed) are named characters, `rank: "boss"`,
`tier: 5`, one tile wide and two tall like the ogre. They are monsters in
every mechanical sense, the same states, anchors and rules as the rest, and
like any creature they `poof` when killed; hold `die`'s last frame (11)
instead if the story wants the body to stay. They are not paperdoll people: nothing they
wear can be swapped. Each has one dialogue portrait, a single picture rather
than layers (§4.7, `portraits.json:monsters`), and an elite like any other
creature (the portrait is the base's).

**The big creatures have long states.** `ogre`, `treant`, `dragon` and the
four lords (and their elites) play `attack`, `walk`, `die` and their own
signature (`fly`, `fire_breath`, `cast`, `roots`, `hurl`, `charge`, `slam`,
`roar`) over **12 frames**, still at 10 fps: 1.2 s. Their `idle`, `hurt` and
`poof` are 6 like everyone's. The state's `frames` says which,
`monsters.json:long_states` lists them per creature, and the strip is
`frames * frame_w` wide. **Never divide a strip's width by 6**; read
`frames`. `tilekit.monster_frames(creature, state)` is the reference.
- A long `attack` is a heavy blow with weight in it: frame 0 the rest pose,
  1-3 the wind-up, 4 the one in-between of the downswing, **5 the impact**,
  6-7 the weapon staying where it landed, 8-11 the recovery back to rest. The
  half second before the blow is the player's dodge window; the half second
  after it is theirs to punish.
- A long `walk` is one cycle of two steps in 1.2 s, cyclic like any walk. A
  six-frame creature takes two steps in 0.6 s, so give the big ones about
  half the ground speed per step you would give a goblin, or the feet slide.
- A long `die` is a giant going down, not a door slamming: frames 1-2 the
  stagger back, 3-4 it comes forward with the knees going, 5-7 the fall,
  each step longer than the last, and **frame 8 the landing**, with dust
  thrown up at both ends of the body. Frame 9 it settles, 10 and 11 it lies
  still while the last dust clears (the body does not move between those
  two). Shake the screen or play the thud on frame 8. What a giant was
  holding (the ogre's club) slides out of its hand on frames 2-4 and is on
  the ground before the body is. `die` has no `impact_frame`; frame 8 is a
  fixed fact of the seven. **Hold frame 11**, or chain `poof`, which is six
  frames and starts on frame 11 exactly.

**Placement.** The creature's position is its *box*, a `box` sized rectangle
whose bottom edge is the ground line and whose bottom-centre is the feet.
- Draw frame `f` of the current (state, facing) at `box_top_left - anchor`.
- A state that reaches further than the box (a lunge, a topple) ships a larger
  frame, padded by whole tiles. `anchor` says where the box sits inside it.
- Using the anchor keeps the body perfectly still across state changes. Never
  centre a padded frame.
- `anchor` differs by facing (a bite pads east when facing right), so look it
  up per facing.

**Y-sort key:** the box's bottom edge (feet), not the frame's.

**State machine rules** (guaranteed by the art):
1. **Idle transitions are seamless.** Frame 0 of every state except the cyclic
   ones (`walk`, `fly`), `die` and `poof` is `idle`'s rest pose, the same pose within 3 px
   (validated). The pencil boil differs about as much as one idle frame differs
   from the next (measured on the shipped strips), so a cut on frame 0 reads as
   ordinary boil. Every looping one-shot (`attack`, `hurt`, `cast`…) plays
   frames 0→`frames - 1` and ends back on the rest pose.
2. **Only enter a state on frame 0.** All strips run on the global clock. To
   start `attack` at an arbitrary moment, either wait for the next frame 0
   (≤ 0.5 s; up to 1.1 s for a twelve-frame state), or run that creature's
   one-shots on a *local* counter from 0 and return to the global clock
   afterwards. Both are safe because frame 0 is the rest pose. For a
   twelve-frame attack use the local counter: a blow that starts a second
   late is not a tell.
3. `walk` and `fly` are **cyclic** (`cyclic: true`): frame 0 is mid-cycle, not
   the rest pose. Loop them while the activity lasts and switch back to `idle`
   at the end of a cycle. `fly` draws the body `hover_px` (17) above the ground;
   its shadow stays on the ground line, so the box does not move.
4. `die` does **not** loop: hold its last frame (a corpse: frame 5, or
   frame 11 for the seven big creatures and their elites), or chain `poof`.
5. `poof` has `follows: "die"`. Its frame 0 is die's last frame pixel for
   pixel (verified on all 240 strips, anchors applied).
   The cloud is gone by frame 4. Frame 5 holds only a few fading sparkles
   (36–50 opaque px, measured on all 240 strips), and the dropped weapon and the
   shadow fade out with it. So when frame 5 ends, delete the entity; nothing
   pops. Never play `poof` without
   `die`.
6. `hurt` is designed to be played once per hit; `attack` and every signature
   but `fly` once per use. They all end on the rest pose, so repeating them
   back-to-back is also clean.

**Facing from movement:** pick the dominant axis of the velocity.
`|vx| >= |vy|` → `right`/`left`, otherwise `down`/`up` (screen y grows
downward, so `vy > 0` is `down`). Turning is a cut between strips at the same
position; the feet line, centroid and shadow were checked to match across
facings.

**Suggested gameplay tiers:** 1 = starter zone, 2 = mid, 3 = late, 4 = the
ogre and the treant (`rank: miniboss`), 5 = the dragon and the four lords
(`rank: boss`). An
elite carries its base's tier: use `elite` to tell them apart.

**Hurtbox:** `states.idle.facings[f].body_bbox` is idle frame 0's opaque ink,
`[x0, y0, x1, y1)` in px relative to the box's top-left, per facing (a wolf is
long facing right and narrow facing down). It excludes the ground shadow. Use it
as the hurtbox in every state; it is a gameplay shape, not a per-frame mask.

**Per-state boxes.** Two more, measured on the shipped strips at alpha >= 160
(a ground shadow is below that) and given in the same coordinates as
`body_bbox`: px relative to the box's top-left, so the anchor is already
taken out and a padded state's values run negative and past the box.
- `bbox_frames`, on every state and facing: one `[x0, y0, x1, y1)` per
  frame, the opaque ink of that frame, or `null` for a frame with none (the
  end of `poof`). It follows a lunge, a crouch, a leap and a topple, so it is
  the hurtbox for a game that wants one per frame: in `die` it is the body
  going down, in `pounce` and `slam` the body in the air. It is *everything*
  drawn, though, and in the states that throw something (a breath, a web, a
  boulder, a shock ring) that is in the box too: there, keep `body_bbox` as
  the hurtbox.
- `hit_bbox`, on every state with an `impact_frame`, per facing: the box of
  what the impact frame draws **beyond** the idle silhouette (the idle frame
  0 ink, grown 4 px so boil and a pixel of lean do not count). It is the
  weapon at the end of its arc, the head thrown forward, the breath, the
  bomb where it bursts: a suggested hitbox, live on `impact_frame` and for
  as long after as the game likes.
  - It is `null` where the body covers its own blow (fewer than 24 new
    pixels), which is common facing down or up at this camera: a wolf's
    bite, a slime's lunge, a frog's tongue facing down, the lion lord's
    roar. There, use a box one body-width deep in front of `body_bbox`.
  - It is a rectangle round everything new on that frame, so it is generous:
    round an arc it takes in the corners, and where the whole body travels
    (`pounce`, `charge`, a bite in profile) it takes in most of the moved
    body and whatever trails it. Clip it to the side the creature faces if
    the game needs it tight.
  - Examples, facing right, body then hit: goblin `attack`
    `[19,18,48,57]` / `[41,37,65,53]`; ogre `attack` `[10,16,50,122]` /
    `[43,36,102,122]`; dragon `fire_breath` `[7,20,122,123]` /
    `[21,24,204,72]`.
- There are no per-state boxes for people (§4); a person's hurtbox is the
  engine's to choose.
`tilekit.monster_boxes(creature, state, facing)` returns all three.

**Impact frame:** `impact_frame` is the frame an offensive state's motion
peaks. In a six-frame state it is 2 for `attack` and 3 for every signature
(`cast`, `web`, `tongue`, `split`, `bubble`, `charge`, `spew`, `roar`,
`ember`, `warcry`, `slam`, `spit`, `venom`, `tide`, `nova`, `cinders`,
`pounce`, `bomb`, `howl`, `cleave`). In a twelve-frame state it is 5 for
`attack`, `fire_breath` and `ramulos`'s `roar`, 6 for `darkhorn`'s `cast`,
the `treant`'s `roots`, `ghorakhar`'s `charge` and `rangoskhar`'s `slam`,
and 8 for the ogre's `hurl` (the boulder landing). Read it from the JSON; do
not assume. Apply damage, spawn the projectile or play the hit sound on that
frame. Attack reach: `hit_bbox`; failing that, the side the state's frame is
padded on (`frame_w/h` > box, and `anchor`) is where the strike goes.

### 3.1 Loot: what a monster leaves behind

`loot.json:loot[item]` → `{file, frame_w, frame_h, loops, kind, icon}`. `kind`
is `gold`, `gem`, `weapon`, `potion` or `key`. Items: `gold`, `gem_ruby`,
`gem_sapphire`, `gem_emerald`, `drop_sword`, `drop_axe`, `potion_health`,
`potion_mana`, `key`.

- A 1×1 cut-out with its own ground shadow, drawn low and centred: put the
  frame's bottom-centre on the dead creature's box bottom-centre (its feet).
- It loops (a glint travels over it) until picked up. Y-sort like anything on
  the ground.
- `icon` names the inventory picture of the same thing in `icons.json` (§4.5),
  or is `null`. The potions and the key have one, so what is picked up off the
  ground and what appears in the bag are the same object; gold, gems and the
  dropped weapons do not.
- **When:** spawn drops when `poof` ends, at the spot where the creature's box
  was. The smoke covers the moment, so the swap never shows.
- **What:** `drops_suggested` is a suggestion, not a rule. Roll each entry
  independently: `chance` is its probability and `pick` chooses uniformly.
  Scatter several drops a few px apart so they don't stack. **An entry with
  chance 0 is never rolled** (the key): a quest or a chest places it.

---

## 4. People (paperdoll): heroes, NPCs, accessories

A person is a stack of 64×64 6-frame strips, all drawn at the **same position**,
bottom first, on the same frame. Nothing is pre-merged.

Each person has:
- **exactly one skin**, `body_<tone>` plus its `-near` band (the arms);
- **one head of hair**: `hair`, or one `hair_<colour>` (+ `-back` band);
- a **beard** (bearded bodies only): `beard`, or one `beard_<colour>`;
- any number of **accessories** (clothes, armour, weapons, shields, cloaks,
  hats), one per slot by convention.

### 4.1 Fast path: pre-resolved builds and looks

- `heroes.json:heroes[body].builds[build].layers[facing]` → ordered file list.
  - Bodies: `hero` (boy), `hero2` (girl).
  - Builds, in progression order: `clothes, leather, ranger, chain, knight,
    plate, battlemage, dragon, dark, light`.
  - The endgame builds are `plate, dragon, dark, light`: the ones made of
    `hero_gear` items (`accessories.json:<item>.hero_gear`). `battlemage` has
    none.
  - `hero_gear` means "keep out of random crowds", not "heroes only": the
    `noble`, `queen` and `king` NPC looks wear `cape_red`, which is hero_gear.
- `npcs.json:npcs[body].looks[look].layers[facing]` → the same.
  - Bodies: `m_lanky m_burly m_portly m_stocky m_elder f_slender f_athletic
    f_curvy f_stout f_elder`.
  - Townsfolk looks: `farmer smith merchant noble guard priest wizard monk
    innkeeper barmaid jester bard hunter sage queen villager lady watchman fisher
    miner herbalist baker shepherd courier pilgrim alchemist healer captain
    sailor marsh_villager king imperial_soldier`.
  - Hostile looks: `bandit bandit_archer necromancer deserter cultist pirate
    dominion_soldier`. Each
    carries `looks[look].hostile_suggested: true`, and the list is in
    `characters.json:hostile_looks_suggested`. It is a suggestion, like every
    gameplay field here. A human enemy is an ordinary person: it attacks with
    what it holds (`bandit` and `deserter` use `attack`, `bandit_archer`
    `shoot`, `necromancer` and `cultist` `cast`), and it **lies dead; it does
    not `poof`**.
  - Any look can go on any NPC body.
  - Items not made for that body are listed under `not_available_for_body` and
    skipped.

These lists use the body's `default_tone` skin. Swap the skin by replacing the
`…/body_<default>_…` and `…/body_<default>-near_…` entries with the same names
for another tone. Everything else is unchanged.

**Hair colour** swaps the same way. `hair` and `beard` are drawn in the body's
`default_hair_color`; `hair_<colour>` and `beard_<colour>` are the *same
drawing* (same locks, same z, same bands, same states) in each of
`characters.json:hair_colors` — `black brown chestnut red blonde grey white`.
Replace the `…/hair_…`, `…/hair-back_…` and `…/beard_…` entries with
`…/hair_<colour>_…`, `…/hair_<colour>-back_…` and `…/beard_<colour>_…`. A body's
own list is `hair_colors` on its record. Every hat that hides `hair` hides
every `hair_<colour>` too. Two things do **not** follow the swap, and are best
avoided on a recoloured head if it matters to you:
- the six hats in `characters.json:hair_peek_items` (`hat_wizard
  hat_wizard_blue hat_straw hat_feather bandana_red cap_jester`) draw a lock of
  the wearer's hair under the brim *in their own strip*, in the default colour;
- eyebrows are part of the skin strip and stay the default colour.

### 4.2 General path: compose any outfit

```python
worn   = ["body_" + tone] + ["hair"] + (["beard"] if body.beard else []) + items   # or hair_<colour>, beard_<colour>
hidden = union(characters.json:hides[it] for it in worn)       # e.g. great helm hides hair, beard
layers = []
for it in worn, it not in hidden:
    if it not in accessories:   recs = body.pieces where rec.item == it     # heroes.json / npcs.json
    else:                       recs = accessories[it].bodies[body].values()  # skip if body missing
    for rec in recs: if facing in rec.files: layers.append((rec.z[facing], rec.piece, rec.files[facing]))
draw files in sorted(layers) order   # sort by (z, piece name)
```

The z order **changes per facing**. A cloak's back is under everything facing
down and over the body facing up; a sword in the right hand sits behind the
body facing left. So re-sort whenever the facing changes.
`tilekit.Kit.person_layers` is the reference, and it was verified pixel-identical
to the factory's own composer on all 1,600 (body × look × facing × frame)
samples.

Accessory record: `accessories[item]` → `{slot, hides:[items], hero_gear, bodies:{<body>:{<band>:{piece, z:{facing:int}, files:{facing:path}}}}}`.
- **Slots:** `body legs feet torso armor tabard cloak beard hair head mainhand offhand`.
- **Bands:** `main` (the item), `back` (what is behind the wearer: a cape,
  quiver or plait) and `near` (the arms and what is on them).

Accessories are **fitted per body**. Only use a file under that body's folder;
never draw one body's piece on another body.

**States:** people ship sixteen, each a 6-frame strip in all four facings
(`characters.json:states`): `idle walk attack hurt die shoot cast roll block
dodge cower cheer interact run flee talk`. **Every body ships every state for
every piece**, so any person can do any of them; who *should* is casting advice
in `characters.json:use_suggested`.

| state | kind | what it is | engine does |
| --- | --- | --- | --- |
| `idle` | loop | standing, breathing | |
| `walk` | cyclic | a stride | moves the person |
| `run` | cyclic | a sprint: long stride, leaning in, arms pumping | moves them ~1.8× walk |
| `flee` | cyclic | running with both arms in the air | moves them ~1.6× walk, away |
| `talk` | cyclic | standing, one hand making the point | nothing; the listener stays `idle` |
| `attack` `shoot` `cast` | one-shot | the three attacks | damage on `release_frame` |
| `hurt` | one-shot | a flinch | |
| `roll` | one-shot | tuck, somersault, come up | slides them ~2 tiles; cannot be hit mid-roll |
| `dodge` | one-shot | a hop back out of reach | slides them ~¾ tile backwards |
| `block` | one-shot, holdable | shield (or weapon) brought across the body | reduces or cancels a hit while it is up |
| `cower` | one-shot, holdable | crouched, arms over the head, shaking | |
| `cheer` | one-shot | a jump with both arms up | |
| `interact` | one-shot, holdable | bends and reaches down and forward | the thing is touched on `effect_frame` |
| `die` | one-shot, stays | falls and lies there | hold frame 5 |

Rules, the same as the monsters' (§3) except where said:
- **Cyclic states** (`characters.json:cyclic_states`: `walk run flee talk`) have
  no rest frame: loop one while its condition holds and cut to anything else on
  any frame. `tilekit.Kit.is_cyclic(state)`.
- **One-shots play once and return to `idle`.** Frame 0 of each is idle's rest
  pose and each ends back on it, so you can cut in on any idle frame.
- **Nothing in a strip travels.** A roll tumbles on the spot and a run runs on
  the spot, exactly as `walk` does; the engine moves the person.
  `characters.json:travel_suggested` gives a distance and the frames to spread
  it over: `roll` 2 tiles over frames 1–4, `dodge` 0.75 tile *opposite the
  facing* over frames 1–3, and `speed_vs_walk` for `run` (1.8) and `flee`
  (1.6). `invulnerable_frames` (`roll` 1–4, `dodge` 1–2) is the suggested
  window in which a blow misses. All of it is a suggestion.
- **Holding a state.** `characters.json:hold_frames[state] = [first, last]`
  (`block` 2–3, `cower` 2–4, `interact` 2–3). To keep a guard up, keep
  cowering or keep working at something: play frames 0..last, loop
  first..last for as long as it lasts, then play last+1..5 to stand back up.
  The loop is seamless on the global clock only if you step it yourself, so
  drive a held state from its own start time: `tilekit.Kit.person_frame(state,
  t, holding=True)` and `release_frame_after_hold(state, t_since_release)`.
- **`effect_frame[state]`** is the frame a state starts to count: `roll` 1 and
  `dodge` 1 (clear of the blow), `block` 2 (the guard is up), `interact` 2 (the
  hand is on the thing). It is to these what `release_frame` is to an attack.
- **A roll shrinks the person**, by up to 28%, around the middle of the body,
  and turns them through 360° over the six frames. Every layer does it
  together, so compose it like any other state. Y-sort by the same feet
  position throughout.
- **`block` needs no shield.** With one, the shield comes across the body;
  without, the weapon does, which reads as a parry. Empty-handed it is a
  braced guard.
- **Getting up is `die` backwards.** Play `die` from frame 5 to 0 for a
  knockdown recovery or a revive; it ends on the rest pose.
- **`die` plays once and stays down.** A person falls and lies on the ground
  from frame 5 on. Hold frame 5 for as long as the body should stay. **People
  never `poof`**: that is a monster-only state, and there is no person `poof`
  strip. Keep y-sorting the body by its feet; the fall stays inside the 64×64
  frame.
- **Which attack:** `characters.json:attack_state_by_item` maps a held item to
  its state: `bow` → `shoot`; `staff`, `staff_crystal`, `staff_orb`, `book`,
  `tome_dark` → `cast`. Anything else uses `attack`. Check the main hand first,
  then the off hand.
- **When it lands:** `characters.json:release_frame` is the frame that does the
  damage: `attack` 2, `shoot` 4 (the arrow leaves the string), `cast` 3 (the
  glow peaks). Spawn the projectile on that frame, of the type
  `projectile_by_item` names, from fx/ (§4.4).

Where the files are:
- Pre-resolved layers: `builds[build].states[state][facing]` (heroes) and
  `looks[look].states[state][facing]` (NPCs), the same shape as `layers`.
- Per piece: `pieces[piece].states[state][facing]`.
- Per accessory: `accessories[item].bodies[body][band].states[state][facing]`.
- File names: `<piece>_<state>_<facing>.png`. Idle stays `<piece>_<facing>.png`.

Compose a state exactly as idle (§4.2), taking every file from that state.
- **A piece missing from a state is not drawn in it.**
- **A one-handed weapon facing down changes band mid-swing.** At rest it is held
  behind the body, in `main`. While it swings it moves to the `near` band, over
  the body, so the blow is visible. Its `main` strip is empty on those frames, so
  just draw every listed layer and it comes out right. The same happens in
  `block`, `roll`, `cheer` and the other new states: a fully transparent frame
  in one band of a weapon is normal.
- **No canvas pad.** Every person strip is 64×64 a frame with no anchor. The
  lunge, the roll and the jump all stay inside the tile.

`tilekit.Kit.build_layers(body, build, facing, state)` is the reference.

### 4.3 Performance

A dressed person is 6–14 layers. For crowds, composite each (body, outfit,
facing) once into a 384×64 strip at load time and cache it. The layers share
the clock, so compositing whole strips is exact. Equipment changes invalidate
that cache entry only.

### 4.4 Ranged and magic: fx

`fx.json:fx[effect]` → `{files:{facing|"any": path}, directional, loops, speed?, from?, impact?}`.

- `arrow`, `bolt` (arcane) and `firebolt` are **projectiles**, shipped in four
  facings. `speed` is a suggested px/s at 1×; `from` is the state that throws
  it; `impact` is the effect to play on contact.
- `spark` is the **hit burst**. It has no facing: its file key is `any`.
- Every fx frame is 64×64, centred on the effect. Draw it at
  `(x − 32, y − 32)`.
- The engine moves a projectile. Its frames animate (the fletching flutters,
  the bolt crackles) but never translate. Spawn it on the shooter's
  `release_frame`, about 22 px above their feet, facing their facing. On
  contact, delete it and play `spark` once (frames 0–5) at the contact point.
- Projectiles have no ground shadow, because they fly at whatever height they
  were released from.
- Draw fx **after** the y-sorted ground layer (§5).

### 4.5 Icons: inventory pictures

`icons.json:icons[name]` → `{file, slot?, hides?:[items]}`. 124 icons, one
still 64×64 frame each — **no state, no facing, no footprint, never
animated, never placed in the world, never y-sorted.** This is UI-only art:
the picture in an inventory slot or shop listing, not a sprite.

- `slot` and `hides` are present whenever `name` is also a key in
  `accessories.json` (same `slot` vocabulary as §4.2: `mainhand offhand
  armor torso tabard cloak beard hair head legs feet body`) — which is all
  but the names in `icons_without_item`.
- `icons_without_item` (also mirrored at `catalog.json:categories.icons.
  without_item`) lists the icons that are not wardrobe items: `key`,
  `potion_health` and `potion_mana` (not worn; each has a dropped twin of the
  same name in `loot.json`, whose `icon` field points back here, §3.1),
  `chest` (the picture of the chest structure) and `skirt_purple` (an icon
  with no `wardrobe.py` garment behind it; the wardrobe only has
  `skirt_red`/`skirt_blue`/`skirt_green`, so treat it as not wearable).
- `tilekit.Kit.icon_image(name)` is the reference: it just opens `file`.

### 4.6 UI: parchment, slots, bars, scroll bar, status icons, minimap, cursors and handwriting

`ui.json`. Everything here is a still drawn in the same pencil as the world:
never animated, never placed in the world. **All text in the game is the
handwriting font below**; do not set a system font beside it.

#### Nine-slice pieces

`ui.json:pieces[name]` → `{file, size, corner, mid, use}`.

| piece | size | corner | mid | use |
| --- | --- | --- | --- | --- |
| `panel` | 96 | 24 | 48 | dialogue boxes, menus, inventory backgrounds |
| `button` | 48 | 12 | 24 | a button at rest |
| `button_hover` | 48 | 12 | 24 | the same button under the pointer or with focus |
| `button_pressed` | 48 | 12 | 24 | held down: no drop shadow; nudge the label 1 px down-right |
| `frame` | 64 | 16 | 32 | the portrait frame (§4.7) |
| `slot` | 72 | 12 | 48 | an inventory or hotbar slot, empty |
| `slot_selected` | 72 | 12 | 48 | the same slot, selected |
| `minimap` | 72 | 20 | 32 | the minimap's frame: **hollow** (see Minimap below) |

Each piece is a square of `corner + mid + corner` px. Cut it into nine with
two lines `corner` px in from each side (`ui.json:nine_slice`):

- corners: drawn once, unscaled;
- edges: **tiled** along their length, the last repeat cut short. Never
  stretch an edge: a stretched pencil line goes soft. The edge slices are
  drawn to repeat (the step across a repeat is smaller than the step between
  neighbouring pixels inside the slice);
- centre: flat paper, stretch or tile it.

The smallest box is `2*corner` square. Keep content `corner/2` px inside.
Godot: `NinePatchRect` or `StyleBoxTexture`, all four margins = `corner`, both
axis stretch modes = Tile. `tilekit.Kit.ui_box(name, w, h)` is the reference.

#### Slots

`ui.json:slots` → `{rule, empty, selected, icon_offset}`. A slot at its drawn
size, 72×72, holds one 64×64 icon (§4.5) at `icon_offset` `[4, 4]`. Selecting
a slot swaps `slot` for `slot_selected`; the icon never moves. Lay a hotbar
out as slots side by side. `tilekit.slot(icon, selected)` is the reference.

#### Bars

`ui.json:bars` → `{rule, tracks, fills}`. `tracks.bar` →
`{file, w, h, cap, mid, inset:[left, top, right, bottom], use}`;
`fills.health | stamina | mana` → `{file, w, h, use}`.

1. The track is three slices along x: `cap` px, a `mid` that **tiles**, `cap`
   px. It is `h` px tall and never scaled in y. A bar W px wide is the left
   cap, `mid` repeated over `W - 2*cap` px (the last repeat cut short), the
   right cap.
2. The fill goes inside the track's `inset`: at 100% it is
   `inner_w = W - left - right` px wide and starts at `(left, top)`.
3. Tile the fill from the left and cut it at `round(inner_w * fraction)`. The
   fill is opaque and tiles on x; its right end is a plain cut.
4. A number or label on a bar is `hand_22` in `chalk` over a fill, in `ink`
   over the empty track.

`tilekit.bar(fill, fraction, w)` is the reference.

#### Scroll bar

`ui.json:scroll` → `{rule, track, thumb}`. `track` →
`{file, w, h, cap, mid, inset:[left, top, right, bottom], use}` (16 px wide,
`cap` 8, `mid` 16, `inset` `[3, 4, 3, 4]`); `thumb` → `{file, w, h, cap, mid,
use}` (10 px wide, `cap` 5, `mid` 8). It is the bar turned upright:

1. Track and thumb are each three slices along **y**: `cap` px, a `mid` that
   **tiles** downward, `cap` px. Neither is ever scaled in x; the smallest of
   either is `2*cap` tall.
2. The thumb goes inside the track's `inset`, at `x = track_x + left`. For a
   track H px tall it travels `travel = H - top - bottom` px.
3. `thumb_h = max(2 * thumb.cap, round(travel * visible / total))` and
   `thumb_y = track_y + top + round((travel - thumb_h) * scroll)`, `scroll`
   from 0 (top) to 1 (bottom).
4. There is one thumb: no hover or pressed picture, and no arrow buttons.
   Vertical only. Do not rotate it for a horizontal bar; the shading would
   run the wrong way.

`tilekit.scroll(h, visible, total, scroll)` is the reference.

#### Status icons

`ui.json:status` → `{rule, effects}`; `effects[effect]` →
`{file, w, h, use, good, chip, color}`. Twelve 24×24 stills, one per effect,
for a row over a health bar or beside a portrait:

| effect | `good` | glyph | `color` |
| --- | --- | --- | --- |
| `poison` | false | a skull | `pencil_green_dark` |
| `burn` | false | a flame | `pencil_orange` |
| `freeze` | false | a snowflake | `pencil_blue` |
| `stun` | false | stars | `pencil_yellow` |
| `bleed` | false | a drop, and one falling after it | `pencil_red` |
| `slow` | false | an hourglass | `pencil_brown` |
| `curse` | false | an eye | `pencil_purple` |
| `silence` | false | a speech bubble, struck out | `skin_peach` |
| `sleep` | false | a crescent moon and a Z | `pencil_blue_dark` |
| `haste` | true | a fast-forward mark | `pencil_teal` |
| `shield` | true | a shield | `pencil_stone_dark` |
| `regen` | true | a plus | `pencil_green` |

- **`good`** says whether the effect helps whoever has it. A harm sits on a
  round chip and a help on a squared one (`chip` is `"round"` or
  `"square"`), so the two are told apart before the glyph is read and without
  colour. Poison and regen are both green, freeze and sleep both blue: never
  key on `color` alone.
- Draw them at 1× or a whole multiple, never a fraction. `tilekit --demo`
  lays the row out at a 28 px pitch.
- They are not inventory icons (§4.5, 64×64) and do not go in a slot. A
  stack count or a timer is `hand_22` beside or under the icon.

`tilekit.status_icon(effect)` is the reference.

#### Minimap

`ui.json:minimap` → `{rule, frame, markers}`. `frame` names a nine-slice piece
(`"minimap"`), and that piece carries three more fields:
`pieces.minimap` → `{…, hollow: true, border: 13, map_inset: 7}`.
`markers.player | quest` → `{file, w, h, hotspot:[x, y], use}`, 16×16.

1. The frame is a nine-slice like any other whose **centre is empty**. Draw
   the map first, into the box shrunk by `map_inset` px on every side; then
   the markers; then the frame over both, with nothing in the centre (Godot:
   `NinePatchRect.draw_center = false`).
2. The frame is opaque from `map_inset` px in, so it covers the map's cut
   edge with no gap, and along an edge its ink ends `border` px in. The
   corners cover more (a compass in the top right, a stud in each of the
   other three), all of it inside `corner`. Keep anything that must be seen
   `border` px inside the box, and `corner` px inside at the corners.
3. A box of `2*corner + k*mid` px (104, 136, 168…) ends on a whole repeat of
   the tick marks along its edges. Any other size cuts the last repeat short,
   as on every nine-slice.
4. A marker is a still: put its `hotspot` on the map position. `player` is an
   arrowhead drawn pointing north; rotate it about its hotspot to the facing.
   `quest` marks a quest or a point of interest and is not rotated.

What the map itself shows is the engine's: a render of the level scaled down,
or one flat colour per terrain. `tilekit.minimap(map_image, markers)` and
`tilekit.marker(name)` are the reference.

#### Cursors

`ui.json:cursors.cursors[name]` → `{file, w, h, hotspot:[x, y], use}`. 32×32
stills; `hotspot` is the pixel that points. Godot:
`Input.set_custom_mouse_cursor(texture, shape, hotspot)`.

#### Handwriting

`ui.json:fonts` → `{rule, chars, aliases, colors, faces, fonts}`;
`faces[face]` → `{fonts:[…], ttf, use, note}`; `fonts[name]` →
`{face, files:{ink, chalk}, fnt, use, cell_w, cell_h, pad, line_height, baseline,
cap_height, x_height, glyphs:{ch:{x, y, advance}}, kerning:{a:{b: px}}}`.

| font | face | cell | line_height | use |
| --- | --- | --- | --- | --- |
| `hand_22` | `hand` | 22 × 27 | 25 | body text: dialogue, labels, numbers |
| `hand_34` | `hand` | 31 × 39 | 37 | names and headings |
| `cute_22` | `cute` | 24 × 27 | 25 | a child's letter, a diary, a note pinned to a door |
| `cute_34` | `cute` | 31 × 39 | 37 | a name on a drawing, a title in the same diary |

Two hands. **`hand`** is the game's own voice, a printed pencil: every letter
is a few strokes with its own lean and size, so a line never sits quite
straight. **`cute`** is a middle-schooler's handwriting, legible first and
cute second: rounder bowls, a taller x-height, flicked feet on the stems and
fat round dots, written more upright and more evenly than `hand`. The two
share `line_height` and `baseline` at a size, so they can sit on one line (a
narrator in `hand`, a child's reply in `cute`).

Each font is a fixed-cell atlas, 16 columns, in two pencils with identical
strokes and alpha: **`ink`** for paper and **`chalk`** for anything dark.
`chars` is 468 characters: ASCII 32–126 first, in the cells it has always
had, then Latin-1, the Latin Extended-A letters of Polish, Czech, Slovak,
Hungarian, Turkish, Romanian and the Baltic languages, the usual typographic
marks (curly quotes, dashes, the ellipsis, €, ™), nine drawn symbols
(`← ↑ → ↓ ★ ♥ ♪ ✓ ✗`), then **monotonic Greek** and the **Cyrillic** of
Russian, Ukrainian, Belarusian, Bulgarian, Serbian and Macedonian, with `№`.
Cells are in the order of `chars` and a character added later goes on the
end, so a cell never moves: the first 303 are where they were. **Never
compute a cell from a code point**: read `glyphs[ch]`.

- **Drawing a line.** Start `pen_x` at the left and `line_top` at the top. For
  each character blit its whole cell (`cell_w × cell_h` at `glyphs[ch].x, .y`)
  to `(pen_x - pad, line_top)`, then `pen_x += glyphs[ch].advance`. Cells
  overlap by `2*pad`, so alpha-blend; never copy.
- A new line is `line_top += line_height`. `baseline` is the row of the
  writing line inside a cell; `cap_height` and `x_height` are measured up
  from it.
- **Kerning.** `fonts[name].kerning[a][b]` is whole px to add to the pen
  between `a` and the `b` that follows it: `pen_x += advance(a) +
  kerning[a][b]`. It is nearly always negative, an open pair drawn in (`AV`,
  `To`, `Гу`), and never more than a pixel or two. A pair that is not listed
  is 0, and most are not. Resolve `aliases` before looking a pair up.
  Skipping kerning is legal and only looser, but measure and draw the same
  way or wrapped text will not fit its box.
- A line's width is the sum of its advances and kerns. Wrap on spaces.
- **Never scale the atlas by a fraction.** Use the other size, or an integer
  multiple.
- **Looking a character up:** `glyphs[ch]`; if it is not there, `aliases[ch]`
  names the character drawn in its place (a no-break space is a space, the
  other hyphens and the minus sign are a hyphen); anything still not found is
  drawn as `?`. There is no CJK, no polytonic Greek and no right-to-left
  script.
- `fnt` is the same data as an AngelCode BMFont text file whose page is the
  ink atlas, aliases and kerning pairs included. Godot 4 imports it as a
  `FontFile` and kerns from it without help; for chalk, modulate the label or
  swap the page texture.
- **`faces[face].ttf`** (`ui/font/hand.ttf`, `cute.ttf`) is the same strokes
  as TrueType outlines, for what an atlas cannot do: an editable text field,
  another size, a rich-text box. It has the letters' shapes and wobble and
  not the pencil's grain, and one drawing of each letter, so prefer the atlas
  wherever its two sizes fit. 1000 units per em, capitals 600 tall: a 36 px
  font size matches the 22s and 56 px the 34s. It has all 468 characters and
  the same kerning pairs, as an OpenType `kern` feature and a legacy `kern`
  table, so a text engine kerns it on its own.

`tilekit.glyph(font, ch)`, `kern(font, a, b)`, `measure(text, font)`,
`wrap(text, width, font)` and `text(text, font, color)` are the reference;
`--demo` writes `demo_dialogue.png` and `demo_hud.png` with every piece above
in use, and `demo_handwriting.png` with both faces and a line of Cyrillic and
Greek.

### 4.7 Dialogue portraits

`portraits.json` → `{size:160, scale:4, frame:{piece, index, pad}, compose, bodies}`;
`bodies[body]` → `{source_crop:[x,y,w,h], pieces:{piece:{item, band, slot, z, file}}}`.
1,799 stills across the 12 bodies (142–157 each).

A portrait is the person **facing down, head and shoulders**, redrawn 4×
larger with a finer pencil, and layered exactly like the sprite, so it shows
whatever the character is wearing:

1. Take the worn items as in §4.2 (`body_<tone>`, the body's hair and beard or
   their `_<colour>` variants, then the accessories).
2. Apply `characters.json:hides` exactly as for the sprite.
3. For each item left, draw every entry of `bodies[body].pieces` whose `item`
   matches, sorted by `z` then piece name, bottom first, all at the same
   position. `z` is the sprite's down-facing z.
4. An item with no entry leaves no ink in the crop (boots, trousers) or is held
   in a hand (`mainhand`, `offhand` are never drawn in a portrait): skip it.
5. Framed: draw `ui` piece `frame` nine-sliced to `size + 2*pad` square
   (180), then the portrait at `(pad, pad)`.

- **Headgear only:** keep the slots `body`, `hair`, `beard`, `head` and the
  shoulders are bare. `slot` is on every piece for this.
- **The face is drawn for the portrait.** At 64 px a sprite's face is two
  eyes and a brow. The portrait's `body_<tone>` piece carries whites, iris,
  pupil, lids, a nose, lips, and each body's own marks (freckles, stubble,
  wrinkles, a scar), in every skin tone. Nothing else differs from the
  sprite, and the sprite itself is unchanged. It is all on the skin piece:
  there is nothing extra to layer.
- **Monsters that speak** (`portraits.json:monsters[name]` →
  `{file, source_crop}`) have **one** still, not a stack: the four lords,
  `ghorakhar`, `rangoskhar`, `ramulos`, `darkhorn`, each its down-facing idle
  frame 0 enlarged the same way. Frame it exactly like a person's.
  `tilekit.monster_portrait(name, framed=True)` is the reference.
- A portrait is a still. `source_crop` is the rectangle of the body's 64×64
  down-facing frame it enlarges; an engine that wants a breathing portrait can
  crop and scale the live sprite there instead (magnified, not re-inked).
- `tilekit.Kit.portrait_layers(body, items, tone, hair, slots)` and
  `portrait(..., framed=True)` are the reference.

---

## 5. Draw order for a frame

1. Terrain display grid: base + overlays per §2.2. It is opaque, so no clear is
   needed. Then wall-kit pieces (§2.5), on the logical grid.
2. Everything standing on the ground (structures, monsters, people), y-sorted
   by ground line (box bottom; a structure with `sort_y_px` uses that row
   instead, §2.4). Ties: x.
3. Flying states (`fly`) still sort by their ground shadow's line, which is the
   box bottom. Loot sorts with the ground layer too.
4. fx (projectiles, sparks) last, over everything.

Scale the final image by an integer factor with nearest-neighbour. UI (§4.6,
§4.7) is drawn after that, in screen space.

---

## 6. Regenerating (for an agent working in the factory repo)

```powershell
python tools\make_transitions.py --krita    # transition atlases (after changing transitions.py or a base terrain)
python tools\make_transitions.py --krita-missing   # paint only the edge textures that do not exist yet, rebuild the rest
python tools\make_walls.py                  # the wall kits, their joints and bonds (runs wallcheck, jointcheck, mixcheck, bondcheck)
python tools\paint_stills.py ui portraits   # the UI pieces, the font atlases and every portrait
python tools\make_font.py                   # the two .ttf faces from the same strokes (needs fonttools)
python tools\package_game.py                # rebuild game/ (copies only changed files; --clean to start over)
python game\reference\tilekit.py --demo <dir>   # smoke test: renders a map + checks composition paths agree
```

Adding content (a terrain, creature, item, state):
1. Paint it in the factory; `CLAUDE.md` covers the art side.
2. If it is a new terrain, add it to `transitions.ELEVATION`, `BASES` and
   `STYLES`, and to `TERRAIN_NAMES` in `package_game.py`. A new creature or
   prop goes in `CREATURE_NAMES` / `PROP_NAMES`.
3. Re-run `package_game.py`.
4. Update this file if any JSON field or rule changed, and bump
   `SCHEMA` in `package_game.py` (`kritatilefactory.game/N`) on a breaking change.
