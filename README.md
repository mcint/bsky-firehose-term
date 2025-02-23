# Grand Aim
A semantically colored feed of bluesky skeets, for your perspective, someone else's or another group's.

## Intermediate goals so far
- [x] Visualize bluesky data.
- [x] Read from jetstream
- [x] Extract interesting fields
- [x] Filter by commit/post type
- [x] Get color selection ergonomic for further development, 24-bit? 32-bit? color, the alpha paramter of colorama is quite useful
  - [x] colorspace, hsla / hsl
  - [x] Vary colors, find balance so nothing draws excessive attention, but noticeable, though gradual, color evolution occurs
        And, for ergonomic use to communicate meaning. Color for cluster / direction. Brightness, inverse to length, for ease of reading, uniformity of gestalt. Saturation for content searching versus scaffolding metadata. Errors in grey too.
- [ ] Get semantic clustering working -- static color. Faiss? enough?  Word2Vec? Queries?
- [ ] Get sematic selection & filtering working, based on keywords, chosen posts
- [ ] Get db/profiles/queries/modes set up -- so every taste selection input can inform any future use
- [ ] Get a streaming web view working -- possibly even fully in-browser
  - fallen? [twitterfall](https://twitterfall.com) inspiration. [hatnote's L2W](https://l2w.hatnote.com)

# Run it
```
uv run --with websockets,colorama,munch,fire python3 bluesky-simple-print.py
```

# What it looks like
![firehose screenshot](/res/Screenshot_20250222_162327.png)
