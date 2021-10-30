#define INPUT_SIZE_BYTES (500)
#define INPUT_SIZE_SEQ (100)
#define PIN_NUM (41)
#define NUM_TRIG (14)
#define NUM_CONTAINER (200)

#include <usb_serial.h>


enum unitDef {
  MILLISEC,
  MICROSEC
};

enum statusHiLo {
  LO,
  HI
};

struct containerStruct {
  unsigned int clock[NUM_TRIG];
} container[NUM_CONTAINER];

struct outpinStruct {
  int              active;
  int              seqIdx;
  int              numVal;
  enum unitDef     unit;
  unsigned int     hiTime;
  unsigned int     loTime;
  unsigned int     startTime;
  unsigned int     stopTime;
  enum statusHiLo  status;
  int              isRestricted;
  int              randMax;
} outPin[PIN_NUM] = {0};

int i, charIdx, input_idx = 0;
char *pChar;
char input[INPUT_SIZE_BYTES];
char inputByte;
unsigned long counter[2], lastCmdCounter;
const char startMarker = '{';
const char endMarker = '}';
bool receiving = false;
bool newData = false;
unsigned int seqArr[INPUT_SIZE_SEQ];


void setup() {

  Serial1.begin(115200);
  
  outPin[0].isRestricted = true;
  outPin[1].isRestricted = true;

  for (int i = 0; i < PIN_NUM; i++) {
    if (outPin[i].isRestricted == false) {
      pinMode(i, OUTPUT);
    }
  }


//  Serial.print(test);


  for (int i = 0; i < PIN_NUM; i++) {
    if (outPin[0].isRestricted == false) {
      digitalWrite(i, LOW);
    }
  }

  memset(container, 0, sizeof container);
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
        lastCmdCounter = counter[0];
      } else {
        input[input_idx++] = inputByte;
        if (input_idx == INPUT_SIZE_BYTES - 1) {
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
        pChar++;
        pin = atoi(pChar);
        if (pin < PIN_NUM && outPin[pin].isRestricted == false) {
          pChar = strchr(pChar, '_') + 1;
          if (strncmp(pChar, "RAND", 4) == 0) {
            Serial.printf("%s\n", pChar);
            pChar = strchr(pChar, '_') + 1;
            Serial.printf("%s\n", pChar);
            outPin[pin].hiTime = atoi(pChar);
                        Serial.printf("%i\n", outPin[pin].hiTime);
            pChar = strchr(pChar, '_') + 1;
            Serial.printf("%s\n", pChar);
            outPin[pin].loTime = atoi(pChar);
                        Serial.printf("%i\n", outPin[pin].loTime);
            outPin[pin].unit = (unitDef)0;
            randomSeed(analogRead(0));
            if (outPin[pin].hiTime * 3 < outPin[pin].loTime) {
              outPin[pin].active = 3;
              outPin[pin].status = HI;
              outPin[pin].stopTime = counter[outPin[pin].unit] + outPin[pin].hiTime;
              digitalWrite(pin, HI);
              Serial.printf("%i\n", outPin[pin].active);
            }
          } else {
            if ((outPin[pin].hiTime = atoi(pChar)) != 0) {
              outPin[pin].active = 1;
              pChar = strchr(pChar, '_') + 1;
              outPin[pin].loTime = atoi(pChar);
              pChar = strchr(pChar, '_') + 1;
              outPin[pin].unit = (unitDef)atoi(pChar);
              outPin[pin].status = HI;
              outPin[pin].stopTime = counter[outPin[pin].unit] + outPin[pin].hiTime;
              digitalWrite(pin, HI);
            } else {
              outPin[pin].active = 0;
              digitalWrite(pin, LO);
            }
          }          
        }
      }
    } else if (strncmp(input, "RESET", 5) == 0) {
      SCB_AIRCR = 0x05FA0004;
    }
    newData = false;
  }

  for (i = 0; i < PIN_NUM; i++) {
    if (outPin[i].active == 1) {
      if (outPin[i].status == HI) {
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          digitalWrite(i, LO);
          if (outPin[i].loTime) {
            outPin[i].startTime = counter[outPin[i].unit] + outPin[i].loTime;
            outPin[i].status = LO;
          } else {
            outPin[i].active == 0;
          }
        }
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          digitalWrite(i, HI);
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].status = HI;
        }
      }
    } else if (outPin[i].active == 2) {
      if (outPin[i].status == HI) {
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          digitalWrite(i, LO);
          outPin[i].startTime = counter[outPin[i].unit] + (seqArr[outPin[i].seqIdx] - outPin[i].hiTime);
          outPin[i].status = LO;
        }
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          digitalWrite(i, HI);
          outPin[i].seqIdx++;
          if (outPin[i].seqIdx > (outPin[i].numVal - 1))
            outPin[i].seqIdx = 0;
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].status = HI;
        }
      }
    } else if (outPin[i].active == 3) {
      if (outPin[i].status == HI) {
        int minval, maxval, randval;
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          digitalWrite(i, LO);
          randval = random(outPin[i].hiTime * 2, outPin[i].loTime);
          outPin[i].startTime = counter[outPin[i].unit] + randval;
          outPin[i].status = LO;
        }
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          digitalWrite(i, HI);
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].status = HI;
        }
      }
    }
  }

#define SWITCH_OFF_AFTER_4h 14400000
#define SWITCH_OFF_AFTER_6h 21600000
#define SWITCH_OFF_AFTER_8h 28800000

  if ((signed long)((lastCmdCounter + SWITCH_OFF_AFTER_4h) - counter[0]) <= 0) {
    SCB_AIRCR = 0x05FA0004;
  } 
}
