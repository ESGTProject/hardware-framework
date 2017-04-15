/*
  ECE 4012 Senior Design project,
  Author: Jonathan, Boa-Lin Lai
  edit: applied thread and ticker for humid/temp sensor.
*/

#include "mbed.h"
#include "DHT11.h"
#include <vector>
#include "rtos.h"
Ticker DHT; // ticker object
Serial pc(USBTX, USBRX);
float vcc = 3.3;
AnalogIn light(p15); // Light sensor
DHT11 humid(p21); // pwmout... From: https://developer.mbed.org/users/s_inoue_mbed/code/DHT11_Hello_World/file/da7b1c04a659/main.cpp
AnalogIn IR(p16); // Sharp IR 10 - 80 cm
AnalogIn sensor4(p18);
AnalogIn sensor5(p19);
AnalogIn sensor6(p20);

volatile int state;
// init buffer
volatile float sensor_buffer[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
void get_DHT() {
  state = humid.readData();
  if (state != DHT11::OK) {
    pc.printf("ERROR\n");   
  } else { 
    sensor_buffer[1] = humid.readHumidity()*1.0f;
    sensor_buffer[2] = 32.0f + ((float)humid.readTemperature() * (9.0f / 5.0f));
  }
}
void get_other_sensors() {
  sensor_buffer[0] = light.read();
  sensor_buffer[3] = IR.read();
}
void DHT_thread() {
  while (true) {
        get_DHT();
        Thread::wait(3000);
  }  
}
int main() {
    Thread t2;
    t2.start(DHT_thread);
    char reqData;
    //DHT.attach(&get_DHT, 3.0);
    DHT.attach(&get_other_sensors, 0.2);
    //buffer = vector<float>(6,0);
    while(1) {
        if (pc.readable()) {
            reqData = pc.getc(); // blocking
            if (reqData == '0') {        
                pc.printf("Light,  Humidity,  Temperature (°F),  ,  DISCONNECTED,  DISCONNECTED");      
            }
            else if (reqData == '1') {                         
                    //pc.printf("%4.4f, %d, %4.4f, %4.4f, %4.4f, %4.4f\n", light.read(), humid.readHumidity(), 32.0f + ((float)humid.readTemperature() * (9.0f / 5.0f)), IR.read(), sensor5.read(), sensor6.read());
                    pc.printf("%4.4f, %4.4f, %4.4f, %4.4f, %4.4f, %4.4f\n", 
                               sensor_buffer[0],
                               sensor_buffer[1],
                               sensor_buffer[2], 
                               sensor_buffer[3],
                               sensor_buffer[4], 
                               sensor_buffer[5]);
            } 
        }
    }
} // end main

