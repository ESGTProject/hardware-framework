#include "mbed.h"
#define DISCONNECTED = "null"

DigitalOut myled(LED1);
Serial pc(USBTX, USBRX);
AnalogIn light(p15);
AnalogIn sensor2(p16);
AnalogIn sensor3(p17);
AnalogIn sensor4(p18);
AnalogIn sensor5(p19);
AnalogIn sensor6(p20);

int main() {
    // TO DO: Put this in a sleep to save energy
    
    char reqData;
    
    while(1) 
    {
        if (pc.readable()) // if RPi requests data
        {
            reqData = pc.getc(); // blocking
            
            if (reqData == '0')        
                pc.printf("Light,  DISCONNECTED,  DISCONNECTED,  DISCONNECTED,  DISCONNECTED,  DISCONNECTED");    
        
            else if (reqData == '1')
            {
                pc.printf("%4.4f,%4.4f,%4.4f,%4.4f,%4.4f,%4.4f\n", light.read(), sensor2.read(), sensor3.read(), sensor4.read(), sensor5.read(), sensor6.read()); // width = 4, precision = 4
            }
        } 
    }
}
