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

def draw_figure(canvas, figure):
    figure.set_size_inches(5, 4, forward=True)  # Force size
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="left", fill="both", expand=True)
    return figure_canvas_agg

layout1 = [ #Define o layout
    [sg.Canvas(key="-CANVAS-", expand_x=True, expand_y=True)]
]

layout0 = [
    [sg.Slider(range=(15,165),enable_events=True,expand_x=True,orientation='horizontal',default_value=90,background_color='#a5a5a5',key='slider')]
]

layout2 = [
    [sg.Text(' Connection: ',background_color='#404040'),sg.Text(Connected,background_color='#404040',key='status') ,sg.Combo(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10"],default_value="COM3",readonly=True,enable_events=True,key='combo',background_color='#a5a5a5'),sg.Button('Reset',button_color='#a5a5a5'),sg.Radio('Off', group_id=1, default=True,background_color='#a5a5a5'), sg.Radio('On', group_id=1,background_color='#a5a5a5')],
    [sg.Frame("Manual Mode",layout0,title_location=sg.TITLE_LOCATION_TOP,background_color='#404040', expand_x=True, expand_y=True)]
]

layout = [
    [sg.Column([
        [sg.Frame("Plots", layout1, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP, background_color='#404040')]
    ], expand_x=True, expand_y=True,background_color='#a5a5a5'),
    
    sg.Column([
        [sg.Frame("Control", layout2, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP, background_color='#404040')]
    ], expand_x=True, expand_y=True,background_color='#a5a5a5')]
]

window = sg.Window("Sonar Control Panel", layout, finalize=True, resizable=True, background_color='#a5a5a5')
window.bind("<Control-w>", "Ctrl+W")
window.maximize()

figure_canvas_agg=draw_figure(window['-CANVAS-'].TKCanvas, fig)

while True:
    # Serial setup
    if not Connected:
        try:
            ser = serial.Serial(COM, 9600, timeout=0.1)
            Connected = True
        except:
            print("Error! Not connected! Try again.")
            Connected = False
    if Connected:
        try:
            ser.read()
            Connected = True
        except:
            Connected = False

    window['status'].update(Connected)
    event, values = window.read(timeout=0.1)
    
    COM=values['combo']
    angulo=values['slider']
    print(values)
    
    if event in (sg.WINDOW_CLOSED, "Ctrl+W"):
        break

    if event == "Reset":
        continue

    figure_canvas_agg.draw()

window.close()
