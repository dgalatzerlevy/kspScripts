#landing form 15250

import krpc
import time
import math


#Setup Connection
conn = krpc.connect(name='Python Lander')
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

def landing():
    scroll_text('Landing program initiated')
    srf_frame = vessel.orbit.body.reference_frame
    srf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
    situation = conn.add_stream(getattr, vessel, 'situation')
    g = conn.space_center.bodies['Duna'].surface_gravity

    sas_reset()
    vessel.control.sas_mode = vessel.control.sas_mode.retrograde
    if srf_altitude() > 50000:
        conn.space_center.rails_warp_factor = conn.space_center.maximum_rails_warp_factor
    scroll_text('Aerobraking')
    scroll_text('')
    while srf_altitude() > 50000:
        text3.content = ('falling: %d' % srf_altitude())
        time.sleep(1)

    conn.space_center.physics_warp_factor = 3

    while srf_altitude() > 5000:
        text3.content = ('falling: %d' % srf_altitude())
        time.sleep(1)

    conn.space_center.physics_warp_factor = 0
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

landing()