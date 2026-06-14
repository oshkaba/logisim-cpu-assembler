#Orest Shkaba
#I pledge my honor that I have abided by the Stevens Honor System.
#Assembler for the Y8-ProtoMav CPU

import argparse
import sys

#Each mnemonic holds a 2 bit opcode field.
#In binary, ADD holds 00, MULT holds 01, LD holds 10, and STR holds 11.
opcodeBits = {"ADD": 0, "MULT": 1, "LD": 2, "STR": 3}

#Short instruction names accepted by the assembler.
aliases = {"A": "ADD", "M": "MULT", "L": "LD", "S": "STR"}

class AssemblerError(Exception):
    """Stores a clean assembler error message."""
    pass

def trim(text):
    """Remove spaces from a line."""
    return text.strip()

def removeComment(text):
    """Remove everything after the comment symbol."""
    pos = text.find("#")
    if pos == -1:
        return text
    return text[:pos]

def normalizeLine(text):
    """Allow either spaces or commas between arguments."""
    return text.replace(",", " ")

def parseNumber(text, lineNumber, fieldName):
    """Parse a decimal, binary, or hex number."""
    try:
        return int(text.strip(), 0)
    except ValueError:
        raise AssemblerError("Line " + str(lineNumber) + ": invalid " + fieldName + " '" + text + "'.")

def parseRegister(text, lineNumber):
    """Parse and validate a register index from 0 to 3."""
    register = parseNumber(text, lineNumber, "register")
    if register < 0 or register > 3:
        raise AssemblerError("Line " + str(lineNumber) + ": register must be between 0 and 3.")
    return register

def parseAddress(text, lineNumber):
    """Parse and validate a 4 bit data memory address."""
    address = parseNumber(text, lineNumber, "address")
    if address < 0 or address > 15:
        raise AssemblerError("Line " + str(lineNumber) + ": address must be between 0 and 15.")
    return address

def parseByte(text, lineNumber):
    """Parse and validate an 8 bit data value."""
    value = parseNumber(text, lineNumber, "data value")
    if value < 0 or value > 255:
        raise AssemblerError("Line " + str(lineNumber) + ": DATA values must be between 0 and 255.")
    return value

def requireArgumentCount(parts, expectedCount, lineNumber):
    """Make sure an instruction has the exact number of arguments."""
    if len(parts) != expectedCount:
        instruction = parts[0] if len(parts) > 0 else "instruction"
        expectedArgs = expectedCount - 1
        actualArgs = len(parts) - 1
        message = "Line " + str(lineNumber) + ": " + instruction + " expects "
        message = message + str(expectedArgs) + " argument(s), but got " + str(actualArgs) + "."
        raise AssemblerError(message)

def getOpcode(text):
    """Return the full instruction name for a mnemonic or short alias."""
    upperText = text.upper()
    if upperText in aliases:
        return aliases[upperText]
    return upperText

def encodeAddOrMultiply(opKind, destRegister, firstRegister, secondRegister):
    """Encode ADD/MULT: opcode, destination register, first register, and second register."""
    opcodeValue = opcodeBits[opKind]
    byteValue = 0
    byteValue = byteValue | ((opcodeValue & 3) << 6)
    byteValue = byteValue | ((destRegister & 3) << 4)
    byteValue = byteValue | ((firstRegister  & 3) << 2)
    byteValue = byteValue | (secondRegister & 3)
    return byteValue

def encodeLoad(destRegister, address):
    """Encode LD: opcode, destination register, and data memory address."""
    opcodeValue = opcodeBits["LD"]
    byteValue = 0
    byteValue = byteValue | ((opcodeValue & 3) << 6)
    byteValue = byteValue | ((destRegister & 3) << 4)
    byteValue = byteValue | (address & 0xF)
    return byteValue

def encodeStore(sourceRegister, address):
    """Encode STR: opcode, source register, and data memory address."""
    opcodeValue = opcodeBits["STR"]
    byteValue = 0
    byteValue = byteValue | ((opcodeValue & 3) << 6)
    byteValue = byteValue | ((sourceRegister & 3) << 4)
    byteValue = byteValue | (address & 0xF)
    return byteValue

def hexByte(value):
    """Convert a value from 0 to 255 into 2 uppercase hex digits."""
    return f"{value:02X}"

def writeHexFile(fileName, byteList, lineNum):
    """Write a Logisim Evolution hex memory file."""
    file = open(fileName, "w")
    file.write("v3.0 hex words addressed\n")
    valuesPerLine = lineNum
    index = 0
    while index < len(byteList):
        file.write(hexByte(index) + ": ")
        count = 0
        while index < len(byteList) and count < valuesPerLine:
            file.write(hexByte(byteList[index]) + " ")
            index = index + 1
            count = count + 1
        file.write("\n")
    file.close()

def writeListingFile(fileName, listingRows):
    """Write a readable listing file that shows source lines and encoded bytes."""
    file = open(fileName, "w")
    file.write("Y8-ProtoMav Assembly Listing\n")
    file.write("Address  Byte  Source\n")
    file.write("-------  ----  ------\n")
    for row in listingRows:
        file.write(row + "\n")
    file.close()

def parseDataLine(parts, lineNumber, dataBytes):
    """Parse a DATA line and add the values into data memory."""
    if len(parts) == 1:
        raise AssemblerError("Line " + str(lineNumber) + ": DATA needs at least one value.")
    for i in range(1, len(parts)):
        value = parseByte(parts[i], lineNumber)
        dataBytes.append(value)

def parseInstruction(parts, lineNumber):
    """Parse one instruction line and return the encoded byte."""
    opUpper = getOpcode(parts[0])
    if opUpper == "ADD" or opUpper == "MULT":
        requireArgumentCount(parts, 4, lineNumber)
        destRegister = parseRegister(parts[1], lineNumber)
        firstRegister = parseRegister(parts[2], lineNumber)
        secondRegister = parseRegister(parts[3], lineNumber)
        return encodeAddOrMultiply(opUpper, destRegister, firstRegister, secondRegister)
    if opUpper == "LD":
        requireArgumentCount(parts, 3, lineNumber)
        destRegister = parseRegister(parts[1], lineNumber)
        address = parseAddress(parts[2], lineNumber)
        return encodeLoad(destRegister, address)
    if opUpper == "STR":
        requireArgumentCount(parts, 3, lineNumber)
        sourceRegister = parseRegister(parts[1], lineNumber)
        address = parseAddress(parts[2], lineNumber)
        return encodeStore(sourceRegister, address)
    raise AssemblerError("Line " + str(lineNumber) + ": unknown instruction '" + parts[0] + "'.")

def assembleLines(lines):
    """Convert assembly source lines into instruction bytes and data bytes."""
    dataBytes = []
    instructionBytes = []
    listingRows = []
    sawInstruction = False
    lineNumber = 0
    for rawLine in lines:
        lineNumber = lineNumber + 1
        text = trim(normalizeLine(removeComment(rawLine)))
        if text == "":
            continue
        parts = text.split()
        opUpper = getOpcode(parts[0])
        if opUpper == "DATA":
            if sawInstruction:
                raise AssemblerError("Line " + str(lineNumber) + ": DATA must appear before instructions.")
            parseDataLine(parts, lineNumber, dataBytes)
            continue
        sawInstruction = True
        byteValue = parseInstruction(parts, lineNumber)
        address = len(instructionBytes)
        instructionBytes.append(byteValue)
        listingRows.append(hexByte(address) + "       " + hexByte(byteValue) + "    " + text)
    if len(instructionBytes) == 0:
        raise AssemblerError("No instructions were found.")
    return instructionBytes, dataBytes, listingRows

def readSourceFile(fileName):
    """Read the assembly input file."""
    try:
        file = open(fileName, "r")
        lines = file.readlines()
        file.close()
        return lines
    except OSError:
        raise AssemblerError("Could not open input file '" + fileName + "'.")

def buildArgumentParser():
    """Create the command line parser for the assembler."""
    parser = argparse.ArgumentParser(description="Assembler for the Y8-ProtoMav CPU.")
    parser.add_argument("source", help="assembly source file, such as demo.asm")
    parser.add_argument("--instr", default="instr.o", help="instruction output file")
    parser.add_argument("--data", default="data.o", help="data output file")
    parser.add_argument("--listing", default="", help="optional readable listing file")
    return parser

def main():
    """Run the assembler from the command line."""
    parser = buildArgumentParser()
    args = parser.parse_args()
    try:
        lines = readSourceFile(args.source)
        instructionBytes, dataBytes, listingRows = assembleLines(lines)
        writeHexFile(args.instr, instructionBytes, 6)
        if len(dataBytes) > 0:
            writeHexFile(args.data, dataBytes, 8)
        if args.listing != "":
            writeListingFile(args.listing, listingRows)
        print("Assembler finished successfully.")
        print("Instruction file: " + args.instr)
        if len(dataBytes) > 0:
            print("Data file: " + args.data)
        if args.listing != "":
            print("Listing file: " + args.listing)
    except AssemblerError as error:
        print("Assembler error: " + str(error))
        sys.exit(1)

if __name__ == "__main__":
    main()
