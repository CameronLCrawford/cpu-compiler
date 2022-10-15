
all:
	g++ -c src/cpp/CPU.cpp -o out/CPU.o
	g++ -c src/cpp/main.cpp -o out/main.o
	g++ out/CPU.o out/main.o -o out/cpu

clean:
	rm -f out/cpu out/CPU.o out/main.o