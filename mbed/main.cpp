#include "mbed.h"
#include "Dht11.h" // humidity + temp sensor
/*
Uncomment when HTU21D Humidity / Temp Sensor purchased

#include "HTU21D.h" // for humidity sensor
HTU21D humidity(p9, p10); // Humudity + Temp Sensor || sda, SCL (Uses Serial on mbed)
*/


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
// Delete sensor2 when Humdity / Temp Sensor purchased
Dht11 humid(p30);
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
    
    while(1) 
    {
         /*
         Uncomment when sonar implemented
         
         mu.checkDistance();     //call checkDistance() as much as possible, as this is where
                                //the class checks if dist needs to be called.
        */
        
        if (pc.readable()) // if RPi requests data
        {
            reqData = pc.getc(); // blocking
            
            if (reqData == '0')
            {        
                // UncommmenT when HTU21D Humidity / Temp Sensor purchased
                pc.printf("Light,  Humidity,  Temperature (°F),  DISCONNECTED,  DISCONNECTED,  DISCONNECTED");    
                //pc.printf("Light,  DISCONNECTED,  DISCONNECTED,  DISCONNECTED,  DISCONNECTED,  DISCONNECTED\n");    
                
            }
        
            else if (reqData == '1')
            {
                humid.read(); // read humidity sensor
                pc.printf("%4.4f, %d, %d, %4.4f, %4.4f, %4.4f\n", light.read(), humid.getHumidity(), humid.getFahrenheit(), sensor4.read(), sensor5.read(), sensor6.read());
                /*
                UncommmenT when HTU21D Humidity / Temp  AND sonar Sensor purchased
                pc.printf("%4.4f,%4.4f", light.read(), humidity.sample_humid());
                wait(0.001); // wait b/t reading both values from humidity sensor 
                pc.printf("%4.4f, %4.4f, %4.4f, %4.4f, %4.4f\n", humidity.sample_ftemp(), distance, sensor5.read(), sensor6.read()); // width = 4, precision = 4
                */
            }
            
        } 
    }
}
