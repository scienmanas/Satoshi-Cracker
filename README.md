# Satoshi Cracker

This script presents a brute force method to find a wallet with funds. Run this on your local computer or a dedicated VPS, who know you might get lucky.

## Motivation

I was scammed by a multi-sg wallet and lost $5, so thought try reviving that. But as well all know the size of prvate key is 256 bits, that is `115792089237316195423570985008687907853269984665640564039457584007913129639936`, pretty impossible to get someone's private key but whats wrong in trying.

## Setting Up

The project is very simple, follow the steps to run it:

1. Create environamt and activate it:
   ```
   python3 -m venv venv
   source venv/bin/activate  (bash terminals)
   ```
2. Configure `.env`,

| Variable | Description                   |
| -------- | ----------------------------- |
| EMAIL    | your email (for notification) |
| PASSWORD | your email password           |

   Addtionally change the recepient email to yours, otherwise I could get notified instead of you.

## Running

1. IInstall dependencies

   ```
   pip3 install -r requirements.txt
   ```
2. Run the script (last step)

   ```
   python3 main.py
   ```

   Done, congrats, lets bruteforce the world.

## Troubleshooting

APi used is https://blockstream.info, in future maybe it become paid or rate limited, once check this if you encounter any error.

## Additionals

The private key commented is compromised and have 0 funds but 1000 transaction. It can be used to test if api is working at that instant or not.
