import krpc

conn = krpc.connect('Episode 1')

vessel = conn.space_center.active_vessel
print(vessel.name)

#Run all the science!
for experiment in vessel.parts.experiments:
    experiment.run()

#Launch, Wait, Stage Chutes
vessel.control.activate_next_stage()

altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')

while altitude() < 1500:
    pass

while altitude() > 1500:
    pass

vessel.control.activate_next_stage()
