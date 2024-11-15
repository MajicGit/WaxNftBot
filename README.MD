# Wax NFT Tipbot
Wax NFT Tipbot written in python.

## Features:
- Random drops for people active in chat (chatloot)
- Two drop commands to send drops to users from different wallets
    - Supports both sending claimlinks and users registering their wallet and receiving the drops directly.
- Daily trickortreat command for users to either get timed-out or a drop
- Command to generate atomichub collection book schema automatically for a collection
- Utility commands (random-active)
- utils library for interacting with wax blockchain

Documentation still WIP


## Setup 
- Requires python3 > 3.8
- Copy `example_settings.py` to `settings.py` and fill out
```
pip3 install -r requirements.txt
```
```
python3 bot.py
```

This Project was inspired by the [Green Wizard](https://github.com/crptomonkeys/greenwiz/tree/master) developed by Vyryn for cryptomonKeys.