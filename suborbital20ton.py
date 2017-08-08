import time
import krpc
# import GravityTurn
conn = krpc.connect(name='20 Ton Lifter Program')
vessel = conn.space_center.active_vessel

def launch():
    print('Commencing Launch Sequence...')
    vessel.auto_pilot.target_pitch_and_heading(90,90)
    vessel.auto_pilot.engage()
    vessel.control.throttle = 1
    for i in range(5,0,-1):
        print(i,'...')
        time.sleep(1)
    vessel.control.activate_next_stage()
    print('Ignition!')

def SRB():
        while vessel.resources.amount('SolidFuel') > 0.1:
            time.sleep(1)
        print('Booster Seperation')
        vessel.control.activate_next_stage()

def gravityTurn():
    print('Gravity Turn Guidence Engaged')
    while vessel.flight().mean_altitude < 10000:
        time.sleep(1)
    print('Gravity Turn Initiated')
    # vessel.auto_pilot.target_pitch_and_heading(60,90)
    pitch = 90
    while pitch > -1:
        vessel.auto_pilot.target_pitch_and_heading(pitch,90)
        time.sleep(1)
        if vessel.orbit.time_to_apoapsis > 40 :
            pitch = pitch - 1
        # elif  vessel.orbit.time_to_apoapsis < 40 and pitch < 90 :
        #     pitch = pitch + 1
        else:
            continue
    print('Gravity Turn Complete')

def oInsert():
    print('Accelerating cargo to max sub-orbital position')
    while vessel.orbit.apoapsis < 700000 and vessel.orbit.periapsis < 630000:
        # vessel.auto_pilot.target_direction = vessel.flight().prograde
        vessel.auto_pilot.target_pitch_and_heading(0,90)
        vessel.control.throttle = 1
        # time.sleep(1)
        # if vessel.orbit.periapsis > 630000:
        #     throttle = 0
        # elif throttle <= 1:
        #     throttle = throttle + .2
        # else: continue
    vessel.control.throttle = 0
    print('MECO... Remaining Fuel:', vessel.resources.amount('LiquidFuel'))
    vessel.control.activate_next_stage()
    print('Fairings Deployed')
    vessel.control.activate_next_stage()
    print(vessel.orbit.apoapsis, vessel.orbit.periapsis)


launch()
SRB()
gravityTurn()
oInsert()
