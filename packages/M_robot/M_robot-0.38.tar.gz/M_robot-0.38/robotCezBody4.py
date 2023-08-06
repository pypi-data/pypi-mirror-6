from pylab import axis, show
import pylab
from matplotlib import animation
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import *
import funkcie as fun
import robot as rob

#zoznamBodov = np.array([(0.0,5),(75,5),(-150.0,-80.0),(110.0,-80),(100.0,-50.0),(-150.0,150.0),(0.0,15.0),(200,-100)])
#zoznamBodov = np.array([(0.0,0.0),(119.5,120.0),(-150.0,-80.0),(110.0,30.0),(-150.0,-80.0),(100.0,-50.0),(-150.0,150.0),(0.0,15.0),(45.0,16.0),(150.0,7.0)])
zoznamBodov = fun.generate_points(N=15)
fun.point_check(zoznamBodov)
zoznamVzdialenosti = []#naplni sa vzdialenostmi medzi jednotlivymi bodmi
zoznamUhlov = []#naplni sa hodnotami uhlov o ake ma byt robot natoceny v radianoch voci y-osi
zoznamUhlovD = []#v stupnoch
k = 100 #konstanta ktora ovplyvnuje rychlost translacie popripade rotacie

zoznamPoctuKrokovRotacie = []
zoznamPoctuKrokovRotacie2= []



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

def dajzoznamVzdialenosti():#naplni zoznam vzdialenostou
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

def dajZoznamPoctuKrokovRotacie():
    '''
    naplni zoznam hodnotami uhla, o ktory sa ma robot zarotovat v 1 kroku animacie medzi 2 bodmi v radianoch
    predpoklada existenciu zoznamu zoznamUhlovD
    '''
    global zoznamUhlovD
    pom_cit = 0 + abs(zoznamUhlovD[0])
    pom_men = 0 + fun.zaokruhli(abs(zoznamUhlovD[0]))
    zoznamPoctuKrokovRotacie.append(np.radians(pom_cit/pom_men))
    for x in xrange(1,len(zoznamUhlovD)):
        '''
        if else kvoli tomu, ze ked ma zoznamUhlovD[x] a zoznamUhlovD[x-1] rovnake znamienko tak musi byt vetva else ina
        '''
        if(((zoznamUhlovD[x-1]>=0) and (zoznamUhlovD[x] <= 0)) or ((zoznamUhlovD[x-1]<=0) and (zoznamUhlovD[x] >= 0))):
            pom_cit = abs(zoznamUhlovD[x-1]) + abs(zoznamUhlovD[x])
            pom_men = fun.zaokruhli(abs(zoznamUhlovD[x-1])) + fun.zaokruhli(abs(zoznamUhlovD[x]))#o kolko stupnov sa ma natocit z aktualnej polohy 
            zoznamPoctuKrokovRotacie.append(np.radians(pom_cit/float(pom_men)))
            zoznamPoctuKrokovRotacie2.append(pom_cit)
        else:
            pom_cit = abs(zoznamUhlovD[x-1]) - abs(zoznamUhlovD[x])
            pom_men = fun.zaokruhli(abs(zoznamUhlovD[x-1])) - fun.zaokruhli(abs(zoznamUhlovD[x]))#o kolko stupnov sa ma natocit z aktualnej polohy 
            zoznamPoctuKrokovRotacie.append(abs(np.radians(pom_cit/float(pom_men))))
            zoznamPoctuKrokovRotacie2.append(pom_cit)
           

    return "done"

def init():#inicializacna funkcia kvoli animacii 
    line.set_data([], [])
    line2.set_data([], [])
    line3.set_data([], [])
    line4.set_data([], [])
    line5.set_data([], [])
    line6.set_data([], [])
    line7.set_data([], [])
    time_text.set_text('')

    return line2,line3,line4,line5,line6,line7,line,time_text,



def vykresliRobota(i):
    zmena = False#ci sa ma otocit naopak ako chcel povodne, lebo je to kratsie
    '''if(robot.alpha>2*np.pi):
        robot.alpha=robot.alpha-2*np.pi
    if(robot.alpha<-2*np.pi):
        robot.alpha=robot.alpha+2*np.pi'''
    N = len(zoznamBodov)
    time_text.set_text(time_template%(np.degrees(robot.gyro.get_gyro_angle())))
    global k
    down = 0 #spodna hranica rotacie
    middle = fun.zaokruhli(abs(zoznamUhlovD[0])) #vrchna hranica rotacie a spodna hranica translacie
    up = fun.zaokruhli(abs(zoznamUhlovD[0])) + fun.zaokruhli(zoznamVzdialenosti[0])+1#vrchna hranica translacie daneho cyklu
    changed = False #flag ci menit data ciar aby nepadlo po skonceni pohybu lebo to x1Rot sa nic nepriradi ak sa nic nemeni
    for x in xrange(0,N-1):
        #rotacia X
        if(down<i<=middle):
            #print(i)
            #uhol_otocenia = np.radians(abs(zoznamUhlovD[x])/ fun.zaokruhli(abs(zoznamUhlovD[x])))
            if(x == 0):
                if(zoznamUhlov[x]<0 and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]>0 and zmena==True):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]>0 and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = -zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]<0 and zmena==True):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = -zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
            else:
                if(zoznamUhlov[x]<0 and zoznamUhlov[x-1]>0 and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]>0 and zoznamUhlov[x-1]<0 and zmena==True):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]>0 and zoznamUhlov[x-1]<0 and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = -zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]<0 and zoznamUhlov[x-1]>0 and zmena==True):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = -zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                '''
                tato cast nastane vtedy, ked zoznamUhlovD obsahuje 2 rovnakoznamienkove prvky po sebe
                '''
                if(zoznamUhlov[x]<0 and zoznamUhlov[x-1]<0 and zoznamUhlov[x-1]<zoznamUhlov[x] and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = -zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]<0 and zoznamUhlov[x-1]<0 and zoznamUhlov[x-1]>zoznamUhlov[x] and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = +zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]>0 and zoznamUhlov[x-1]>0 and zoznamUhlov[x-1]>zoznamUhlov[x] and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = +zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                if(zoznamUhlov[x]>0 and zoznamUhlov[x-1]>0 and zoznamUhlov[x-1]<zoznamUhlov[x] and zmena==False):#kvoli rotacii do dobreho smeru
                    x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.rotateRobot2(uhol = -zoznamPoctuKrokovRotacie[x], okoloStredu = True)
                    changed = True
                
        #translacia X
        if(middle<i<up):
            x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot = robot.translateRobot2((zoznamVzdialenosti[x])/fun.zaokruhli(zoznamVzdialenosti[x]))
            changed = True
            #print(i)
            #print(up)
            #print(middle)
        if(x != N-2):#kvoli list index out of range
            down = up
            if(((zoznamUhlovD[x]>=0) and (zoznamUhlovD[x+1] <= 0)) or ((zoznamUhlovD[x]<=0) and (zoznamUhlovD[x+1] >= 0))):
                medzi = fun.zaokruhli(abs(zoznamUhlovD[x])) + fun.zaokruhli(abs(zoznamUhlovD[x+1]))#o kolko stupnov sa ma natocit z aktualnej polohy 
            else:
                medzi = fun.zaokruhli(abs(zoznamUhlovD[x])) - fun.zaokruhli(abs(zoznamUhlovD[x+1]))#o kolko stupnov sa ma natocit z aktualnej polohy 
                medzi = abs(medzi)
            middle = down + medzi
            up = middle + fun.zaokruhli(zoznamVzdialenosti[x+1])
            #print(down)
            #print(middle)
            #print(up)

    if(changed==True):
        line2.set_data((x1Rot[0],x1Rot[1]),(y1Rot[0],y1Rot[1])) 
        line3.set_data((x2Rot[0],x2Rot[1]),(y2Rot[0],y2Rot[1]))
        line4.set_data((x1Rot[1],x2Rot[1]),(y1Rot[1],y2Rot[1]))
        line5.set_data((x1Rot[0],x2Rot[0]),(y1Rot[0],y2Rot[0]))
        line6.set_data((xLkRot[0],xLkRot[1]),(yLkRot[0],yLkRot[1]))
        line7.set_data((xPkRot[0],xPkRot[1]),(yPkRot[0],yPkRot[1]))
    return  line2,line3,line4,line5,line6,line7,line,time_text,

#-------------------------- konic classu ROBOT ----------------------------------
# -------------- main -----------------------------------------------------------
# nastavenie figur, osi ...
fig, ax = plt.subplots()
#nastavenie ciar
time_text = ax.text(0.05, 0.95, '', transform=ax.transAxes)
time_template = 'uhol = %.1f stupnov'


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
dajZoznamPoctuKrokovRotacie()
#vytvorenie objektu
sirka=30
robot=rob.Robot(x=(zoznamBodov[0][0]-sirka/2.,zoznamBodov[0][1]-sirka/2.),sirka=sirka) 
#nastavenia limitu x a y osi  
os=180
plt.subplots_adjust( bottom=0.10)
axis('scaled')
pylab.xlim(-os*5/4.,os*5/4.)
pylab.ylim(-os,os)
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
anim = animation.FuncAnimation(fig,vykresliRobota, frames=1000000,init_func=init, interval=0.1, blit=True)
show()
