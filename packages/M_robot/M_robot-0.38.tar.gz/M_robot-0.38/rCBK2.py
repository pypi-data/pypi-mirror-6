from pylab import axis, show
import pylab
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import *
import funkcie as fun
import robot as rob

zoznamBodov = np.array([(1,1),(10,-120),(200,-230),(320,-10),(-200,100),(-210,-400),(200,-450)])
zoznamVzdialenosti = []#naplni sa vzdialenostmi medzi jednotlivymi bodmi
zoznamUhlov = []#naplni sa hodnotami uhlov o ake sa ma robot natocit v radianoch
zoznamUhlovD= []#v stupnoch
k = 100 #ovplyvnenie rychlostu

#toto je kvoli zachovaniu konstantnej rychlosti
zoznamPolomerov = []#naplni sa hodnotami polomerov kruznic po akych sa bude robot pohybovat medzi jednotlivymi bodmi
zoznamUhlovNatoceniaD = []#naplni sa hodnotami o aky uhol v stupnoch sa ma robot natocit za jednotku casu animacie 
zoznamUhlovNatoceniaD2 = []
zoznamPoctuKrokovAnimacie = []#naplni sa poctom krokov animacie medzi jednotlivymi 2 bodmi
zoznamBodovOtacania = []


def vratUholYos(ax,ay):#vrati uhol ktory zvieraju spojnica 2 bodov a y-OS od 0-2PI, aby robot vedel v akej je polohe
    alpha = np.arctan((ax[0]-ay[0])/(ax[1]-ay[1]))
    nAlpha = alpha
    if((ay[0]<ax[0]) and (ay[1]>ax[1])):
        nAlpha=-alpha
    if((ay[0]<ax[0]) and (ay[1]<ax[1])):
        nAlpha=np.pi-alpha 
    if((ay[0]>ax[0]) and (ay[1]<ax[1])):
        nAlpha=np.pi-alpha
    if((ay[0]>ax[0]) and (ay[1]>ax[1])):
        nAlpha=2*np.pi - alpha
    return np.degrees(nAlpha)

def dajzoznamVzdialenosti():#naplni zoznam vzdialenostu
    global zoznamBodov
    global zoznamVzdialenosti
    for x in xrange(1,len(zoznamBodov)):
        pom=np.sqrt((zoznamBodov[x-1][0]-zoznamBodov[x][0])**2 + (zoznamBodov[x-1][1]-zoznamBodov[x][1])**2)
        zoznamVzdialenosti.append(pom)
    return "done"

def dajZoznamUhlov():#naplni zoznamy uhlov
    global zoznamBodov
    global zoznamUhlov
    for x in xrange(1,len(zoznamBodov)):
        pom = fun.uholYOS(zoznamBodov[x-1][0],zoznamBodov[x-1][1],zoznamBodov[x][0],zoznamBodov[x][1])
        zoznamUhlov.append(pom)
        zoznamUhlovD.append(np.degrees(pom))
    return "done"

def dajZoznamPolomerov():
	global zoznamBodov
	global k #ovplyvnuje rychlost
	zoznamUhlovNatoceniaD.append(0)
	sumaUhlov = 0
	for x in xrange(1,len(zoznamBodov)):
		sumaUhlov = sumaUhlov + zoznamUhlovNatoceniaD[x-1]# + np.degrees(np.pi/2.)
		print(sumaUhlov)
		pom=fun.dajSuradniceStreduAPolomer(zoznamBodov[x-1][0],zoznamBodov[x-1][1],zoznamBodov[x][0],zoznamBodov[x][1],0+np.radians(sumaUhlov)+np.pi/2.)
		#zoznamBodov[0][0],zoznamBodov[0][1],zoznamBodov[1][0],zoznamBodov[1][1],robot.alpha+np.pi/2.
		zoznamBodovOtacania.append((pom[0],pom[1]))
		zoznamPolomerov.append(pom[2])
		zoznamUhlovNatoceniaD.append(pom[3])
	for x in xrange(1,len(zoznamBodov)):
		omega = k/float(zoznamPolomerov[x-1])
		zoznamUhlovNatoceniaD2.append(omega)
		nk = zoznamUhlovNatoceniaD[x]/float(zoznamUhlovNatoceniaD2[x-1])
		nk = abs(nk)
		zoznamPoctuKrokovAnimacie.append(nk)
	return "zone"


def init():#inicializacna funkcia kvoli animacii
    line.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])
    line5.set_data([], [])
    line6.set_data([], [])
    line7.set_data([], [])
    return line2,line3,line4,line5,line6,line7,line,

def vykresliRobota(i):

    N = len(zoznamBodov)
    down = 0 #spodna hranica rotacie
    up = zoznamPoctuKrokovAnimacie[0] #vrchna hranica cyklu
    changed = False
    for x in xrange(0,N-1):
	    if(down<=i<up):
	        robot.bodRotacie = zoznamBodovOtacania[x]
	        x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = np.radians(zoznamUhlovNatoceniaD2[x]),okoloStredu = False)
	        changed=True
	    down = up
	    if(x!=N-2):
	    	up = up + zoznamPoctuKrokovAnimacie[x+1]

    if(changed==True):
        line2.set_data((x1Rot[0],x1Rot[1]),(y1Rot[0],y1Rot[1])) 
        line3.set_data((x2Rot[0],x2Rot[1]),(y2Rot[0],y2Rot[1]))
        line4.set_data((x1Rot[1],x2Rot[1]),(y1Rot[1],y2Rot[1]))
        line5.set_data((x1Rot[0],x2Rot[0]),(y1Rot[0],y2Rot[0]))
        line6.set_data((xLkRot[0],xLkRot[1]),(yLkRot[0],yLkRot[1]))
        line7.set_data((xPkRot[0],xPkRot[1]),(yPkRot[0],yPkRot[1]))
    return  line2,line3,line4,line5,line6,line7,line,

#-------------------------- konic classu ROBOT ----------------------------------
# -------------- main -----------------------------------------------------------
# nastavenie figur, osi ...
fig, ax = plt.subplots()
#nastavenie ciar
line, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=2, color = 'green', alpha = 0.4)
line3, = ax.plot([], [], lw=2, color = 'blue', alpha = 0.4)
line4, = ax.plot([], [], lw=2, color = 'red', alpha = 0.4)
line5, = ax.plot([], [], lw=2, color = 'black', alpha = 0.4)
line6, = ax.plot([], [], lw=2, color = 'green', alpha = 1)
line7, = ax.plot([], [], lw=2, color = 'blue', alpha = 1)
#naplnenie zoznamov
dajzoznamVzdialenosti()
dajZoznamUhlov()
dajZoznamPolomerov()
#vytvorenie objektu
sirka=30
robot=rob.Robot(x=(zoznamBodov[0][0]-sirka/2.,zoznamBodov[0][1]-sirka/2.),sirka=sirka) 
hodnoty = robot.dajSuradniceStreduAPolomer(zoznamBodov[0][0],zoznamBodov[0][1],zoznamBodov[1][0],zoznamBodov[1][1],robot.gyro.get_gyro_angle()+np.pi/2.)
print(hodnoty)
hodnoty = robot.dajSuradniceStreduAPolomer(zoznamBodov[0][0],zoznamBodov[0][1],zoznamBodov[1][0],zoznamBodov[1][1],robot.gyro.get_gyro_angle()+np.pi/2.)
#print(robot.alpha)
hodnoty2=(0,0,0,0,0)

plt.plot(hodnoty[0],hodnoty[1],'go')
#plt.plot(-14.80822515197238, -273.5821970079758,'go',label='stred')
#plt.plot(-15.225254636553846, -344.3366414216951,'go',label='stred')
robot.bodRotacie = (hodnoty[0],hodnoty[1])
#plt.plot(hodnoty2[0],hodnoty2[1],'go')
#nastavenia limitu x a y osi  
plt.subplots_adjust( bottom=0.10)
axis('scaled')
os=500
pylab.xlim(-os*5/4.,os*5/4.)
pylab.ylim(-os-100,os-100)
plt.gca().xaxis.set_major_formatter(FormatStrFormatter('%d cm'))
plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%d cm'))
plt.setp(plt.xticks()[1], rotation=90)
pylab.grid()
#plotnutie bodov zo zoznamu aj s poradim
data=zoznamBodov
labels = ['{0}'.format(i) for i in range(1,len(zoznamBodov)+1)]
plt.scatter(
    data[:, 0], data[:, 1], marker = 'o', c = 'red',
    cmap = plt.get_cmap('Spectral'))
for label, x, y in zip(labels, data[:, 0], data[:, 1]):
    plt.annotate(
        label, 
        xy = (x, y), xytext = (-20, 20),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
#maximalizacia okna
mng = plt.get_current_fig_manager()
mng.frame.Maximize(True)
plt.show()
anim = animation.FuncAnimation(fig,vykresliRobota, frames=1000000,init_func=init, interval=20, blit=True)
show()
