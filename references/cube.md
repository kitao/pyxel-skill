# Pyxel Cube

Cube renders a 3D scene into the Pyxel screen. For a first scene, find `cube/c01_hello_cube` in `pyxel_info.examples`. Read `pyxel://examples/cube/c01_hello_cube` or run its returned path. For geometry built in code, see `cube/c03_custom_shapes`. For a class's constructor and members, use `lookup_api` with a name such as `cube.Camera`.

## Put the scene on screen

Choose a camera that shows what the player needs to judge. Play one interaction from that view at the intended resolution. For a jump, for example, can the player see the landing surface and tell when the character reaches it?

If a model blends into the background, try setting `outline` on its root node (Pyxel 3.0.4+). The palette index gives the group a one-pixel outline around its combined silhouette. Compare the moving model with and without the outline from the gameplay camera, especially where thin parts overlap.

- Import from `pyxel.cube`. Attach child nodes with `add_child`. A `Node` subclass calls `super().__init__()` and implements `on_update` or `on_draw` as needed. Call the scene root's `update()` once per game update. It also updates its children.
- Assign a `Camera` to the root. Position it with `Mat4.look_at(eye, target)`. Set `camera.clear_color` to fill the viewport or leave it as `None` to draw over existing pixels.
- Call `scene.draw(0, 0, pyxel.width, pyxel.height)` from the app's draw callback. It respects the target's 2D camera, clip, palette remapping, and dithering. Reset any settings that belong only to the world before drawing a screen-space HUD.
- Draw geometry inside a node's `on_draw`, for example `self.box(Mat4.IDENTITY, Vec3(8, 8, 8), 11)`. Cube uses +Y up, −Z forward, and degrees. Node transforms are parent-relative. Assign the result of a transform operation, since vectors, matrices, and quaternions are immutable.

If a moving node is missing on screen, inspect a numeric component such as `box.world_transform.pos.x` and a rendered frame at the same moment. Check the camera direction, viewport, and inherited visibility. A node's `visible` flag affects drawing while `active` controls updates, motions, and physics. For frame-rate work, measure the scene at the intended resolution on the target device.

## Import a model and play its motions

In `cube/c04_mesh_and_motion`, `Mesh.from_glb` loads the asset and `Node.from_mesh(mesh)` creates an instance. Reuse the mesh for other instances. If the project has a custom palette, set it before import. Check the model's silhouette and colors from the gameplay camera.

For an animated model, pass the game's FPS to `Mesh.from_glb` to preserve the authored timing. Find the desired clip in `mesh.motions` and call `actor.play_motion(clip)` on that mesh's instance when the action starts or changes. Each call restarts playback, and updating the scene advances it. Use `loop=False` for a one-shot action or `actor.apply_motion(clip, frame, loop=False)` to inspect a particular pose. Watch the motion from the gameplay camera through the loop or final pose.

When authoring an animated GLB, keyframe translation, rotation, or scale on separate nodes with pivots at their joints. Export triangles with embedded buffers and textures. Cube ignores skin deformation, rejects files with morph-weight animation, and skips all clips in files that use `KHR_animation_pointer`. For cutouts, use `MASK` and leave a palette index free for transparency. Materials using `BLEND` render opaque. The [Cube user guide](https://kitao.dev/pyxel/user-guide/cube/) gives the Blockbench export settings.

## Handle contacts

Start with `cube/c05_3d_collision` for a character or `cube/c06_3d_physics` for physical response. Give each moving body its own collider. Apply visual scaling to a child so the primitive collider and its ancestors retain translation and rotation only.

- Collider velocity is a world-space displacement per update. Mesh colliders serve as terrain. Zero mass affects contact resolution, and a non-mesh collider with assigned velocity can still move.
- In `on_collide(other, contact)`, use the supplied correction for the response your game needs. For solid contact, the suggested push-out is `contact.normal * contact.depth` in world space. Convert it to parent space when applying it to a local transform. The [Cube API reference](https://kitao.dev/pyxel/api-reference/cube/) documents velocity corrections as well.
- Use `trigger=True` for pickups or goal volumes. Contacts for the current update are already queued. Guard a one-time award and drive the player into the trigger to check both the effect and the score.
