#Import libraries
import serial
import psycopg2
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from datetime import datetime

#Conexao base dados PostgreSQL
#conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=postgres")
#cur = conn.cursor()
#cur.execute("select id_utilizador,pass from utilizadores where email=%s", (email,))#verifica se existe email
#for linha in cur.fetchall():
#        ID,Pass,=linha
#cur.close()
#conn.close()

COM="COM3"

# Serial setup
try:
    ser = serial.Serial(COM, 9600, timeout=0.1)
    Connected = True
except:
    print("Error! Not connected! Try again.")
    Connected = False

#======================================================================
# Global variables to hold data
max_distance = 50  # Maximum radar range in cm
max_points = 100  # Number of points to display in seismograph
angles = []
distances = []
recorded_distances = []  # To record all distances
recorded_times = []  # To record all times
seismo_times = []  # For last 50 times
seismo_distances = [0] * max_points  # Initialize with zeros
start_time = datetime.now().timestamp()  # Record start time
ang = [[' ' for x in range(4)] for y in range(5)] 
#======================================================================

fig=plt.figure() #Initialize figure

#======================================================================
# Sonar (polar plot)
radar_ax = plt.subplot(3, 1, (1, 2), polar=True)

radar_ax.set_theta_zero_location("W")  # 0 degrees in the left
radar_ax.set_theta_direction(1)       # Anticlockwise direction
radar_ax.set_ylim(0, max_distance)      # Define max distance
radar_ax.set_title("Sonar")
radar_ax.grid(color="gray", linestyle="--", linewidth=0.5)
radar_ax.set_thetamin(15)
radar_ax.set_thetamax(165)

sweep_line, = radar_ax.plot([], [], color="green", linewidth=2) # Sonar green line
scatter = radar_ax.scatter([], [], color="red", s=10) # Sonar red dots
#======================================================================

#======================================================================
# Distances (2D plot) 
seismo_ax = plt.subplot(3,1,3)

seismo_ax.set_xlim(0, max_points)
seismo_ax.set_ylim(0, max_distance)
seismo_ax.set_title("Distance over time")
seismo_ax.set_xlabel("Time")
seismo_ax.set_ylabel("Distance (cm)")
seismo_ax.grid(color="gray", linestyle="--", linewidth=0.5)

line, = seismo_ax.plot([], [], color="red", linewidth=2)
#======================================================================


#======================================================================
# Update graphs
def update(frame):
    global angles, distances, seismo_distances

    # Read data from Arduino
    if ser.in_waiting > 0:
        try:
            data = ser.readline().decode().strip()
            angle, distance = map(int, data.split(","))
            angle_rad = np.deg2rad(angle)  # Convert angle to radians

            # Add data to radar
            angles.append(angle_rad)
            distances.append(distance)

            # Add data to seismograph
            current_time = datetime.now().timestamp()
            recorded_times.append(current_time)
            recorded_distances.append(distance)

            #print("Tempo: ",current_time,"Angulo: ",angle,"Distancia: ",distance)
            
            # Slice for the last `max_points`
            seismo_times = recorded_times[-max_points:]
            seismo_distances = recorded_distances[-max_points:]

            # Limit the number of radar points
            if len(angles) > 30:
                angles.pop(0)
                distances.pop(0)

            siz=len(angles)
            if siz>5:
                siz=5
            for j in range(5):
                if angles[-1]<max_distance:
                    ang[j][0]='Angle: '
                    ang[j][1]=angles[(-1-j)]
                    ang[j][2]=' Distance: '
                    ang[j][3]=distances[(-1-j)]

        except (ValueError, IndexError):
            pass  # Ignore invalid data

    # Update radar
    current_angle = angles[-1] if angles else 0
    sweep_line.set_data([0, current_angle], [0, max_distance])
    scatter.set_offsets(np.c_[angles, distances])

    # Update seismograph
    line.set_data(range(len(seismo_distances)), seismo_distances)

    return sweep_line, scatter, line

try:
    # Update plots with Animation
    ani = FuncAnimation(fig, update, interval=1, blit=True, cache_frame_data=False)
except:
    ani = 1

#======================================================================
#PySimpleGUI
sg.change_look_and_feel('SystemDefault')

def draw_figure(canvas, figure):
    figure.set_size_inches(5, 4, forward=True)  # Force size
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="left", fill="both", expand=True)
    return figure_canvas_agg

layout0 = [ #Plots
    [sg.Canvas(key="-CANVAS-", expand_x=True, expand_y=True)]
]

layout1 = [ #Slider
    [sg.Slider(range=(15,165),enable_events=True,expand_x=True,orientation='horizontal',default_value=90,key='slider')],
    [sg.Text(' Delay: '),sg.Combo(["10","20","30","40","50"],default_value="30",readonly=True,enable_events=True,key='combo_time'),sg.Text(' Distance: '),sg.Combo(["10","20","30","40","50","60","70","80","90","100"],default_value="50",readonly=True,enable_events=True,key='combo')]
]


layout2 = [
    [sg.Text(ang[0][0]),sg.Text(ang[0][1]),sg.Text(ang[0][2]),sg.Text(ang[0][3])],
    [sg.Text(ang[0][0]),sg.Text(ang[0][1]),sg.Text(ang[0][2]),sg.Text(ang[0][3])],
    [sg.Text(ang[0][0]),sg.Text(ang[0][1]),sg.Text(ang[0][2]),sg.Text(ang[0][3])],
    [sg.Text(ang[0][0]),sg.Text(ang[0][1]),sg.Text(ang[0][2]),sg.Text(ang[0][3])]
]

layout3 = [
    [sg.Text('Connection:'),sg.Text(Connected,key='status') ,sg.Text(' Port:'),sg.Combo(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10"],default_value="COM3",readonly=True,enable_events=True,key='combo'),sg.Text(' Mode:'),sg.Radio('Off', group_id=1, default=True,key='Off'), sg.Radio('On', group_id=1,key='On'),sg.Text(' Sound:'),sg.Radio('Off', group_id=2,key='B_Off'), sg.Radio('On', group_id=2, default=True,key='B_On'),sg.Button('Reset')],
    [sg.Frame("Logs",layout2,title_location=sg.TITLE_LOCATION_TOP, expand_x=True, expand_y=True)],
    [sg.Frame("Manual Mode",layout1,title_location=sg.TITLE_LOCATION_TOP, expand_x=True, expand_y=True)]
]

layout = [
    [sg.Column([
        [sg.Frame("Plots", layout0, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP)]
    ], expand_x=True, expand_y=True),
    
    sg.Column([
        [sg.Frame("Control", layout3, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP)]
    ], expand_x=True, expand_y=True)]
]

window = sg.Window("Sonar Control Panel", layout, finalize=True, resizable=True)
window.bind("<Control-w>", "Ctrl+W")
window.maximize()

figure_canvas_agg=draw_figure(window['-CANVAS-'].TKCanvas, fig)

status=False

while True:

    window['status'].update(Connected)
    event, values = window.read(timeout=0.1)
    
    COM=values['combo']
    angulo=values['slider']

    if values['B_On']:
        buzzer=True

    if values['B_Off']:
        buzzer=False

    if not Connected:
        try:
            ser = serial.Serial(COM, 9600, timeout=0.1)
            Connected = True
        except:
            Connected = False
            
    if Connected:
        try:
            if status != values['Off'] and status==False:
                ser.write("DEFAULT".encode())
                status=values['On']

            if status != values['On'] and status==False:
                ser.write("BUTTON".encode())
                status=values['Off']

            Connected = True
        except:
            Connected = False
    
    if event in (sg.WINDOW_CLOSED, "Ctrl+W"):
        break

    if event == "Reset":
        continue

    figure_canvas_agg.draw()

window.close()
