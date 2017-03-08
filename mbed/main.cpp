#include "mbed.h"
#include "Dht11.h"

/*
Uncomment when sonar implemented
void dist(int distance) // gets called by 'mu' every 0.1 sec
{
   distance *= 0.00328084f; // conv dist mm -> feet
}
ultrasonic sonar(p6, p7, .1, 1, &dist); // p6 = OUTPUT, p7 = CLOCK
*/
DigitalOut myled(LED1);
Serial pc(USBTX, USBRX);
AnalogIn light(p15);
//DHT humid(p16,SEN11301P);
Dht11 humid(p16);
AnalogIn sensor3(p17);
AnalogIn sensor4(p18);
AnalogIn sensor5(p19);
AnalogIn sensor6(p20);

/*
Uncommet when sonar implemented

float g_dist; // for sonar
*/

int main() {
    // TO DO: Put this in a sleep to save energy
    char reqData;
    /*
    Uncomment when sonar implemented
    
    mu.startUpdates();//start measuring the distance
    */
    while(1) {
      // if RPi requests data
      //bool working_flag = false;
      if (pc.readable()) {
      reqData = pc.getc(); // blocking
      if (reqData == '0') {        
      // UncommmenT when HTU21D Humidity / Temp Sensor purchased
        pc.printf("Light,  Humidity,  Temperature (°F),  DISCONNECTED,  DISCONNECTED,  DISCONNECTED");      
      }
      else if (reqData == '1') {
        
        //int  err = humid.readData(); // err is the status code 
        //if (err == 0 || working_flag == true) {
          //working_flag = true;
          humid.read(); // update humidity + temp readings
          pc.printf("%4.4f, %4.4f, %4.4f, %4.4f, %4.4f, %4.4f\n", light.read(), humid.getHumidity(), 1.0*humid.getFahrenheit(), sensor4.read(), sensor5.read(), sensor6.read());
        } else {
          pc.printf("Not printing humidity\n");
        }   
      }
    }
}

