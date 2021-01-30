#define INPUT_SIZE_BYTES (1000)
#define INPUT_SIZE_SEQ (100)
#define AZDELIVERY_2_RELAIS

enum unitDef {
  MILLISEC,
  MICROSEC  
};

enum statusHiLo {
  LO,
  HI  
};

enum pinDef {
  RESET,
  SWITCH_ON,
  SIG1,
  KTX,
  SIG2,
  TRIGGER,

  OUT_PIN_NUM
};

struct OutPin {
  int             active;
  int             pin;
  int             inverted;
  int             seqIdx;
  int             numVal;
  char            bitMask;
  unsigned int    hiTime;
  unsigned int    loTime;
  enum unitDef    unit;
  enum statusHiLo setStatus;
  unsigned long   startTime;
  unsigned long   stopTime;
  
};

int i, charIdx, input_idx = 0;
char *pChar;
char input[INPUT_SIZE_BYTES];
char inputByte;
unsigned long counter[2];
const char startMarker = '{';
const char endMarker = '}';
boolean receiving = false;
boolean newData = false;
unsigned int seqArr[INPUT_SIZE_SEQ];

OutPin outPin[OUT_PIN_NUM] = {0};

void setup() {
  outPin[RESET].pin           = 2;
  outPin[SWITCH_ON].pin       = 4;
  outPin[SIG1].pin            = 6;
  outPin[KTX].pin             = 8;
  outPin[SIG2].pin            = 10;
  outPin[TRIGGER].pin         = 12;

   for (int i = 0; i < OUT_PIN_NUM; i++) {
    pinMode(outPin[i].pin, OUTPUT);
  }

  /* AZ-Delivery 2-Relais: input inverted... */
#ifdef AZDELIVERY_2_RELAIS
  outPin[RESET].inverted      = 1;
  outPin[SWITCH_ON].inverted  = 1;  
  digitalWrite(outPin[RESET].pin,HIGH); 
  digitalWrite(outPin[SWITCH_ON].pin,HIGH);
#endif

  outPin[RESET].bitMask     = 0x04;
  outPin[SWITCH_ON].bitMask = 0x10;
  outPin[SIG1].bitMask      = 0x40;
  outPin[KTX].bitMask       = 0x01;
  outPin[SIG2].bitMask      = 0x04;
  outPin[TRIGGER].bitMask   = 0x10;

  Serial.begin(9600); 
}

void loop() {
  counter[0] = millis();
  counter[1] = micros();
  
  if (Serial.available() > 0) {
    inputByte = Serial.read();
//    Serial.println(inputByte);
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
    pChar = strchr(input, '_');
    charIdx = pChar - input;

    if (pChar != NULL) {
      if (strncmp(input, "ON", charIdx) == 0) {
        PORTD &= ~outPin[SWITCH_ON].bitMask;
        outPin[SWITCH_ON].active = 1;
        outPin[SWITCH_ON].unit = MILLISEC;
        outPin[SWITCH_ON].hiTime = atoi(pChar+1);
        outPin[SWITCH_ON].loTime = 0;
        outPin[SWITCH_ON].stopTime = counter[0] + outPin[SWITCH_ON].hiTime;
        outPin[SWITCH_ON].setStatus = HI;
      } else if (strncmp(input, "RST", charIdx) == 0) {
        PORTD &= ~outPin[RESET].bitMask;
        outPin[RESET].active = 1;
        outPin[RESET].unit = MILLISEC;
        outPin[RESET].hiTime = atoi(pChar+1);
        outPin[RESET].loTime = 0;
        outPin[RESET].stopTime = counter[0] + outPin[RESET].hiTime;
        outPin[RESET].setStatus = HI;
      } else if (strncmp(input, "KTX", charIdx) == 0) {
        if ((outPin[KTX].hiTime = atoi(pChar+1)) != 0) {
          outPin[KTX].active = 1;
          pChar = strchr(pChar+1, '_');
          outPin[KTX].loTime = atoi(pChar+1);
          pChar = strchr(pChar+1, '_');
          outPin[KTX].unit = atoi(pChar+1);
          outPin[KTX].setStatus = HI;
          outPin[KTX].stopTime = counter[outPin[KTX].unit] + outPin[KTX].hiTime;
          PORTB |= outPin[KTX].bitMask;
        } else {
          outPin[KTX].active = 0;
          PORTB &= ~outPin[KTX].bitMask;
        }
      } else if (strncmp(input, "TRG", charIdx) == 0) {
        if ((outPin[TRIGGER].hiTime = atoi(pChar+1)) != 0) {
          outPin[TRIGGER].active = 1;
          pChar = strchr(pChar+1, '_');
          outPin[TRIGGER].loTime = atoi(pChar+1);
          pChar = strchr(pChar+1, '_');
          outPin[TRIGGER].unit = atoi(pChar+1);
          outPin[TRIGGER].setStatus = HI;
          outPin[TRIGGER].stopTime = counter[outPin[TRIGGER].unit] + outPin[TRIGGER].hiTime;
          PORTB |= outPin[TRIGGER].bitMask;
        } else {
          outPin[TRIGGER].active = 0;
          PORTB &= ~outPin[TRIGGER].bitMask;
        }
      } else if (strncmp(input, "SIG1", charIdx) == 0) {
        if ((outPin[SIG1].hiTime = atoi(pChar+1)) != 0) {
          outPin[SIG1].active = 1;
          pChar = strchr(pChar+1, '_');
          outPin[SIG1].loTime = atoi(pChar+1);
          pChar = strchr(pChar+1, '_');
          outPin[SIG1].unit = atoi(pChar+1);
          outPin[SIG1].setStatus = HI;
          outPin[SIG1].stopTime = counter[outPin[SIG1].unit] + outPin[SIG1].hiTime;
          PORTD |= outPin[SIG1].bitMask;
        } else {
          outPin[SIG1].active = 0;
          PORTD &= ~outPin[SIG1].bitMask;
        }
      } else if (strncmp(input, "SIG2", charIdx) == 0) {
        if (strncmp(pChar+1, "SEQ", 3) == 0) {
          int err = 0;
          pChar = strchr(pChar+1, '_');
          outPin[SIG2].numVal = atoi(pChar+1);
          pChar = strchr(pChar+1, '_');
          outPin[SIG2].hiTime = atoi(pChar+1);
          if (outPin[SIG2].numVal > INPUT_SIZE_SEQ)
            outPin[SIG2].numVal = INPUT_SIZE_SEQ;
          for (i = 0; i < outPin[SIG2].numVal; i++) {
            pChar = strchr(pChar+1, '_');
            seqArr[i] = atoi(pChar+1);
            if (seqArr[i] < outPin[SIG2].hiTime) {
              err = 1;
              break;
            }
          }
          if (!err) {
            outPin[SIG2].active = 2;
            outPin[SIG2].unit = 0;
            outPin[SIG2].seqIdx = 0;
            outPin[SIG2].setStatus = HI;
            outPin[SIG2].stopTime = counter[outPin[SIG2].unit] + outPin[SIG2].hiTime;
            PORTB |= outPin[SIG2].bitMask;
          }
        } else if (strncmp(pChar+1, "RAND", 4) == 0) {
          int seed;
          pChar = strchr(pChar+1, '_');
          outPin[SIG2].hiTime = atoi(pChar+1);
          pChar = strchr(pChar+1, '_');
          outPin[SIG2].loTime = atoi(pChar+1);
          pChar = strchr(pChar+1, '_');
          seed = atoi(pChar+1);
          outPin[SIG2].unit = 0;
          if ( !seed) {
            randomSeed(analogRead(0));
          } else {
            randomSeed(seed);
          }
          if (outPin[SIG2].hiTime*3 < outPin[SIG2].loTime) {
            outPin[SIG2].active = 3;
            outPin[SIG2].setStatus = HI;
            outPin[SIG2].stopTime = counter[outPin[SIG2].unit] + outPin[SIG2].hiTime;
            PORTB |= outPin[SIG2].bitMask;
          }
        } else {
          if ((outPin[SIG2].hiTime = atoi(pChar+1)) != 0) {
            outPin[SIG2].active = 1;
            pChar = strchr(pChar+1, '_');
            outPin[SIG2].loTime = atoi(pChar+1);
            pChar = strchr(pChar+1, '_');
            outPin[SIG2].unit = atoi(pChar+1);
            outPin[SIG2].setStatus = HI;
            outPin[SIG2].stopTime = counter[outPin[SIG2].unit] + outPin[SIG2].hiTime;
            PORTB |= outPin[SIG2].bitMask;
          } else {
            outPin[SIG2].active = 0;
            PORTB &= ~outPin[SIG2].bitMask;
          }
        }
      }
    }
    newData = false;
  }

  for (i = 0; i < OUT_PIN_NUM; i++) {
    if (outPin[i].active == 1) {
      if (outPin[i].setStatus == HI) {
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
           if (outPin[i].inverted) {
            if (i > SIG1) {
              PORTB |= outPin[i].bitMask;
            } else {
              PORTD |= outPin[i].bitMask;
            }
          } else {
            if (i > SIG1) {
              PORTB &= ~outPin[i].bitMask;
            } else {
              PORTD &= ~outPin[i].bitMask;
            }
          }
          if (outPin[i].loTime) {
            outPin[i].startTime = counter[outPin[i].unit] + outPin[i].loTime;
            outPin[i].setStatus = LO;
          } else {
            outPin[i].active == 0;
          }
        }        
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          if (outPin[i].inverted) {
            if (i > SIG1) {
              PORTB &= ~outPin[i].bitMask;
            } else {
              PORTD &= ~outPin[i].bitMask;
            }
          } else {
            if (i > SIG1) {
              PORTB |= outPin[i].bitMask;
            } else {
              PORTD |= outPin[i].bitMask;
            }
          }

          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].setStatus = HI;
        }  
      }
    } else if (outPin[i].active == 2) {
      if (outPin[i].setStatus == HI) {
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          if (i > SIG1) {
            PORTB &= ~outPin[i].bitMask;
          } else {
            PORTD &= ~outPin[i].bitMask;
          }
          outPin[i].startTime = counter[outPin[i].unit] + (seqArr[outPin[i].seqIdx] - outPin[i].hiTime);
          outPin[i].setStatus = LO;
        }
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          if (i > SIG1) {
            PORTB |= outPin[i].bitMask;
          } else {
            PORTD |= outPin[i].bitMask;
          }
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
          if (i > SIG1) {
            PORTB &= ~outPin[i].bitMask;
          } else {
            PORTD &= ~outPin[i].bitMask;
          }
          randval = random(outPin[i].hiTime*3, outPin[i].loTime);
          outPin[i].startTime = counter[outPin[i].unit] + randval;
          outPin[i].setStatus = LO;
        }
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          if (i > SIG1) {
            PORTB |= outPin[i].bitMask;
          } else {
            PORTD |= outPin[i].bitMask;
          }
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].setStatus = HI;
        }
      }
    }
  }
}
