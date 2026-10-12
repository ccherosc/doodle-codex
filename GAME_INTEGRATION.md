# GAME_INTEGRATION.md

Audience: an AI agent or programmer wiring this art into a game engine.
Everything the engine needs is in `game/`. Nothing outside `game/` is needed at
runtime. `game/reference/tilekit.py` (Pillow only) implements every rule below;
when porting to an engine, port that file and the behaviour is right by
construction. Run `python game/reference/tilekit.py --demo OUT` to see a
rendered map with terrain, transitions, a structure, a monster and two heroes,
`demo_scene.png`: a walled yard built from the wall kit, a chest and two trees
with a person behind one crown and in front of the other trunk, and `demo_dialogue.png`: a nine-sliced panel, three framed portraits and the buttons.

Maintained by: `tools/package_game.py` builds `game/`, and this file is copied
there. **Whoever changes the package layout, a JSON schema, or a rule the engine
must follow updates this file in the same change** (see CLAUDE.md).

---

## 0. Invariants (true for every sprite)

| fact | value | source |
| --- | --- | --- |
| tile | 64 px, square | `catalog.json:tile` |
| frames per animation | 6 | `catalog.json:animation.frames` |
| playback | 10 fps (100 ms/frame) | `catalog.json:animation.fps` |
| strip layout | horizontal: frame `i` at `x = i*frame_w`, `y = 0` | all `*.png` except atlases |
| atlas layout | row = autotile mask 0..15, column = frame 0..5; 384×1024 | `terrain/transitions/**` |
| facings | `down`, `left`, `right`, `up` — every facing is its own file | `catalog.json:facings` |
| filtering | nearest-neighbour only; integer scale only | the pencil grain dies under bilinear |
| format | PNG RGBA, straight (non-premultiplied) alpha | |

**One global clock.** `frame = floor(seconds * 10) % 6`, the same value for
every sprite on screen: terrain, overlays, structures, monsters and every
paperdoll layer. Never give a tile or a layer its own phase. Transition overlays
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
  terrain/transitions/cliff/<terrain>.png         16x6 atlas, RGBA: a height step of one terrain (6 terrains)
  terrain/transitions/overlay_b|shore_b|scorch_b/<upper>.png   second-seed alternates of the three overlay kinds
  terrain/walls/walls.json                        the hand-placeable wall kits: pieces, doors, lookup, rule
  terrain/walls/<kind>/<label>.png                one still 64x64 cut-out: 47 labelled pieces per kind
  terrain/walls/<kind>/<door|gate>_<where>_<state>.png   a door or gate piece, closed and open
  structures/structures.json
  structures/<name>.png                           cut-out strip, frame = footprint*64
  structures/<name>_<state>.png                   the same frame in another state (open, raided)
                                                  (structures.json: `scale` = map landmark or person-scale)
  monsters/monsters.json
  monsters/<creature>/<state>_<facing>.png        cut-out strip, frame may be padded
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
  ui/ui.json                                      nine-slice parchment, slots, bars, cursors, fonts: every rule
  ui/<piece>.png                                  panel, button[_hover|_pressed], frame, slot[_selected] (nine-slice stills)
  ui/bar.png, ui/bar_fill_<what>.png              a bar's track and its health|stamina|mana fills
  ui/cursor_<name>.png                            32x32 pointers, with a hotspot
  ui/font/<font>_<ink|chalk>.png, <font>.fnt      the handwriting: fixed-cell atlases + BMFont files
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

**Elevation order** (low → high): `water < lava < ice < cave < ash < sand < desert < swamp < dirt < farmland < snow < roads < grass < forest < mountain < peaks < rock`
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
heights nothing changes. `cliff/<T>.png` exists for **grass, dirt, sand,
desert, snow and ash** and is laid out like an overlay (row = mask, where a
set bit is a corner on the *upper* level). It draws the upper level's ground,
a bank `cliff_face_px` (16) tall where the edge faces **south**, and a cast
shadow; the lower side is transparent, so a grass plateau stands on dirt or
sand as readily as on grass. Per display tile:

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

Limits, measured on the proofs and not to be designed around: only a
south-facing edge has a face. North, west and east edges are a rim line and a
soft shadow, which is correct for the camera and faint at 1x. There is **no
ramp or stair art**; where a unit may change height is the map's decision. A
cliff standing in water gets no foam. A terrain not in `transitions.cliff`
has no step (`tilekit` raises); for rock, build with the wall kit (§2.5). On
masks 6 and 9 the lower level joins, like every other terrain.
`tilekit.Kit.render_map(grid, frame, heights=...)` is the reference.

**Alternates: a second seed** (`transitions.alternates`). Optional. Each
`overlay`, `shore` and `scorch` atlas has a twin under `overlay_b/`,
`shore_b/`, `scorch_b/`: other strokes and another contour between the same
edge crossings, to break up a long border that would otherwise repeat every
64 px. Choose per display tile by a stable hash of its (x, y) (the reference
uses the variant hash `& 1`) and use that one choice for every layer of the
tile. Any mix is seamless: an alternate's outer 2 px ring is its primary's
pixels in every mask and frame. Pair and cliff atlases have no alternate.
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

`structures.json:structures[name]` -> `{file, footprint_tiles:[cols,rows], blocked_cells_suggested, passable, scale, frame_w, frame_h, loops, variant_of?, ground_suggested?, perch?, states?, solid_px_suggested?, sort_y_px?, walk_behind?}`.

Fifty-one structures:

| group | names |
| --- | --- |
| landmarks | `castle`, `tower`, `dungeon` |
| second designs | `castle_citadel`, `tower_wizard`, `dungeon_crypt` |
| towns | `town_hamlet`, `town_crossroads`, `town_market`, `town_village` |
| wayside | `windmill`, `ruins`, `graveyard`, `mine`, `camp`, `well`, `signpost`, `fence` |
| crossings | `bridge` (2x1, east-west), `bridge_ns` (1x2, north-south), `dock` (2x1) |
| great landmarks, 3x2 | `volcano`, `stronghold`, `city`, `castle_ruin` |
| great landmarks, 2x2 | `palace`, `bastion`, `fort`, `great_tree` |
| great landmarks, 2x1 and 1x2 | `ship`, `cave_mouth`, `sea_serpent`, `stilt_village` (2x1), `spires` (1x2) |
| great landmarks, added | `tower_legend`, `lighthouse` (1x2), `temple` (2x2), `mountain_fortress` (3x2) |
| local scale, outdoors | `tree_oak`, `tree_pine`, `tree_birch` (1x2), `chest` (1x1), `hut`, `house` (2x2), `inn` (3x2) |
| local scale, furniture | `table`, `shelf`, `barrel`, `crate`, `hearth` (1x1), `bed` (1x2) |

- **`scale` is `"map"` or `"local"`.** A map structure is a landmark on an
  overworld: a whole castle is two tiles wide and a person beside it is a
  marker. A local structure is drawn at a person's own scale (the hut's door is
  as tall as the people who use it) for a scene people walk around in. The
  thirteen in the last two rows are local; the other thirty-eight are map. Do
  not put a map building and a local building in one scene.
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
  `bridge_ns` and `dock`. Their `blocked_cells_suggested` is `[]`. Lay a bridge
  over water cells (`bridge` for a crossing that runs east-west, `bridge_ns`
  for one that runs north-south) and treat those cells as walkable; a `dock`
  runs out from a shore over water the same way. Draw a passable structure
  *under* the units on it rather than y-sorting it.
- `variant_of` names the structure this one is a second design of
  (`castle_citadel` -> `castle`, `tower_wizard` -> `tower`, `dungeon_crypt` ->
  `dungeon`). The footprints match, so a map can swap one for the other, by
  hand or by a hash of the cell.
- **The great landmarks are the named places of a world map**, two, four and
  six tiles each, for the zoomed-in map layer: one per place, not scattered.
  A six-tile one is 192x128 and stands on a 3x2 block of cells. They block
  their whole footprint and have no states.
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

**Structure states.** `states` is present on ten structures and maps a state
name to `{file, frame_w, frame_h, loops, label}`. `file` at the top level is
idle. A state's frame has the same size and position as idle's.

| state | on | loops | how to play it |
| --- | --- | --- | --- |
| `open` | `castle`, `castle_citadel` | `false` | Frame 0 is the closed gate: idle's frame 0, pixel for pixel (measured on both castles). Play 0->5 once and **hold frame 5**: the gate stays up. To close it, play the strip backwards. |
| `open` | `chest`, `hut`, `house`, `inn` | `false` | The same contract (frame 0 measured identical to idle's on each): the chest's lid tilts back on its rear hinge, one connected shape in every frame, onto gold; the door swings in. Hold frame 5; play backwards to close. An opened chest stays on frame 5. |
| `raided` | the four `town_*` | `true` | The settlement on fire. Swap it in for idle for as long as the raid lasts; it loops on the global clock. |

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
  "rule": "...", "door_rule": "...", "naming": {...}, "blocks": "...", "draw": "...",
  "kinds": { "<kind>": {
      "note", "inset_px": 8, "inset_px_by_side": {"n","s","e","w"}, "face_px",
      "gameplay_suggested": {...},
      "pieces": { "<label>": { "file", "wall_neighbours": [...], "open_sides": [...], "has_face": bool } },
      "doors":  { "<name>":  { "file", "replaces", "what", "state", "passable", "opening_px": [x0,y0,x1,y1] } },
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

  Kinds do not join each other: a `stone` cell beside a `timber` cell counts
  as not-wall for the other. `stone_low` and `timber` stand further in from
  their open sides than the rest (`inset_px_by_side`); they still block the
  whole cell.
- **Automatic placement.** For a wall cell, OR together `neighbour_bits` of the
  eight neighbours that are also wall (of the same kind), and draw
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
- `tilekit.wall_piece(wall, x, y, kind)`, `door_piece(piece, what, state, kind)` and
  `render_walls(img, cells, kind, doors)` are the reference.

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
      "loops": bool, "follows": null | "<state>", "cyclic": bool, "hover_px": number,
      "impact_frame": int,              // offensive states only (attack, cast, web, tongue, split, fire_breath,
                                        //   bubble, charge, spew, roar, ember, warcry, slam, roots)
      "facings": { "<facing>": { "file", "frame_w", "frame_h", "anchor": [ax, ay],
                                 "body_bbox": [x0, y0, x1, y1] } } } } }   // body_bbox: idle only
```

There are thirty creatures and twenty-six elites, 56 entries in all. Every
one has `idle, walk, attack, hurt, die, poof`. Signature states (the other
thirteen have none: `rat`, `goblin`, `wolf`, `orc`, `ogre`, three of the lords
and the five regional monsters below):
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
  breaking out of the ground ahead. All four are effects like `web`, impact
  frame 3. Measured reach past the idle ink, facing right: 20, 14, 26 and
  35 px. Facing down or up the `slam` and `roots` spread sideways across the
  whole 64 px frame instead (9-11 px and 5-6 px past the body each side);
- `bat` and `harpy` have `fly`;
- `skeleton`, `wraith` and `darkhorn` have `cast`;
- `spider` has `web`;
- `dragon` has `fly` and `fire_breath`.

**Elites.** Every creature but the four lords has an elite: `<creature>_elite`, with
`elite: true` and `elite_of: "<creature>"`. It is the same drawing in another
palette, shipped as its own strips, so no runtime recolouring is needed. Its
states, frame sizes, anchors, `impact_frame`s and tier are its base's, so it
can stand in for its base anywhere; what makes it stronger is the engine's
business. That includes the `ogre`, the `treant` and the `dragon`, whose
elites are as big as they are. Only the four lords have none. An elite's
*effects* are not recoloured: an elite imp throws the same orange coal.

**Regional rank and file.** `imp` (tier 1) is a small red horned devil with
bat wings, a coal-tipped tail and a fork, for volcanic and ashen ground;
`beastman` (tier 2) is a bull-headed, hooved soldier with a two-handed axe,
the foot soldier of the horned lords. Five more belong to a region each:
`serpent` (tier 1, a coiled desert snake) and `scorpion` (tier 2) for sand and
desert; `merrow` (tier 2), a fish-man with a trident who comes ashore, for
coasts and swamp; `frostshard` (tier 3), a hovering ice crystal, for snow and
ice; `ashfiend` (tier 3), an elemental of cinders, for ash and lava banks.
All seven are ordinary 1x1 creatures. The five regional ones have the six
common states and no signature.

**The lords.** `ghorakhar` (a horned warlord in black plate, spear),
`rangoskhar` (his horned reaver, poleaxe), `ramulos` (the lion lord,
greatsword) and `darkhorn` (a horned sorcerer, staff; `cast` is his ranged
attack, impact frame as listed) are named characters, `rank: "boss"`,
`tier: 5`, one tile wide and two tall like the ogre. They are monsters in
every mechanical sense, the same states, anchors and rules as the rest, and
like any creature they `poof` when killed; hold `die` frame 5 instead if the
story wants the body to stay. They are not paperdoll people: nothing they
wear can be swapped. Each has one dialogue portrait, a single picture rather
than layers (§4.7, `portraits.json:monsters`).

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
   frames 0→5 and ends back on the rest pose.
2. **Only enter a state on frame 0.** All strips run on the global clock. To
   start `attack` at an arbitrary moment, either wait for the next frame 0
   (≤ 0.5 s), or run that creature's one-shots on a *local* counter from 0 and
   return to the global clock afterwards. Both are safe because frame 0 is the
   rest pose.
3. `walk` and `fly` are **cyclic** (`cyclic: true`): frame 0 is mid-cycle, not
   the rest pose. Loop them while the activity lasts and switch back to `idle`
   at the end of a cycle. `fly` draws the body `hover_px` (17) above the ground;
   its shadow stays on the ground line, so the box does not move.
4. `die` does **not** loop: hold frame 5 (a corpse), or chain `poof`.
5. `poof` has `follows: "die"`. Its frame 0 is die's frame 5 pixel for pixel
   (verified on all 224 strips, anchors applied).
   The cloud is gone by frame 4. Frame 5 holds only a few fading sparkles
   (36–50 opaque px, measured on all 224 strips), and the dropped weapon and the
   shadow fade out with it. So when frame 5 ends, delete the entity; nothing
   pops. Never play `poof` without
   `die`.
6. `hurt` is designed to be played once per hit; `attack`, `cast`, `web`,
   `tongue`, `split`, `bubble`, `charge`, `spew`, `roar` and `fire_breath` once per use. They all end on the rest pose, so
   repeating them back-to-back is also clean.

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

**Impact frame:** `impact_frame` is the frame an offensive state's motion
peaks. It is 2 for every `attack`, and 3 for `cast`, `web`, `tongue`, `split`,
`bubble`, `charge`, `spew`, `roar` and `fire_breath`. Apply damage, spawn the projectile or play the hit sound on that
frame. Attack reach: the side the state's frame is padded on
(`frame_w/h` > box, and `anchor`) is where the strike goes.

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

### 4.6 UI: parchment, slots, bars, cursors and handwriting

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

#### Cursors

`ui.json:cursors.cursors[name]` → `{file, w, h, hotspot:[x, y], use}`. 32×32
stills; `hotspot` is the pixel that points. Godot:
`Input.set_custom_mouse_cursor(texture, shape, hotspot)`.

#### Handwriting

`ui.json:fonts` → `{rule, chars, colors, fonts}`; `fonts[name]` →
`{files:{ink, chalk}, fnt, use, cell_w, cell_h, pad, line_height, baseline,
cap_height, x_height, glyphs:{ch:{x, y, advance}}}`.

| font | cell | line_height | use |
| --- | --- | --- | --- |
| `hand_22` | 22 × 27 | 25 | body text: dialogue, labels, numbers |
| `hand_34` | 31 × 39 | 37 | names and headings |

It is a schoolchild's pencil hand: every letter is a few strokes with its own
lean and size, so a line never sits quite straight. ASCII 32–126 (`chars`),
16 columns, in two pencils with identical strokes and alpha: **`ink`** for
paper and **`chalk`** for anything dark.

- **Drawing a line.** Start `pen_x` at the left and `line_top` at the top. For
  each character blit its whole cell (`cell_w × cell_h` at `glyphs[ch].x, .y`)
  to `(pen_x - pad, line_top)`, then `pen_x += glyphs[ch].advance`. Cells
  overlap by `2*pad`, so alpha-blend; never copy.
- A new line is `line_top += line_height`. `baseline` is the row of the
  writing line inside a cell; `cap_height` and `x_height` are measured up
  from it.
- A line's width is the sum of its advances. Wrap on spaces.
- **Never scale the atlas by a fraction.** Use the other size, or an integer
  multiple.
- A character outside `chars` is drawn as `?`.
- `fnt` is the same data as an AngelCode BMFont text file whose page is the
  ink atlas. Godot 4 imports it as a `FontFile`; for chalk, modulate the label
  or swap the page texture.

`tilekit.measure(text, font)`, `wrap(text, width, font)` and
`text(text, font, color)` are the reference; `--demo` writes
`demo_dialogue.png` and `demo_hud.png` with every piece above in use.

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
python tools\make_walls.py                  # the wall kit (after make_transitions; runs wallcheck)
python tools\paint_stills.py ui portraits   # the UI pieces and every portrait (after changing ui.py, a body or the wardrobe)
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
