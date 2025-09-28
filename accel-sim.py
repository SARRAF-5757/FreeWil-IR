import math
import time
from dataclasses import dataclass

from freewili import FreeWili
from freewili.framing import ResponseFrame
from freewili.types import EventType, EventDataType, AccelData, IRData

# LED constants
NUM_LED_SLOTS = 7

# Physics
ACCEL_LPF_ALPHA = 0.4
FRAME_DELAY_SEC = 0.01

# Sensitivity
DEADZONE_X = 1        # ignore small tilts
SENSITIVITY_X = 0.01

@dataclass
class AccelState:
    x: float = 0.0
    y: float = 0.0
    z: float = 1.0


# Globals updated by callback
latest_accel = AccelState()
running = True


def safe_set_led(device: FreeWili, led_index: int, r: int, g: int, b: int, retries: int = 3, backoff: float = 0.03) -> None:
    """Best-effort LED setter with small retries to avoid transient timeouts."""
    for _ in range(retries):
        try:
            res = device.set_board_leds(led_index, r, g, b)
            if res.is_ok():
                return
        except Exception:
            pass
        time.sleep(backoff)


def clear_leds(device: FreeWili) -> None:
    for i in range(NUM_LED_SLOTS):
        safe_set_led(device, i, 0, 0, 0)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def map_tilt_to_slot(ax: float) -> int:
    """Map X tilt to discrete LED slot across all LEDs."""
    if abs(ax) < DEADZONE_X:
        ax_adj = 0.0
    else:
        ax_adj = (abs(ax) - DEADZONE_X) * SENSITIVITY_X
        ax_adj = math.copysign(ax_adj, ax)
    ax_adj = clamp(ax_adj, -1.0, 1.0)
    t = clamp((ax_adj + 1.0) / 2.0, 0.0, 1.0)
    slot = int(round(t * (NUM_LED_SLOTS - 1)))
    return clamp(slot, 0, NUM_LED_SLOTS - 1)


def event_callback(event_type: EventType, frame: ResponseFrame, data: EventDataType) -> None:
    global latest_accel
    if isinstance(data, AccelData):
        latest_accel.x = lerp(latest_accel.x, data.x, ACCEL_LPF_ALPHA)
        latest_accel.y = lerp(latest_accel.y, data.y, ACCEL_LPF_ALPHA)
        latest_accel.z = lerp(latest_accel.z, data.z, ACCEL_LPF_ALPHA)


def main() -> None:
    print("Say hi to Tiltie!")
    print("- Tilt left/right to move the light trail")
    print("- Ctrl+C to exit\n")

    dev = FreeWili.find_first().expect("Failed to find FreeWili")
    dev.open().expect("Failed to open")

    try:
        time.sleep(0.4)
        clear_leds(dev)

        # Enable events
        dev.set_event_callback(event_callback)
        dev.enable_accel_events(True, 90).expect("Failed to enable accel events")

        # Cursor smoothing and trail state
        current_slot: int = NUM_LED_SLOTS // 2
        prev_slot: int | None = None
        trail_positions: list[int] = [current_slot]
        decay_levels = [12, 8, 5, 3]    # Fade values
        base_rgb = (0, 25, 25)  # Color
        # Track previously applied per-LED RGB to minimize writes (efficiency)
        prev_led_rgb: list[tuple[int, int, int]] = [(0, 0, 0) for _ in range(NUM_LED_SLOTS)]

        while running:
            dev.process_events()

            # Map tilt to target slot
            target_slot = int(map_tilt_to_slot(latest_accel.x))

            # Step by 1 toward target
            if target_slot > current_slot:
                current_slot += 1
            elif target_slot < current_slot:
                current_slot -= 1

            current_slot = int(clamp(current_slot, 0, NUM_LED_SLOTS - 1))

            # Update trail list only when slot changes
            if prev_slot is None or current_slot != prev_slot:
                trail_positions.insert(0, current_slot)
                dedup = []
                for pos in trail_positions:
                    if not dedup or dedup[-1] != pos:
                        dedup.append(pos)
                trail_positions = dedup[: len(decay_levels)]
                prev_slot = current_slot

            # If head is at either end collapse tail into head
            at_end = current_slot == 0 or current_slot == NUM_LED_SLOTS - 1
            no_motion = target_slot == current_slot
            if at_end and no_motion and len(trail_positions) > 1:
                collapsed: list[int] = [current_slot]
                for pos in trail_positions[1:]:
                    if pos == current_slot:
                        collapsed.append(pos)
                        continue
                    step = 1 if current_slot > pos else -1
                    new_pos = pos + step
                    # Clamp to head so segments don't overshoot
                    if (step > 0 and new_pos > current_slot) or (step < 0 and new_pos < current_slot):
                        new_pos = current_slot
                    collapsed.append(new_pos)
                # Remove duplicates from back
                dedup_back: list[int] = []
                for p in collapsed:
                    if not dedup_back or dedup_back[-1] != p:
                        dedup_back.append(p)
                trail_positions = dedup_back[: len(decay_levels)]

            # Compute desired per-LED RGB based on trail with decay
            desired_rgb: list[tuple[int, int, int]] = [(0, 0, 0) for _ in range(NUM_LED_SLOTS)]
            for idx, pos in enumerate(trail_positions):
                level = decay_levels[idx]
                r = int(base_rgb[0] * level / 12)
                g = int(base_rgb[1] * level / 12)
                b = int(base_rgb[2] * level / 12)
                # Mix taking max per channel to avoid dimming brighter head
                cr, cg, cb = desired_rgb[pos]
                desired_rgb[pos] = (max(cr, r), max(cg, g), max(cb, b))

            # Apply only changed LEDs
            for i in range(NUM_LED_SLOTS):
                if desired_rgb[i] != prev_led_rgb[i]:
                    rr, gg, bb = desired_rgb[i]
                    safe_set_led(dev, i, rr, gg, bb)
                    prev_led_rgb[i] = desired_rgb[i]


            time.sleep(FRAME_DELAY_SEC)

    except KeyboardInterrupt:
        pass
    finally:
        try:
            dev.enable_accel_events(False).expect("Failed to disable accel events")
        except Exception:
            pass
        try:
            clear_leds(dev)
        except Exception:
            pass
        try:
            dev.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
