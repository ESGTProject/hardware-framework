#include "mbed.h"
//#include "HTU21D.h"
#include "DHT11.h"

Serial pc(USBTX, USBRX);
float vcc = 3.3;

AnalogIn light(p15); // Light sensor
DHT11 humid(p21); // pwmout... From: https://developer.mbed.org/users/s_inoue_mbed/code/DHT11_Hello_World/file/da7b1c04a659/main.cpp
AnalogIn IR(p16); // Sharp IR 10 - 80 cm
AnalogIn sensor4(p18);
AnalogIn sensor5(p19);
AnalogIn sensor6(p20);


int main() {
    char reqData;
    int state;
    while(1) {
        if (pc.readable()) {
            reqData = pc.getc(); // blocking
            if (reqData == '0') {        
                pc.printf("Light,  Humidity,  Temperature (°F),  ,  DISCONNECTED,  DISCONNECTED");      
            }
            else if (reqData == '1') {                        
                state = humid.readData();
                if (state != DHT11::OK) {
                    pc.printf("ERROR\n");   
                } 
                else {   
                    pc.printf("%4.4f, %d, %4.4f, %4.4f, %4.4f, %4.4f\n", light.read(), humid.readHumidity(), 32.0f + ((float)humid.readTemperature() * (9.0f / 5.0f)), IR.read(), sensor5.read(), sensor6.read());
                    
                }
            } 
            wait(3);
        }
    }
} // end main

