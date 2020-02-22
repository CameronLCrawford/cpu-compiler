#pragma once

#include <cstdint>
#include <bitset>

class CPU
{
private:
	//Control signals
	std::bitset<32> controlLines;

	//Enum used so that bitset addressing for writing individual control signals is
	//more legible
	enum controls
	{
		inControl0, inControl1, inControl2, inControl3,
		outControl0, outControl1, outControl2, outControl3,
		aluControl0, aluControl1, aluControl2, aluControl3,
		counterIncrement, addressIncrement, stackIncrement, stackDecrement,
		moveCounterAddress, moveStackAddress, moveHLAddressAccumulator,
		zeroFlagOut, signFlagOut,
		ramIn, ramOut, resetMicroTick, out, halt
	};

	//8 bit registers
	std::uint8_t registers[15];

	//Used for addressing the registers
	enum registerTypes
	{
		aRegister, bRegister, hRegister, lRegister, counterHRegister, counterLRegister,
		baseHRegister, baseLRegister, addressHRegister, addressLRegister, 
		stackHRegister, stackLRegister, instructionRegister, aTempRegister, outputRegister
	};

	//A register that stores the flags from the ALU
	std::bitset<4> flags;

	//Used to more easily address the flags
	enum flagTypes
	{
		carry, parity, zero, sign
	};

	//Internal data bus
	uint8_t dataBus;

	//64K array of heap allocated 8 bit words representing RAM
	char* ram = new char[65536];

	//ROM which holds the instruction lookup table used in decoding instructions
	uint32_t* instructionRom = new uint32_t[65536];

	//The output generated by the ALU
	uint8_t aluOutput;

	//Microinstruction counter counts the microstep of the whole instruction
	uint8_t microinstructionCounter = 0;

public:
	CPU();
	~CPU();
	void run();

private:
	void tick();
	void controlTick();
	void programTick();
	void tickALU();
	void updateFlags();
};
