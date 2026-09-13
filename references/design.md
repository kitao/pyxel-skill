# Design Defaults

Defaults for a game that should feel finished. Apply them when creating a new game or when asked to polish one; skip any that fight the request. Judge presentation from the inline frame, not from state.

## Scene

- Never leave the background solid black. A gradient, a star field, or a tiled floor is enough.
- Use three color levels from the 16-color palette: dark for background (0, 1, 5), mid tones for the environment (3, 4, 13), bright for what the player controls or wants (8, 10, 11). Finished games use 10 to 14 colors with clear roles.
- Keep HUD text legible with a one-pixel shadow or border, placed away from the busiest part of the play area.
- Give a title screen a pixel-art title, one animated element, the controls, and a blinking prompt.
- Draw 8x8 sprites with 3 or 4 colors and distinct silhouettes for player, enemies, and pickups.

## Feedback

- Give every player-visible event visible feedback: a `pal()` flash, particles, screen shake, or a brief size change. A state change without feedback reads as a bug.
- Give every event a sound: move, jump, hit, collect, clear, fail, start. The collect or clear sound matters most; make it bright and short.
- Let effects cut through music with square (`"s"`) or pulse (`"p"`) tones at volume 5 to 7; noise (`"n"`) alone is hard to hear. Keep effects on channel 3 and music on channels 0 to 2.
- Add parallax or scrolling to platformers and shooters; it is the highest-impact single technique.

## Flow

- Show the controls before the first input is needed.
- Make failure recoverable with one input from the game-over screen.
- Reach the first playable moment within a few frames of start; put long intros behind a key press.
