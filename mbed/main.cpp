#include "mbed.h"
#include "Dht11.h"


DigitalOut myled(LED1);
Serial pc(USBTX, USBRX);
Ticker tick;
float valIR = 0;

AnalogIn light(p15);
//DHT humid(p18,SEN11301P);
Dht11 humid(p16);
AnalogIn IR(p17); // Sharp IR 10 - 80 cm
AnalogIn sensor4(p18);
AnalogIn sensor5(p19);
AnalogIn sensor6(p20);

void averageIR()
{ // 1 sec total time
    float val = 0;
    for (int i = 0; i < 10; i++) {
        // sum of 10 samples
        val += IR.read();
        wait (0.1);
    }
    // take avg. Scale from 0.0 - 1.0
     valIR = (val / 10.0f) / 3.3f; // set global
     return;  
}

int main() {
    // TO DO: Put this in a sleep to save energy
    char reqData;
    // call every 5 sec
    tick.attach(&averageIR, 5.0); 
    while(1) {
      // if RPi requests data
      //bool working_flag = false;
        if (pc.readable()) {
            reqData = pc.getc(); // blocking
            if (reqData == '0') {        
                pc.printf("Light,  Humidity,  Temperature (°F),  DISCONNECTED,  DISCONNECTED,  DISCONNECTED");      
            }
            else if (reqData == '1') {
            
            //TO DO :  Refer to page 5 of  http://www.sharp-world.com/products/device/lineup/data/pdf/datasheet/gp2y0a21yk_e.pdf
            // Use this for distance
        
                humid.read(); // Required. Update humidity + temp readings
                pc.printf("%4.4f, %4.4f, %4.4f, %4.4f, %4.4f, %4.4f\n", light.read(), humid.getHumidity(), humid.getFahrenheit(), (valIR / 3.3f), sensor5.read(), sensor6.read());
            } else {
                pc.printf("Not printing humidity\n");
            }   
        }
    }
} // end main

