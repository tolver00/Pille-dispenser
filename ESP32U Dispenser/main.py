import gc
gc.collect()
import time
import network
import ntptime
from machine import Pin, RTC, lightsleep, reset
import requests
import json
import pid_motorfunction

def time_ms_until_next_pill(hour1,hour2,minute_current,second_current):
    
    buffer_time = 120000
    
    if hour1 < hour2:
        print(hour1, hour2)
        return (hour2-hour1)*3600000-((minute_current*60000)+(second_current*1000)+buffer_time)
    
    elif hour1 > hour2 or hour1 == hour2:
        return (24-hour1+hour2)*3600000-((minute_current*60000)+(second_current*1000)+buffer_time)

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    print('WLAN status:', wlan.status())
    wlan.active(True)
    
    try:
        if not wlan.isconnected():
            print('connecting to network...')
            wlan.connect('x','x')
            print('WLAN status:', wlan.status())
            start = time.ticks_ms()
            while not wlan.isconnected():
                if time.ticks_ms() - start > 10000:
                    print("Could not connect to wifi!")
                    break

    except Exception as e:
        print(f"WiFi error '{e}' occured, rebooting system")
        reset()
    finally:
        if wlan.isconnected():
            print("Connected to wifi!")
            print(f"wifi statuscode {wlan.status()}")
    return wlan  

timer_runs = 1

wlan=do_connect()

rtc = RTC()

ntptime.settime()
utc_offset = list(rtc.datetime())
utc_offset[4] = utc_offset[4] + 1
rtc.datetime(tuple(utc_offset))

request_data = requests.get('http://172.20.0.2:41000/fetch_patient_timestamps/2')
check_data = json.loads(request_data.content)
print('get request data', check_data)

with open('time.txt') as file:
     time_data = file.read()
     fixed_time_data = time_data.replace("'", "\"")
     time_data = json.loads(fixed_time_data)

# checker om der er kommet opdateringer til pillerne og hvis der er opdater .txt filen
if check_data['start_date'] != time_data['start_date'] and check_data['end_date'] != time_data['end_date']:
    with open('time.txt', 'w') as file:
        file.write(str(check_data))
        file.close()
    time_data = check_data
    

timestamps = tuple(time_data['timestamps'].split('-'))


while True:
    
    if rtc.datetime()[4] == int(timestamps[timer_runs]):
        
        pid_motorfunction.dispense_pills()
        send_heartbeat = requests.post('http://172.20.0.2:41000/device/heartbeat/ESP32')
        
        
        if timer_runs == len(timestamps)-1: #genstart state når alle tider har været igennem
            timer_runs = 0
            print(time_ms_until_next_pill(int(timestamps[len(timestamps)-1]), int(timestamps[timer_runs]), rtc.datetime()[5], rtc.datetime()[6]))
            time.sleep(3)
            lightsleep(time_ms_until_next_pill(int(timestamps[len(timestamps)-1]), int(timestamps[timer_runs]), rtc.datetime()[5], rtc.datetime()[6]))
                
        else: #eller skift til næste state
            timer_runs += 1
            print(time_ms_until_next_pill(int(timestamps[timer_runs-1]), int(timestamps[timer_runs]), rtc.datetime()[5], rtc.datetime()[6]))
            time.sleep(3)
            lightsleep(time_ms_until_next_pill(int(timestamps[timer_runs-1]), int(timestamps[timer_runs]), rtc.datetime()[5], rtc.datetime()[6]))
        
        
        
        
        

