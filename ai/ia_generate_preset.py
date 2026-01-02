from ollama import chat
import json

MODEL = "llama3:8b"

SYSTEM_PROMPT = """
You are an AI specialized in generating presets for VOX Valvetronix amplifiers.
You think like a professional guitarist and sound designer.

STRICT OUTPUT RULES:
- You MUST respond with VALID JSON ONLY.
- No text before or after the JSON.
- All required fields MUST be present.
- All numeric values MUST be integers.
- All values must be realistic and musically coherent.
- If an effect is disabled, ALL its numeric values MUST be set to 0.

SIGNAL CHAIN ORDER:
AMP → EQ → PEDALS → REVERB

AMP MODELS:
deluxe_cl
tweed_4x10
vox_ac30
boutique_od
vox_ac30tb
brit_800
brit_or_mkii
double_rec

COMMENTAIRE RULES:
- One single sentence
- Musician vocabulary only
- Describe inspiration and musical intention
- No invented artists

REQUIRED JSON FORMAT:
{
  "commentaire": "string",
  "amp": "string",
  "eq": {
    "gain": 0,
    "bass": 0,
    "middle": 0,
    "treble": 0,
    "volume": 0
  },
  "pedal1": {
    "enabled": true,
    "type": "string",
    "value1": 0,
    "value2": 0
  },
  "pedal2": {
    "enabled": true,
    "type": "string",
    "rate": 0,
    "depth": 0,
    "feedback": 0,
    "stage": 0
  },
  "reverb": {
    "enabled": true,
    "type": "string",
    "level": 0,
    "time": 0,
    "predelay": 0,
    "tone": 0,
    "character": 0
  }
}
"""

STYLE_LIBRARY = {
    "prince": "Emotional melodic lead guitar with warm mids and expressive phrasing",
    "steve vai": "High gain virtuosic lead tone with sustain and articulation",
    "bob marley": "Clean reggae rhythm tone with bright skank and low gain"
}

def build_prompt(user_prompt: str) -> str:
    lower = user_prompt.lower()
    context = ""
    for key in STYLE_LIBRARY:
        if key in lower:
            context = STYLE_LIBRARY[key]
            break
    return context + "\nUser request: " + user_prompt

def clamp_value(value, min_v, max_v):
    if not isinstance(value, int):
        return min_v
    if value < min_v:
        return min_v
    if value > max_v:
        return max_v
    return value

def sanitize_preset(data: dict) -> dict:
    eq = data["eq"]
    eq["gain"] = clamp_value(eq["gain"], 5, 127)
    eq["bass"] = clamp_value(eq["bass"], 10, 127)
    eq["middle"] = clamp_value(eq["middle"], 10, 127)
    eq["treble"] = clamp_value(eq["treble"], 10, 127)
    eq["volume"] = clamp_value(eq["volume"], 10, 127)

    p1 = data["pedal1"]
    p1["value1"] = clamp_value(p1["value1"], 0, 16383)
    p1["value2"] = clamp_value(p1["value2"], 0, 100)

    p2 = data["pedal2"]
    p2["rate"] = clamp_value(p2["rate"], 0, 127)
    p2["depth"] = clamp_value(p2["depth"], 0, 127)
    p2["feedback"] = clamp_value(p2["feedback"], 0, 127)
    p2["stage"] = clamp_value(p2["stage"], 0, 127)

    r = data["reverb"]
    r["level"] = clamp_value(r["level"], 0, 127)
    r["time"] = clamp_value(r["time"], 0, 127)
    r["predelay"] = clamp_value(r["predelay"], 0, 127)
    r["tone"] = clamp_value(r["tone"], 0, 127)
    r["character"] = clamp_value(r["character"], 0, 127)

    return data

def validate_preset(data: dict):
    if not isinstance(data.get("commentaire"), str) or not data["commentaire"]:
        raise ValueError("invalid commentaire")
    eq = data["eq"]
    for k in eq:
        if not isinstance(eq[k], int) or not 0 <= eq[k] <= 127:
            raise ValueError("eq value out of range")

def generate_preset_ai(user_prompt: str, max_retry: int = 5) -> dict:
    final_prompt = build_prompt(user_prompt)
    attempt = 1
    while attempt <= max_retry:
        response = chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": final_prompt}
            ],
        )
        try:
            data = json.loads(response.message.content)
            data = sanitize_preset(data)
            validate_preset(data)
            print(f"\n {data} \n")
            return data
        except:
            attempt += 1
    raise RuntimeError("AI failed to generate a valid preset")
