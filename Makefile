
all:
	g++ -c src/cpp/CPU.cpp -o out/CPU.o
	g++ -c src/cpp/main.cpp -o out/main.o
	g++ out/CPU.o out/main.o -o out/cpu

clean:
	rm -f out/cpu out/CPU.o out/main.o

test:
	python3 src/python/compiler.py testing/test.stn testing/test_ast.xml testing/test_ass.txt testing/test_rom.bin
	./out/cpu resources/instruction_rom.bin testing/test_rom.bin