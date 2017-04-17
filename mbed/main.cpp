/*
  ECE 4012 Senior Design project,
  Author: Jonathan Osei-Owusu, Boa-Lin Lai
  Edit 04/15/17: Applied thread and ticker for humid/temp sensor.
*/

#include "mbed.h"
#include "DHT11.h"
#include <vector>
#include "rtos.h"

Ticker DHT; // ticker object
Serial pc(USBTX, USBRX);
float vcc = 3.3;
const int number_of_sensor = 6;
AnalogIn light(p15); // Light sensor
DHT11 humid(p21); // pwmout... From: https://developer.mbed.org/users/s_inoue_mbed/code/DHT11_Hello_World/file/da7b1c04a659/main.cpp
AnalogIn sensor3(p16); // Sharp IR 10 - 80 cm
AnalogIn sensor4(p18);
AnalogIn sensor5(p19);
AnalogIn sensor6(p20);

volatile int state;
// init buffer
volatile float sensor_buffer[number_of_sensor];

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
  sensor_buffer[3] = sensor3.read();
}

void DHT_thread() {
  while (true) {
        get_DHT();
        Thread::wait(3000);
  }  
}
void init_buffer() {
  for (int i = 0; i < number_of_sensor; i++) {
    sensor_buffer[i] = 0.0;
  }   
}

int main() {
  init_buffer();
  Thread t2;
  t2.start(DHT_thread); 
  char reqData;
  DHT.attach(&get_other_sensors, 0.2);
  while(1) {
    if (pc.readable()) {
      reqData = pc.getc(); // blocking
      if (reqData == '0') {        
       pc.printf("Light, Humidity, Temperature (F), DISCONNECTED, DISCONNECTED, DISCONNECTED");      
      } else if (reqData == '1') { 
        for (int i = 0; i < number_of_sensor; i++) {
          pc.printf("%4.4f",sensor_buffer[i]);
          if (i != number_of_sensor -1) pc.printf(","); // print the common instead of last one
        }
      } 
    }
  }
} // end main

