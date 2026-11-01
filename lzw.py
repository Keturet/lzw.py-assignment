import struct
import sys

DICT_START = 256          
MAX_CODES = 1 << 16       


def encode(text):
    """Encode a string with LZW and return the list of integer codes."""
    if not text:
        return []

    dictionary = {chr(i): i for i in range(DICT_START)}
    next_code = DICT_START
    result = []

    current = ""
    for char in text:
        candidate = current + char
        if candidate in dictionary:
            current = candidate
        else:
            result.append(dictionary[current])
            if next_code < MAX_CODES:
                dictionary[candidate] = next_code
                next_code += 1
            current = char

    print(dictionary)
    result.append(dictionary[current])
    print(f"Result {result}")
    return result


def decode(codes):
    """Decode a list of LZW integer codes and return the original string."""
    if not codes:
        return ""

    dictionary = {i: chr(i) for i in range(DICT_START)}
    next_code = DICT_START

    previous = dictionary[codes[0]]
    output = [previous]

    for code in codes[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code:
            # The code is being defined in this very step (e.g. "ABA" in
            # "ABABABA"): it must be previous + first char of previous.
            entry = previous + previous[0]
        else:
            raise ValueError(f"Invalid LZW code: {code}")

        output.append(entry)
        if next_code < MAX_CODES:
            dictionary[next_code] = previous + entry[0]
            next_code += 1
        previous = entry

    return "".join(output)


def readTextFromFile(path):
    """Return the content of a text file as a string."""
    # latin-1 maps every byte 0-255 to one character; newline="" keeps
    # line endings exactly as they are in the file.
    with open(path, "r", encoding="latin-1", newline="") as file:
        return file.read()


def saveTextToFile(text, path):
    """Write a string to a text file."""
    with open(path, "w", encoding="latin-1", newline="") as file:
        file.write(text)


def readCodeFromFile(path):
    """Read 2-byte codes from a binary file and return them as a list."""
    with open(path, "rb") as file:
        data = file.read()
    count = len(data) // 2
    return list(struct.unpack(f">{count}H", data[:count * 2]))


def saveCodeToFile(codes, path):
    """Write a list of codes to a binary file, 2 bytes per code."""
    with open(path, "wb") as file:
        file.write(struct.pack(f">{len(codes)}H", *codes))


def compressionRatio(text, codes):
    """Compressed size / original size in percent, rounded down."""
    if not text:
        return 0
    return (len(codes) * 2 * 100) // len(text)


def encodeFile(input_path, output_path):
    text = readTextFromFile(input_path)
    codes = encode(text)
    saveCodeToFile(output_path, codes)
    print(f"Compression ratio: {compressionRatio(text, codes)}%")


def decodeFile(input_path, output_path):
    codes = readCodeFromFile(input_path)
    text = decode(codes)
    saveTextToFile(output_path, text)


def main():
    if len(sys.argv) != 4:
        print("Usage: python lzw.py <mode> <input_file> <output_file>")
        sys.exit(1)

    mode, input_path, output_path = sys.argv[1], sys.argv[2], sys.argv[3]

    if mode == "encode":
        encodeFile(input_path, output_path)
    elif mode == "decode":
        decodeFile(input_path, output_path)
    else:
        print("Invalid mode. Use 'encode' or 'decode'.")
        sys.exit(1)


if __name__ == "__main__":
    main()