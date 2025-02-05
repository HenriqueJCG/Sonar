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

Connected=False
#======================================================================
# Global variables to hold data
max_distance = 50  # Maximum radar range in cm
max_points = 100  # Number of points to display in seismograph
angles = []
distances = []
Log_angle = []
Log_distances = []
Log_times = []
recorded_distances = []  # To record all distances
seismo_times = []  # For last 50 times
seismo_distances = [0] * max_points  # Initialize with zeros
Logs = [[' ' for x in range(6)] for y in range(10)] 
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
        data = ser.readline().decode().strip()
        angle, distance = map(int, data.split(","))
        angle_rad = np.deg2rad(angle)  # Convert angle to radians

        # Add data to radar
        angles.append(angle_rad)
        distances.append(distance)

        # Add data to seismograph
        current_time = datetime.now().timestamp()
        current_time = date_format = datetime.fromtimestamp(current_time).strftime('%H:%M:%S %d-%m-%Y')
        recorded_distances.append(distance)

        #print("Tempo: ",current_time,"Logsulo: ",angle,"Distancia: ",distance)
        
        # Slice for the last `max_points`
        seismo_distances = recorded_distances[-max_points:]

        # Limit the number of radar points
        if len(angles) > 30:
            angles.pop(0)
            distances.pop(0)

        if distance < max_distance:
            Log_distances.append(distance)
            Log_angle.append(angle)
            Log_times.append(current_time)

        if len(Log_angle) > 10:
            Log_angle.pop(0)
            Log_distances.pop(0)
            Log_times.pop(0)

        siz=len(Log_angle)
        if siz>10:
            siz=10
        for j in range(siz):
            Logs[j][0]='Angle: '
            Logs[j][1]=Log_angle[(-1-j)]
            Logs[j][2]='°,   Distance: '
            Logs[j][3]=Log_distances[(-1-j)]
            Logs[j][4]='cm,  Time: '
            Logs[j][5]=Log_times[(-1-j)]

    # Update radar
    current_angle = angles[-1] if angles else 0
    sweep_line.set_data([0, current_angle], [0, max_distance])
    scatter.set_offsets(np.c_[angles, distances])

    # Update seismograph
    line.set_data(range(len(seismo_distances)), seismo_distances)

#ani = FuncAnimation(fig, update, interval=1, blit=True, cache_frame_data=False)

#======================================================================
#PySimpleGUI
sg.change_look_and_feel('SystemDefault')# Choose Theme

#===================================================================================
#Layouts
layout0 = [ #Plots
    [sg.Canvas(key="-CANVAS-", expand_x=True, expand_y=True)]
]

layout1 = [ #Slider
    [sg.Slider(range=(15,165),enable_events=True,expand_x=True,orientation='horizontal',default_value=90,key='slider')],
    [sg.Text(' Delay: '),sg.Combo(["70","85","100","115","130"],default_value="100",readonly=True,enable_events=True,key='combo_time'),sg.Text(' Distance: '),sg.Combo(["10","20","30","40","50","60","70","80","90","100"],default_value="50",readonly=True,enable_events=True,key='combo_distance')]
]


layout2 = [
    [sg.Text(f"{Logs[0][0]} {Logs[0][1]} {Logs[0][2]} {Logs[0][3]} {Logs[0][4]} {Logs[0][5]}", key='Log0')],
    [sg.Text(f"{Logs[1][0]} {Logs[1][1]} {Logs[1][2]} {Logs[1][3]} {Logs[1][4]} {Logs[1][5]}", key='Log1')],
    [sg.Text(f"{Logs[2][0]} {Logs[2][1]} {Logs[2][2]} {Logs[2][3]} {Logs[2][4]} {Logs[2][5]}", key='Log2')],
    [sg.Text(f"{Logs[3][0]} {Logs[3][1]} {Logs[3][2]} {Logs[3][3]} {Logs[3][4]} {Logs[3][5]}", key='Log3')],
    [sg.Text(f"{Logs[4][0]} {Logs[4][1]} {Logs[4][2]} {Logs[4][3]} {Logs[4][4]} {Logs[4][5]}", key='Log4')],
    [sg.Text(f"{Logs[5][0]} {Logs[5][1]} {Logs[5][2]} {Logs[5][3]} {Logs[5][4]} {Logs[5][5]}", key='Log5')],
    [sg.Text(f"{Logs[6][0]} {Logs[6][1]} {Logs[6][2]} {Logs[6][3]} {Logs[6][4]} {Logs[6][5]}", key='Log6')],
    [sg.Text(f"{Logs[7][0]} {Logs[7][1]} {Logs[7][2]} {Logs[7][3]} {Logs[7][4]} {Logs[7][5]}", key='Log7')],
    [sg.Text(f"{Logs[8][0]} {Logs[8][1]} {Logs[8][2]} {Logs[8][3]} {Logs[8][4]} {Logs[8][5]}", key='Log8')],
    [sg.Text(f"{Logs[9][0]} {Logs[9][1]} {Logs[9][2]} {Logs[9][3]} {Logs[9][4]} {Logs[9][5]}", key='Log9')],
]

layout3 = [
    [sg.Text('Connection:'),sg.Text(Connected,key='status') ,sg.Text(' Port:'),sg.Combo(["COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9","COM10"],default_value="COM3",readonly=True,enable_events=True,key='combo_COM'),sg.Text(' Mode:'),sg.Radio('Off', group_id=1, default=True,key='Off'), sg.Radio('On', group_id=1,key='On'),sg.Text(' Sound:'),sg.Radio('Off', group_id=2,key='B_Off'), sg.Radio('On', group_id=2, default=True,key='B_On'),sg.Button('Reset')],
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
#===================================================================================
#Window
window = sg.Window("Sonar Control Panel", layout, finalize=True, resizable=True)
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

#===================================================================================

#===================================================================================
#GUI Loop
while True:

    #Update Text values
    window['status'].update(Connected)
    window['Log0'].update(f"{Logs[0][0]} {Logs[0][1]} {Logs[0][2]} {Logs[0][3]} {Logs[0][4]} {Logs[1][5]}")
    window['Log1'].update(f"{Logs[1][0]} {Logs[1][1]} {Logs[1][2]} {Logs[1][3]} {Logs[1][4]} {Logs[1][5]}")
    window['Log2'].update(f"{Logs[2][0]} {Logs[2][1]} {Logs[2][2]} {Logs[2][3]} {Logs[2][4]} {Logs[2][5]}")
    window['Log3'].update(f"{Logs[3][0]} {Logs[3][1]} {Logs[3][2]} {Logs[3][3]} {Logs[3][4]} {Logs[3][5]}")
    window['Log4'].update(f"{Logs[4][0]} {Logs[4][1]} {Logs[4][2]} {Logs[4][3]} {Logs[4][4]} {Logs[4][5]}")
    window['Log5'].update(f"{Logs[5][0]} {Logs[5][1]} {Logs[5][2]} {Logs[5][3]} {Logs[5][4]} {Logs[5][5]}")
    window['Log6'].update(f"{Logs[6][0]} {Logs[6][1]} {Logs[6][2]} {Logs[6][3]} {Logs[6][4]} {Logs[6][5]}")
    window['Log7'].update(f"{Logs[7][0]} {Logs[7][1]} {Logs[7][2]} {Logs[7][3]} {Logs[7][4]} {Logs[7][5]}")
    window['Log8'].update(f"{Logs[8][0]} {Logs[8][1]} {Logs[8][2]} {Logs[8][3]} {Logs[8][4]} {Logs[8][5]}")
    window['Log9'].update(f"{Logs[9][0]} {Logs[9][1]} {Logs[9][2]} {Logs[9][3]} {Logs[9][4]} {Logs[9][5]}")

    #Read values from GUI
    event, values = window.read(timeout=0.01)
    
    #Events
    if event == 'combo_COM':
        COM=values['combo_COM']
        try:
            ser.close()
        except:
            pass
        Connected=False
    
    if event == 'slider':
        angulo=values['slider']

    if event == 'combo_distance':
        distancia=values['combo_distance']

    if event == 'combo_time':
        tempo=values['combo_time']

    if event in (sg.WINDOW_CLOSED, "Ctrl+W"):
        break

    if event == "Reset":
        continue

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
        except:
            Connected = False

    #===================================================================================

    try:
        update(None)
    except:
        Connected=False
        #Clear plot and Logs data
        angles.clear()
        distances.clear()
        seismo_distances = [0] * max_points  
        recorded_distances.clear()
        sweep_line.set_data([], [])
        scatter.set_offsets(np.empty((0, 2)))
        line.set_data([], [])
        Log_angle.clear()
        Log_distances.clear()
        Log_times.clear()
        Logs.clear()
        Logs = [[' ' for x in range(6)] for y in range(10)]     

    figure_canvas_agg.draw_idle()   

window.close()
#===================================================================================