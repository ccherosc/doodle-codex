# Doodle Codex: full asset catalog

The art library for *Norfair Chronicles*, a real-time overhead action RPG (Godot 4, flat 2D, y-sorted): a world map for travel and local scenes for play. Everything is drawn in one pencil-doodle style on a 64x64 grid, animated as 6-frame horizontal strips at 10 fps (12 frames for a big creature's attack, walk, signature and death: read `frames` per state), in four facings (down, left, right, up) where a thing can turn.

This file is the text inventory. It is generated from the shipped game package, so the names here are the real asset names. Site: https://ccherosc.github.io/doodle-codex/

## How to look at the art without running the page

Each of these is a static PNG with every asset labelled:

- [Terrain: 20 bases then 88 variants (frame 0, 2x)](https://ccherosc.github.io/doodle-codex/sheets/terrain.png) (1666x1562)
- [Transitions: proof map 0: every terrain meeting its neighbours](https://ccherosc.github.io/doodle-codex/sheets/transition_map_0.png) (1280x896)
- [Transitions: proof map 1](https://ccherosc.github.io/doodle-codex/sheets/transition_map_1.png) (1280x896)
- [Transitions: proof map 2](https://ccherosc.github.io/doodle-codex/sheets/transition_map_2.png) (1280x896)
- [Transitions: one-cell diagonal paths stay continuous](https://ccherosc.github.io/doodle-codex/sheets/transition_diagonals.png) (1176x1888)
- [Transitions: pair: grass over water, 16 masks (shore)](https://ccherosc.github.io/doodle-codex/sheets/transition_pair_water__grass.png) (896x768)
- [Transitions: pair: roads and grass](https://ccherosc.github.io/doodle-codex/sheets/transition_pair_roads__grass.png) (896x768)
- [Transitions: pair: grass over lava (scorch)](https://ccherosc.github.io/doodle-codex/sheets/transition_pair_lava__grass.png) (896x768)
- [Transitions: pair: ash and snow](https://ccherosc.github.io/doodle-codex/sheets/transition_pair_ash__snow.png) (896x768)
- [Transitions: pair: rock over grass (dual-grid cliff)](https://ccherosc.github.io/doodle-codex/sheets/transition_pair_grass__rock.png) (896x768)
- [Transitions: cliffs: a height step in each of 15 terrains](https://ccherosc.github.io/doodle-codex/sheets/transition_cliffs_sheet.png) (1376x2444)
- [Transitions: cliff: grass plateaus over grass, dirt and sand](https://ccherosc.github.io/doodle-codex/sheets/transition_cliff_grass.png) (1536x1152)
- [Transitions: cliff wash: a step standing in water (foam) and in lava (char)](https://ccherosc.github.io/doodle-codex/sheets/transition_cliff_wash_sheet.png) (1376x4068)
- [Transitions: alternates: the same border in each of its four drawings](https://ccherosc.github.io/doodle-codex/sheets/transition_alternates.png) (784x3860)
- [Transitions: alternates: one coast with the primary only, and with all four mixed](https://ccherosc.github.io/doodle-codex/sheets/transition_alternates_map.png) (1304x478)
- [Transitions: cliff alternates: the same height step in each of its four drawings](https://ccherosc.github.io/doodle-codex/sheets/transition_cliff_alternates.png) (784x3004)
- [Interior wall kit: 55 labelled pieces, doors and windows (2x)](https://ccherosc.github.io/doodle-codex/sheets/walls_interior.png) (1390x1058)
- [Walls: interior: a yard, a maze and a line built from the kit](https://ccherosc.github.io/doodle-codex/sheets/walls_interior_demo.png) (1152x768)
- [Walls: interior: the pieces in place, labelled](https://ccherosc.github.io/doodle-codex/sheets/walls_interior_pieces.png) (1132x1062)
- [Rock wall kit: 51 labelled pieces, doors and windows (2x)](https://ccherosc.github.io/doodle-codex/sheets/walls_rock.png) (1390x1058)
- [Walls: rock: a yard, a maze and a line built from the kit](https://ccherosc.github.io/doodle-codex/sheets/walls_rock_demo.png) (1152x768)
- [Walls: rock: the pieces in place, labelled](https://ccherosc.github.io/doodle-codex/sheets/walls_rock_pieces.png) (1132x1062)
- [Stone wall kit: 59 labelled pieces, doors and windows (2x)](https://ccherosc.github.io/doodle-codex/sheets/walls_stone.png) (1390x1058)
- [Walls: stone: a yard, a maze and a line built from the kit](https://ccherosc.github.io/doodle-codex/sheets/walls_stone_demo.png) (1152x768)
- [Walls: stone: the pieces in place, labelled](https://ccherosc.github.io/doodle-codex/sheets/walls_stone_pieces.png) (1132x1212)
- [Stone_low wall kit: 47 labelled pieces, doors and windows (2x)](https://ccherosc.github.io/doodle-codex/sheets/walls_stone_low.png) (1390x890)
- [Walls: stone_low: a yard, a maze and a line built from the kit](https://ccherosc.github.io/doodle-codex/sheets/walls_stone_low_demo.png) (1152x768)
- [Walls: stone_low: the pieces in place, labelled](https://ccherosc.github.io/doodle-codex/sheets/walls_stone_low_pieces.png) (1132x912)
- [Timber wall kit: 59 labelled pieces, doors and windows (2x)](https://ccherosc.github.io/doodle-codex/sheets/walls_timber.png) (1390x1058)
- [Walls: timber: a yard, a maze and a line built from the kit](https://ccherosc.github.io/doodle-codex/sheets/walls_timber_demo.png) (1152x768)
- [Walls: timber: the pieces in place, labelled](https://ccherosc.github.io/doodle-codex/sheets/walls_timber_pieces.png) (1132x1212)
- [Walls: all five kits in one building: a butt joint wherever two materials meet](https://ccherosc.github.io/doodle-codex/sheets/walls_mixed_demo.png) (1408x1408)
- [Walls: the same kinds of wall bonded: the stronger kit keyed into the weaker one's face](https://ccherosc.github.io/doodle-codex/sheets/walls_bonds_demo.png) (1544x704)
- [Walls: bonds close up: a butt joint beside its bond, for each pair of kits](https://ccherosc.github.io/doodle-codex/sheets/walls_bonds_closeup.png) (1920x2352)
- [Structures: 78 props and their states (1x)](https://ccherosc.github.io/doodle-codex/sheets/structures.png) (1626x2402)
- [Monster slime: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_slime.png) (1606x896)
- [Monster rat: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_rat.png) (1606x896)
- [Monster bat: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_bat.png) (1606x1792)
- [Monster frog: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_frog.png) (1606x896)
- [Monster crab: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_crab.png) (1606x896)
- [Monster imp: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_imp.png) (1222x448)
- [Monster serpent: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_serpent.png) (1606x896)
- [Monster goblin: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_goblin.png) (1222x448)
- [Monster skeleton: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_skeleton.png) (1606x1792)
- [Monster wolf: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_wolf.png) (1606x896)
- [Monster boar: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_boar.png) (1606x896)
- [Monster zombie: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_zombie.png) (1222x448)
- [Monster harpy: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_harpy.png) (1606x1792)
- [Monster beastman: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_beastman.png) (1606x896)
- [Monster scorpion: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_scorpion.png) (1606x896)
- [Monster merrow: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_merrow.png) (1606x896)
- [Monster orc: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_orc.png) (1606x896)
- [Monster spider: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_spider.png) (1606x896)
- [Monster wraith: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_wraith.png) (1606x896)
- [Monster yeti: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_yeti.png) (1606x896)
- [Monster golem: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_golem.png) (1606x896)
- [Monster frostshard: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_frostshard.png) (1606x896)
- [Monster ashfiend: every state x 6 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_ashfiend.png) (1606x896)
- [Monster ogre: every state x 6 or 12 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_ogre.png) (2374x1344)
- [Monster treant: every state x 6 or 12 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_treant.png) (2374x896)
- [Monster dragon: every state x 6 or 12 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_dragon.png) (3910x1024)
- [Monster ghorakhar: every state x 6 or 12 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_ghorakhar.png) (3142x896)
- [Monster rangoskhar: every state x 6 or 12 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_rangoskhar.png) (3142x1344)
- [Monster ramulos: every state x 6 or 12 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_ramulos.png) (3142x1344)
- [Monster darkhorn: every state x 6 or 12 frames, facing right](https://ccherosc.github.io/doodle-codex/sheets/monster_darkhorn.png) (2374x896)
- [Monsters: 30 creatures by tier, then 30 elites (idle, facing down, 2x)](https://ccherosc.github.io/doodle-codex/sheets/monsters.png) (1872x2714)
- [People: 12 bodies, 9 skins, 7 hair colours (2x)](https://ccherosc.github.io/doodle-codex/sheets/people_bodies.png) (1390x554)
- [Hero builds: 2 heroes x 10 sets (2x)](https://ccherosc.github.io/doodle-codex/sheets/people_heroes.png) (1390x386)
- [NPC looks: 39 (2x), each on one sample body](https://ccherosc.github.io/doodle-codex/sheets/people_npcs.png) (1390x722)
- [People: every state as a 6-frame strip (hero in leather, 1x)](https://ccherosc.github.io/doodle-codex/sheets/people_states.png) (1192x882)
- [Wardrobe: 119 items, each alone on the hero body (2x) [slot]](https://ccherosc.github.io/doodle-codex/sheets/wardrobe.png) (1666x1730)
- [Dialogue portraits: a sample (1x). Any body x any outfit composes.](https://ccherosc.github.io/doodle-codex/sheets/portraits.png) (1340x710)
- [UI: nine-slice pieces sliced to a box, bars, cursors, status icons, scroll bar, minimap pins (2x)](https://ccherosc.github.io/doodle-codex/sheets/ui.png) (1860x2610)
- [Handwriting: two faces (hand, cute), two sizes, ink and chalk (1x)](https://ccherosc.github.io/doodle-codex/sheets/font.png) (1134x1186)
- [Loot (9), effects (4), icons (124) (2x)](https://ccherosc.github.io/doodle-codex/sheets/items.png) (1666x2066)
- [Ground decor (35) (2x)](https://ccherosc.github.io/doodle-codex/sheets/decor.png) (1666x554)
- [Scene: a local scene: walled yard, trees a person walks behind, chest, people](https://ccherosc.github.io/doodle-codex/sheets/demo_scene.png) (576x384)
- [Scene: a map assembled by the reference loader: terrain, transitions, structures, monsters](https://ccherosc.github.io/doodle-codex/sheets/demo_map.png) (896x640)
- [Scene: the same field without and with the decor layer: stones, flowers, logs and footprints off the grid](https://ccherosc.github.io/doodle-codex/sheets/demo_decor.png) (1296x448)
- [Scene: a dialogue box: nine-slice panel, composed portraits, handwritten text](https://ccherosc.github.io/doodle-codex/sheets/demo_dialogue.png) (890x262)
- [Scene: a HUD: bars, status icons, a minimap, a scrolling list, inventory slots, cursors, all from the package](https://ccherosc.github.io/doodle-codex/sheets/demo_hud.png) (640x236)
- [Scene: a grass plateau with a knoll and its flights: heights per cell, cliff atlases, alternates on](https://ccherosc.github.io/doodle-codex/sheets/demo_cliff.png) (640x448)
- [Scene: one cliff with the primary drawing only, and with all four mixed](https://ccherosc.github.io/doodle-codex/sheets/demo_cliff_alternates.png) (640x448)
- [Scene: the same step standing in water and in lava: foam and char at its foot](https://ccherosc.github.io/doodle-codex/sheets/demo_cliff_wash.png) (640x448)
- [Scene: five wall kits in one plan, joined where they meet](https://ccherosc.github.io/doodle-codex/sheets/demo_walls_mixed.png) (640x448)
- [Scene: the same plan with bonds in place of the joints](https://ccherosc.github.io/doodle-codex/sheets/demo_walls_bonded.png) (640x448)
- [Scene: both handwriting faces: accents, symbols, Greek, Cyrillic, kerned](https://ccherosc.github.io/doodle-codex/sheets/demo_handwriting.png) (470x240)
- [Scene: a street: two lamps (one dark), four trade signs, two stalls, windows in a stone and a timber wall](https://ccherosc.github.io/doodle-codex/sheets/demo_street.png) (704x384)
- [Scene: a room: a rug under the table, two windows in the interior wall, furniture](https://ccherosc.github.io/doodle-codex/sheets/demo_room.png) (448x256)
- [Scene: a river crossing a cliff edge by the waterfall](https://ccherosc.github.io/doodle-codex/sheets/demo_waterfall.png) (448x384)
- [Scene: every map-scale state beside its idle picture](https://ccherosc.github.io/doodle-codex/sheets/demo_landmark_states.png) (1568x952)
- [Scene: the map, animated: the ogre's blow takes twelve frames](https://ccherosc.github.io/doodle-codex/sheets/demo_map.gif) (896x640)
- [Scene: the local scene, animated](https://ccherosc.github.io/doodle-codex/sheets/demo_scene.gif) (576x384)
- [Scene: the street, animated: the lamp and the signs swing](https://ccherosc.github.io/doodle-codex/sheets/demo_street.gif) (704x384)
- [Scene: the waterfall, animated](https://ccherosc.github.io/doodle-codex/sheets/demo_waterfall.gif) (448x384)

The engine contract (file layout, JSON fields, autotile rule, paperdoll composition): [GAME_INTEGRATION.md](https://ccherosc.github.io/doodle-codex/GAME_INTEGRATION.md). Machine-readable summary: [catalog.json](https://ccherosc.github.io/doodle-codex/catalog.json).

## Counts

- terrain tiles: 108
- structures: 78
- creatures: 30
- elites: 30
- bodies: 12
- wardrobe items: 119
- NPC looks: 39
- icons: 124
- decor pieces: 35
- wall pieces: 259

## Known gaps (what the library does not have yet)

1. **The street is a first set.** One lamp, four trade signs (inn, smith, shop, healer), two stalls, one rug and one mat, beside two houses, an inn, six pieces of furniture and two floors. No bench, cart, fountain, notice board or washing line; no sign for a temple, a stable or a guild. A window sits in a south-facing wall only, on the stone, timber and interior kits: none in a side wall or at a corner, no shutter that closes, no stained glass. A bond between two wall kits lives in a face, on an east or west side: a boundary on a north or south side is still a butt joint, and the interior kit keys into nothing.
2. **Cliffs and stairs.** A height step has a drawn bank on its south-facing edge only; the north, west and east edges are a lit lip, a rim line and a shade. Fifteen terrains have a cliff; mountain, peaks, rock, water and lava do not, by design. The waterfall faces south, is one cell wide and one level tall, and nothing falls into lava. A flight climbs one level (16 px) or onto a stone wall (30 px); no other wall kit has one. Ramps are earth only: no sand or snow version.
3. **Landmarks.** Sixteen of the seventeen great landmarks have a state, and the ruin has none by design. Only the city has a second design (a timber town): no pirate ship, no second volcano or palace. The wayside props (bridge, mine, camp, well) have one design and no state.
4. **Monsters.** Twelve-frame animation covers the attack, walk, signature and death of the seven creatures bigger than a tile; their hurt, and every state of every smaller creature and every person, are six frames. Some elite effects keep the base's colours by nature (a web, a tongue, a war-cry, a howl, a thrown boulder). Monster portraits exist for the lords only.
5. **Portraits.** Stills, facing the viewer, one expression per body. No talking or blinking frames.
6. **UI.** The two handwriting faces cover Latin, monotonic Greek and Cyrillic (468 characters): no CJK, no polytonic Greek, no right-to-left script. The scroll bar is vertical only and has one thumb state. Twelve status icons; an effect outside that list has none.
7. **Faces.** Sprites keep two eyes and a brow at 64 px by design; all face detail is in the portraits.
8. **Terrain.** Farmland runs east-west or north-south, not diagonally. Borders come in four interchangeable looks; within 10 px of the drawn contour any two differ on 11 to 45 percent of pixels (mean 24), and where a border crosses the tile edge is fixed, so a border is varied, not unique. A cliff has four looks too, but its face is mostly its own hatching: any two differ on 11 to 14 percent of drawn pixels. Pair atlases have one look.
9. **Gameplay data.** Only suggested data ships: walkability per terrain, blocked cells, idle hurtboxes, impact frames, and for monsters a measured box per frame and a hit box per state. Those are boxes round ink, not designed colliders. People have no per-state boxes: a paperdoll's ink depends on what it wears.

## Terrain (20 terrains, 88 variants)

Seamless 64x64 tiles, 6 frames. Listed low to high in elevation (draw order).

| terrain | gameplay (suggested) | variants |
| --- | --- | --- |
| water | not walkable | shallows_lilies (lily pads, one in flower); shallows_rocks (rocks breaking the surface); shallows_reeds (reed beds with cattails); shallows_sandbar (a sandbar with foam); shallows_wreck (the ribs of a wrecked hull) |
| lava | not walkable, hazard burn | magma_crust (a wide plate of cracked crust); magma_vent (a spitting spatter cone); magma_rocks (basalt rocks in the flow); magma_whirl (a slow turning eddy); magma_obsidian (blades of obsidian); magma_bones (a charred ribcage and skull) |
| ice | walk x1.0, slippery | floe_hole (a fishing hole with a rod); floe_drifts (wind-carved snowdrifts); floe_rocks (snow-capped rocks frozen in); floe_ridge (a pressure ridge of heaved slabs) |
| cave | walk x1.0 | cavern_crystals (glowing crystal outcrops); cavern_stalagmites (tall stalagmites); cavern_pool (a still black pool with a drip); cavern_mushrooms (glowing fungus) |
| ash | walk x0.9 | cinders_stumps (three charred trunks); cinders_fissure (a glowing fissure); cinders_stones (black standing stones with a red rune); cinders_vent (a smoking fumarole) |
| sand | walk x0.85 | beach_shells (shells, a conch and a starfish); beach_ripples (wind ripples and a few pebbles); beach_tidepool (a tide pool with a starfish); beach_grass (tussocks of marram grass) |
| desert | walk x0.8 | dunes_cactus (saguaros and a barrel cactus); dunes_bones (a ribcage and a horned skull); dunes_rocks (red sandstone outcrops); dunes_oasis (an oasis pool with two palms); dunes_ruin (a half-buried colonnade) |
| swamp | walk x0.6 | bog_cattails (tall stands of cattails); bog_snag (a drowned dead tree); bog_lilies (open water with lilies); bog_toadstools (a toadstool ring and fireflies) |
| flagstones | walk x1.0 | flags_cracked (a slab broken across, a corner gone); flags_moss (moss in the joints); flags_grate (an iron drain grate); flags_worn (a sunk slab holding a puddle) |
| floorboards | walk x1.0 | planks_knots (knotty boards); planks_stain (an old dark stain); planks_patch (a new board let in and a loose one); planks_trapdoor (a trapdoor with an iron ring) |
| dirt | walk x1.0 | packed_rocks (stones, dry grass and cracks); packed_puddle (a rain puddle); packed_ruts (cart ruts and hoofprints); packed_scrub (dry thorn scrub) |
| farmland | walk x0.9 | furrows_wheat (rows of ripe wheat); furrows_pumpkins (a pumpkin patch); furrows_scarecrow (a scarecrow and a crow); furrows_cabbages (rows of cabbages) |
| farmland_ns | walk x0.9 | furrows_ns_wheat (files of ripe wheat); furrows_ns_pumpkins (a pumpkin patch); furrows_ns_scarecrow (a scarecrow and a crow); furrows_ns_cabbages (files of cabbages) |
| snow | walk x0.75 | snowfield_pines (snow-laden pines); snowfield_rocks (snow-capped boulders); snowfield_tracks (a line of footprints); snowfield_snowman (a snowman with a red scarf) |
| roads | walk x1.25 | cobble_moss (moss and weeds in the joints); cobble_worn (a missing stone and a cracked one); cobble_puddle (a rain puddle on the paving); cobble_leaves (autumn leaves in the joints) |
| grass | walk x1.0 | meadow_flowers (three drifts of wildflowers); meadow_wild (mixed wildflowers, clover, long grass); meadow_rocks (field stones and toadstools); meadow_stump (an old stump with toadstools); meadow_stones (a ring of standing stones) |
| forest | walk x0.7, blocks sight | canopy_pines (a stand of conifers); canopy_autumn (trees turning orange and gold); canopy_clearing (a glade with a fallen log); canopy_pond (a forest pool with a lily); canopy_deadwood (a blighted stand of bare trees); canopy_ruin (old stones in an overgrown glade) |
| mountain | not walkable, blocks projectiles, blocks sight | crags_high (one high snow-capped summit); crags_twin (two high peaks as a massif); crags_boulders (a rockfall of boulders); crags_cave (a cave mouth under a high peak); crags_tarn (a tarn in a stone bowl) |
| peaks | not walkable, blocks projectiles, blocks sight | summit_spire (one great spire); summit_glacier (a crevassed glacier tongue); summit_cairn (a cairn with a red pennant); summit_pines (snow-laden pines) |
| rock | not walkable, blocks projectiles, blocks sight | wall_moss (moss and grass in the hollows); wall_ore (seams of gold ore); wall_crack (a branching fissure); wall_crystals (teal crystals in the face) |

## Transitions (19 overlay, 19 shore, 18 scorch, 15 cliff atlases)

Corner-Wang (16 masks) on a dual grid; overlay per higher terrain, `shore` over water, `scorch` over lava. Elevation: water < lava < ice < cave < ash < sand < desert < swamp < flagstones < floorboards < dirt < farmland < farmland_ns < snow < roads < grass < forest < mountain < peaks < rock.

Cliffs (a height step within one terrain, heights per cell; a bank on the south-facing edge, a rim on the others, a wash atlas where the step stands in water or lava; the stairs_*, stairs_wood_* and ramp_* structures cross it, and `waterfall` carries water over it): ash, cave, desert, dirt, farmland, farmland_ns, flagstones, floorboards, forest, grass, ice, roads, sand, snow, swamp. Alternates: 3 more drawings of every overlay, shore, scorch and cliff atlas and of the cliff's two washes, seam-safe in any mix.


## Wall kits (5 materials x 47 pieces, 24 door and gate pieces, 12 windows)

For a wall cell, OR together neighbour_bits of the eight neighbours that are also wall cells, of any kind, and index `lookup` with the result. A diagonal neighbour only matters when both orthogonal neighbours beside it are wall; lookup already accounts for that. Draw the piece in the cell, y-sorted or on the ground layer above terrain.

A door or gate is a wall cell whose piece is swapped: where lookup answers a door's `replaces`, draw the door instead. Closed, it blocks like any wall. Open, the cell is walkable and the piece is drawn over whoever stands in it. Swap closed for open to open it; there is no strip.

A window is a wall cell whose piece is swapped, exactly as a door is: where lookup answers a window's `replaces`, draw the window instead. It always blocks, as the wall does. `state` is dark or lit: whether light comes through the glass at the viewer. seen_from outside (stone, timber), lit is a lamp indoors, for night; seen_from inside (interior), lit is daylight and dark is the night sky. glass_px is the pane, [x0, y0, x1, y1] in cell px, for an engine that adds its own glow. Only kits with a `windows` table have one.

Kits join with a butt joint. A wall cell of any kind counts as a neighbour when choosing a piece, so each kit runs to the edge of its own cell. Then, for each of the four sides where the neighbour is a wall of ANOTHER kind, draw this kind's joint over the piece: pieces[piece].joints[side] names it (a door uses its `replaces` piece's). Both cells of a boundary do this, each from its own kit. A joint lies inside its own cell and its own piece.

A bond is a joint with teeth, for two kits built as one wall: the stronger kit's blocks run a few px into the weaker one's face. To use it, where the join rule says to draw joint J on a side whose neighbour is of kind K, draw bonds[K][J] instead if it exists, and the joint if not. Both cells do this, each from its own kit. Bonds exist for east and west sides that show face; a north or south side, and any side with wall at its south corner, keeps its joint. Use bonds or joints for a whole wall, not a mix. Strength, weakest first: interior < timber < stone_low < stone < rock.

Naming: `single` = a lone pillar; `end_<side>` = the <side> end of a one-cell-wide wall; `straight_ns / straight_ew` = a one-cell-wide run; `bend_<corner>` = a one-cell-wide wall turning; <corner> is the outside of the turn; `corner_<corner>` = the <corner> corner of a solid block; `edge_<side>` = the <side> edge of a solid block (edge_s shows the face); `tee_<side>` = a one-cell-wide T; <side> is the side with no branch; `inner_<diagonal>` = solid, with the <diagonal> neighbour missing (an inside corner); `cross` = a one-cell-wide crossing; `solid` = interior: the top, no edge; `*_notch_<diagonals>` = the same piece with inside corners at those diagonals; `door_<where>_<state> / gate_<where>_<state>` = a door (18 px) or gate (38 px) in a south face; <where> is ew (replaces straight_ew) or edge_s (replaces edge_s); `window_<where>_<state>` = a window (13 px of glass) in a south face, dark or lit; <where> as for a door

Pieces (the same 47 labels in every kind): `single`, `end_w`, `end_s`, `end_n`, `end_e`, `bend_sw`, `corner_sw`, `bend_nw`, `corner_nw`, `straight_ew`, `corner_se`, `straight_ns`, `bend_se`, `corner_ne`, `bend_ne`, `edge_s`, `edge_w_notch_se`, `edge_w`, `edge_s_notch_nw`, `edge_s_notch_ne`, `tee_w`, `edge_w_notch_ne`, `tee_s`, `edge_n`, `edge_n_notch_sw`, `edge_n_notch_se`, `tee_n`, `edge_e`, `edge_e_notch_sw`, `edge_e_notch_nw`, `tee_e`, `solid`, `inner_sw`, `inner_se`, `solid_notch_se_sw`, `inner_nw`, `solid_notch_sw_nw`, `solid_notch_se_nw`, `solid_notch_se_sw_nw`, `inner_ne`, `solid_notch_ne_sw`, `solid_notch_ne_se`, `solid_notch_ne_se_sw`, `solid_notch_ne_nw`, `solid_notch_ne_sw_nw`, `solid_notch_ne_se_nw`, `cross`

- **interior**: face 36 px; doors and gates: `door_ew_closed`, `door_ew_open`, `door_edge_s_closed`, `door_edge_s_open`; windows: `window_ew_dark`, `window_ew_lit`, `window_edge_s_dark`, `window_edge_s_lit`
- **rock**: face 24 px; doors and gates: `door_ew_closed`, `door_ew_open`, `door_edge_s_closed`, `door_edge_s_open`; windows: none
- **stone**: face 30 px; doors and gates: `door_ew_closed`, `door_ew_open`, `door_edge_s_closed`, `door_edge_s_open`, `gate_ew_closed`, `gate_ew_open`, `gate_edge_s_closed`, `gate_edge_s_open`; windows: `window_ew_dark`, `window_ew_lit`, `window_edge_s_dark`, `window_edge_s_lit`
- **stone_low**: face 12 px; doors and gates: none; windows: none
- **timber**: face 28 px; doors and gates: `door_ew_closed`, `door_ew_open`, `door_edge_s_closed`, `door_edge_s_open`, `gate_ew_closed`, `gate_ew_open`, `gate_edge_s_closed`, `gate_edge_s_open`; windows: `window_ew_dark`, `window_ew_lit`, `window_edge_s_dark`, `window_edge_s_lit`

## Structures and props (78 props, 39 at a person's scale)

| name | tiles | scale | passable | states | description |
| --- | --- | --- | --- | --- | --- |
| castle | 2x2 | map |  | open | A keep behind a curtain wall, corner towers, a gatehouse, one banner. |
| tower | 1x2 | map |  |  | A watchtower: battered shaft, machicolated crown, one small pennant. |
| dungeon | 1x1 | map |  |  | A trilithon doorway into a rocky mound. Almost still; something blinks. |
| town_hamlet | 1x1 | map |  | raided | Two dwellings and a fence. The smallest settlement that reads as one. |
| town_crossroads | 2x1 | map |  | raided | Three buildings strung along a road: cottage, inn, barn. |
| town_market | 2x1 | map |  | raided | A hall and three stalls under awnings. The awnings are what move. |
| town_village | 2x2 | map |  | raided | Two rows of buildings, a well and a tree. The largest settlement. |
| bridge | 2x1 | map | yes |  | A humped stone bridge on two arches, seen from the side. |
| windmill | 1x2 | map |  |  | A whitewashed tower mill. The sails turn; nothing else does. |
| ruins | 2x1 | map |  |  | What is left of a temple: a wall end, a colonnade, one lintel still up. |
| graveyard | 1x1 | map |  |  | Five markers behind an iron railing, a fresh grave, and a wisp. |
| mine | 1x1 | map |  |  | A timbered adit into a hillside, with rails running out of it. |
| camp | 1x1 | map |  |  | A ridge tent and a fire. Somebody is nearby, or was a minute ago. |
| bridge_ns | 1x2 | map | yes |  | The same stone bridge, running north to south: you look along its deck. |
| dock | 2x1 | map | yes |  | A plank jetty on four piles, with a rowboat tied up at the end. |
| fence | 1x1 | map |  |  | A run of post-and-rail, one rail slipped. The edge of somebody's field. |
| well | 1x1 | map |  |  | A stone well under a little roof. The bucket swings; nothing else does. |
| signpost | 1x1 | map |  |  | A fingerpost with two boards and a crow on top of it. |
| castle_citadel | 2x2 | map |  | open | A sandstone citadel: one great round tower under a spire, two turrets. |
| tower_wizard | 1x2 | map |  |  | A mage's tower: it leans, the top is too big for it, the hat is bent. |
| dungeon_crypt | 1x1 | map |  |  | A little mausoleum: steps, two columns, a pediment, a way down. |
| tree_oak | 1x2 | local |  |  |  |
| tree_pine | 1x2 | local |  |  |  |
| tree_birch | 1x2 | local |  |  |  |
| chest | 1x1 | local |  | open | A banded chest. `open` swings the lid up and back on its rear hinge; frame 0 of `open` is the idle drawing, and an engine holds frame 5. |
| hut | 2x2 | local |  | open | A log hut with a door a person fits. `open` swings the door in on its left hinge; frame 0 is idle, and an engine holds frame 5 while it is open. |
| table | 1x1 | local |  |  | A plank table laid for one: a mug, a loaf and a candle. |
| bed | 1x2 | local |  |  | A bed with its head to the north wall, one tile wide and two long. |
| shelf | 1x1 | local |  |  | A dresser against the wall: books above, jars and a pot, a cupboard below. The back is dark so that what stands on the boards shows. |
| barrel | 1x1 | local |  |  | A coopered barrel standing on end. |
| crate | 1x1 | local |  |  | A slatted packing crate: raw planks in a frame, one diagonal brace. |
| hearth | 1x1 | local |  |  | A stone fireplace with a fire in it, against the north wall. |
| volcano | 3x2 | map |  | erupt | A fire mountain, six tiles: Hellfire Island, the Firebreak Peaks. |
| palace | 2x2 | map |  | raided | A palace of domes and minarets on its own rock, four tiles. |
| ship | 2x1 | map |  | moored | A two-masted ship under sail, two tiles: the sea lanes of the map. |
| stronghold | 3x2 | map |  | open | A black fortress of spires, six tiles: the Ghora'Khar Dominion. |
| city | 3x2 | map |  | open, raided | A walled city, six tiles: the Imperial Capital, Veylorn, LeManns. |
| city_timber | 3x2 | map |  | open, raided | A walled town of timber and thatch, six tiles: the second city. |
| castle_ruin | 3x2 | map |  |  | An abandoned castle on a crag, six tiles: DragonLock. |
| bastion | 2x2 | map |  | open | An iron works with walls on, four tiles: Coghollow Bastion. |
| fort | 2x2 | map |  | open, raided | A timber fort, four tiles: the Rogue Marches, the border states. |
| great_tree | 2x2 | map |  | raided | A tree that is a place, four tiles: Silver Arrow Woods, Draco Forest. |
| cave_mouth | 2x1 | map |  | sealed | A cave in a rock outcrop, two tiles: the Cave of Descendants. |
| sea_serpent | 2x1 | map |  | dive | A serpent breaking the surface, two tiles: here be monsters. |
| stilt_village | 2x1 | map |  | raided | Thatched huts on stilts over a marsh, two tiles: Poko, the Flooding Plains. |
| spires | 1x2 | map |  | awake | Needles of black glass, two tiles tall: the Obsidian Wastes, the Valley of Shadows. |
| house | 2x2 | local |  | open | A half-timbered cottage under red tiles, with a front gable. |
| inn | 3x2 | local |  | open | An inn, six tiles: two storeys, a hanging sign, a counter under an awning. |
| tower_legend | 1x2 | map |  | dark | The Tower of Legend, two tiles tall: a shaft that widens as it climbs. |
| lighthouse | 1x2 | map |  | dark | A lighthouse on its own rock, two tiles tall. The lamp is the animation. |
| mountain_fortress | 3x2 | map |  | open | A fortress built up the face of a mountain, six tiles. |
| temple | 2x2 | map |  | dark | A temple, four tiles: steps, a colonnade, a pediment, and a god at home. |
| stairs_s | 1x2 | local | yes |  | A stone flight down a bank that faces the viewer: treads and risers. |
| stairs_n | 1x2 | local | yes |  | The flight down the far side of a step: you look along it from above. |
| stairs_e | 2x1 | local | yes |  | The flight down a step's east flank. See `_stairs_flank`. |
| stairs_w | 2x1 | local | yes |  | The flight down a step's west flank. See `_stairs_flank`. |
| stairs_wood_s | 1x2 | local | yes |  | A plank flight down a bank that faces the viewer: `stairs_s` in wood. |
| stairs_wood_n | 1x2 | local | yes |  | The plank flight down the far side of a step: `stairs_n` in wood. |
| stairs_wood_e | 2x1 | local | yes |  | The plank flight down a step's east flank. See `_wood_flank`. |
| stairs_wood_w | 2x1 | local | yes |  | The plank flight down a step's west flank. See `_wood_flank`. |
| ramp_s | 1x2 | local | yes |  | An earth ramp down a bank that faces the viewer. No risers at all. |
| ramp_n | 1x2 | local | yes |  | The earth ramp down the far side of a step: you look along it. |
| ramp_e | 2x1 | local | yes |  | The earth ramp down a step's east flank. See `_ramp_flank`. |
| ramp_w | 2x1 | local | yes |  | The earth ramp down a step's west flank. See `_ramp_flank`. |
| stairs_wall_s | 1x2 | local | yes |  | A stone flight down the south face of a `stone` wall: twice `stairs_s`. |
| stairs_wall_n | 1x2 | local | yes |  | The flight down the north side of a `stone` wall: `stairs_n`, longer. |
| stairs_wall_e | 2x1 | local | yes |  | The flight down the east end of a stone wall. See `_wall_flank`. |
| stairs_wall_w | 2x1 | local | yes |  | The flight down the west end of a stone wall. See `_wall_flank`. |
| lamp | 1x2 | local |  | dark | A street lamp: an iron post on a stone foot, a lantern on a crook. |
| sign_inn | 1x2 | local |  |  | The tankard: somewhere to eat, drink and sleep. See `_shop_sign`. |
| sign_smith | 1x2 | local |  |  | The anvil: arms and armour, made and mended. See `_shop_sign`. |
| sign_shop | 1x2 | local |  |  | The purse and its coin: things bought and sold. See `_shop_sign`. |
| sign_healer | 1x2 | local |  |  | The red flask: potions and mending. See `_shop_sign`. |
| stall | 2x2 | local |  |  | A greengrocer's stall under a red awning. See `_stall`. |
| stall_wares | 2x2 | local |  |  | A pedlar's stall under a blue awning: pots and cloth. See `_stall`. |
| rug | 2x1 | local | yes |  | A long woven rug, two cells: a border, three lozenges, a fringe. |
| mat | 1x1 | local | yes |  | A round rag mat, one cell: a braid coiled out from its middle. |
| waterfall | 1x2 | local |  |  | A river over a south-facing step, one cell wide (`transitions.CLIFFS`). |

## Monsters (30 creatures, 30 elites, 211 states x 4 facings)

| creature | tier | rank | tiles | states | description |
| --- | --- | --- | --- | --- | --- |
| slime | 1 | normal | 1x1 | idle, walk, attack, hurt, die, split, poof | A dome of goo that squashes and stretches in place. |
| rat | 1 | normal | 1x1 | idle, walk, attack, hurt, die, pounce, poof | A rat seen from the front or from behind; `_rat_side` is its profile. |
| bat | 1 | normal | 1x1 | idle, walk, attack, hurt, die, fly, poof | Head-on, hovering, wings beating. |
| frog | 1 | normal | 1x1 | idle, walk, attack, hurt, die, tongue, poof | A giant frog: all mouth, two eyes on top, and legs folded like springs. |
| crab | 1 | normal | 1x1 | idle, walk, attack, hurt, die, bubble, poof | A crab: a wide shell on six legs, two eyes on stalks and one claw much too big for it. |
| imp | 1 | normal | 1x1 | idle, walk, attack, hurt, die, ember, poof | A goblin's worth of devil: horns up, wings out, a tail with a coal on it. |
| serpent | 1 | normal | 1x1 | idle, walk, attack, hurt, die, spit, poof | A marsh adder: two coils on the ground and a neck standing out of them. |
| goblin | 2 | normal | 1x1 | idle, walk, attack, hurt, die, bomb, poof | Head too big, ears too wide, knife too eager. |
| skeleton | 2 | normal | 1x1 | idle, walk, attack, hurt, die, cast, poof | Bone, so it barely boils - it is the one creature nearly as still as a wall. |
| wolf | 2 | normal | 1x1 | idle, walk, attack, hurt, die, howl, poof | A wolf seen from the front or from behind; `_wolf_side` is its profile. |
| boar | 2 | normal | 1x1 | idle, walk, attack, hurt, die, charge, poof | A boar seen from the front or from behind; `_boar_side` is its profile. |
| zombie | 2 | normal | 1x1 | idle, walk, attack, hurt, die, spew, poof | A zombie: a goblin's height and nobody home. Arms out, head on one side. |
| harpy | 2 | normal | 1x1 | idle, walk, attack, hurt, die, fly, poof | A harpy: yellow wings, bird legs, a pale face and a shock of blue hair. |
| beastman | 2 | normal | 1x1 | idle, walk, attack, hurt, die, warcry, poof | The Dominion's foot soldier: a bull's head on an orc's shoulders. |
| scorpion | 2 | normal | 1x1 | idle, walk, attack, hurt, die, venom, poof | A desert scorpion: a low plated body, two claws out in front, and a tail arched over all of it with a barb on the end. |
| merrow | 2 | normal | 1x1 | idle, walk, attack, hurt, die, tide, poof | A fish-man out of the surf: a fin crest on the skull, fins for ears, flippers for feet, a pale belly and a trident carried like a staff. |
| orc | 3 | normal | 1x1 | idle, walk, attack, hurt, die, cleave, poof | Shoulders first. An orc is a goblin that got the gym membership. |
| spider | 3 | normal | 1x1 | idle, walk, attack, hurt, die, web, poof | Eight legs, and the legs are the whole animal. |
| wraith | 3 | normal | 1x1 | idle, walk, attack, hurt, die, cast, poof | A hood with nothing in it, and a hem that never reaches the ground. |
| yeti | 3 | normal | 1x1 | idle, walk, attack, hurt, die, roar, poof | A yeti: a tile-filling heap of white fur with a blue face set into it. |
| golem | 3 | normal | 1x1 | idle, walk, attack, hurt, die, slam, poof | A golem: stacked grey blocks, two boulder fists and a rune that is lit. |
| frostshard | 3 | normal | 1x1 | idle, walk, attack, hurt, die, nova, poof | An ice elemental: one big crystal hanging in the air with two cold eyes in it, and four splinters hanging round it. Nothing touches the ground. |
| ashfiend | 3 | normal | 1x1 | idle, walk, attack, hurt, die, cinders, poof | An ash elemental: a whirling column of cinders rooted where it stands, two coals for eyes and two arms of smoke. |
| ogre | 4 | miniboss | 1x2 | idle, walk (12 frames), attack (12 frames), hurt, die (12 frames), hurl (12 frames), poof | 1x2. Twice a tile tall, and the height is the point. |
| treant | 4 | miniboss | 1x2 | idle, walk (12 frames), attack (12 frames), hurt, die (12 frames), roots (12 frames), poof | A treant: a walking trunk a tile wide and two tall, leaves for a head. |
| dragon | 5 | boss | 2x2 | idle, walk (12 frames), attack (12 frames), hurt, die (12 frames), fly (12 frames), fire_breath (12 frames), poof | 2x2. The one creature with four tiles to be drawn in. |
| ghorakhar | 5 | boss | 1x2 | idle, walk (12 frames), attack (12 frames), hurt, die (12 frames), charge (12 frames), poof | 1x2. Ghora'Khar, warlord of the Unlands: a black bull in bronze. |
| rangoskhar | 5 | boss | 1x2 | idle, walk (12 frames), attack (12 frames), hurt, die (12 frames), slam (12 frames), poof | 1x2. Rangos'Khar: a grey minotaur, white-maned, with an axe in both hands and horns that burn along their cracks. |
| ramulos | 5 | boss | 1x2 | idle, walk (12 frames), attack (12 frames), hurt, die (12 frames), roar (12 frames), poof | 1x2. Ramulos the Lion Lord, Ghora'Khar's rival: gold over navy, a mane wider than his shoulders and a small crown lost in it. |
| darkhorn | 5 | boss | 1x2 | idle, walk (12 frames), attack (12 frames), hurt, die (12 frames), cast (12 frames), poof | 1x2. Darkhorn, the horned sorcerer: a hood with nothing in it but two green lights, a spiked mantle, and a robe that reaches the ground. |

Elites (palette swaps, same states and frame counts as their base; what they throw is dyed from their own palette): slime_elite, rat_elite, bat_elite, frog_elite, crab_elite, goblin_elite, skeleton_elite, wolf_elite, boar_elite, zombie_elite, harpy_elite, orc_elite, spider_elite, wraith_elite, yeti_elite, golem_elite, serpent_elite, scorpion_elite, merrow_elite, frostshard_elite, ashfiend_elite, imp_elite, beastman_elite, ogre_elite, treant_elite, dragon_elite, ghorakhar_elite, rangoskhar_elite, ramulos_elite, darkhorn_elite


## People: heroes and NPCs (12 bodies, 9 skins, 7 hair colours, 16 states)

Paperdoll: body + skin + hair + wardrobe items, stacked by the engine. Bodies: hero, hero2, m_lanky, m_burly, m_portly, m_stocky, m_elder, f_slender, f_athletic, f_curvy, f_stout, f_elder. Skins: porcelain, fair, tan, brown, umber, deep, ash, sylvan, azure. Hair colours: black, brown, chestnut, red, blonde, grey, white. States: idle, walk, attack, hurt, die, shoot, cast, roll, block, dodge, cower, cheer, interact, run, flee, talk.

### Hero builds

| build | items |
| --- | --- |
| clothes | shirt_linen, trousers_brown, shoes, toy_sword, toy_shield |
| leather | shirt_linen, trousers_brown, jerkin_leather, boots, cap_leather, sword, buckler |
| ranger | tunic_green, leggings_leather, jerkin_ranger, boots, cloak_green, hood_green, bow |
| chain | gambeson, trousers_grey, hauberk_chain, boots, coif_chain, mace, shield_round |
| knight | gambeson, chausses_chain, hauberk_chain, boots, tabard_blue, helm_nasal, sword, shield_kite |
| plate | gambeson, greaves_plate, cuirass_plate, sabatons_plate, cloak_red, helm_great, longsword, shield_kite |
| battlemage | robe_blue, boots, mantle_mage, cape_purple, circlet_gold, staff_crystal, book |
| dragon | gambeson_red, greaves_dragon, cuirass_dragon, sabatons_dragon, cape_red, helm_dragon, sword_dragon, shield_dragon |
| dark | gambeson_black, greaves_dark, cuirass_dark, sabatons_dark, cape_tattered, helm_dark, sword_dark, shield_dark |
| light | gambeson_white, greaves_light, cuirass_light, sabatons_light, cape_white, helm_light, sword_light, shield_light |

### NPC looks (any look fits any body)

| look | hostile | items |
| --- | --- | --- |
| farmer |  | shirt_linen, breeches_tan, boots, hat_straw, pitchfork |
| smith |  | trousers_grey, boots, apron_leather, bandana_red, hammer |
| merchant |  | doublet_teal, trousers_blue, shoes, hat_feather, book |
| noble |  | doublet_purple, trousers_black, boots_tall, cape_red, circlet_gold, scimitar |
| guard |  | gambeson, trousers_brown, hauberk_chain, boots, tabard_red, helm_kettle, spear, shield_round |
| priest |  | robe_white, sandals, circlet_gold, staff, book |
| wizard |  | robe_purple, shoes, hat_wizard, staff_orb, tome_dark |
| monk |  | robe_brown, sandals, hood_brown, staff |
| innkeeper |  | dress_green, shoes, apron_white, headscarf_blue, lantern |
| barmaid |  | blouse_white, skirt_red, shoes, apron_white |
| jester |  | doublet_red, trousers_blue, shoes, cap_jester |
| bard |  | tunic_red, trousers_green, boots_tall, hat_feather, cape_purple, dagger |
| hunter |  | tunic_brown, leggings_leather, boots, hood_green, bow |
| sage |  | robe_grey, sandals, cane, lantern |
| queen |  | dress_purple, shoes, crown_gold, cape_red |
| villager |  | dress_blue, shoes, headscarf_blue |
| lady |  | dress_red, shoes, circlet_gold, cloak_blue |
| watchman |  | tunic_blue, trousers_black, boots, cap_leather, torch, axe |
| cultist | yes | robe_grey, sandals, hood_black, tome_dark, dagger |
| fisher |  | tunic_blue, breeches_tan, boots_tall, hat_straw, fishing_rod, basket |
| miner |  | shirt_linen, trousers_grey, boots, cap_leather, pickaxe, lantern |
| herbalist |  | tunic_green, skirt_green, shoes, hood_green, basket |
| baker |  | blouse_white, trousers_brown, shoes, apron_white, bandana_red, sack |
| shepherd |  | tunic_brown, breeches_tan, boots, cloak_brown, hat_straw, staff |
| courier |  | doublet_red, trousers_grey, boots_tall, cap_leather, sack |
| pilgrim |  | tunic_brown, trousers_brown, sandals, cloak_brown, hood_brown, cane, sack |
| alchemist |  | robe_blue, shoes, apron_leather, hat_wizard_blue, book |
| healer |  | robe_white, shoes, apron_white, headscarf_blue, basket |
| captain |  | gambeson, chausses_chain, hauberk_chain, boots_tall, tabard_red, cloak_blue, helm_nasal, sword, shield_kite |
| sailor |  | shirt_linen, trousers_blue, boots, bandana_red, sack |
| marsh_villager |  | tunic_green, breeches_tan, sandals, hat_straw, basket |
| king |  | doublet_purple, trousers_black, boots_tall, cape_red, crown_gold, longsword |
| imperial_soldier |  | gambeson_white, chausses_chain, hauberk_chain, boots, tabard_blue, helm_nasal, spear, shield_kite |
| pirate | yes | shirt_linen, trousers_black, boots_tall, bandana_red, cape_tattered, scimitar |
| dominion_soldier | yes | gambeson_black, trousers_black, hauberk_chain, boots, tabard_red, helm_great, axe, shield_round |
| bandit | yes | tunic_brown, trousers_black, jerkin_leather, boots, hood_black, scimitar, buckler |
| bandit_archer | yes | tunic_brown, trousers_black, jerkin_ranger, boots, bandana_red, bow |
| necromancer | yes | robe_black, boots, hood_black, staff_orb, tome_dark |
| deserter | yes | gambeson, chausses_chain, hauberk_chain, boots, cloak_brown, coif_chain, axe, shield_round |

### Wardrobe items by slot

- **tabard**: apron_leather, apron_white, tabard_blue, tabard_red
- **mainhand**: axe, bow, cane, dagger, fishing_rod, hammer, longsword, mace, pickaxe, pitchfork, scimitar, spear, staff, staff_crystal, staff_orb, sword, sword_dark, sword_dragon, sword_light, toy_sword
- **head**: bandana_red, cap_jester, cap_leather, circlet_gold, coif_chain, crown_gold, hat_feather, hat_straw, hat_wizard, hat_wizard_blue, headscarf_blue, helm_dark, helm_dragon, helm_great, helm_kettle, helm_light, helm_nasal, hood_black, hood_brown, hood_green
- **offhand**: basket, book, buckler, lantern, sack, shield_dark, shield_dragon, shield_kite, shield_light, shield_round, tome_dark, torch, toy_shield
- **torso**: blouse_white, doublet_purple, doublet_red, doublet_teal, dress_blue, dress_green, dress_purple, dress_red, gambeson, gambeson_black, gambeson_red, gambeson_white, robe_black, robe_blue, robe_brown, robe_grey, robe_purple, robe_white, shirt_linen, tunic_blue, tunic_brown, tunic_green, tunic_red
- **feet**: boots, boots_tall, sabatons_dark, sabatons_dragon, sabatons_light, sabatons_plate, sandals, shoes
- **legs**: breeches_tan, chausses_chain, greaves_dark, greaves_dragon, greaves_light, greaves_plate, leggings_leather, skirt_blue, skirt_green, skirt_red, trousers_black, trousers_blue, trousers_brown, trousers_green, trousers_grey
- **cloak**: cape_purple, cape_red, cape_tattered, cape_white, cloak_blue, cloak_brown, cloak_green, cloak_red
- **armor**: cuirass_dark, cuirass_dragon, cuirass_light, cuirass_plate, hauberk_chain, jerkin_leather, jerkin_ranger, mantle_mage

## UI and portraits (8 nine-slice pieces, 3 bar fills, 2 cursors, 4 fonts, portraits for 12 bodies and 4 lords)

Status icons (24x24 stills; harm on a round chip, help on a squared one): poison (harm), burn (harm), freeze (harm), stun (harm), bleed (harm), slow (harm), haste (help), shield (help), regen (help), curse (harm), silence (harm), sleep (harm). Scroll bar: an upright three-slice track and thumb. Minimap: the hollow nine-slice `minimap` drawn over the map, and the pins player, quest.

UI pieces: panel, button, button_hover, button_pressed, frame, slot, slot_selected, minimap. Bar fills: health, stamina, mana. Cursors: cursor, cursor_target. Fonts (handwriting, 468 characters: ASCII, Latin-1, Latin Extended-A, typographic marks, nine symbols, monotonic Greek and Cyrillic; kerning pairs per font: hand_22 3711, hand_34 3711, cute_22 2274, cute_34 2274; ink and chalk; faces hand, cute, each also a .ttf): hand_22, hand_34, cute_22, cute_34. Portraits compose for all 12 bodies from the worn items; the lords ghorakhar, rangoskhar, ramulos, darkhorn have one still each.


## Loot, effects and icons (9 drops, 4 effects, 124 icons)

Loot: gold, gem_ruby, gem_sapphire, gem_emerald, drop_sword, drop_axe, potion_health, potion_mana, key. Effects: arrow, bolt, firebolt, spark.

Icons by slot:

- **tabard**: apron_leather, apron_white, tabard_blue, tabard_red
- **mainhand**: axe, bow, cane, dagger, fishing_rod, hammer, longsword, mace, pickaxe, pitchfork, scimitar, spear, staff, staff_crystal, staff_orb, sword, sword_dark, sword_dragon, sword_light, toy_sword
- **head**: bandana_red, cap_jester, cap_leather, circlet_gold, coif_chain, crown_gold, hat_feather, hat_straw, hat_wizard, hat_wizard_blue, headscarf_blue, helm_dark, helm_dragon, helm_great, helm_kettle, helm_light, helm_nasal, hood_black, hood_brown, hood_green
- **offhand**: basket, book, buckler, lantern, sack, shield_dark, shield_dragon, shield_kite, shield_light, shield_round, tome_dark, torch, toy_shield
- **torso**: blouse_white, doublet_purple, doublet_red, doublet_teal, dress_blue, dress_green, dress_purple, dress_red, gambeson, gambeson_black, gambeson_red, gambeson_white, robe_black, robe_blue, robe_brown, robe_grey, robe_purple, robe_white, shirt_linen, tunic_blue, tunic_brown, tunic_green, tunic_red
- **feet**: boots, boots_tall, sabatons_dark, sabatons_dragon, sabatons_light, sabatons_plate, sandals, shoes
- **legs**: breeches_tan, chausses_chain, greaves_dark, greaves_dragon, greaves_light, greaves_plate, leggings_leather, skirt_blue, skirt_green, skirt_red, trousers_black, trousers_blue, trousers_brown, trousers_green, trousers_grey
- **cloak**: cape_purple, cape_red, cape_tattered, cape_white, cloak_blue, cloak_brown, cloak_green, cloak_red
- **other**: chest, key, potion_health, potion_mana, skirt_purple
- **armor**: cuirass_dark, cuirass_dragon, cuirass_light, cuirass_plate, hauberk_chain, jerkin_leather, jerkin_ranger, mantle_mage

## Ground decor (35 pieces)


## Ground decor (35)

Scattered per terrain (weights in `decor/decor.json`), or placed by hand:

- **cave**: drip, pebbles, rubble, rubble_b, crystals, stalagmite, bones, glowcaps
- **dirt**: puddle, puddle_b, puddle_pair, stones_b, pebbles, tuft, straw, footprints
- **flagstones**: pebbles, bones, straw
- **floorboards**: straw
- **forest**: log, log_bare, branch, stones, toadstools, fern, tuft, leaves, leaves_green
- **grass**: log, branch, stones, stones_b, pebbles, flowers, flowers_b, flowers_white, toadstools, tuft, tuft_b, leaves_green
- **placed by hand**: woodchips, timbers, rockfall, spoil, pick, horde_mark
- **water**: lilypads, reeds
