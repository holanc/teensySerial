#define INPUT_SIZE_BYTES (500)
#define INPUT_SIZE_SEQ (100)
#define PIN_NUM_MAX (54) 
#define PIN_NUM (PIN_NUM_MAX-2)
#define PIN_START (2)

#define NUM_TRIG (10)
#define NUM_CONTAINER (200)

#define Bit0 0x1
#define Bit1 0x2
#define Bit2 0x4
#define Bit3 0x8
#define Bit4 0x10
#define Bit5 0x20
#define Bit6 0x40
#define Bit7 0x80

enum unitDef:byte {
  MILLISEC,
  MICROSEC  
};

enum statusHiLo:byte {
  LO,
  HI  
};

struct container {
  unsigned int clock[NUM_TRIG];
} CONTAINER[NUM_CONTAINER];

struct out_pin {
  byte              active;
  byte              pin;
  volatile uint8_t* port;
  byte              seqIdx;
  byte              numVal;
  byte              bitMask;
  unsigned int      hiTime;
  unsigned int      loTime;
  byte              unit;
  byte              setStatus;
  unsigned long     startTime;
  unsigned long     stopTime;
} outPin[PIN_NUM];

byte reservedPins[] = {};
#define RESERVED_PINS_NUM sizeof reservedPins / sizeof reservedPins[0]

int i, charIdx, input_idx = 0;
char *pChar;
char input[INPUT_SIZE_BYTES];
char inputByte;
unsigned long counter[2];
const char startMarker = '{';
const char endMarker = '}';
bool receiving = false;
bool newData = false;
unsigned int seqArr[INPUT_SIZE_SEQ];


int isPinReserved(int pin) 
{
  for (int i = 0; i < RESERVED_PINS_NUM; i++) {
    if (pin == reservedPins[i]) {
      return 1;
    }
  }
  return 0;
}

void setup() {
  int test = sizeof (statusHiLo);
  
  Serial.begin(115200); 

  for (int i = PIN_START; i < PIN_NUM; i++) {
    pinMode(i, OUTPUT);
  }


  Serial.print(test);

  outPin[0].pin = 0;
  outPin[0].port = &PORTE;
  outPin[0].bitMask = Bit0;
  outPin[1].pin = 1;
  outPin[1].port = &PORTE;
  outPin[1].bitMask = Bit1;
  outPin[2].pin = 1;
  outPin[2].port = &PORTE;
  outPin[2].bitMask = Bit4;
  outPin[3].pin = 1;
  outPin[3].port = &PORTE;
  outPin[3].bitMask = Bit5;
  outPin[4].pin = 1;
  outPin[4].port = &PORTG;
  outPin[4].bitMask = Bit5;
  outPin[5].pin = 1;
  outPin[5].port = &PORTE;
  outPin[5].bitMask = Bit3;
  outPin[6].pin = 1;
  outPin[6].port = &PORTH;
  outPin[6].bitMask = Bit3;
  outPin[7].pin = 1;
  outPin[7].port = &PORTH;
  outPin[7].bitMask = Bit4;
  outPin[8].pin = 1;
  outPin[8].port = &PORTH;
  outPin[8].bitMask = Bit5;
  outPin[9].pin = 1;
  outPin[9].port = &PORTH;
  outPin[9].bitMask = Bit6;
  outPin[10].pin = 1;
  outPin[10].port = &PORTB;
  outPin[10].bitMask = Bit4;
  outPin[11].pin = 1;
  outPin[11].port = &PORTB;
  outPin[11].bitMask = Bit5;
  outPin[12].pin = 1;
  outPin[12].port = &PORTB;
  outPin[12].bitMask = Bit6;
  outPin[13].pin = 1;
  outPin[13].port = &PORTB;
  outPin[13].bitMask = Bit7;

  for (int i = PIN_START; i < PIN_NUM; i++) {
    digitalWrite(i, LOW);
  }

  memset(CONTAINER, 0, sizeof CONTAINER);
}

void loop() {
  counter[0] = millis();
  counter[1] = micros();
  
  if (Serial.available() > 0) {
    inputByte = Serial.read();
    if (inputByte == startMarker) {
      receiving = true;
    } else if (receiving) {
      if (inputByte == endMarker) {
        input[input_idx] = '\0';
        input_idx = 0;
        receiving = false;
        newData = true;
      } else {
        input[input_idx++] = inputByte;
        if (input_idx == INPUT_SIZE_BYTES-1) {
          receiving = false;
          input_idx = 0;
        }
      }
    }
  }
  
  if (newData) {
    int pin = 999;
    pChar = strchr(input, '_');
    charIdx = pChar - input;

    if (pChar != NULL) {
      if (strncmp(input, "SIG", charIdx) == 0) {
        pin = atoi(pChar+1);
        if (pin >= PIN_START && pin < PIN_NUM) {
          pChar = strchr(pChar+1, '_');
          if (strncmp(pChar+1, "SEQ", 3) == 0) {
            int err = 0;
            pChar = strchr(pChar+1, '_');
            outPin[pin].numVal = atoi(pChar+1);
            pChar = strchr(pChar+1, '_');
            outPin[pin].hiTime = atoi(pChar+1);
            if (outPin[pin].numVal > INPUT_SIZE_SEQ)
              outPin[pin].numVal = INPUT_SIZE_SEQ;
            for (i = 0; i < outPin[pin].numVal; i++) {
              pChar = strchr(pChar+1, '_');
              seqArr[i] = atoi(pChar+1);
              if (seqArr[i] < outPin[pin].hiTime) {
                err = 1;
                break;
              }
            }
            if (!err) {
              outPin[pin].active = 2;
              outPin[pin].unit = 0;
              outPin[pin].seqIdx = 0;
              outPin[pin].setStatus = HI;
              outPin[pin].stopTime = counter[outPin[pin].unit] + outPin[pin].hiTime;
              *outPin[pin].port |= outPin[pin].bitMask;
            }
          } else if (strncmp(pChar+1, "RAND", 4) == 0) {
            int seed;
            pChar = strchr(pChar+1, '_');
            outPin[pin].hiTime = atoi(pChar+1);
            pChar = strchr(pChar+1, '_');
            outPin[pin].loTime = atoi(pChar+1);
            pChar = strchr(pChar+1, '_');
            seed = atoi(pChar+1);
            outPin[pin].unit = (unitDef)0;
            if ( !seed) {
              randomSeed(analogRead(0));
            } else {
              randomSeed(seed);
            }
            if (outPin[pin].hiTime*3 < outPin[pin].loTime) {
              outPin[pin].active = 3;
              outPin[pin].setStatus = HI;
              outPin[pin].stopTime = counter[outPin[pin].unit] + outPin[pin].hiTime;
              *outPin[pin].port |= outPin[pin].bitMask;
            }
          } else {
            if ((outPin[pin].hiTime = atoi(pChar+1)) != 0) {
              outPin[pin].active = 1;
              pChar = strchr(pChar+1, '_');
              outPin[pin].loTime = atoi(pChar+1);
              pChar = strchr(pChar+1, '_');
              outPin[pin].unit = (unitDef)atoi(pChar+1);
              outPin[pin].setStatus = HI;
              outPin[pin].stopTime = counter[outPin[pin].unit] + outPin[pin].hiTime;
              *outPin[pin].port |= outPin[pin].bitMask;
            } else {
              outPin[pin].active = 0;
              *outPin[pin].port &= ~outPin[pin].bitMask;
            }
          }
        }
      }
    }
    newData = false;
  }

  for (i = PIN_START; i < PIN_NUM; i++) {
    if (outPin[i].active == 1) {
      if (outPin[i].setStatus == HI) {
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          *outPin[i].port &= ~outPin[i].bitMask;
          if (outPin[i].loTime) {
            outPin[i].startTime = counter[outPin[i].unit] + outPin[i].loTime;
            outPin[i].setStatus = LO;
          } else {
            outPin[i].active == 0;
          }
        }        
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          *outPin[i].port |= outPin[i].bitMask;
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].setStatus = HI;
        }  
      }
    } else if (outPin[i].active == 2) {
      if (outPin[i].setStatus == HI) {
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          *outPin[i].port &= ~outPin[i].bitMask;
          outPin[i].startTime = counter[outPin[i].unit] + (seqArr[outPin[i].seqIdx] - outPin[i].hiTime);
          outPin[i].setStatus = LO;
        }
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          *outPin[i].port |= outPin[i].bitMask;
          outPin[i].seqIdx++;
          if (outPin[i].seqIdx > (outPin[i].numVal - 1))
            outPin[i].seqIdx = 0;
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].setStatus = HI;
        }
      }
    } else if (outPin[i].active == 3) {
      if (outPin[i].setStatus == HI) {
        int minval, maxval, randval;
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          *outPin[i].port &= ~outPin[i].bitMask;
          randval = random(outPin[i].hiTime*3, outPin[i].loTime);
          outPin[i].startTime = counter[outPin[i].unit] + randval;
          outPin[i].setStatus = LO;
        }
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          *outPin[i].port |= outPin[i].bitMask;
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].setStatus = HI;
        }
      }
    }
  }
}
