# news-image-20261124 — make.fun entry

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/mannamemmna/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/mannamemmna/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One 1024x1024 PNG that sums up the world's news of **Tuesday 24 November 2026**
as a dark newsprint front page: masthead, one hero story with a drawn
illustration, four story cards with vector glyphs, a bonus-news ticker.

## What it shows (all cross-checked in 2+ independent outlets)

- **HERO — AI & markets:** Nvidia reinstates Jensen Huang as CEO; Trump pressed
  the board; Nasdaq set to add ~$2 trillion; stock jumped as much as 36.6%
  (Reuters, Straits Times, The Standard HK, Euronews)
- **CLIMATE:** COP31 talks in Turkey collapse with no deal over fossil fuels —
  first blank since Copenhagen 2009 (BBC, AP, AFP, NPR)
- **NATO:** three Russian Kh-101 missiles landed in Poland; NATO sends AWACS
  (Reuters, AP, Al Jazeera)
- **UKRAINE:** sea drones sink Russian corvette *Merkury* at Benghazi, Libya
  (Reuters, BBC, NBC, Politico)
- **SPORT:** FIFA awards the 2031 Women's World Cup to US, Mexico, Costa Rica
  and Jamaica (FIFA, AP, US Soccer)
- **TICKER:** NATO vows space defence over a reported Russian nuclear satellite
  (BBC, France 24, NATO transcript)

## Run

```sh
python3 main.py                 # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=output python3 main.py   # writes ./output/entry.png
```

Python 3.13, stdlib + Pillow only. Fully deterministic: no network, no RNG,
no clock — identical bytes on every run.

## Files

- `main.py` — the generator (PIL shapes and text only)
- `output/entry.png` — the rendered entry, for the record
- `LICENSE` — MIT, author mannamemmna
