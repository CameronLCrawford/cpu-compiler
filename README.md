# cpu-compiler
A simulation of an 8-bit CPU (virtual machine) with a compiler for a simple high-level language that runs on the CPU.

# The CPU
The CPU is a 8-bit and can address 64k of RAM. It is losely based off of the intel 8080 but it has far greater support for stack processing as this was necessary for the implementation of the high level language. The virtual machine the CPU is run as is as representational of the actual hardware as possible with the instructions being carried out by setting the control bus according to an instruction ROM ("instruction_rom.bin") each clock cycle. There are 4 general purpose registers, a stack pointer, a base pointer, and other registers like the instruction register and program counter which are controlled by the CPU. The program counter, stack pointer, and the base pointer are composed of two 8 bit registers to mimic a 16 bit address. The accumulator has a separate temporary A register which is used in arithmetic operations. The CPU has 4 flags: sign, zero, carry, and parity. There is a simulated output register which will print the value in the accumulator to the terminal whenever the "output" control is set. The CPU reads machine code from "program_rom.bin" and executes it, starting execution from address 32k as the memory is split into the first half being data and the second half being for the instructions.

# Storn
Storn is a made up C-like language created solely to show off the capabilities of the compiler. It has a single byte-sized variable type and facilitates functions, while loops, for loops, and if conditions.

# The Compiler
The compiler takes in plaintext from the document "storn_main.stn" and compiles it into what eventually becomes the binary in "program_rom.bin". This happens in a set of stages which are detailed here:
  1. The document is read in and fed into a tokeniser which finds all valid tokens from the Storn language and stores them in a list in sequential order.
  2. The parser reads in the tokens and (according to the language definition) creates an abstract syntax tree which represents the structure of the program. This is stored in the file "abstract_syntax_tree.xml" in a pretty format to show the internals of the compiler during its operation. The parser is a recursive descent parser so it parses by generating base xml nodes then recursively populating them with elements.
  3. The AST (abstract syntax tree) is then read in to the code generator which generates the assembly for the program. The compiler is based off a stack machine so the majority of instructions are stack related. These assembly instructions are written to the file "program.txt".
  4. The assembler reads in the assembly instructions and assembles them into machine code which is written to "instruction_rom.bin". All instructions the CPU can execute are defined in "Final_ROM.py". These are defined through the set of control signals that the instruction is comprised of. There are about 150 assembly instructions but the compiler only utilises about 40 so it is a valid option to write code in pure assembly for the CPU and make use of those other instructions to write more optimised programs.
  5. There is also an optimiser (Optimiser.py) which reads in compiled assembly code and edits it to decrease reliance on stack operations as these are often the most taxing for the CPU to perform. This includes replacing "push x, pop y" with "mov y x" and replacing "push integer_constant, pop y" with "ldr y integer_constant".


# Running this project
There are several stages in order to be able to run a Storn program on the virtual machine.

## Compiling C++ code
This can be performed using any C++ compiler, although there is a Makefile that can be ran from the root directory using the command `make`.

## Generating program ROM
This is done by writing a Storn file and then calling `python Compiler.py <path to stn file>`. This will generate the program ROM as a `.bin` file

## Running the VM
The `out/cpu` executable is ran using `./out/cpu <path to instruction ROM> <path to program ROM>`. Any output will be put on the terminal window and the process will block until ENTER is pressed once the CPU has halted.