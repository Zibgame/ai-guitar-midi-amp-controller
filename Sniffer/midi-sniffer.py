import mido
import time

def list_input_ports():
    ports = mido.get_input_names()
    print("Available MIDI input ports:")
    i = 0
    while i < len(ports):
        print(f"{i}: {ports[i]}")
        i += 1
    return ports

def listen(port_name):
    print(f"\nListening on port: {port_name}\n")
    with mido.open_input(port_name) as port:
        while True:
            for msg in port.iter_pending():
                if msg.type == "sysex":
                    data = " ".join(f"{b:02X}" for b in msg.data)
                    print(f"[SYSEX] {data}")
                else:
                    print(f"[MIDI] {msg}")
            time.sleep(0.01)

def main():
    ports = list_input_ports()
    if not ports:
        print("No MIDI input port detected")
        return
    try:
        index = int(input("\nSelect port index: "))
    except:
        return
    if index < 0 or index >= len(ports):
        return
    listen(ports[index])

if __name__ == "__main__":
    main()
