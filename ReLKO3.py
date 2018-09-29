# 15 Ton >2.5m Reusable. Attach payload to fairing.

import math
import time
import krpc

time_start = time.time()

#Setup Connection
conn = krpc.connect(name='Python1 Reusable Rocket Program2')
vessel = conn.space_center.active_vessel


#Create the display:
canvas = conn.ui.stock_canvas
screen_size = canvas.rect_transform.size
panel = canvas.add_panel()
rect = panel.rect_transform
rect.size =(200,80)
rect.position = (110-(screen_size[0]/2), 400)
text = panel.add_text('Loading Program')
text.rect_transform.position = (0, 20)
text.color = (1, 1, 1)
text.size = 18
text2 = panel.add_text("")
text2.rect_transform.position = (0, 0)
text2.color = (1, 1, 1)
text2.size = 18
text3 = panel.add_text("")
text3.rect_transform.position = (0, -20)
text3.color = (1, 1, 1)
text3.size = 18

def scroll_text(new_text):
    text.content = text2.content
    text2.content = text3.content
    text3.content = new_text

scroll_text('Systems Active...')
time.sleep(0.5)


def sas_reset():
    vessel.control.sas = False
    time.sleep(0.05)
    vessel.control.sas = True
    vessel.control.sas_mode = vessel.control.sas_mode.stability_assist
    scroll_text('SAS Reset')
    time.sleep(0.05)


def assent():
    scroll_text('Initiating...')
    time.sleep(1)
    # Establish Launch Parameters:
    scroll_text('Loading Settings...')
    time.sleep(0.5)

    pressure_limit = 20000
    scroll_text('Q-limit: %d' % pressure_limit)
    time.sleep(0.5)

    turn_start_altitude = 500
    scroll_text('Start Turn: %d' % turn_start_altitude)
    time.sleep(0.5)

    turn_end_altitude = 35000
    scroll_text('End Turn: %d' % turn_end_altitude)
    time.sleep(0.5)

    target_altitude = 75000
    scroll_text('Final Orbit: %d' % target_altitude)
    time.sleep(0.5)

    sas_reset()
    vessel.control.rcs = False
    vessel.control.throttle = 1
    scroll_text('Throttle to 100%')
    time.sleep(0.5)
    for i in range(3,0,-1):
        scroll_text('%d ...' % i)
        time.sleep(1)
    scroll_text('Launch!')
    vessel.control.activate_next_stage()



    # GRAVITY TURN GOES HERE
    scroll_text('Initiated assent program')
    vessel.auto_pilot.engage()
    scroll_text('Autopilot engaged')
    vessel.auto_pilot.target_pitch_and_heading(90, 90)
    turn_angle = 0

    srf_frame = vessel.orbit.body.reference_frame
    dynamic_pressure = conn.add_stream(getattr, vessel.flight(srf_frame), 'dynamic_pressure')
    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
    while True:

        if dynamic_pressure() / pressure_limit > 1:
            x = 0.5 - (dynamic_pressure() / pressure_limit) / 5
            vessel.control.throttle = x
        elif dynamic_pressure() / pressure_limit < 0.8:
            vessel.control.throttle = 1
        else:
            x = float((1 - dynamic_pressure() / pressure_limit) + 0.8)
            vessel.control.throttle = x

        if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
            frac = ((altitude() - turn_start_altitude) /
                    (turn_end_altitude - turn_start_altitude))
            new_turn_angle = frac * 90

            if abs(new_turn_angle - turn_angle) > 0.5:
                turn_angle = new_turn_angle
                vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

        if apoapsis() > target_altitude * 0.9:
            scroll_text('Approaching target apoapsis')
            break

        time.sleep(0.1)

    vessel.control.throttle = 0.25

    while apoapsis() < target_altitude:
        time.sleep(0.1)
    scroll_text('Target Apoapsis Reached')
    vessel.control.throttle = 0.0
    vessel.auto_pilot.disengage()
    vessel.control.sas = True
    time.sleep(0.1)
    vessel.control.sas_mode = vessel.control.sas_mode.prograde
    time.sleep(5)
    scroll_text('Coasting out of the Atmosphere')
    conn.space_center.physics_warp_factor = 3

    while altitude() < 70500:
        time.sleep(0.1)

    conn.space_center.physics_warp_factor = 0
    vessel.control.activate_next_stage()
    scroll_text('Fairing Deployed')


def cirucularization():
    # Plan circularization burn (using vis-viva equation)
    scroll_text('Planning circularization burn')
    ut = conn.add_stream(getattr, conn.space_center, 'ut')
    mu = vessel.orbit.body.gravitational_parameter
    r = vessel.orbit.apoapsis
    a1 = vessel.orbit.semi_major_axis
    a2 = r
    v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
    v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
    delta_v = v2 - v1
    node = vessel.control.add_node(
        ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

    # Calculate burn time (using rocket equation)
    F = vessel.available_thrust
    Isp = vessel.specific_impulse * 9.82
    m0 = vessel.mass
    m1 = m0 / math.exp(delta_v / Isp)
    flow_rate = F / Isp
    burn_time = (m0 - m1) / flow_rate


    scroll_text('Waiting until circularization burn')
    burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time / 2.)
    lead_time = 15
    conn.space_center.warp_to(burn_ut - lead_time)

    scroll_text('Locking Gimbals')
    for engine in vessel.parts.engines:
        engine.gimbal_locked = True

    # Execute burn
    scroll_text('Ready to execute burn')
    time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
    #  Orientate ship
    vessel.control.sas_mode = vessel.control.sas_mode.maneuver
    time.sleep(10)
    while time_to_apoapsis() - (burn_time / 2.) > 0:
        time.sleep(0.1)
    scroll_text('Executing burn')
    vessel.control.throttle = 1.0
    time.sleep(burn_time - 0.1)
    scroll_text('Fine tuning')
    vessel.control.throttle = 0.05
    remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
    while remaining_burn()[1] > 1:
        time.sleep(0.1)
    vessel.control.throttle = 0.0
    node.remove()

    scroll_text('Launch complete')
    vessel.control.activate_next_stage()
    scroll_text('Payload Deployed')
    time.sleep(2)




def reentry():
    obt_frame = vessel.orbit.body.non_rotating_reference_frame
    long = conn.add_stream(getattr, vessel.flight(obt_frame), 'longitude')
    vessel.control.speed_mode = vessel.control.speed_mode.surface

    time.sleep(1)
    scroll_text('Moving to Reentry')
    angle = 73
    position = 0
    ksc_loc = (1.301492 - angle * math.pi / 180)
    conn.space_center.rails_warp_factor = conn.space_center.maximum_rails_warp_factor
    while abs(position - ksc_loc) < 5.9:
        position = (long() + 180) * math.pi / 180
        print(round(abs(position - ksc_loc), 5), "waiting")
        time.sleep(1)

    conn.space_center.rails_warp_factor = 0
    scroll_text('Approaching Reentry')
    sas_reset()
    vessel.control.sas_mode = vessel.control.sas_mode.retrograde

    while abs(position - ksc_loc) > 0.01:
        position = (long() + 180) * math.pi / 180
        print(round(abs(position - ksc_loc), 5))
        time.sleep(1)

    time.sleep(1)
    scroll_text('De-orbiting')
    while (vessel.orbit.periapsis_altitude > 0):
        vessel.control.throttle = 0.05
    vessel.control.throttle = 0.0
    scroll_text('De-orbit complete')

def landing():
    scroll_text('Landing program initiated')
    srf_frame = vessel.orbit.body.reference_frame
    srf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
    situation = conn.add_stream(getattr, vessel, 'situation')
    g = conn.space_center.bodies['Kerbin'].surface_gravity

    sas_reset()
    vessel.control.sas_mode = vessel.control.sas_mode.retrograde
    time.sleep(1)
    conn.space_center.rails_warp_factor = conn.space_center.maximum_rails_warp_factor
    scroll_text('Aerobraking')
    scroll_text('')
    if srf_altitude() > 70000:
        conn.space_center.rails_warp_factor = conn.space_center.maximum_rails_warp_factor
    while srf_altitude() > 5000:
        text3.content = ('falling: %d' % srf_altitude())
        time.sleep(1)

    vessel.control.activate_next_stage()
    scroll_text('Drogues Deployed')
    scroll_text('')

    while srf_altitude() > 2300:
        text3.content = ('falling: %d' % srf_altitude())
        time.sleep(1)

    vessel.control.gear = True
    vessel.control.activate_next_stage()
    scroll_text('Chutes Deployed')
    scroll_text('Gear Lowered')
    scroll_text('')

    while srf_altitude() > 50:
        text3.content = ('falling: %d' % srf_altitude())
        time.sleep(1)

    # while situation() != conn.space_center.VesselSituation.landed and situation() != conn.space_center.VesselSituation.splashed:
    while srf_altitude() > 0:
        weight = vessel.mass * g
        thrust = vessel.mass * ((srf_speed() ** 2) / 2 + srf_altitude() * g) / (srf_altitude())
        hover_thrust = weight / vessel.max_thrust
        active_throttle = thrust / vessel.max_thrust
        if srf_speed() < 1.0:
            active_throttle = hover_thrust - 0.02
        vessel.control.throttle = active_throttle
        text3.content = 'Throttle at %d' % (active_throttle * 100)
        text2.content = 'Speed %d m/s' % srf_speed()
        text.content = 'Altitude %d' % srf_altitude()
        if situation() == conn.space_center.VesselSituation.landed or situation() == conn.space_center.VesselSituation.splashed:
            break

    vessel.control.throttle = 0
    text3.content = ''
    text2.content = ''
    text.content = 'Landing Complete'
    time.sleep(3)

    # if vessel.recoverable:
    #     vessel.recover()




assent()
cirucularization()

reentry()
landing()
conn.close()

print('Total Runtime: %d min' % round((time.time()-time_start)/60, 4))