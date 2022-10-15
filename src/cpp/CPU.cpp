#include "CPU.hpp"
#include <fstream>
#include <iostream>

CPU::CPU(std::string instructionPath, std::string programPath)
{
	// Initalise RAM
	ram = new char[65536];
	// Initialise instruction ROM
	instructionRom = new uint32_t[65536];
	//Sets counter to start address
	registers[counterHRegister] = 128;
	registers[stackHRegister] = 8;
	// Initialise microinstruction counter to 0
	microinstructionCounter = 0;
	//Load instruction ROM from file
	std::ifstream instructionRomFile(instructionPath, std::ios::binary);
	char buffer[4];
	int value;
	for (int i = 0; i < 65536; i++)
	{
		instructionRomFile.read((char*)&value, 4);
		instructionRom[i] = value;
	}
	//Load program from file ROM into RAM
	std::ifstream programRomFile(programPath, std::ios::binary);
	programRomFile.read(ram, 65536);
}

CPU::~CPU()
{
}

void CPU::run()
{
	while (controlLines[halt] == false)
	{
		tick();
	}
	std::cout << "Program execution halted. Press <ENTER> to quit\n";
	std::cin.get();
}

void CPU::tick()
{
	controlTick();
	programTick();
}

void CPU::controlTick()
{
	//Address of the next set of control lines in the instruction rom
	std::uint16_t instructionAddress;
	instructionAddress = (flags.to_ulong() << 12) | (registers[instructionRegister] << 4) | microinstructionCounter;
	std::bitset<32> instruction = instructionRom[instructionAddress];
	controlLines = instruction;
	tickALU();
	if (controlLines[counterIncrement])
	{
		uint16_t counterAddress = (registers[counterHRegister] << 8) | registers[counterLRegister];
		counterAddress++;
		registers[counterHRegister] = counterAddress >> 8;
		registers[counterLRegister] = counterAddress;
	}
	if (controlLines[addressIncrement])
	{
		uint16_t memoryAddress = (registers[addressHRegister] << 8) | registers[addressLRegister];
		memoryAddress++;
		registers[addressHRegister] = memoryAddress >> 8;
		registers[addressLRegister] = memoryAddress;
	}
	if (controlLines[stackIncrement])
	{
		uint16_t stackAddress = (registers[stackHRegister] << 8) | registers[stackLRegister];
		stackAddress++;
		registers[stackHRegister] = stackAddress >> 8;
		registers[stackLRegister] = stackAddress;
	}
	if (controlLines[stackDecrement])
	{
		uint16_t stackAddress = (registers[stackHRegister] << 8) | registers[stackLRegister];
		stackAddress--;
		registers[stackHRegister] = stackAddress >> 8;
		registers[stackLRegister] = stackAddress;
	}
	if (controlLines[zeroFlagOut])
	{
		dataBus = (int)flags[zero];
	}
	if (controlLines[signFlagOut])
	{
		dataBus = (int)flags[sign];
	}
	//Sets the data bus according to the 4-bit output control word which dictates which
	//registers output their data onto the bus
	std::bitset<4> controlWord;
	controlWord[0] = controlLines[outControl0];
	controlWord[1] = controlLines[outControl1];
	controlWord[2] = controlLines[outControl2];
	controlWord[3] = controlLines[outControl3];

	//Converts the control word to an integer between 0 and 15
	std::uint8_t controlValue = controlWord.to_ulong();

	if (controlValue > 0 && controlValue < 15)
	{
		dataBus = registers[controlValue - 1];
	}
	else if (controlValue == 15)
	{
		dataBus = flags.to_ulong();
	}

	if (controlLines[ramOut])
	{
		uint16_t globalRamAddress;
		globalRamAddress = (registers[addressHRegister] << 8) | registers[addressLRegister];
		dataBus = ram[globalRamAddress];
	}
	if (controlLines[moveCounterAddress])
	{
		registers[addressHRegister] = registers[counterHRegister];
		registers[addressLRegister] = registers[counterLRegister];
	}
	if (controlLines[moveStackAddress])
	{
		registers[addressHRegister] = registers[stackHRegister];
		registers[addressLRegister] = registers[stackLRegister];
	}
	if (controlLines[moveHLAddressAccumulator])
	{
		registers[addressHRegister] = registers[hRegister];
		registers[addressLRegister] = registers[lRegister];
	}
	microinstructionCounter++;
}

void CPU::programTick()
{
	if (controlLines[resetMicroTick])
	{
		microinstructionCounter = 0;
	}

	//Sets the registers according to the 4-bit output control word which dictates which
	//registers read in their data from the bus
	std::bitset<4> controlWord;
	controlWord[0] = controlLines[inControl0];
	controlWord[1] = controlLines[inControl1];
	controlWord[2] = controlLines[inControl2];
	controlWord[3] = controlLines[inControl3];

	//Converts the control word to an integer between 0 and 15
	std::uint8_t controlValue = controlWord.to_ulong();

	if (controlValue > 0 && controlValue < 15)
	{
		registers[controlValue - 1] = dataBus;
	}
	else if (controlValue == 15)
	{
		flags = dataBus;
	}
	if (controlLines[out])
	{
		registers[outputRegister] = dataBus;
		std::cout << "Output: " << (int)registers[outputRegister] << '\n';
	}
	if (controlLines[ramIn])
	{
		uint16_t globalRamAddress;
		globalRamAddress = (registers[addressHRegister] << 8) | registers[addressLRegister];
		ram[globalRamAddress] = dataBus;
	}
}

void CPU::tickALU()
{
	std::bitset<4> controlWord;
	controlWord[0] = controlLines[aluControl0];
	controlWord[1] = controlLines[aluControl1];
	controlWord[2] = controlLines[aluControl2];
	controlWord[3] = controlLines[aluControl3];

	//Converts the control word to an integer between 0 and 15
	std::uint8_t controlValue = controlWord.to_ulong();

	if (controlValue == 0)
	{
		return;
	}

	uint8_t aRegisterValue = registers[aRegister];
	uint8_t aTempRegisterValue = registers[aTempRegister];

	switch (controlValue)
	{
	case 0: //Do nothing with ALU
		break;
	case 1: //Add
		aluOutput = aRegisterValue + aTempRegisterValue;
		flags[carry] = aRegisterValue + aTempRegisterValue > 255;
		updateFlags();
		break;
	case 2: //Subtract
		aluOutput = aRegisterValue - aTempRegisterValue;
		flags[carry] = aTempRegisterValue > aRegisterValue;
		updateFlags();
		break;
	case 3: //Binary AND
		aluOutput = aRegisterValue & aTempRegisterValue;
		break;
	case 4: //Binary OR
		aluOutput = aRegisterValue | aTempRegisterValue;
		break;
	case 5: //Binary XOR
		aluOutput = aRegisterValue ^ aTempRegisterValue;
		break;
	case 6: //Increment A
		aluOutput = aRegisterValue + 1;
		flags[carry] = aluOutput == 0;
		updateFlags();
		break;
	case 7: //Decrement A
		aluOutput = aRegisterValue - 1;
		flags[carry] = aluOutput == 255;
		updateFlags();
		break;
	case 8: //Negates A register
		aluOutput = !aRegisterValue;
		break;
	case 9: //Add carry conditional
		if (flags[carry])
		{
			aluOutput = aRegisterValue + aTempRegisterValue + 1;
			flags[carry] = aRegisterValue + aTempRegisterValue + 1 > 255;
		}
		else
		{
			aluOutput = aRegisterValue + aTempRegisterValue;
			flags[carry] = aRegisterValue + aTempRegisterValue > 255;
		}
		updateFlags();
		break;
	case 10: //Subtract carry conditional
		if (flags[carry])
		{
			aluOutput = aRegisterValue - aTempRegisterValue - 1;
			flags[carry] = aRegisterValue - aTempRegisterValue - 1 < 0;
		}
		else
		{
			aluOutput = aRegisterValue - aTempRegisterValue;
			flags[carry] = aTempRegisterValue > aRegisterValue;
		}
		updateFlags();
		break;
	case 11: //Increment A carry conditional
		if (flags[carry])
		{
			aluOutput = aRegisterValue + 1;
		}
		else
		{
			aluOutput = aRegisterValue;
		}
		flags[carry] = aluOutput == 0;
		updateFlags();
		break;
	case 12: //Decrement A carry conditional
		if (flags[carry])
		{
			aluOutput = aRegisterValue - 1;
		}
		else
		{
			aluOutput = aRegisterValue;
		}
		flags[carry] = aluOutput == 255;
		updateFlags();
		break;
	case 13: //Unary negate on A
		aluOutput = -aRegisterValue;
		break;
	}
	dataBus = aluOutput;
}

void CPU::updateFlags()
{
	//Checks if negative (two's complement)
	flags[sign] = aluOutput >> 7;
	//Checks if the result is zero
	flags[zero] = aluOutput == 0;
	//Checks if the result is even
	flags[parity] = aluOutput % 2;
}
