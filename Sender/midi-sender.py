import os
import sys
import mido
import json
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from ai.ia_generate_preset import generate_preset_ai

VOX_HEADER = [0x42, 0x30, 0x00, 0x01, 0x34, 0x41]

PEDAL1_COMPRESSOR = 0
PEDAL1_CHORUS = 1
PEDAL1_OVERDRIVE = 2
PEDAL1_DISTORTION = 3

PEDAL2_FLANGER = 0
PEDAL2_PHASER = 1
PEDAL2_TREMOLO = 2
PEDAL2_DELAY = 3

REVERB_ROOM = 0
REVERB_SPRING = 1
REVERB_HALL = 2
REVERB_PLATE = 3

AMP_DELUXE_CL = 0
AMP_TWEED_4X10 = 1
AMP_VOX_AC30 = 2
AMP_BOUTIQUE_OD = 3
AMP_VOX_AC30TB = 4
AMP_BRIT_800 = 5
AMP_BRIT_OR_MKII = 6
AMP_DOUBLE_REC = 7

AMP_NAME_TO_ID = {
    "deluxe_cl": AMP_DELUXE_CL,
    "tweed_4x10": AMP_TWEED_4X10,
    "vox_ac30": AMP_VOX_AC30,
    "boutique_od": AMP_BOUTIQUE_OD,
    "vox_ac30tb": AMP_VOX_AC30TB,
    "brit_800": AMP_BRIT_800,
    "brit_or_mkii": AMP_BRIT_OR_MKII,
    "double_rec": AMP_DOUBLE_REC,
}

def safe_delay():
    time.sleep(0.05)

def clamp(v, a, b):
    return max(a, min(b, v))

def split_14bit(v):
    v = clamp(v, 0, 0x3FFF)
    return v & 0x7F, (v >> 7) & 0x7F

def normalize_type(t):
    if isinstance(t, int):
        return str(t)
    return str(t).lower()

def find_output_port():
    for name in mido.get_output_names():
        if "Valvetronix" in name:
            return name
    return None

def send_sysex(out, data):
    out.send(mido.Message("sysex", data=data))

def set_amp_model(out, amp_name):
    if not isinstance(amp_name, str):
        return
    amp_id = AMP_NAME_TO_ID.get(amp_name.lower(), AMP_DELUXE_CL)
    send_sysex(out, VOX_HEADER + [0x03, 0x00, amp_id, 0])
    safe_delay()

def pedal2_reset(out):
    i = 0
    while i < 6:
        send_sysex(out, VOX_HEADER + [0x06, i, 0, 0])
        i += 1
    safe_delay()

def sweep_pedal2_rate(out, target):
    v = 0
    target = clamp(target, 0, 127)
    while v <= target:
        set_pedal2_v(out, 0, v)
        time.sleep(0.01)
        v += 2

def ask_int(label, a=0, b=127):
    try:
        return clamp(int(input(f"{label}: ")), a, b)
    except:
        return a

def print_commentary_if_any(preset):
    comment = preset.get("commentaire")
    if isinstance(comment, str) and comment.strip():
        print("\n--- Commentaire du preset ---")
        print(comment)
        print("-----------------------------\n")

def set_gain(out, v):
    send_sysex(out, VOX_HEADER + [0x04, 0x00, clamp(v, 0, 127), 0])

def set_treble(out, v):
    send_sysex(out, VOX_HEADER + [0x04, 0x01, clamp(v, 0, 127), 0])

def set_middle(out, v):
    send_sysex(out, VOX_HEADER + [0x04, 0x02, clamp(v, 0, 127), 0])

def set_bass(out, v):
    send_sysex(out, VOX_HEADER + [0x04, 0x03, clamp(v, 0, 127), 0])

def set_volume(out, v):
    send_sysex(out, VOX_HEADER + [0x04, 0x04, clamp(v, 0, 127), 0])

def enable_pedal1(out, on):
    send_sysex(out, VOX_HEADER + [0x02, 0x01, 1 if on else 0, 0])
    safe_delay()

def select_pedal1(out, pid):
    send_sysex(out, VOX_HEADER + [0x03, 0x01, pid, 0])
    safe_delay()

def set_pedal1_v1_7(out, v):
    send_sysex(out, VOX_HEADER + [0x05, 0x00, clamp(v, 0, 127), 0])

def set_pedal1_v1_14(out, v):
    l, m = split_14bit(v)
    send_sysex(out, VOX_HEADER + [0x05, 0x00, l, m])

def set_pedal1_v2(out, v):
    send_sysex(out, VOX_HEADER + [0x05, 0x01, clamp(v, 0, 100), 0])

def apply_pedal1(out, p):
    enable_pedal1(out, False)
    t = normalize_type(p["type"])
    if t in ("compressor", "0"):
        select_pedal1(out, PEDAL1_COMPRESSOR)
        set_pedal1_v1_7(out, p["value1"])
    elif t in ("chorus", "1"):
        select_pedal1(out, PEDAL1_CHORUS)
        set_pedal1_v1_14(out, p["value1"])
    elif t in ("overdrive", "2"):
        select_pedal1(out, PEDAL1_OVERDRIVE)
        set_pedal1_v1_7(out, p["value1"])
    elif t in ("distortion", "3"):
        select_pedal1(out, PEDAL1_DISTORTION)
        set_pedal1_v1_7(out, p["value1"])
    set_pedal1_v2(out, p["value2"])
    enable_pedal1(out, True)

def enable_pedal2(out, on):
    send_sysex(out, VOX_HEADER + [0x02, 0x02, 1 if on else 0, 0])
    safe_delay()

def select_pedal2(out, pid):
    send_sysex(out, VOX_HEADER + [0x03, 0x02, pid, 0])
    safe_delay()

def set_pedal2_v(out, idx, v):
    send_sysex(out, VOX_HEADER + [0x06, idx, clamp(v, 0, 127), 0])

def apply_pedal2(out, p):
    enable_pedal2(out, False)
    pedal2_reset(out)
    t = normalize_type(p["type"])
    if t in ("flanger", "0"):
        select_pedal2(out, PEDAL2_FLANGER)
        sweep_pedal2_rate(out, p["rate"])
        set_pedal2_v(out, 1, p["depth"])
        set_pedal2_v(out, 2, p["feedback"])
    elif t in ("phaser", "1"):
        select_pedal2(out, PEDAL2_PHASER)
        sweep_pedal2_rate(out, p["rate"])
        set_pedal2_v(out, 1, p["depth"])
        set_pedal2_v(out, 2, p["feedback"])
        set_pedal2_v(out, 3, p["stage"])
    elif t in ("tremolo", "2"):
        select_pedal2(out, PEDAL2_TREMOLO)
        sweep_pedal2_rate(out, p["rate"])
        set_pedal2_v(out, 1, p["depth"])
    elif t in ("delay", "3"):
        select_pedal2(out, PEDAL2_DELAY)
        set_pedal2_v(out, 0, p["rate"])
        set_pedal2_v(out, 1, p["depth"])
        set_pedal2_v(out, 2, p["feedback"])
        set_pedal2_v(out, 3, p["stage"])
    enable_pedal2(out, True)

def enable_reverb(out, on):
    send_sysex(out, VOX_HEADER + [0x02, 0x04, 1 if on else 0, 0])
    safe_delay()

def select_reverb(out, rid):
    send_sysex(out, VOX_HEADER + [0x03, 0x04, rid, 0])
    safe_delay()

def set_reverb_v(out, idx, v):
    send_sysex(out, VOX_HEADER + [0x08, idx, clamp(v, 0, 127), 0])

def apply_reverb(out, r):
    enable_reverb(out, False)
    t = normalize_type(r["type"])
    if t in ("room", "0"):
        select_reverb(out, REVERB_ROOM)
    elif t in ("spring", "1"):
        select_reverb(out, REVERB_SPRING)
    elif t in ("hall", "2"):
        select_reverb(out, REVERB_HALL)
    elif t in ("plate", "3"):
        select_reverb(out, REVERB_PLATE)
    set_reverb_v(out, 0, r["level"])
    set_reverb_v(out, 1, r["time"])
    set_reverb_v(out, 2, r["predelay"])
    set_reverb_v(out, 3, r["tone"])
    set_reverb_v(out, 4, r["character"])
    enable_reverb(out, True)

def ask_amp_manual():
    print("\nAmp model:")
    print("0 Deluxe CL")
    print("1 Tweed 4x10")
    print("2 Vox AC30")
    print("3 Boutique OD")
    print("4 Vox AC30TB")
    print("5 Brit 800")
    print("6 Brit OR MKII")
    print("7 Double Rec")
    try:
        v = clamp(int(input("> ")), 0, 7)
    except:
        v = 0
    for name, idx in AMP_NAME_TO_ID.items():
        if idx == v:
            return name
    return "deluxe_cl"

def manual_build_preset():
    preset = {}
    preset["commentary"] = "Manually built preset"
    preset["amp"] = ask_amp_manual()
    preset["eq"] = {
        "gain": ask_int("Gain"),
        "bass": ask_int("Bass"),
        "middle": ask_int("Middle"),
        "treble": ask_int("Treble"),
        "volume": ask_int("Volume"),
    }
    use_p1 = input("Enable Pedal 1 (y/n): ").lower() == "y"
    if use_p1:
        ptype = input("Pedal 1 type (0-3): ")
        preset["pedal1"] = {
            "enabled": True,
            "type": ptype,
            "value1": ask_int("Value 1", 0, 16383),
            "value2": ask_int("Value 2", 0, 100),
        }
    else:
        preset["pedal1"] = {"enabled": False, "type": "compressor", "value1": 0, "value2": 0}
    use_p2 = input("Enable Pedal 2 (y/n): ").lower() == "y"
    if use_p2:
        ptype = input("Pedal 2 type (0-3): ")
        preset["pedal2"] = {
            "enabled": True,
            "type": ptype,
            "rate": ask_int("Rate"),
            "depth": ask_int("Depth"),
            "feedback": ask_int("Feedback"),
            "stage": ask_int("Stage"),
        }
    else:
        preset["pedal2"] = {"enabled": False, "type": "flanger", "rate": 0, "depth": 0, "feedback": 0, "stage": 0}
    use_rev = input("Enable Reverb (y/n): ").lower() == "y"
    if use_rev:
        rtype = input("Reverb type (0-3): ")
        preset["reverb"] = {
            "enabled": True,
            "type": rtype,
            "level": ask_int("Level"),
            "time": ask_int("Time"),
            "predelay": ask_int("Predelay"),
            "tone": ask_int("Tone"),
            "character": ask_int("Character"),
        }
    else:
        preset["reverb"] = {"enabled": False, "type": "room", "level": 0, "time": 0, "predelay": 0, "tone": 0, "character": 0}
    return preset

def load_preset(path):
    with open(path, "r") as f:
        return json.load(f)

def main():
    port = find_output_port()
    if port is None:
        print("VOX amplifier not detected")
        sys.exit(1)
    out = mido.open_output(port)
    print("1 Manual configuration")
    print("2 Load JSON preset")
    print("3 AI preset")
    mode = input("> ")
    if mode == "1":
        preset = manual_build_preset()
    elif mode == "2":
        preset = load_preset(input("Preset path: "))
        print_commentary_if_any(preset)
    elif mode == "3":
        preset = generate_preset_ai(input("Describe the tone: "))
        print_commentary_if_any(preset)
    else:
        sys.exit(1)
    set_amp_model(out, preset["amp"])
    eq = preset["eq"]
    set_gain(out, eq["gain"])
    set_bass(out, eq["bass"])
    set_middle(out, eq["middle"])
    set_treble(out, eq["treble"])
    set_volume(out, eq["volume"])
    apply_pedal1(out, preset["pedal1"]) if preset["pedal1"]["enabled"] else enable_pedal1(out, False)
    apply_pedal2(out, preset["pedal2"]) if preset["pedal2"]["enabled"] else enable_pedal2(out, False)
    apply_reverb(out, preset["reverb"]) if preset["reverb"]["enabled"] else enable_reverb(out, False)
    print("Configuration sent")

if __name__ == "__main__":
    main()
