import xml.etree.ElementTree as element_tree
from xml.dom import minidom
from Tokenizer import Tokenizer
from Parser import Parser
from Code_generator import Generator
from Final_assembler import assemble
from Optimiser import optimise

code = []
with open("storn_main.stn", "r") as code_file:
    code = code_file.read()

tokenizer = Tokenizer(code)

tokens = tokenizer.scan()

parser = Parser(tokens)
parser.parse_program()
tree = element_tree.tostring(parser.root)
pretty_tree = minidom.parseString(tree).toprettyxml(indent="    ")
with open("abstract_syntax_tree.xml", 'w') as xml_file:
    xml_file.write(pretty_tree)

generator = Generator(parser.root, parser.symbol_table)
assembly = generator.compile_program()

with open("program.txt", 'w') as assembly_file:
    for instruction in assembly:
        assembly_file.write(instruction)
        assembly_file.write("\n")

optimise()

assemble()