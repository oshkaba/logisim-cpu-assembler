# Y8-ProtoMav CPU Assembler

Y8-ProtoMav is a custom CPU project made in Logisim Evolution. The circuit uses a small custom instruction set with five instructions: `DATA`, `LD`, `STR`, `ADD`, and `MULT`.

This project also includes a Python assembler. The assembler reads a `.asm` program and creates Logisim Evolution memory files that can be loaded into the CPU circuit.

## Files

```text
assembler.py                 Python assembler for the custom CPU
CPU.circ                     Logisim Evolution CPU circuit
demo.asm                     Example assembly program
Y8-ProtoMav CPU Manual.pdf   CPU manual and instruction format reference
```

## Custom Instructions

The CPU uses four registers, numbered `0` through `3`. Data memory addresses are numbered `0` through `15`. Data values are 8-bit values from `0` through `255`.

### DATA

`DATA` places values into the data memory file. It must appear before the actual CPU instructions.

```asm
DATA 170 60 255 85
```

This writes the values into data memory starting at address `0`.

### LD

`LD` loads a value from data memory into a register.

```asm
LD 0 4
```

This loads the value at data memory address `4` into register `0`.

### STR

`STR` stores a register value into data memory.

```asm
STR 2 8
```

This stores the value from register `2` into data memory address `8`.

### ADD

`ADD` adds two registers and stores the result in a destination register.

```asm
ADD 3 1 2
```

This adds register `1` and register `2`, then stores the result in register `3`.

### MULT

`MULT` multiplies two registers and stores the result in a destination register.

```asm
MULT 0 0 1
```

This multiplies register `0` and register `1`, then stores the result in register `0`.

## Requirements

This project requires:

* Ubuntu or WSL Ubuntu
* Python 3
* Logisim Evolution

Install Python 3 on Ubuntu:

```bash
sudo apt update
sudo apt install python3
```

## Build Memory Files

Run the assembler on the demo program:

```bash
python3 assembler.py demo.asm
```

This creates:

```text
instr.o   instruction memory file
data.o    data memory file
```

These files can be loaded into the matching memory components in the Logisim Evolution CPU circuit.
Specifically, the instr.o file is loaded into the memory RAM while the data.o is loaded into the data RAM.

## Optional Listing File

You can also create a readable listing file that shows each instruction and its encoded byte:

```bash
python3 assembler.py demo.asm --listing listing.txt
```

## Custom Output Names

The default output files are `instr.o` and `data.o`. You can choose different names:

```bash
python3 assembler.py demo.asm --instr my_instr.o --data my_data.o
```

## Help

Show command line help:

```bash
python3 assembler.py --help
```

## Supported Assembly Format

The assembler supports decimal, hex, and binary numbers:

```text
LD 0 0
LD 1 0x4
LD 2 0b1000
```

It also supports commas between arguments:

```text
ADD 3, 2, 2
MULT 0, 0, 1
STR 0, 15
```

Instruction names are not case sensitive:

```text
ld 0 0
add 3 2 2
mult 0 0 1
str 0 15
```

Short aliases are also supported:

```text
A 3 2 2
M 0 0 1
L 0 0
S 0 15
```

## Validation Added

The assembler checks for common mistakes before writing output files:

```text
missing arguments
too many arguments
unknown instructions
bad register numbers
bad memory addresses
bad DATA values
DATA appearing after instructions
missing input file
```

These checks do not change the Logisim Evolution circuit or the instruction encoding. They only make the Python assembler easier to use and debug.
