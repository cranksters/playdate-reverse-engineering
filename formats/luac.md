Lua-based Playdate games use a tweaked version of Lua 5.4.3. You will only find compiled Lua bytecode in [`.pdz`](/formats/pdz.md) files.

### Compile Flags

`#define LUA_32BITS = 1` set in `luaconf.h`.

### Header Differences

TODO

### Opcode Differences

To maintain backwards-compatibility with Lua 5.4-beta bytecode from [pre-release versions of the Playdate SDK](#pre-sdk-version-180), additional Lua 5.4.3 opcodes were appended to the opcode map like so:

```
LUAI_DDEF const lu_byte luaP_opmodes[NUM_OPCODES] = {
/*       MM OT IT T  A  mode		   opcode  */
  opmode(0, 0, 0, 0, 1, iABC)		/* OP_MOVE */
 ,opmode(0, 0, 0, 0, 1, iAsBx)		/* OP_LOADI */
 ,opmode(0, 0, 0, 0, 1, iAsBx)		/* OP_LOADF */
 ,opmode(0, 0, 0, 0, 1, iABx)		/* OP_LOADK */
 ,opmode(0, 0, 0, 0, 1, iABx)		/* OP_LOADKX */
 ,opmode(0, 0, 0, 0, 1, iABx)		/* OP_UNKNOWN */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_LOADNIL */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_GETUPVAL */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_SETUPVAL */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_GETTABUP */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_GETTABLE */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_GETI */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_GETFIELD */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_SETTABUP */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_SETTABLE */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_SETI */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_SETFIELD */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_NEWTABLE */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_SELF */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_ADDI */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_ADDK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_SUBK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_MULK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_MODK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_POWK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_DIVK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_IDIVK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_BANDK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_BORK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_BXORK */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_SHRI */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_SHLI */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_ADD */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_SUB */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_MUL */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_MOD */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_POW */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_DIV */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_IDIV */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_BAND */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_BOR */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_BXOR */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_SHL */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_SHR */
 ,opmode(1, 0, 0, 0, 0, iABC)		/* OP_MMBIN */
 ,opmode(1, 0, 0, 0, 0, iABC)		/* OP_MMBINI*/
 ,opmode(1, 0, 0, 0, 0, iABC)		/* OP_MMBINK*/
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_UNM */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_BNOT */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_NOT */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_LEN */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_CONCAT */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_CLOSE */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_TBC */
 ,opmode(0, 0, 0, 0, 0, isJ)		/* OP_JMP */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_EQ */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_LT */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_LE */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_EQK */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_EQI */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_LTI */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_LEI */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_GTI */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_GEI */
 ,opmode(0, 0, 0, 1, 0, iABC)		/* OP_TEST */
 ,opmode(0, 0, 0, 1, 1, iABC)		/* OP_TESTSET */
 ,opmode(0, 1, 1, 0, 1, iABC)		/* OP_CALL */
 ,opmode(0, 1, 1, 0, 1, iABC)		/* OP_TAILCALL */
 ,opmode(0, 0, 1, 0, 0, iABC)		/* OP_RETURN */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_RETURN0 */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_RETURN1 */
 ,opmode(0, 0, 0, 0, 1, iABx)		/* OP_FORLOOP */
 ,opmode(0, 0, 0, 0, 1, iABx)		/* OP_FORPREP */
 ,opmode(0, 0, 0, 0, 0, iABx)		/* OP_TFORPREP */
 ,opmode(0, 0, 0, 0, 0, iABC)		/* OP_TFORCALL */
 ,opmode(0, 0, 0, 0, 1, iABx)		/* OP_TFORLOOP */
 ,opmode(0, 0, 1, 0, 0, iABC)		/* OP_SETLIST */
 ,opmode(0, 0, 0, 0, 1, iABx)		/* OP_CLOSURE */
 ,opmode(0, 1, 0, 0, 1, iABC)		/* OP_VARARG */
 ,opmode(0, 0, 1, 0, 1, iABC)		/* OP_VARARGPREP */
 ,opmode(0, 0, 0, 0, 0, iAx)		/* OP_EXTRAARG */

 // opcodes appended:

 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_LOADFALSE */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_LFALSESKIP */
 ,opmode(0, 0, 0, 0, 1, iABC)		/* OP_LOADTRUE */
};
```

## Pre SDK Version 1.8.0

Prior to SDK version 1.8.0 (which was only available to developer preview members - 1.9.0 was the first publicly available SDK release), the Playdate Lua runtime was based on [prerelease/beta version of Lua 5.4](https://github.com/lua/lua/tree/6c0e44464b9eef4be42e2c8181aabfb3301617ad). This version used a slightly nonstandard bytecode header structure.

It is possible to execute Playdate Lua bytecode from this version of the SDK by compiling the Lua 5.4-beta with `#define LUA_32BITS = 1` set in `luaconf.h`.

### Header

| Offset | Type    | Detail |
|:-------|:--------|:-------|
| `0`    | `byte[4]` | Constant `LUA_SIGNATURE` (hex `1B 4C 75 61`) |
| `4`    | `uint16`  | Version (`0x03F8` = 5.4.0 prerelease) |
| `6`    | `byte`    | Constant `LUAC_FORMAT` (hex `00`) |
| `7`    | `byte[6]` | Constant `LUAC_DATA` (hex `19 93 0D 0A 1A 0A`) |
| `13`   | `uint8`   | Instruction size (always `4`) |
| `14`   | `uint8`   | Integer size (always `4`) |
| `15`   | `uint8`   | Number size (always `4`) |
| `16`   | `lua int`  | Constant `LUA_INT` (`0x5678`) |
| `20`   | `lua float`  | Constant `LUA_NUM` (`370.5`) |