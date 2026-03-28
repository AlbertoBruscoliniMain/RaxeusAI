from agent import chat, reset, memory
from sessions import save_session, list_sessions, load_session
from config import AI_NAME

HELP = "Comandi: 'esci'  'reset'  'salva'  'sessioni'  'carica <N>'"

print(f"=== {AI_NAME} ===")
print(f"{HELP}\n")

while True:
    try:
        user = input("Tu: ").strip()
    except (EOFError, KeyboardInterrupt):
        print(f"\n{AI_NAME}: Ci si becca capo")
        break

    if not user:
        continue

    if user.lower() == "esci":
        print(f"{AI_NAME}: Ci si becca capo")
        break

    if user.lower() == "reset":
        reset()
        continue

    if user.lower() == "salva":
        path = save_session(memory.get())
        print(f"Sessione salvata → {path}\n")
        continue

    if user.lower() == "sessioni":
        sessions = list_sessions()
        if not sessions:
            print("Nessuna sessione salvata.\n")
        else:
            print("Sessioni disponibili:")
            for i, s in enumerate(sessions, 1):
                print(f"  {i}. {s}")
            print()
        continue

    if user.lower().startswith("carica "):
        try:
            n = int(user.split()[1]) - 1
            sessions = list_sessions()
            if 0 <= n < len(sessions):
                messages = load_session(sessions[n])
                memory.load(messages)
                print(f"Sessione caricata: {sessions[n]}\n")
            else:
                print("Numero sessione non valido.\n")
        except (ValueError, IndexError):
            print("Uso: carica <numero>\n")
        continue

    print(f"{AI_NAME}: ", end="", flush=True)
    chat(user)
    print()
