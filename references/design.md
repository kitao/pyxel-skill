# Designing for the Pyxel screen

## Make the action playable

Choose an encounter that lets the player use the requested mechanic and see its consequence. In a delivery game, for example, put a parcel and a destination within reach and play one delivery before designing more streets. In an existing game, tune the encounter that prompted the request.

Set the logical resolution and sprite size together. At the intended speed, how long is a hazard visible before the player must react? Measure the distance from its first visible position to contact, in pixels, and divide by the closing speed in pixels per update. Play that interval at the game's configured FPS. Adjust the approach distance, speed, or warning cue if the player must act before they can read the threat.

## Draw for decisions

Look at an actual gameplay frame at native size. Can the player locate their character, tell what they can interact with, and see where they can move? Give important objects distinct silhouettes and enough contrast against the busiest background they cross. For sprite art, design the resting pose first and keep its identifying features legible across animation frames. Use the existing art and palette when extending a game.

Place the HUD where it can coexist with the action. If the camera scrolls, check the HUD while the world is moving. If the objective changes, show the next meaningful action at the moment it becomes available.

## Tune feedback in play

Tie feedback to the event that caused it. For a pickup, watch the frame before contact, the disappearance or animation, and the score change. Play the same encounter while holding the action button to catch accidental repeat rewards. When a game has a retry, play it after changing score, position, or inventory so stale state is visible. Choose the checks that fit the game's rules.
