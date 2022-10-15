import sys # for command-line arguments
import xml.etree.ElementTree as element_tree
from xml.dom import minidom
from tokeniser import tokenise
from parser import parse
from assembler import assemble
from optimiser import optimise
from generate_assembly import generate_assembly

def compile(storn_file, xml_file, assembly_file, program_rom):

    # Read in Storn
    code = []
    with open(storn_file, "r") as code_file:
        code = code_file.read()

    # Tokenise
    tokens = tokenise(code)

    # Generate and prettify abstract syntax tree
    parsed, symbol_table  = parse(tokens)
    tree = element_tree.tostring(parsed)
    pretty_tree = minidom.parseString(tree).toprettyxml(indent="    ")
    with open(xml_file, 'w') as xml_file:
        xml_file.write(pretty_tree)

    # Generate, write, and optimise assembly
    assembly = generate_assembly(parsed, symbol_table)
    with open(assembly_file, 'w') as assembly_file:
        for instruction in assembly:
            assembly_file.write(instruction)
            assembly_file.write("\n")
    optimise(assembly_file)

    # Finally, generate machine code
    assemble(assembly_file, program_rom)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("ERROR: expected 4 arguments")
    else:
        compile(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])