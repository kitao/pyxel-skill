# Pyxel Cube

Cube renders a 3D scene into the Pyxel screen. For a first scene, find `cube/c01_hello_cube` in `pyxel_info.examples`. Read `pyxel://examples/cube/c01_hello_cube` or run its returned path. For a class's constructor and members, use `lookup_api` with a name such as `cube.Camera`.

## Put the scene on screen

- Import from `pyxel.cube`. Attach child nodes with `add_child`. A `Node` subclass calls `super().__init__()` and implements `on_update` or `on_draw` as needed. Call the scene root's `update()` once per game update. It also updates its children.
- Assign a `Camera` to the root. Position it with `Mat4.look_at(eye, target)`. Set `camera.clear_color` to fill the viewport or leave it as `None` to draw over existing pixels.
- Call `scene.draw(0, 0, pyxel.width, pyxel.height)` from the app's draw callback. It respects the target's 2D camera, clip, palette remapping, and dithering. Reset any settings that belong only to the world before drawing a screen-space HUD.
- Draw geometry inside a node's `on_draw`, for example `self.box(Mat4.IDENTITY, Vec3(8, 8, 8), 11)`. Cube uses +Y up, −Z forward, and degrees. Node transforms are parent-relative. Assign the result of a transform operation, since vectors, matrices, and quaternions are immutable.

If a moving node is missing on screen, inspect a numeric component such as `box.world_transform.pos.x` and a rendered frame at the same moment. Check the camera direction, viewport, and inherited visibility. A node's `visible` flag affects drawing while `active` controls updates, motions, and physics. For frame-rate work, measure the scene at the intended resolution on the target device.

## Import a model

The `cube/c04_mesh_and_motion` example shows how to load a self-contained GLB with `Mesh.from_glb`, create its tree with `Node.from_mesh`, and play a motion from the mesh. Reuse the loaded mesh when making more instances. Set the palette before import and pass the game's FPS to `Mesh.from_glb` so motion frames match playback speed.

Use part transforms for animation. Skinning, morph animations, and translucent BLEND materials have import or rendering limitations. For cutouts, use MASK. Check the model's silhouette, colors, and pose in a rendered game frame. The [Cube user guide](https://kitao.dev/pyxel/user-guide/cube/) describes the supported GLB features.

## Handle contacts

Start with `cube/c05_3d_collision` for a character or `cube/c06_3d_physics` for physical response. Give each moving body its own collider. Apply visual scaling to a child so the primitive collider and its ancestors retain translation and rotation only.

- Collider velocity is a world-space displacement per update. Mesh colliders serve as terrain. Zero mass affects contact resolution, and a non-mesh collider with assigned velocity can still move.
- In `on_collide(other, contact)`, use the supplied correction for the response your game needs. For solid contact, the suggested push-out is `contact.normal * contact.depth` in world space. Convert it to parent space when applying it to a local transform. The [Cube API reference](https://kitao.dev/pyxel/api-reference/cube/) documents velocity corrections as well.
- Use `trigger=True` for pickups or goal volumes. Contacts for the current update are already queued. Guard a one-time award and drive the player into the trigger to check both the effect and the score.
