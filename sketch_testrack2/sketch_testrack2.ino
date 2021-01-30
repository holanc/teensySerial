#define INPUT_SIZE_BYTES (16)

enum unitDef {
  MILLISEC,
  MICROSEC  
};

enum statusHiLo {
  LO,
  HI  
};

enum pinDef {
  
  TRIGGER,
  CONVEYOR_CYCLE,
  SWITCH_ON,
  RESET,
  

  OUT_PIN_NUM
};

struct OutPin {
  int             active;
  int             pin;
  char            bitMask;
  unsigned int    hiTime;
  unsigned int    loTime;
  enum unitDef    unit;
  enum statusHiLo setStatus;
  unsigned long   startTime;
  unsigned long   stopTime;
};

int bytesCount, i, charIdx;
char *pChar;
char input[INPUT_SIZE_BYTES];
unsigned long counter[2];

OutPin outPin[OUT_PIN_NUM] = {0};

void setup() {
  outPin[RESET].pin           = 6;
  outPin[SWITCH_ON].pin       = 8;
  outPin[CONVEYOR_CYCLE].pin  = 10;
  outPin[TRIGGER].pin         = 12;

  outPin[TRIGGER].bitMask         = 0x10;
  outPin[CONVEYOR_CYCLE].bitMask  = 0x4;
  outPin[SWITCH_ON].bitMask       = 0x1;
  outPin[RESET].bitMask           = 0x1 << 6;
  
  for (int i = 0; i < OUT_PIN_NUM; i++) {
    pinMode(outPin[i].pin, OUTPUT);
  }
  Serial.begin(9600); 
}

void loop() {
  counter[0] = millis();
  counter[1] = micros();
  
  if (Serial.available() > 0) {
    bytesCount = Serial.readBytes(input, INPUT_SIZE_BYTES);
    input[bytesCount-1] = 0;
    pChar = strchr(input, '_');
    charIdx = pChar - input;
//    Serial.write(input);

    if (pChar != NULL) {
      if (strncmp(input, "ON", charIdx) == 0) {
//        Serial.print(input);
        PORTB |= outPin[SWITCH_ON].bitMask;
        outPin[SWITCH_ON].active = 1;
        outPin[SWITCH_ON].unit = MILLISEC;
        outPin[SWITCH_ON].hiTime = atoi(pChar+1);
        outPin[SWITCH_ON].loTime = 0;
        outPin[SWITCH_ON].stopTime = counter[0] + outPin[SWITCH_ON].hiTime;
        outPin[SWITCH_ON].setStatus = HI;
      } else if (strncmp(input, "RST", charIdx) == 0) {
//        Serial.print(input);
        PORTD |= outPin[RESET].bitMask;
        outPin[RESET].active = 1;
        outPin[RESET].unit = MILLISEC;
        outPin[RESET].hiTime = atoi(pChar+1);
        outPin[RESET].loTime = 0;
        outPin[RESET].stopTime = counter[0] + outPin[RESET].hiTime;
        outPin[RESET].setStatus = HI;
      } else if (strncmp(input, "KTX", charIdx) == 0) {
        if ((outPin[CONVEYOR_CYCLE].hiTime = atoi(pChar+1)) != 0) {
          outPin[CONVEYOR_CYCLE].active = 1;
          pChar = strchr(pChar+1, '_');
          outPin[CONVEYOR_CYCLE].loTime = atoi(pChar+1);
          pChar = strchr(pChar+1, '_');
          outPin[CONVEYOR_CYCLE].unit = atoi(pChar+1);
          outPin[CONVEYOR_CYCLE].setStatus = HI;
          outPin[CONVEYOR_CYCLE].stopTime = counter[outPin[CONVEYOR_CYCLE].unit] + outPin[CONVEYOR_CYCLE].hiTime;
          PORTB |= outPin[CONVEYOR_CYCLE].bitMask;
        } else {
          outPin[CONVEYOR_CYCLE].active = 0;
          PORTB &= ~outPin[CONVEYOR_CYCLE].bitMask;
        }
      } else if (strncmp(input, "TRG", charIdx) == 0) {
        Serial.print(input);
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
      }    
    } else {
      PORTB |= outPin[SWITCH_ON].bitMask;
      outPin[SWITCH_ON].active = 1;
      outPin[SWITCH_ON].unit = MILLISEC;
      outPin[SWITCH_ON].hiTime = 2000;
      outPin[SWITCH_ON].loTime = 0;
      outPin[SWITCH_ON].stopTime = counter[0] + outPin[SWITCH_ON].hiTime;
      outPin[SWITCH_ON].setStatus = HI;
    }
  }

  for (i = 0; i < OUT_PIN_NUM-1; i++) {
    if (outPin[i].active == 1) {
      if (outPin[i].setStatus == HI) {
        if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
          PORTB &= ~outPin[i].bitMask;
          if (outPin[i].loTime) {
            outPin[i].startTime = counter[outPin[i].unit] + outPin[i].loTime;
            outPin[i].setStatus = LO;
          } else {
            outPin[i].active == 0;
          }
        }        
      } else {
        if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
          PORTB |= outPin[i].bitMask;
          outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
          outPin[i].setStatus = HI;
        }  
      }
    }
  }
  
  if (outPin[i].active == 1) {
    if (outPin[i].setStatus == HI) {
      if (((signed long)(outPin[i].stopTime - counter[outPin[i].unit])) <= 0) {
        PORTD &= ~outPin[i].bitMask;
        if (outPin[i].loTime) {
          outPin[i].startTime = counter[outPin[i].unit] + outPin[i].loTime;
          outPin[i].setStatus = LO;
        } else {
          outPin[i].active == 0;
        }
      }        
    } else {
      if (((signed long)(outPin[i].startTime - counter[outPin[i].unit])) <= 0) {
        PORTD |= outPin[i].bitMask;
        outPin[i].stopTime = counter[outPin[i].unit] + outPin[i].hiTime;
        outPin[i].setStatus = HI;
      }  
    }
  }
}
