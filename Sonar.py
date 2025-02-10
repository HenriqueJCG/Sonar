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


Connected=False
#======================================================================
# Global variables to hold data
max_distance = 50  # Maximum radar range in cm
max_points = 100  # Number of points to display in seismograph
Logs_max= 10
num_detections = 0
session_start = ""
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

#=====================================================================================================================================================================
# Update graphs
def update(frame):
    global angles, distances, seismo_distances, seismo_angles, num_detections

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
                num_detections += 1

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

    # Update radar
    current_angle = angles[-1] if angles else 0
    sweep_line.set_data([0, current_angle], [0, max_distance])
    scatter.set_offsets(np.c_[angles, distances])

    # Update seismograph
    line.set_data(range(len(seismo_distances)), seismo_distances)
    line2.set_data(range(len(seismo_angles)), seismo_angles)

#ani = FuncAnimation(fig, update, interval=1, blit=True, cache_frame_data=False)

#=====================================================================================================================================================================


#===================================================================================
#Values variables
COM='COM3'
#===================================================================================

#=======================================================================================================================================================================
while True:

    #===================================================================================
    #Update connection status
    if not Connected:
        try:
            ser = serial.Serial(COM, 9600, timeout=0.1)
            Connected = True
            session_start = datetime.now().timestamp()
            session_start = date_format = datetime.fromtimestamp(session_start).strftime('%H:%M:%S %d-%m-%Y')
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
            ser.close()
        except:
            pass

        #Update windows
        #Clear plot and Logs data
        session_start=''
        num_detections=0
        angulo=90
        tempo=100
        max_distance=50
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

    fig.canvas.draw_idle()  # Draw the updated figure
    fig.canvas.flush_events()  # Process UI events
    plt.pause(0.01)  # Pause to allow GUI update

#=======================================================================================================================================================================