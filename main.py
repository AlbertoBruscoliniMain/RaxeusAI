from agent import chat, reset
from config import AI_NAME

print(f"=== {AI_NAME} ===")
print("Scrivi 'esci' per uscire, 'reset' per cancellare la memoria.\n")

while True:
    user = input("Tu: ").strip()

    if not user:
        continue
    if user.lower() == "esci":
        print(f"{AI_NAME}: Ci si becca capo")
        break
    if user.lower() == "reset":
        reset()
        continue

    reply = chat(user)
    print(f"{AI_NAME}: {reply}\n")
