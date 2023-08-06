from pylab import axis, show
import pylab
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import *
from matplotlib.widgets import Slider

import funkcie as fun
import robot as rob 
import zapisDoSuboru as zap

def init():
    #dot.set_offsets([])
    line.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])
    line5.set_data([], [])
    line6.set_data([], [])
    line7.set_data([], [])

    dline.set_data([], [])
    dline2.set_data([], [])
    dline3.set_data([], [])
    dline4.set_data([], [])
    dline5.set_data([], [])
    dline6.set_data([], [])
    dline7.set_data([], [])
    return line2,line3,line4,line5,line6,line7,line,dline2,dline3,dline4,dline5,dline6,dline7,dline,

def vykresliRobota(i):
    chyba = fun.vzdialenost_2_bodov_v_rovine(robot.adstred[0],robot.adstred[1],robot.astred[0],robot.astred[1])
    chyba_uhla = robot.gyro.get_gyro_angle() - robot.gyro_sum.get_gyro_angle()
    if(i%50 ==0):
        zap.vykresli_all()
        
    zap.zapis_data_do_suboru(str("{:5.2f}".format(i*0.02))+str('\t')+str("{:12.8f}".format(robot.adstred[0]))+str(' ')+str("{:12.8f}".format(robot.adstred[1]))+str('\t')+str("{:12.8f}".format(robot.astred[0]))+str(' ')+str("{:12.8f}".format(robot.astred[1]))+str('\t')+str("{:12.8f}".format(chyba))+str('\t')+str("{:12.8f}".format(np.degrees(chyba_uhla)))+str('\t')+str("{:4.2f}".format(robot.f1))+str('\t')+str("{:4.2f}".format(robot.f2)))
    
    robot.bodRotacieChyba = robot.setPoint(napravo = True, vzdialenost = robot.radiusChyba,chyba=True)
    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = 0.017*robot.uhlovaRychlostRobota,chyba=False)#vrati 4 vrcholy robota +2 body kazdeho kolesa        line2.set_data((x1Rot[0],x1Rot[1]),(y1Rot[0],y1Rot[1]))
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
    robot.radiusChyba=fun.chybaPolomeru2(robot.radius,percentoChyby=0.8)


    dx1Rot,dy1Rot,dx2Rot,dy2Rot,dxLkRot,dyLkRot,dxPkRot,dyPkRot = robot.rotateRobot2(uhol = 0.017*robot.uhlovaRychlostRobota,chyba=True)#vrati 4 vrcholy robota +2 body kazdeho kolesa        line2.set_data((x1Rot[0],x1Rot[1]),(y1Rot[0],y1Rot[1]))
    dx1Rot,dy1Rot,dx2Rot,dy2Rot,dxLkRot,dyLkRot,dxPkRot,dyPkRot = robot.rotateRobot2(uhol = fun.chybaUhla(0.017),chyba=True,okoloStredu=True)
    dline2.set_data((dx1Rot[0],dx1Rot[1]),(dy1Rot[0],dy1Rot[1]))    
        #pravo
    dline3.set_data((dx2Rot[0],dx2Rot[1]),(dy2Rot[0],dy2Rot[1]))
        #predok a zadok je navrhnuty ako spojnica uz vypocitanych bodov
        #predok
    dline4.set_data((dx1Rot[1],dx2Rot[1]),(dy1Rot[1],dy2Rot[1]))
        #zadok
    dline5.set_data((dx1Rot[0],dx2Rot[0]),(dy1Rot[0],dy2Rot[0]))
        #lave koleso
    dline6.set_data((dxLkRot[0],dxLkRot[1]),(dyLkRot[0],dyLkRot[1]))
        #prave koleso
    dline7.set_data((dxPkRot[0],dxPkRot[1]),(dyPkRot[0],dyPkRot[1]))

    #dline.set_data((0,robot.bodRotacieChyba[0]),(0,robot.bodRotacieChyba[1]))
    #dline.set_data((0,30),(0,10))
    

    return  line2,line3,line4,line5,line6,line7,line,dline2,dline3,dline4,dline5,dline6,dline7,dline,

#-------------------------- konic classu ROBOT ----------------------------------
# -------------- main -----------------------------------------------------------
# nastavenie figur, osi ...
fig, ax = plt.subplots()
robot = rob.RobotSChybou(opacity=1)
line, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=2, color = 'green', alpha = 1)
line3, = ax.plot([], [], lw=2, color = 'blue', alpha = 1)
line4, = ax.plot([], [], lw=2, color = 'red', alpha = 1)
line5, = ax.plot([], [], lw=2, color = 'black', alpha = 1)
line6, = ax.plot([], [], lw=2, color = 'green', alpha = 1)
line7, = ax.plot([], [], lw=2, color = 'blue', alpha = 1)

dline, = ax.plot([], [], lw=2)
dline2, = ax.plot([], [], lw=2, color = 'green', alpha = 0.4)
dline3, = ax.plot([], [], lw=2, color = 'blue', alpha = 0.4)
dline4, = ax.plot([], [], lw=2, color = 'red', alpha = 0.4)
dline5, = ax.plot([], [], lw=2, color = 'black', alpha = 0.4)
dline6, = ax.plot([], [], lw=2, color = 'green', alpha = 0.4)
dline7, = ax.plot([], [], lw=2, color = 'blue', alpha = 0.4)

os=180
plt.subplots_adjust( bottom=0.25)
axis('scaled')
pylab.xlim(-os,os)
pylab.ylim(-os,os)
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
    robot.radiusChyba=fun.chybaPolomeru2(radius)
    robot.uhlovaRychlostRobota = np.abs((2*np.pi*robot.polomerKolieska)*(robot.f2-robot.f1)/robot.s)
    #radius moze byt aj zaporny, pouvazovat nad tym
    if(radius>0):
        ax.set_xlim(bodX-20-2*(radius+robot.s+robot.sk),bodX+20+2*(radius+robot.s+robot.sk))
        ax.set_ylim(bodY-50-2*(radius+robot.s+robot.sk),bodY+50+2*(radius+robot.s+robot.sk))#po zmene bodu okolo ktoreho sa robot toci
    if(radius<0):
        ax.set_xlim(bodX-20-2*(-radius+robot.s+robot.sk),bodX+20+2*(-radius+robot.s+robot.sk))
        ax.set_ylim(bodY-50-2*(-radius+robot.s+robot.sk),bodY+50+2*(-radius+robot.s+robot.sk))#po zmene bodu okolo ktoreho sa robot toci

    
    fig.canvas.draw_idle()
sfreq1.on_changed(update)
sfreq2.on_changed(update)