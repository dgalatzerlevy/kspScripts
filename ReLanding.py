import krpc
import time
conn = krpc.connect(name='Landing Program')
vessel = conn.space_center.active_vessel
srf_frame = vessel.orbit.body.reference_frame
srf_altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
srf_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'speed')
situation = conn.add_stream(getattr, vessel, 'situation')
g = conn.space_center.bodies['Kerbin'].surface_gravity
vert_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'vertical_speed')
horz_speed = conn.add_stream(getattr, vessel.flight(srf_frame), 'horizontal_speed')


try:
    weight = vessel.mass * g
    hoverthrust = weight / vessel.max_thrust
    twr = vessel.thrust / weight
except:
    print('Starting Engines')
    vessel.control.throttle = 0
    vessel.control.activate_next_stage()

time_start = time.time()
vessel.control.sas = True
vessel.control.activate_next_stage()


# try:
#     vessel.control.sas_mode = vessel.control.sas_mode.retrograde
# except:
#     pass
#
# while srf_altitude() > 250:
#     time.sleep(1)
#     print('holding')

# vessel.control.sas_mode = vessel.control.sas_mode.retrograde
vessel.control.rcs = True
vessel.control.brakes = True
vessel.control.lights = True
vessel.control.sas_mode = vessel.control.sas_mode.retrograde
active_throttle = 1
vessel.control.throttle = active_throttle
active_throttle = 0
vessel.control.throttle = active_throttle

while srf_altitude() > 1550:
    thrust = vessel.mass * ((srf_speed() ** 2) / 2 + (srf_altitude()) * g) / (srf_altitude())
    active_throttle = thrust / vessel.max_thrust
    if active_throttle < 0.9:
        vessel.control.throttle = 0
        print('falling! %d' % srf_altitude(), end='\r')
        time.sleep(0.5)
    else:
        vessel.control.throttle = active_throttle - 0.5
        print('slowing')
        time.sleep(0.5)
    print('throttle:', vessel.control.throttle, 'active_throttle: ', active_throttle)


while srf_altitude() <= 1550:
    vessel.control.gear = True
    while situation() != conn.space_center.VesselSituation.landed:
        weight = vessel.mass * g
        hover_thrust = weight / vessel.max_thrust
        twr = vessel.thrust/weight
        # if round(time.time()-timer)%3 == 0:
        #     print(weight, srf_altitude())

        # thrust = vessel.mass*((srf_speed()**2)/2+srf_altitude()*g)/(srf_altitude())
        thrust = vessel.mass * ((srf_speed() ** 2) / 2 + srf_altitude() * g) / ((srf_altitude()))
        print('adjusting')


        active_throttle = thrust / vessel.max_thrust
        if srf_speed() < 1.0:
            active_throttle = hover_thrust - 0.1*hover_thrust
            print('lowering')


        vessel.control.throttle = active_throttle
        print('Throttle= ',active_throttle, '\n Hspeed= ',horz_speed(),'\n Vspeed= ',vert_speed(),)
    vessel.control.throttle = 0
    break
