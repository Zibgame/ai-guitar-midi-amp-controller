# AI Guitar Midi Amp Controller

AI-powered guitar amplifier controller that generates and applies presets **in real time** using MIDI SysEx messages.

This project allows you to **control a VOX Valvetronix amplifier entirely from Python**, either manually or automatically using **AI-generated presets from a simple text prompt**.

The core idea is simple:
> 🎸 *You describe a guitar sound in one sentence → the AI generates a preset → the amplifier is configured instantly.*

---

## ✨ Key Features

- 🤖 **AI-controlled guitar amplifier**
- 📝 Generate full amp presets from **natural language prompts**
- 🎛 Manual configuration mode (amp, EQ, pedals, reverb)
- 🎹 Real-time **MIDI SysEx control** of VOX Valvetronix amplifiers
- 📦 JSON preset system (AI & manual compatible)
- 🔍 MIDI reverse engineering tools (sniffer) included
- ⚡ Preset generation in **1–2 seconds** from a single phrase

---

## 🧠 How It Works (High Level)

1. You write a short text prompt (example: *"cloud heaven ambient guitar"*)
2. The AI (LLaMA 3.1) generates a **musically coherent JSON preset**
3. The application translates this JSON into **MIDI SysEx messages**
4. Your VOX Valvetronix amplifier is configured **live**

The AI decides:
- amp model
- gain and EQ balance
- pedals and effects
- reverb type and space

---

## 🤖 AI Engine

This project uses **Ollama** with the model:

```
llama3.1:8b
```

The AI is responsible for:
- understanding musical language
- detecting style, mood, and intention
- generating structured presets that respect musical rules

⚠️ The AI **does not guess artists or songs** unless explicitly mentioned by the user.

---

## 📦 Requirements

### System

- Python **3.10+** (tested with 3.11)
- A **VOX Valvetronix amplifier** with MIDI support
- USB-MIDI or MIDI interface

---

### Python Dependencies

Install required Python packages:

```bash
pip install mido python-rtmidi
```

Standard libraries used:

- `os`
- `sys`
- `json`
- `time`

External library:

- `mido` → MIDI communication with the amplifier

---

### Ollama Installation

Install Ollama:

👉 https://ollama.com

Then pull the required model:

```bash
ollama pull llama3.1:8b
```

Make sure Ollama is running before launching the application:

```bash
ollama serve
```

---

## 🎹 Supported Amplifier

- **VOX Valvetronix series**

The app communicates using **raw MIDI SysEx messages**, allowing deep control of:

- amp models
- EQ (gain, bass, mid, treble, volume)
- pedal 1 (compressor, chorus, overdrive, distortion)
- pedal 2 (modulation, delay)
- reverb (room, spring, hall, plate)

---

## 🔍 MIDI Reverse Engineering

This project includes a **MIDI sniffer / reverse engineering workflow** used to:

- capture SysEx messages sent by the official VOX software
- identify amp models, effects, and parameters
- rebuild full control logic in Python

This makes the project:
- hardware-aware
- low-level
- close to real embedded / audio engineering work

---

## ▶️ Usage

Launch the application:

```bash
python Sender/midi-sender.py
```

You can choose:

```
1 = Configuration manuelle
2 = Charger un preset JSON
3 = Option IA
```

### AI Mode (Main Feature)

- Select option `3`
- Describe a guitar sound in one sentence
- The AI generates and applies the preset automatically

Example:

```
Decrit le preset: dreamy ambient cloud guitar
```

Result:
- preset generated
- commentary displayed
- amplifier configured instantly

---

## 🎯 Why This Project Matters

This project demonstrates:

- real-time hardware control
- MIDI SysEx protocol understanding
- AI + audio integration
- reverse engineering skills
- clean software architecture
- practical use of LLMs beyond chatbots

It is designed as a **technical showcase** for audio, embedded, and software engineering roles.

---

## ⚠️ Disclaimer

This project is for educational and experimental purposes.
VOX and Valvetronix are trademarks of their respective owners.

---

## 🚀 Future Ideas

- preset browser UI
- live parameter morphing
- multi-amp support
- footswitch / controller integration
- model fine-tuning for guitar tones

---

🎸 *Describe a sound. Let the AI play your amp.*

