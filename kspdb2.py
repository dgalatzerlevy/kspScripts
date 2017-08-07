import sqlite3
import krpc
import time
import matplotlib.pyplot as plt

conn = krpc.connect(name='TelemetryDB')
dbcon = sqlite3.connect('ksp.sqlite')
cur = dbcon.cursor()
vessel = conn.space_center.active_vessel

print('Collecting Data for:', vessel.name)

def resetTable():
    print('Resesting Table')
    cur.executescript('''DROP TABLE IF EXISTS altitude;

    CREATE TABLE altitude (
        id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        met  REAL ,
        altitude REAL
    );
    ''')
    # dbcon.commit()

def recordData():
    print('Recording data. Ctrl-C to stop')
    altitude = conn.add_stream(getattr, vessel.flight(), 'surface_altitude')
    met = conn.add_stream(getattr, vessel, 'met')
    data = list()
    while True:
        try:
            cur.execute('INSERT INTO altitude (met,altitude) VALUES (?,?)',(round(met(),2), round(altitude())))
            # dbcon.commit
            print('T=',round(met(),2), 'Alt=',round(altitude()))
            data.append((round(met(),2), round(altitude())))
            time.sleep(1)
        except KeyboardInterrupt:
            break
    print('commiting?')
    return data
    # dbcon.commit()

def graphit(self):
    x = [x[0] for x in self]
    y = [x[1] for x in self]
    plt.plot(x,y)
    plt.ylabel('Altitude')
    plt.xlabel('MET')
    plt.show()

resetTable()
data = recordData()

displayYN = input('Display Altitude Data? y/n:')

if displayYN == 'y':
    print('working')
    graphit(data)

commitYN = input('Save to DB? y/n')

if commitYN == 'y':
    dbcon.commit()
