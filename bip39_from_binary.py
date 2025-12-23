import hashlib
import curses
from datetime import datetime, timezone
from interactive_input import interactive_entropy_input


LOG_FILE = "entropy_log.txt"
WORDLIST = "bip-0039-wordlists-en.txt"

VALID_LENGTHS = (128, 160, 192, 224, 256)


def load_wordlist(path: str = WORDLIST) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip() for w in f.readlines()]


def binary_to_mnemonic(binary_entropy: str, wordlist: list[str]) -> str:
    ent_len = len(binary_entropy)

    if ent_len not in VALID_LENGTHS:
        raise ValueError("Invalid entropy length")

    entropy_bytes = int(binary_entropy, 2).to_bytes(ent_len // 8, "big")
    checksum_len = ent_len // 32
    hash_bits = bin(
        int.from_bytes(hashlib.sha256(entropy_bytes).digest(), "big")
    )[2:].zfill(256)

    full_bits = binary_entropy + hash_bits[:checksum_len]

    return " ".join(
        wordlist[int(full_bits[i:i + 11], 2)]
        for i in range(0, len(full_bits), 11)
    )


def invert_entropy(entropy: str) -> str:
    return "".join("1" if b == "0" else "0" for b in entropy)


def log_entropy(entropy, entropy_inv, mnemonic, mnemonic_inv):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"Entropy length : {len(entropy)} bits\n\n")
        f.write("Original entropy:\n" + entropy + "\n\n")
        f.write("Inverted entropy:\n" + entropy_inv + "\n\n")
        f.write("Mnemonic (original):\n" + mnemonic + "\n\n")
        f.write("Mnemonic (inverted):\n" + mnemonic_inv + "\n")


def choose_entropy_length() -> int:
    print("Choose entropy length:")
    for i, bits in enumerate(VALID_LENGTHS, start=1):
        print(f"{i}) {bits} bits")

    mapping = {str(i): b for i, b in enumerate(VALID_LENGTHS, start=1)}
    return mapping.get(input("> ").strip(), 0)


def choose_mode() -> str:
    print("\nChoose input mode:")
    print("1) Interactive (step-by-step)")
    print("2) Direct binary input")

    return input("> ").strip()


def direct_entropy_input(bits: int) -> str:
    print(f"\nEnter binary entropy ({bits} bits):")
    entropy = input("> ").strip()

    if len(entropy) != bits:
        raise ValueError("Incorrect entropy length")

    if not all(c in "01" for c in entropy):
        raise ValueError("Entropy must contain only 0 and 1")

    return entropy


def preflight_checks():
    # wordlist
    try:
        with open(WORDLIST, "r", encoding="utf-8"):
            pass
    except Exception as e:
        print(f"❌ Cannot access {WORDLIST}:", e)
        return False

    # log file (directory write)
    try:
        with open(LOG_FILE, "a", encoding="utf-8"):
            pass
    except Exception as e:
        print(f"❌ Cannot write {LOG_FILE}:", e)
        return False

    return True


def main():
    if not preflight_checks():
        return

    bits = choose_entropy_length()
    if bits == 0:
        print("Invalid entropy length selection")
        return

    mode = choose_mode()
    if mode not in ("1", "2"):
        print("Invalid mode")
        return

    print("\n⚠️  WARNING:")
    print("Final entropy and mnemonic WILL be written to entropy_log.txt")
    print("Use only in offline / secure environment.\n")

    if mode == "1":
        try:
            entropy = curses.wrapper(interactive_entropy_input, bits)
        except Exception as e:
            print("Error during interactive input:", e)
            return
    else:
        try:
            entropy = direct_entropy_input(bits)
        except ValueError as e:
            print("Error:", e)
            return

    entropy_inv = invert_entropy(entropy)
    wordlist = load_wordlist()

    mnemonic = binary_to_mnemonic(entropy, wordlist)
    mnemonic_inv = binary_to_mnemonic(entropy_inv, wordlist)

    print("\n=== RESULT ===\n")
    print("Mnemonic (original):\n")
    print(mnemonic)
    print("\nMnemonic (inverted):\n")
    print(mnemonic_inv)

    log_entropy(entropy, entropy_inv, mnemonic, mnemonic_inv)

    print("\n✔ Saved to entropy_log.txt")


if __name__ == "__main__":
    main()
