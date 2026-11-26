# Designing for the Pyxel screen

## Make the action playable

Choose an encounter that lets the player use the requested mechanic and see its consequence. In a delivery game, for example, put a parcel and a destination within reach and play one delivery before designing more streets. In an existing game, tune the encounter that prompted the request.

Set the logical resolution and sprite size together. When a hazard requires a timed response, divide the gap to the player at first sight by the closing speed in pixels per update. Play that interval at the game's configured FPS. Adjust the approach distance, speed, or warning cue if the player must act before they can read the threat.

## Draw for decisions

Look at an actual gameplay frame at native size. Can the player recognize the setting, locate their character, tell what they can interact with, and see where they can move? Give important objects distinct silhouettes and enough contrast against the busiest background they cross. Use the existing art and palette when extending a game.

Draw or refine small sprites such as 8×8 or 16×16 on the final pixel grid. When using an image generator for detailed artwork, specify the subject, final dimensions, and palette. Check the imported art at game size.

Check each part's size against the whole sprite in its intended pose and viewpoint. At integer zoom, follow the pixel steps along the silhouette. If the style uses a one-pixel outline, look for unintended thick spots. Compare revisions in the same scene at native size and check contact with surrounding objects where it matters.

For tiny animations, start with a readable key pose and reuse unchanged pixel groups. A shift of one pixel may convey the motion. Play the sequence at game speed. Can you read the action in a few poses? Do rigid parts stay attached and keep the proportions their motion and viewpoint imply?

Place the HUD where it can coexist with the action. If the camera scrolls, check the HUD while the world is moving. If the objective changes, show the next meaningful action at the moment it becomes available.

## Tune feedback in play

Tie feedback to the event that caused it. For a pickup, watch the frame before contact, the disappearance or animation, and the score change. Play the same encounter while holding the action button to catch accidental repeat rewards. When a game has a retry, play it after changing score, position, or inventory so stale state is visible. Choose the checks that fit the game's rules.
