# Tennis Automated ATP Fantasy Weekly Model

## Objective
Publish one fantasy cheat sheet per ATP Fantasy tournament week that helps readers make faster lineup decisions than the field.

The page should answer five questions:

1. Who is the best `Bonus Ball` spend-up?
2. Which players project for the deepest runs?
3. Which players have scoring profiles that outperform simple ranking-based pricing?
4. Which popular names carry draw, fatigue, or fitness risk?
5. What changes after the official draw is released?

## Official ATP Fantasy Rules To Build Around

Source: ATP Tour, `ATP Fantasy: How to play, choose your team, win points & climb leaderboards`, published March 31, 2026.

- Managers get `100 credits`.
- Rosters use `6 starters` and `2 alternates`.
- Pricing is based on the `PIF ATP Live Rankings`.
- One player can be tagged as the `Bonus Ball` and scores `double points`.
- Managers receive `2 free switches` per tournament week.
- Unused free switches roll forward, up to `8`.
- Extra switches cost `50 fantasy points` each.
- Chips:
  - `Alternates`: alternate points count.
  - `Triple Bounce`: Bonus Ball scores triple.
  - `Swing Switch`: unlimited switches with no penalty.
- Bonus/penalty events:
  - `+2` per ace
  - `+10` straight-sets win
  - `+20` upset win
  - `-2` per double fault
  - `-10` for losing a set `0-6`
  - `-20` upset loss

## What Readers Care About

The page should not read like a generic tournament preview. Fantasy readers care about:

- `Ceiling`: who can realistically win the week.
- `Value`: who is underpriced relative to form, surface, or draw.
- `Floor`: who is likely to give at least one or two wins.
- `Bonus profile`: aces, straight-set potential, upset equity.
- `Fragility`: double faults, workload, injuries, retirement risk, rough draw paths.
- `Leverage`: who can separate a team from the obvious chalk.

## Weekly Page Structure

Use the same structure every week:

1. `Week snapshot`
2. `Rules that matter this week`
3. `Tournament slate`
4. `Best Bonus Ball candidates`
5. `Core plays`
6. `Value targets`
7. `Contrarian pivots`
8. `Trap list`
9. `Tournament-by-tournament notes`
10. `Late swap / draw update plan`
11. `Sources`

## Data Needed Each Week

### 1. Schedule and event mix
Use:

- ATP Tour calendar PDF
- ATP tournament overview pages

Needed fields:

- Week number
- Dates
- Tournament category
- Surface
- Draw size
- Number of concurrent events

### 2. Entry list and final draw
Use:

- ATP tournament preview articles (`history/draw/schedule`)
- ATP tournament overview pages
- ATP media notes / alpha lists
- Official draw pages once released

Needed fields:

- Confirmed field
- Seeds
- Byes
- Quarter placement after draw
- Qualifier and wildcard spots

### 3. Fantasy-specific pricing
Use:

- ATP Fantasy app
- ATP Tour ATP Fantasy articles

Needed fields:

- Player credit cost
- Starter vs alternate decision points

Note:
ATP explicitly states that player prices are based on the `PIF ATP Live Rankings`, so pricing can be estimated from rank before the market opens.

Officially confirmed examples from ATP coverage:

- `Rank 1` Carlos Alcaraz: `40`
- `Rank 2` Jannik Sinner: `36`
- `Rank 3` Alexander Zverev: `33`
- `Rank 4` Novak Djokovic: `30`
- Alejandro Davidovich Fokina was described by ATP as `8 coins` in the Monte-Carlo launch week

Operationally:

- Build a `rank -> estimated price` table from official examples and weekly observations
- Verify the exact prices in the ATP Fantasy app once the market opens
- Store both `estimated_price` and `official_price`

Important caveat:
ATP does not expose a public unauthenticated pricing endpoint. The fantasy API exists, but `players-list` is authenticated, so exact week-specific prices still need app verification unless ATP publishes the full schedule.

### 4. Ranking and form
Use:

- PIF ATP Rankings / Live Rankings
- ATP player profile pages
- ATP match reports
- ATP media notes

Needed fields:

- Current ranking
- 2026 win-loss
- Last 5 matches
- Recent titles / finals / semis
- Surface-specific performance notes

### 5. Scoring-profile stats
Use:

- ATP Stats pages
- ATP player profile stat widgets
- Match reports with Infosys ATP Stats callouts

Needed fields:

- Aces per match
- Double faults per match
- Straight-set win rate
- Service games won
- Break points saved / converted

### 6. Risk signals
Use:

- ATP news and match reports
- Tournament schedule pages
- Withdrawals / retirements on ATP coverage

Needed fields:

- Recent retirement or physical issue
- Heavy workload from previous week
- Surface transition
- Travel turnarounds

## Recommended Scoring Model

Score each player with a simple weighted model:

`Weekly Fantasy Score = Deep Run + Bonus Profile + Value + Leverage - Risk`

Suggested component weights:

- `Deep Run` 45%
- `Bonus Profile` 20%
- `Value` 20%
- `Leverage` 5%
- `Risk` 10%

### Component definitions

`Deep Run`
- Estimate expected rounds won from ranking tier, surface history, recent form, and draw strength.

`Bonus Profile`
- Favor players with ace volume, straight-set tendencies, and realistic upset-win paths.
- Penalize high double-fault players unless their upside is extreme.

`Value`
- Compare projected fantasy points to player credit cost.
- The best values are usually players whose ranking-based price lags their surface-specific level.

`Leverage`
- Tag obvious chalk separately from strong but less-discussed alternatives.

`Risk`
- Subtract for retirement concerns, Monte-Carlo fatigue, bad quarter placement, or unstable serving.

## Recommended Workflow

### Friday
- Publish `pre-draw edition`.
- Focus on likely core players, early values, and risk watch.

### Saturday after draw release
- Update:
  - Bonus Ball ranking
  - Draw winners / losers
  - First-round upset spots
  - Best six-man core

### Monday morning
- Post final swaps and chip notes.

## Spreadsheet Columns

Use one row per player with these columns:

- `week`
- `player`
- `tournament`
- `surface`
- `category`
- `ranking`
- `price`
- `seed`
- `draw_quarter`
- `last_5`
- `2026_record`
- `surface_note`
- `aces_score`
- `double_fault_risk`
- `straight_sets_score`
- `upset_score`
- `deep_run_score`
- `value_score`
- `risk_score`
- `final_rating`
- `tag`

Recommended tags:

- `Bonus Ball`
- `Core`
- `Value`
- `Pivot`
- `Trap`
- `Watchlist`

## Minimum Viable Weekly Production Stack

- `Official ATP pages` for schedule, fields, draws, results, rankings, and news
- `ATP Fantasy app` for prices
- `Spreadsheet or Airtable` for player scoring
- `Static HTML page` for publishing

## Sources

- [ATP Fantasy: How to play, choose your team, win points & climb leaderboards](https://www.atptour.com/en/news/atp-fantasy-2026-how-to-play)
- [ATP launches official fantasy game](https://www.atptour.com/en/news/atp-launches-official-fantasy-game-2026)
- [2026 ATP Tour calendar PDF](https://www.atptour.com/-/media/files/calendar-pdfs/2025/2026-atp-tour-calendar-december-2025.pdf)
- [ATP Daily Media Notes](https://www.atptour.com/en/media/daily-media-notes)
