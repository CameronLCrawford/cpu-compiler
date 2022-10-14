#include "CPU.hpp"
#include <iostream>

// Two arguments expected: path to instructionROM and path
// to programROM
int main(int argc, char *argv[])
{
	if (argc != 3) 
	{ 
		std::cout << "ERROR: two arguments expected\n";
		return -1;
	}
	std::string instructionPath = argv[1];
	std::string programPath = argv[2];
	CPU cpu(instructionPath, programPath);
	cpu.run();
	return 0;
}