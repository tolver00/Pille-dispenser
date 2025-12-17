from machine import PWM, Pin
from rotary_irq_esp import RotaryIRQ
import time

def dispense_pills():

    prev_time = 0
    prev_error = 0
    error_integral = 0
    target = 11

    IN1 = PWM(16)
    IN2 = PWM(4)
    IN3 = Pin(17, Pin.OUT)
    IN4 = Pin(5, Pin.OUT)

    encoder = RotaryIRQ(pin_num_clk=18,
                  pin_num_dt=19,
                  reverse=True,
                  range_mode=RotaryIRQ.RANGE_UNBOUNDED)

    pos_old = encoder.value()

    def setMotor(direction,pwr,IN1,IN2):
        
        if direction == 1:
            IN2 = Pin(4, Pin.OUT)
            IN2.value(0)
            IN1 = PWM(16)
            IN1.freq(1000)
            IN1.duty(1023)
            time.sleep_ms(1)
            IN1.duty(pwr)
            
        elif direction == -1:
            IN1 = Pin(16, Pin.OUT)
            IN1.value(0)
            IN2 = PWM(4)
            IN2.freq(1000)
            IN2.duty(1023)
            time.sleep_ms(1)
            IN2.duty(pwr)
            
        else:
            IN1 = Pin(16, Pin.OUT)
            IN1.value(0)
            IN2 = Pin(4, Pin.OUT)
            IN2.value(0)
            stop = True

    while True:
        pos = encoder.value()
        
        if pos_old != pos:
            pos_old = pos
        
        # PID constants
        kp = 1
        kd = 0.00
        ki = 0.00

        # time difference
        current_time = time.ticks_ms()
        deltaT = current_time - prev_time
        prev_time = current_time

        # error
        error= target - pos

        # derivative
        if deltaT == 0:
            dedt = 0
        else:
            dedt = (error- prev_error ) / deltaT

        # integral
        error_integral = error_integral +error * deltaT

        # control signal
        u = kp * error + kd * dedt + ki * error_integral
        

        # motor power
        pwr = abs(int(u))
        
        
        if pwr > 1023:
            pwr = 1023


        # motor direction
        
        if u < 0:
            direction = -1
            
        if u > 0:
            direction = 1
        
        if u == 0:
            direction = 0
            
            
        # signal the motor
        setMotor(direction,pwr,IN1,IN2)
        
        
        if direction == 0:
            break
    


        # store previous error
        prev_error = error
        
        
        time.sleep_ms(10)
    
    IN3.value(1)
    time.sleep_ms(400)
    IN3.value(0)


