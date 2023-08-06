#ifndef NGSP__BITPACK_H_
#define NGSP__BITPACK_H_

#ifdef __cplusplus
extern "C" {
#endif

/* A: 0b00, C: 0b01, G: 0b10, T: 0b11 */
/* note: the DNA complement is the bitwise not */
const unsigned char _ACGT[] = "ACGT";

/* Quick lookup based on ASCII codes. */
/* note: the lookup is case insensitive */
/* note: any character outside of ACGT is considered as an A,
 *       checks are the programmer's responsibility */
const unsigned char _ASCII_TO_BIT2[] = \
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
   0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};


/* A: 0b000, C: 0b001, G: 0b010, T: 0b011 */
/* N:0b100 unknown base */
/* $:0b111 separator */
/* 0b110 and 0b101 are not assigned*/
/* note: the DNA complement is the bitwise not for the two last bits */
const unsigned char _ACGTN[] = "ACGTN??$";

/* Same as _ASCII_TO_BIT2. Case insensitive for ACGT. The default is no longer 
   the code for A but the one for '?' */  
/* 
   _ASCII_TO_BIT3 = list(_ACGTN.index('?') for x in range(256))
   for i, x in enumerate(_ACGTN):
       _ASCII_TO_BIT3[ord(x)] = i
       _ASCII_TO_BIT3[ord(x.lower())] = i
   for x in range(0, 256, 20):
       print(', '.join(str(y) for y in _ASCII_TO_BIT3[x:(x+20)]), ',')
*/
const unsigned char _ASCII_TO_BIT3[] = \
  {5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 7, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 6, 5, 0, 5, 1, 5, 5, 5, 2, 5, 5, 5, 5, 5, 5, 4, 5 ,
   5, 5, 5, 5, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 0, 5, 1 ,
   5, 5, 5, 2, 5, 5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 5, 3, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5 ,
   5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5};
  
const int NGSP_WORD_SIZE = 4;

#ifdef __cplusplus
}
#endif

#endif /* !NGSP__BITPACK_H_ */

