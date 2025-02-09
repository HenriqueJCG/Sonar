#Import libraries
import os
import sys
import serial
import psycopg2
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from datetime import datetime

#conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=postgres")
#cur = conn.cursor()
#cur.execute("select id_utilizador,pass from utilizadores where email=%s", (email,))#verifica se existe email
#for linha in cur.fetchall():
#        ID,Pass,=linha
#cur.close()
#conn.close()

Connected=False
#======================================================================
# Global variables to hold data
max_distance = 50  # Maximum radar range in cm
max_points = 100  # Number of points to display in seismograph
Logs_max= 10
angles = []
distances = []
Log_angle = []
Log_distances = []
Log_times = []
recorded_distances = []  
recorded_angles = []
seismo_angles = [0] * max_points  # Initialize with zeros
seismo_distances = [0] * max_points  # Initialize with zeros
Logs = [[' ' for x in range(6)] for y in range(10)] 
#======================================================================
fig=plt.figure() #Initialize figure
gs = gridspec.GridSpec(4, 1, height_ratios=[5, 1.5, 0.1, 1.5])  # Custom height ratios

# Choose Themes
fig.patch.set_facecolor("#e5dece")
sg.change_look_and_feel('Tan Blue')

#======================================================================
# Sonar (polar plot)
radar_ax = plt.subplot(gs[0], polar=True)

radar_ax.set_theta_zero_location("E")  # 0 degrees in the left
radar_ax.set_theta_direction(1)       # Anticlockwise direction
radar_ax.set_ylim(0, max_distance)      # Define max distance
radar_ax.set_title("Sonar")
radar_ax.title.set_color('#063289')
radar_ax.grid(color="gray", linestyle="--", linewidth=0.5)
radar_ax.set_thetamin(15)
radar_ax.set_thetamax(165)

sweep_line, = radar_ax.plot([], [], color="green", linewidth=2) # Sonar green line
scatter = radar_ax.scatter([], [], color="red", s=10) # Sonar red dots
#======================================================================

#======================================================================
# Distances (2D plot) 
seismo_ax = plt.subplot(gs[1])

seismo_ax.set_xlim(0, max_points)
seismo_ax.set_ylim(0, max_distance)
seismo_ax.set_title("Distance over time")
seismo_ax.set_ylabel("Distance (cm)")
seismo_ax.title.set_color('#063289')
#seismo_ax.yaxis.label.set_color('#063289')
seismo_ax.grid(color="gray", linestyle="--", linewidth=0.5)

line, = seismo_ax.plot([], [], color="red", linewidth=2)
#======================================================================

#======================================================================
# Angles (2D plot) 
angle_ax = plt.subplot(gs[3])

angle_ax.set_xlim(0, max_points)
angle_ax.set_ylim((15), (165))
angle_ax.set_title("Angle over time")
angle_ax.set_ylabel("Angle (°)")
angle_ax.title.set_color('#063289')
#angle_ax.yaxis.label.set_color('#063289')
angle_ax.grid(color="gray", linestyle="--", linewidth=0.5)

line2, = angle_ax.plot([], [], color="blue", linewidth=2)
#======================================================================


#======================================================================
# Update graphs
def update(frame):
    global angles, distances, seismo_distances, seismo_angles

    # Read data from Arduino
    if ser.in_waiting > 0:
        data = ser.readline().decode().strip()
        if data[0].isdigit():
              
            angle, distance = map(int, data.split(","))
            angle_rad = np.deg2rad(angle)  # Convert angle to radians

            # Add data to radar
            angles.append(angle_rad)
            distances.append(distance)

            # Add data to seismograph
            current_time = datetime.now().timestamp()
            current_time = date_format = datetime.fromtimestamp(current_time).strftime('%H:%M:%S %d-%m-%Y')
            recorded_distances.append(distance)
            recorded_angles.append(angle)

            #print("Tempo: ",current_time,"Logsulo: ",angle,"Distancia: ",distance)
            
            # Slice for the last `max_points`
            seismo_distances = recorded_distances[-max_points:]
            seismo_angles = recorded_angles[-max_points:]

            # Limit the number of radar points
            if len(angles) > 30:
                angles.pop(0)
                distances.pop(0)

            if distance < max_distance:
                Log_distances.append(distance)
                Log_angle.append(angle)
                Log_times.append(current_time)

            if len(Log_angle) > Logs_max:
                Log_angle.pop(0)
                Log_distances.pop(0)
                Log_times.pop(0)

            for j in range(len(Log_angle)):
                Logs[j][0]='Angle: '
                Logs[j][1]=Log_angle[(-1-j)]
                Logs[j][2]='°,   Distance: '
                Logs[j][3]=Log_distances[(-1-j)]
                Logs[j][4]='cm,  Time: '
                Logs[j][5]=Log_times[(-1-j)]
        else:
            #Checks for mode change with physical button
            if data in ["DEFAULT", "AUTO", "MANUAL"]:  
                window["Off"].update(value=(data == "DEFAULT"))
                window["Auto"].update(value=(data == "AUTO"))
                window["Manual"].update(value=(data == "MANUAL"))

    # Update radar
    current_angle = angles[-1] if angles else 0
    sweep_line.set_data([0, current_angle], [0, max_distance])
    scatter.set_offsets(np.c_[angles, distances])

    # Update seismograph
    line.set_data(range(len(seismo_distances)), seismo_distances)
    line2.set_data(range(len(seismo_angles)), seismo_angles)

#ani = FuncAnimation(fig, update, interval=1, blit=True, cache_frame_data=False)

#================================================================================

#================================================================================
#PySimpleGUI

#Layouts
layout0 = [ #Plots
    [sg.Canvas(key="-CANVAS-", expand_x=True, expand_y=True)]
]

layout1 = [ #Manual Mode
    [sg.Text('\nDetection Angle: (°)',justification='center', expand_x=True)],
    [sg.Slider(range=(15,165),enable_events=True,expand_x=True,orientation='horizontal',default_value=90,key='slider_angle',pad=(75,0))],
    [sg.Text('\nMax Distance Detection: (cm)',justification='center', expand_x=True)],
    [sg.Slider(range=(10,90),enable_events=True,expand_x=True,orientation='horizontal',default_value=50,key='slider_distance',pad=(75,0))],
    [sg.Text('\nDetection Delay: (ms)',justification='center', expand_x=True)],
    [sg.Slider(range=(70,130),enable_events=True,expand_x=True,orientation='horizontal',default_value=100,key='slider_delay',pad=(75,0))],
    [sg.Text('')]
]

layout2 = [] #Logs
for i in range(Logs_max):
    layout2.append([sg.Text(" ".join(map(str, Logs[i])), key=f'Log{i}', expand_x=True, expand_y=True, justification="center")])
    
    if i < Logs_max - 1:
        layout2.append([sg.HorizontalSeparator(pad=(75,0))])

layout3 = [
    [sg.Text('')],
    [sg.Text(' Connection:'),sg.Text(Connected,key='status'), sg.VSeparator(),sg.Text('  Port:'),sg.Combo(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10"],default_value="COM3",readonly=True,enable_events=True,key='combo_COM'),sg.VSeparator(),sg.Text('  Mode:'),sg.Radio('Off', group_id=1, default=True,key='Off',enable_events=True), sg.Radio('Auto', group_id=1,key='Auto',enable_events=True),sg.Radio('Manual',group_id=1,key='Manual',enable_events=True),sg.VSeparator(),sg.Text('  Sound:'),sg.Radio('On', group_id=2, default=True,key='B_On',enable_events=True),sg.Radio('Off', group_id=2,key='B_Off',enable_events=True),sg.VSeparator(),sg.Button('Reset')],
    [sg.Frame("Logs",layout2,title_location=sg.TITLE_LOCATION_TOP, expand_x=True, expand_y=True,font=("Any", 12, "bold"))],
    [sg.Frame("Manual Mode",layout1,title_location=sg.TITLE_LOCATION_TOP, expand_x=True, expand_y=False,font=("Any", 12, "bold"))]
]

tab_layout1 = [
    [sg.Column([
        [sg.Frame("", layout0, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP,font=("Any", 12, "bold"))]
    ], expand_x=True, expand_y=True),
    
    sg.Column([
        [sg.Frame("", layout3, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP,font=("Any", 12, "bold"))]
    ], expand_x=True, expand_y=True)]
]

layout5 = [
    [sg.Text("")]
]

layout6 = [
    [sg.Text("")]
]

tab_layout2 = [
    [sg.Column([
        [sg.Frame("", layout5, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP,font=("Any", 12, "bold"))]
    ], expand_x=True, expand_y=True),
    
    sg.Column([
        [sg.Frame("", layout6, size=(600, 600), expand_x=True, expand_y=True, title_location=sg.TITLE_LOCATION_TOP,font=("Any", 12, "bold"))]
    ], expand_x=True, expand_y=True)]
]

layout = [[sg.TabGroup([[sg.Tab("Control Panel", tab_layout1,font=("Any", 12, "bold")), sg.Tab("Records", tab_layout2,font=("Any", 12, "bold"))]], expand_x=True, expand_y=True)]]
#===================================================================================
#Window
window = sg.Window("Sonar Control Panel", layout, finalize=True, resizable=True,return_keyboard_events=True)
window.bind("<Control-w>", "Ctrl+W")
window.maximize()

#Canvas
figure_canvas_agg = FigureCanvasTkAgg(fig,window['-CANVAS-'].TKCanvas)
figure_canvas_agg.get_tk_widget().pack(side="left", fill="both", expand=True)
figure_canvas_agg.draw()

#===================================================================================
#Values variables
COM='COM3'
angulo=90
distancia=50
tempo=100

# 0-DEFAULT_MODE 1-AUTO_MODE 2-MANUAL_MODE
Mode=0
Sound=True

elements_to_disable = [
    'slider_angle', 'slider_delay', 'slider_distance', 'Off', 'B_On', 'B_Off'  ,'Auto','Manual'
]
#===================================================================================

#===================================================================================
#GUI Loop
while True:

    #Read values from GUI
    event, values = window.read(timeout=0.01)

    if event in (sg.WINDOW_CLOSED, "Ctrl+W"):
        break

    #Update Text values and Blocked elements
    color = "green" if Connected else "red"
    window['status'].update(Connected, text_color=color)

    for i in range(Logs_max):  
        window[f'Log{i}'].update(" ".join(map(str, Logs[i])))

    for element in elements_to_disable:
        window[element].update(disabled=not Connected)

    window['slider_angle'].update(disabled=not (values['Manual']))
    window['slider_delay'].update(disabled=not (values['Manual'])) 
    window['slider_distance'].update(disabled=not (values['Manual']))      
        
    #Events
    if event == 'combo_COM':
        COM=values['combo_COM']
        try:
            window["Off"].update(value=True)
            window["Auto"].update(value=False)
            window["Manual"].update(value=False)
            window["B_On"].update(value=True)
            window["B_Off"].update(value=False)
            ser.close()
        except:
            pass
        Connected=False

    #===================================================================================
    #Update modes and sound with radios

    try:
        if event in ('Auto', 'Manual', 'Off'):  # Radio button event
            if values['Auto']:
                ser.write(b"AUTO\n")  # Send "AUTO" to Arduino
            elif values['Manual']:
                ser.write(b"MANUAL\n")  # Send "MANUAL" to Arduino
            elif values['Off']:
                ser.write(b"DEFAULT\n")  # Send "DEFAULT" to Arduino
    except:
        pass

    #Blocks other mode
    #window['Auto'].update(disabled=not Connected or values['Manual'])
    #window['Manual'].update(disabled=not Connected or values['Auto'])

    try:
        if event in ('B_On', 'B_Off'):
            if values['B_On']:
                ser.write(b"BUZZ_ON\n")  # Turn buzzer ON
            else:
                ser.write(b"BUZZ_OFF\n") # Turn buzzer OFF
    except:
        pass

    #===================================================================================
    #Detects new events
    if event == 'slider_angle':
        angulo=values['slider_angle']

    if event == 'slider_distance':
        max_distance=values['slider_distance']
        radar_ax.set_ylim(0, max_distance)
        seismo_ax.set_ylim(0, max_distance)

    if event == 'slider_delay':
        tempo=values['slider_delay']

    if event == "Reset":
        try:
            ser.close()  # Close if open
        except:
            pass
        window.close()
        sys.stdout.flush()
        os.execv(sys.executable, ['python'] + sys.argv)

    #===================================================================================
    #Update connection status
    if not Connected:
        try:
            ser = serial.Serial(COM, 9600, timeout=0.1)
            Connected = True
        except:
            Connected = False
            
    if Connected:
        try:
            if ser.is_open:
                Connected = True
            else:
                Connected = False
        except:
            Connected = False

    #===================================================================================
    #Update values
    try:
        update(None)
    except:
        try:
            window["Off"].update(value=True)
            window["Auto"].update(value=False)
            window["Manual"].update(value=False)
            window["B_On"].update(value=True)
            window["B_Off"].update(value=False)
            ser.close()
        except:
            pass
        #Clear plot and Logs data
        angles.clear()
        distances.clear()
        seismo_distances = [0] * max_points 
        seismo_angles = [0] * max_points 
        recorded_distances.clear()
        recorded_angles.clear()
        sweep_line.set_data([], [])
        scatter.set_offsets(np.empty((0, 2)))
        line.set_data([], [])
        line2.set_data([], [])
        Log_angle.clear()
        Log_distances.clear()
        Log_times.clear()
        Logs.clear()
        Logs = [[' ' for x in range(6)] for y in range(10)]     

    figure_canvas_agg.draw_idle()   

window.close()
#===================================================================================