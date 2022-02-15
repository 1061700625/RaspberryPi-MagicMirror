//
//mydht11.c
//
#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
 
typedef unsigned char uint8;
typedef unsigned int  uint16;
typedef unsigned long uint32;
 
#define HIGH_TIME 32
 
int pinNumber = 7;  //use gpio1 to read data
uint32 databuf;
 
uint8 readSensorData(void)
{
    uint8 crc; 
    uint8 i;
 
    pinMode(pinNumber,OUTPUT); // set mode to output
    digitalWrite(pinNumber, 1); // output a low level
    delayMicroseconds(4);
    digitalWrite(pinNumber, 0); // output a high level 
    delay(25);
    digitalWrite(pinNumber, 1); // output a low level
    delayMicroseconds(60); 
    pinMode(pinNumber, INPUT); // set mode to input
    pullUpDnControl(pinNumber,PUD_UP);
 
    if(digitalRead(pinNumber)==0) //SENSOR ANS
    {
        while(!digitalRead(pinNumber)); //wait to high
        delayMicroseconds(80);
        for(i=0;i<32;i++)
        {
          while(digitalRead(pinNumber)); //data clock start
          while(!digitalRead(pinNumber)); //data start
          delayMicroseconds(HIGH_TIME);
          databuf*=2;
          if(digitalRead(pinNumber)==1) //1
          {
            databuf++;
          }
        }
 
        for(i=0;i<8;i++)
        {
          while(digitalRead(pinNumber)); //data clock start
          while(!digitalRead(pinNumber)); //data start
          delayMicroseconds(HIGH_TIME);
          crc*=2;  
          if(digitalRead(pinNumber)==1) //1
          {
            crc++;
          }
        }
      return 1;
    }
    else
    {
      return 0;
    }
}
 
int main (void)
{
    if (-1 == wiringPiSetup()) {
      //printf("Setup wiringPi failed!");
      return 1;
    }
 
    pinMode(pinNumber, OUTPUT); // set mode to output
    digitalWrite(pinNumber, 1); // output a high level 
 
    //while(1) 
    //{
    pinMode(pinNumber,OUTPUT); // set mode to output
    digitalWrite(pinNumber, 1); // output a high level 
    //delay(3000);
    if(readSensorData())
    {
      //printf("OK!\n");
      //printf("RH:%d.%d\n",(databuf>>24)&0xff,(databuf>>16)&0xff); 
      //printf("TMP:%d.%d\n",(databuf>>8)&0xff,databuf&0xff);
      printf("{\"RH\":\"%d.%d\", \"TMP\":\"%d.%d\"}",(databuf>>24)&0xff,(databuf>>16)&0xff,(databuf>>8)&0xff,databuf&0xff);
      databuf=0;
    }
    else
    {
      printf("");
      databuf=0;
    }
    //}
  return 0;
}
