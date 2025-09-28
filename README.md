# FreeWil-IR

Initial commit.

FreeWili two-player demo
=========================

This repository contains two helper scripts that demonstrate how to build a
simple two-player game using FreeWili devices and IR communication.

Files
-----

- `game.py` — Dual-mode hardware runner
  - Runs both send-and-receive behavior simultaneously on a FreeWili device.
  - Polls local buttons; when a button press is detected it sends a challenge
    message (payload: `b'G' + idx`).
  - Listens for IR; when it receives a challenge (`b'G' + idx`) it lights the
    corresponding LED (best-effort) and replies with `b'R' + idx`.
  - Keeps the original example snippets (send and listen) available as
    `--example send` and `--example listen`.

- `two_player_game.py` — Minimal challenge/response demo with simulation
  - Provides a challenger/responder flow and a `--simulate` mode for
    development without hardware.
  - In simulation mode it prompts the user for keyboard input to emulate IR
    payloads and button presses.
  - Uses a small message format: `b'G' + led_index` for challenge and
    `b'R' + led_index` for response.

Quick start
-----------

Hardware (single device, dual-mode):
- Connect a FreeWili device and run on the device or a host that can talk to it:

```bash
python game.py
```

This will:
- Poll buttons and send a challenge whenever a local button is pressed.
- Listen for incoming challenges and respond automatically.

Hardware (original examples):
- Send a single IR packet (original example):

```bash
python game.py --example send
```

- Run original IR event listener:

```bash
python game.py --example listen
```

Simulation (no hardware required):
- Use the simulation script to iterate on game logic locally.

```bash
python two_player_game.py --simulate --role challenger
python two_player_game.py --simulate --role responder
```

Simulation mode accepts typed hex bytes for IR payloads and keyboard responses
for button presses. This helps debug the messaging and state transitions
without a physical device.

IR protocol
-----------

- Challenge: `b'G' + idx` where `idx` is a single byte (LED/button index)
- Response: `b'R' + idx`

These are intentionally tiny for clarity. For production you should:
- Add a device-id (so multiple games nearby don't collide)
- Add a sequence number or timestamp to avoid replay/duplicate issues
- Add a simple checksum or HMAC for integrity if needed

Notes and troubleshooting
-------------------------

- LED / button APIs: the code uses the public FreeWili APIs found in this
  workspace (`send_ir`, `set_event_callback`, `enable_ir_events`,
  `process_events`, `read_all_buttons`) and attempts to call a few likely
  LED helper names (`set_board_leds`, `setBoardLED`). If your runtime uses a
  different LED method or signature, update the call in `game.py`.

- If IR messages appear as `bytearray` or `list` rather than `bytes`, convert
  incoming payloads with `bytes(event_data.value)` before comparing.

- If you want fully independent concurrent behavior, convert the main loop
  to use threads (one thread to poll/send, one thread to respond) — the
  current implementation is cooperative and runs both duties sequentially in
  a single loop.

Next steps / improvements
------------------------

- Wire exact LED/button API names and signatures so lighting and button reads
  are robust and deterministic.
- Add device ID and sequence numbers to IR messages for reliability.
- Add scoring, round timers, and game-over logic (the scripts intentionally
  leave termination logic minimal).
- Convert button polling to event-driven callbacks if the runtime provides
  them.

Contact
-------

If you want me to wire specific LED or button APIs (or add device IDs to the
protocol), tell me the function names/signatures and I will update the
scripts accordingly.