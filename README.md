# blackjack
A functionally complete blackjack simulator written in pure Python.

<br>

<p align="center">
  <img src="./table.jpg" width="400">
</p>

## Installation

Clone the repository.

```
$ git clone git@github.com:ellisandrews/blackjack.git
```

Change directory.

```
$ cd blackjack/
```

Create a _python3_ virtual environment and activate it.

```
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Install the requirements.

```
$ pip install -r requirements.txt
```

## Game Modes

There are two different game modes that can be run:

#### 1. Interactive Mode

This mode launches an interactive CLI game for the user to play blackjack against an automated dealer. The user can either use a default configuration for quick-play, or they will be prompted to enter information to set up the game. The user plays against the dealer until they "cash out" or run out of money. All actions that could be taken at a real blackjack table are available, including splitting, doubling, insurance and more!

To launch the interactive game mode, run this script:

```
$ python play.py
```

The user can pass an optional `--default` flag to use the default game configuration instead of setting it up in-game.

#### 2. Simulation Mode

This mode allows the user to quickly simulate an arbitrary number of configurable games of blackjack. The user specifies a "strategy" to play (more on this later) and then runs it against an automated dealer. At the conclusion of the simulation, some basic analytics and charts are created for the user summarizing the results.

To launch the simulation game mode, run this script:

```
$ python simulate.py
```

This script exposes simulation configuration through several optional command line arguments:

| Flag | Help | Type | Default | 
|---|---|---|---|
| `-a`, `--auto-wager` | Initial gambler auto-wager amount | Float | `100.0` |
| `-b`, `--bankroll` | Initial gambler bankroll amount | Float | `1000.0` |
| `-c`, `--concurrency` | Number of game subprocesses to run simultaneously | Integer | `4` |
| `-d`, `--decks` | Number of decks per game | Integer | `3` |
| `-g`, `--games` | Number of games to simulate | Integer | `100` |
| `-s`, `--strategy` | Name of the gameplay strategy to use | String | `"default"` |
| `-t`, `--turns` | Max number of turns to play per game | Integer | `100` |

Note that there's even a progress bar while multiprocessing game simulations!

## Strategies

A `Strategy` is responsible for making in-game decisions. They can be found (and added!) in the `blackjack/strategies/` directory.

#### Implementation

All strategies must inherit from `BaseStrategy`, which is an [abstract base class](https://docs.python.org/3/library/abc.html) that lays out the methods that each `Strategy` must implement to make in-game decisions. Currently, there are two flavors of child `Strategy` classes:

1. `UserInputStrategy`
    - Inherits directly from `BaseStrategy`.
    - Prompts the user for a valid response for each in-game decision. 
    - Powers the "interactive" game mode.

2. `StaticStrategy`
    - Group of strategies that inherit from `BaseStaticStrategy`, which in turn inherits from `BaseStrategy`.
    - `BaseStaticStrategy` loads CSVs for static decision making into Pandas DataFrames.
    - Descendents of `BaseStaticStrategy` can implement the other required methods of `BaseStrategy` however they like.
    - Powers the "simulation" game mode.

#### Decision CSVs

`StaticStrategy` classes all use a common mechanism for making decisions about actions to take on a given hand (e.g. hit, stand, double, split). Specifically, they rely on three CSVs to be fed to them that outline these decisions (examples can be found in the `blackjack/strategies/csv/` directory). A user can edit the data in these CSVs however they like to construct a strategy, but they must follow the template. The three kinds of CSVs are:

1. `hard.csv` - Specifies actions based on the gambler's "hard" hand total (no Aces counted as 11).
2. `soft.csv` - Specifies actions based on the gambler's "soft" hand total (at least one Ace counted as 11).
3. `split.csv` - Specifies whether or not to split if the gambler's cards are of equal rank.

The header row of each CSV is the dealer's up card (meaning the card the dealer is showing). The first column of each CSV represents the gambler's hand. Thus, the action to take (the "decision") is found at the intersection of checking the gambler's hand and the dealer's up card, applying some logic to hierarchically check the three CSVs until a single action is decided upon.

CSVs named according to the above convention can be placed into their own directory under the aforementioned `csv/` directory and can be easily loaded by specifying the name of that directory in their `StaticStrategy` class definition.

## Analytics

Each instance of a blackjack game is set up to track a handful of metrics over its lifetime. Before exiting, both game modes print some simple analytics using these tracked metrics such as:

- Counts and percentages of hand outcomes (wins, losses, pushes, insurance wins).
- Maximum, minimum, and average bankroll amount.
- Gross winnings and percent change in bankroll.

In addition to the analytics summary, [matplotlib](https://matplotlib.org/) is used to create some basic charts visualizing the collected data.
