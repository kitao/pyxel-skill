# Pyxel Cube

Use for Pyxel 3D tasks. Cube is part of Pyxel 3 and renders in software to the same screen as 2D drawing. Follow the requested 2D or 3D style.

## API and examples

- Import Cube classes from `pyxel.cube`. Consult the [Cube user guide](https://kitao.dev/pyxel/user-guide/cube/) and [Cube API reference](https://kitao.dev/pyxel/api-reference/cube/) for supported behavior.
- `pyxel_info.cube_stubs_path` points to the installed Cube signatures. Its `examples` list includes Cube entries such as `cube/c01_hello_cube`. Read that example's source through `pyxel://examples/cube/c01_hello_cube`, and pass its returned absolute `path` to `run` so bundled assets resolve correctly.
- Start with `c01_hello_cube.py` for a scene, `c05_3d_collision.py` for character movement and contacts, or `c06_3d_physics.py` for collision response.

## Scene and drawing

- Subclass `Node`, call `super().__init__()`, and implement `on_update` and `on_draw`. Attach nodes with `add_child`. Call the root's `update()` once from the app's update callback and `draw(0, 0, pyxel.width, pyxel.height)` from its draw callback; do not separately update children already in that tree.
- Assign a `Camera` to the root and set `camera.transform = Mat4.look_at(eye, target)`. Use `camera.clear_color` to clear its viewport; `None` preserves the existing background. Draw the 2D HUD after the scene. `Camera.ortho_size` selects an orthographic view; `None` selects perspective.
- Cube uses a right-handed system: +Y is up and forward is -Z. Angles are in degrees. `Vec3`, `Mat4`, and `Quat` are immutable; assign the result of a transform operation. `translation * rotation` applies rotation first. Node transforms are relative to the parent; use `world_transform` when world coordinates are required.
- Draw primitives inside `on_draw`, such as `self.box(Mat4.IDENTITY, Vec3(16, 16, 16), 11)`. Positions and sizes are in 3D units; the root's drawing rectangle and 2D HUD use screen pixels. Assign `Shading(pyxel.colors)` to the root when shading is wanted.
- `active` gates updates, motion playback, and physics; `visible` gates rendering. Each also affects descendants. Hiding a node does not disable its collisions.

## Models and motions

- Load a self-contained GLB with `Mesh.from_glb(path)` and create its node tree with `Node.from_mesh(mesh)`. Load assets during setup and reuse meshes. Set `pyxel.colors[:]` before import so colors map to the intended palette.
- Cube supports triangle geometry and part transforms. Embed images and geometry in the GLB. Use part-based animation, as exported by Blockbench; skinning is not applied, and morph animations cannot be loaded. GLB cameras and lights are not used.
- Use `alphaMode: MASK` for cutout textures; `BLEND` translucency is not applied. Texture sampling clamps UVs to 0–1 and ignores glTF sampler wrap settings. Bake repeating textures into the image. See the user guide for material and transparency limits.
- Play a motion from `mesh.motions` on the node created from that mesh. Match `Mesh.from_glb(..., fps=...)` to `pyxel.init(..., fps=...)`, since GLB animation times are converted into frames.

## Collisions

- Give each moving node its own `Collider`; colliders hold velocity as well as shape. Use sphere, capsule, or box colliders for moving bodies, and a mesh collider for terrain. A mesh collider does not move under velocity or gravity.
- Collider velocity is displacement per update in world coordinates. Use `gravity=0` when code handles gravity, `mass=0` for fixed surfaces, and `trigger=True` for contact-only areas. Apply only translation and rotation to primitive collider nodes and their parents; put visual scaling on children.
- `on_collide(other, contact)` reports contact but does not automatically separate or bounce objects. Apply position and velocity corrections appropriate to the game. Contact normals and corrections are in world coordinates; convert them when a transformed parent requires it. Use the bundled collision or physics example as a starting point.
- Contact callbacks for an update are already queued. Guard one-time effects such as collecting an item; setting `active=False` does not cancel the remaining notifications for that update.

## Verification

- Use the existing `run` inputs, `until`, and screen snapshots. Inspect numeric paths such as `scene.camera.transform.pos.x` or `player.collider.velocity.y`; whole Cube objects become text representations. Expose derived gameplay values as app attributes when useful.
- Asset readers inspect image banks, tilemaps, and audio; they do not export a Cube scene or mesh. Check imported models, camera framing, occlusion, HUD readability, and motion in rendered frames. Exercise relevant collisions and transitions through input and state checks.
- `validate` recognizes selected Python/Pyxel patterns, not Cube scene correctness. Check a `cls_missing` warning against the actual camera clear behavior before changing the draw code.
- Software rendering and collision cost depend on scene complexity. For performance work, measure representative scenes at the intended resolution on the target device; headless correctness checks do not establish playable frame rates.
