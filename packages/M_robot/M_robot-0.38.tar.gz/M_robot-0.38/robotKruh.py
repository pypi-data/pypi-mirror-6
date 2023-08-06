from pylab import axis, show
import pylab
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import *
from matplotlib.widgets import Slider

import robot as rob

def init():
    #dot.set_offsets([])
    line.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])
    line5.set_data([], [])
    line6.set_data([], [])
    line7.set_data([], [])
    return line2,line3,line4,line5,line6,line7,line,

def vykresliRobota(i):
    #lavo
    #0.017 rad
    a,b = robot.setPoint(20)
    #line.set_data((a,0),(b,0))
    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = 0.017*robot.uhlovaRychlostRobota)#vrati 4 vrcholy robota +2 body kazdeho kolesa        line2.set_data((x1Rot[0],x1Rot[1]),(y1Rot[0],y1Rot[1]))
    line2.set_data((x1Rot[0],x1Rot[1]),(y1Rot[0],y1Rot[1]))    
        #pravo
    line3.set_data((x2Rot[0],x2Rot[1]),(y2Rot[0],y2Rot[1]))
        #predok a zadok je navrhnuty ako spojnica uz vypocitanych bodov
        #predok
    line4.set_data((x1Rot[1],x2Rot[1]),(y1Rot[1],y2Rot[1]))
        #zadok
    line5.set_data((x1Rot[0],x2Rot[0]),(y1Rot[0],y2Rot[0]))
        #lave koleso
    line6.set_data((xLkRot[0],xLkRot[1]),(yLkRot[0],yLkRot[1]))
        #prave koleso
    line7.set_data((xPkRot[0],xPkRot[1]),(yPkRot[0],yPkRot[1]))
        #dot.set_offsets((5, 5))
    return  line2,line3,line4,line5,line6,line7,line,

# nastavenie figur, osi ...
fig, ax = plt.subplots()
#dot = ax.scatter([],[], s=3, color='green', alpha=0.4)
line, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=2, color = 'green', alpha = 0.4)
line3, = ax.plot([], [], lw=2, color = 'blue', alpha = 0.4)
line4, = ax.plot([], [], lw=2, color = 'red', alpha = 0.4)
line5, = ax.plot([], [], lw=2, color = 'black', alpha = 0.4)
line6, = ax.plot([], [], lw=2, color = 'green', alpha = 1)
line7, = ax.plot([], [], lw=2, color = 'blue', alpha = 1)
robot=rob.Robot()   
os=180
plt.subplots_adjust( bottom=0.35)
axis('scaled')
pylab.xlim(-os*5/4.,os*5/4.)
pylab.ylim(-os,os)
plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d cm'))
plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%d cm'))
plt.setp(plt.xticks()[1], rotation=90)
pylab.grid()
anim = animation.FuncAnimation(fig,vykresliRobota, frames=1000000,init_func=init, interval=20, blit=True)

#SLIDRE

axcolor = 'lightgoldenrodyellow'
axfreq1 = plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
axfreq2  = plt.axes([0.25, 0.15, 0.65, 0.03], axisbg=axcolor)

sfreq1 = Slider(axfreq1, 'f1 [Hz]', -5, 10.0, valinit=robot.f1, color='blue')
sfreq2 = Slider(axfreq2, 'f2 [Hz]', -5, 10.0, valinit=robot.f2, color='green')

show()

def update(val):#update zmenenych hodnot cez slider
    freq1 = sfreq1.val
    freq2 = sfreq2.val
   
    robot.f1=freq1
    robot.f2=freq2
   
    radius=robot.getOnlyRadius();
    #bodX,bodY=robot.nastavBodOtacania(True,radius)
    bodX,bodY=robot.setPoint(True,radius)
    robot.bodRotacie=(bodX,bodY)
    robot.radius=radius
    robot.uhlovaRychlostRobota = np.abs((2*np.pi*robot.polomerKolieska)*(robot.f2-robot.f1)/robot.s)
    #radius moze byt aj zaporny, pouvazovat nad tym
    if(radius>0):
        ax.set_xlim((bodX-20-2*(radius+robot.s+robot.sk)*3/2.),(bodX+20+2*(radius+robot.s+robot.sk))*3/2.)
        ax.set_ylim(bodY-50-2*(radius+robot.s+robot.sk),bodY+50+2*(radius+robot.s+robot.sk))#po zmene bodu okolo ktoreho sa robot toci
    if(radius<0):
        ax.set_xlim((bodX-20-2*(-radius+robot.s+robot.sk))*3/2.,(bodX+20+2*(-radius+robot.s+robot.sk))*3/2.)
        ax.set_ylim((bodY-50-2*(-radius+robot.s+robot.sk)),(bodY+50+2*(-radius+robot.s+robot.sk)))#po zmene bodu okolo ktoreho sa robot toci

    
    fig.canvas.draw_idle()
sfreq1.on_changed(update)
sfreq2.on_changed(update)