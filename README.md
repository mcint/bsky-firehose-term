# Grand Aim
A semantically colored feed of bluesky skeets, for your perspective, someone else's or another group's.

## Intermediate goals so far
- [ ] Visualize bluesky data.
- [ ] Get color selection ergonomic for further development, 24-bit? 32-bit? color, the alpha paramter of colorama is quite useful
  - [ ] colorspace, hsla / hsl
  - [ ] Vary colors, find balance so nothing draws excessive attention, but noticeable, though gradual, color evolution occurs
- [ ] Get semantic clustering working -- static color
- [ ] Get sematic selection & filtering working, based on keywords, chosen posts
- [ ] Get db/profiles/queries/modes set up -- so every taste selection input can inform any future use
- [ ] Get a streaming web view working -- possibly even fully in-browser
  - fallen? twitterfall.com inspiration

# Run it
```
uv run --with websockets,colorama,munch,fire python3 bluesky-simple-print.py
```
