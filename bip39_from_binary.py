import hashlib

# Загружаем BIP39 wordlist
def load_wordlist(path="bip-0039-wordlists-en.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip() for w in f.readlines()]

def binary_to_mnemonic(binary_entropy, wordlist):
    ENT_LEN = len(binary_entropy)

    if ENT_LEN not in [128, 160, 192, 224, 256]:
        raise ValueError("Неверная длина энтропии")

    # ENT -> bytes
    entropy_bytes = int(binary_entropy, 2).to_bytes(ENT_LEN // 8, byteorder="big")

    # Checksum
    checksum_length = ENT_LEN // 32
    hash_bytes = hashlib.sha256(entropy_bytes).digest()
    hash_bits = bin(int.from_bytes(hash_bytes, "big"))[2:].zfill(256)

    checksum = hash_bits[:checksum_length]

    # ENT + CS
    full_bits = binary_entropy + checksum

    # Разбиваем по 11 бит
    words = []
    for i in range(0, len(full_bits), 11):
        idx = int(full_bits[i:i+11], 2)
        words.append(wordlist[idx])

    return " ".join(words)

def main():
    print("Введите бинарную строку (0 и 1):")
    binary_entropy = input().strip()

    if not all(c in "01" for c in binary_entropy):
        print("Ошибка: допустимы только 0 и 1")
        return

    wordlist = load_wordlist()

    try:
        mnemonic = binary_to_mnemonic(binary_entropy, wordlist)
        print("\nМнемоническая фраза:")
        print(mnemonic)
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
