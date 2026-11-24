
import sys
import re

# ROLL NUMBER CONFIGURATION
ROLL_NO = 11
K = ROLL_NO % 100

# Box configuration for K = 11
BOX_WIDTH = 64
BOX_HEIGHT = 20
START_ROW = 11
END_ROW = START_ROW + BOX_HEIGHT - 1

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001",
    "-D": "0001111", "-A": "0110011", "-M": "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110110",
    "D+A": "0000010", "D-A": "0010011", "A-D": "0000111",
    "D&A": "0000000", "D|A": "0010101",
    "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101"
}

DEST = {
    "": "000", "M": "001", "D": "010", "MD": "011",
    "A": "100", "AM": "101", "AD": "110", "AMD": "111"
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}


def predefined_symbols():
    table = {
        "SP": 0, "LCL": 1, "ARG": 2,
        "THIS": 3, "THAT": 4,
        "SCREEN": 16384, "KBD": 24576
    }

    for i in range(16):
        table["R" + str(i)] = i

    return table


def clean(line):
    line = line.split("//")[0]
    return "".join(line.split())


def valid_symbol(name):
    return re.fullmatch(
        r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", name
    ) is not None


# PASS 1: Find labels and their ROM addresses

def first_pass(lines, symbols):
    rom_address = 0
    instructions = []
    duplicate_labels = []

    for line_no, line in lines:

        if line.startswith("(") and line.endswith(")"):

            label = line[1:-1]

            if not valid_symbol(label):
                raise ValueError(
                    f"Line {line_no}: Invalid label"
                )

            if label in symbols:
                print(
                    f"Warning: Duplicate or predefined label "
                    f"'{label}' at line {line_no}"
                )
                duplicate_labels.append(label)
                continue

            symbols[label] = rom_address

        else:
            instructions.append((line_no, line))
            rom_address += 1

    return instructions, duplicate_labels


# Convert A-instruction into 16-bit binary

def encode_a(line, symbols, state):

    name = line[1:]

    if not name:
        raise ValueError("Empty A-instruction")

    if name.isdigit():
        value = int(name)

    else:
        if not valid_symbol(name):
            raise ValueError("Invalid symbol")

        if name not in symbols:
            symbols[name] = state["next_var"]
            state["next_var"] += 1

        value = symbols[name]

    if value < 0 or value > 32767:
        raise ValueError("Address out of range")

    return format(value, "016b")


# Convert C-instruction into 16-bit binary

def encode_c(line):

    dest = ""
    comp = line
    jump = ""

    if "=" in comp:
        if comp.count("=") != 1:
            raise ValueError("Invalid destination")

        dest, comp = comp.split("=")

    if ";" in comp:
        if comp.count(";") != 1:
            raise ValueError("Invalid jump")

        comp, jump = comp.split(";")

    if any(ch not in "ADM" for ch in dest):
        raise ValueError("Invalid destination")

    if len(set(dest)) != len(dest):
        raise ValueError("Duplicate destination")

    dest = "".join(ch for ch in "AMD" if ch in dest)

    if comp not in COMP:
        raise ValueError("Invalid computation")

    if dest not in DEST:
        raise ValueError("Invalid destination")

    if jump not in JUMP:
        raise ValueError("Invalid jump")

    return "111" + COMP[comp] + DEST[dest] + JUMP[jump]


# PASS 2: Convert instructions into binary

def assemble_lines(raw_lines):

    symbols = predefined_symbols()
    cleaned = []

    for line_no, line in enumerate(raw_lines, start=1):

        line = clean(line)

        if line:
            cleaned.append((line_no, line))

    instructions, duplicates = first_pass(
        cleaned, symbols
    )

    state = {"next_var": 16}
    output = []

    for line_no, line in instructions:

        try:

            if line.startswith("@"):
                binary = encode_a(line, symbols, state)

            else:
                binary = encode_c(line)

            output.append(binary)

        except ValueError as e:
            raise ValueError(f"Line {line_no}: {e}")

    return output, symbols, duplicates


# Read assembly file and generate hack file

def assemble_file(path):

    try:

        with open(path, "r") as file:
            raw_lines = file.readlines()

        binary, symbols, duplicates = assemble_lines(
            raw_lines
        )

        out_path = path.rsplit(".", 1)[0] + ".hack"

        with open(out_path, "w") as file:
            file.write("\n".join(binary) + "\n")

        print("\n========== CAPSTONE ASSEMBLER ==========")
        print("Roll Number:", ROLL_NO)
        print("K Value:", K)
        print("Box Width:", BOX_WIDTH)
        print("Box Height:", BOX_HEIGHT)
        print("Starting Row:", START_ROW)
        print("Ending Row:", END_ROW)

        print("\nSymbol Table:")

        predefined = predefined_symbols()

        for name, address in symbols.items():

            if name not in predefined:
                print(f"{name} = {address}")

        print("\nDuplicate Labels:", len(duplicates))
        print("Total Instructions:", len(binary))
        print("Output File:", out_path)

        print("\nAssembler completed successfully!")

    except (ValueError, OSError) as e:
        print("Error:", e)
        sys.exit(1)


# MAIN PROGRAM

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print("Usage: python assembler.py <file.asm>")

    else:

        assemble_file(sys.argv[1])
