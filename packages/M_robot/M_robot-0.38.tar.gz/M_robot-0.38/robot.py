import numpy as np
import pohyb as poh
import funkcie as fun

class Gyro(object):
    """gyroskop senzor"""
    def __init__(self,gyro_start_angle = 0):
        self.gyro_angle = 0 
    def get_gyro_angle(self):
        return self.gyro_angle
    def set_gyro_angle(self,angle):
        self.gyro_angle = angle
        return 0

class Robot(object):

    def __init__(self, sirka=30, dlzka=30, sirkakolies=2, x=(5,10),uhol=0,f1 = 1.2,f2 = 0.5,polomerKolieska=3):
        self.s = sirka
        self.d = dlzka
        self.sk = sirkakolies
        
        #lava ciara robota (green)
        self.x = x
        self.y = (self.x[0],self.x[1]+self.d)

        #prava ciara robota
        self.xz = (self.x[0]+self.s,self.x[1])
        self.yz = (self.y[0]+self.s,self.y[1])
        
        #lave koleso
        self.xlk=(self.x[0]-self.sk,self.x[1]+self.d/3)
        self.ylk=(self.x[0]-self.sk,self.y[1]-self.d/3.)
        #prave koleso
        self.xpk=(self.x[0]+self.sk+self.s,self.xlk[1])
        self.ypk=(self.x[0]+self.sk+self.s,self.ylk[1])
        #stred robota
        self.stred =((self.y[0]+self.xz[0])/2.,(self.y[1]+self.xz[1])/2.)

        self.pociatocnyUhol = uhol
        #self.alpha = uhol #in radians
        self.f1 = f1
        self.f2 = f2
        self.radius = self.getOnlyRadius()
        self.polomerKolieska = polomerKolieska
        self.uhlovaRychlostRobota = np.abs((2*np.pi*self.polomerKolieska)*(self.f2-self.f1)/self.s)
        self.gyro = Gyro()

        #aktualneHodnoty polohy robota
        self.ax = self.x
        self.ay = self.y
        self.axz = self.xz
        self.ayz = self.yz
        self.axlk = self.xlk
        self.aylk = self.ylk
        self.axpk = self.xpk
        self.aypk = self.ypk
        self.astred = self.stred

        self.bodRotacie = self.setPoint(napravo=True)
        self.i=0

    def vratUholYos(self):#vrati uhol ktory zvieraju spojnica 2 bodov a y-OS od 0-2PI
        ax = self.ax
        ay = self.ay
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
        return nAlpha

    def rotateRobot2(self,uhol=0.,okoloStredu=False):
        if(okoloStredu==False):
            x1Rot,y1Rot = poh.rotate((self.ax[0],self.ay[0]),(self.ax[1],self.ay[1]),uhol,self.bodRotacie)#lavy bok robota (green)
            
            x2Rot,y2Rot = poh.rotate((self.axz[0],self.ayz[0]),(self.axz[1],self.ayz[1]),uhol,self.bodRotacie)#pravy bok robota (blue)
            
            xLkRot,yLkRot = poh.rotate((self.axlk[0],self.aylk[0]),(self.axlk[1],self.aylk[1]),uhol,self.bodRotacie)#lave koleso robota
            
            xPkRot,yPkRot = poh.rotate((self.axpk[0],self.aypk[0]),(self.axpk[1],self.aypk[1]),uhol,self.bodRotacie)#lave koleso robota

            self.aktualizujPolohu((x1Rot[0],y1Rot[0]),(x1Rot[1],y1Rot[1]),(x2Rot[0],y2Rot[0]),(x2Rot[1],y2Rot[1]),(xLkRot[0],yLkRot[0]),(xLkRot[1],yLkRot[1]),(xPkRot[0],yPkRot[0]),(xPkRot[1],yPkRot[1]))
            self.gyro.set_gyro_angle(self.gyro.get_gyro_angle() + uhol)
        else:
            x1Rot,y1Rot = poh.rotate((self.ax[0],self.ay[0]),(self.ax[1],self.ay[1]),uhol,self.astred)#lavy bok robota (green)
            
            x2Rot,y2Rot = poh.rotate((self.axz[0],self.ayz[0]),(self.axz[1],self.ayz[1]),uhol,self.astred)#pravy bok robota (blue)
            
            xLkRot,yLkRot = poh.rotate((self.axlk[0],self.aylk[0]),(self.axlk[1],self.aylk[1]),uhol,self.astred)#lave koleso robota
            
            xPkRot,yPkRot = poh.rotate((self.axpk[0],self.aypk[0]),(self.axpk[1],self.aypk[1]),uhol,self.astred)#lave koleso robota

            self.aktualizujPolohu((x1Rot[0],y1Rot[0]),(x1Rot[1],y1Rot[1]),(x2Rot[0],y2Rot[0]),(x2Rot[1],y2Rot[1]),(xLkRot[0],yLkRot[0]),(xLkRot[1],yLkRot[1]),(xPkRot[0],yPkRot[0]),(xPkRot[1],yPkRot[1]))
            self.gyro.set_gyro_angle(self.gyro.get_gyro_angle() + uhol) #update uhla
        return x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot
        

    def translateRobot(self,vektor=np.array([0,0])):
        x1Tra,y1Tra = poh.translate(np.array([self.ax[0],self.ay[0]]),np.array([self.ax[1],self.ay[1]]),vektor)#lavy bok robota (green)
        
        x2Tra,y2Tra = poh.translate(np.array([self.axz[0],self.ayz[0]]),np.array([self.axz[1],self.ayz[1]]),vektor)#pravy bok robota (blue)
        
        xLkTra,yLkTra = poh.translate(np.array([self.axlk[0],self.aylk[0]]),np.array([self.axlk[1],self.aylk[1]]),vektor)#lave koleso robota
        
        xPkTra,yPkTra = poh.translate(np.array([self.axpk[0],self.aypk[0]]),np.array([self.axpk[1],self.aypk[1]]),vektor)#lave koleso robota

        self.aktualizujPolohu((x1Tra[0],y1Tra[0]),(x1Tra[1],y1Tra[1]),(x2Tra[0],y2Tra[0]),(x2Tra[1],y2Tra[1]),(xLkTra[0],yLkTra[0]),(xLkTra[1],yLkTra[1]),(xPkTra[0],yPkTra[0]),(xPkTra[1],yPkTra[1]))

        return x1Tra,y1Tra,x2Tra,y2Tra,xLkTra,yLkTra,xPkTra,yPkTra

    def translateRobot2(self,vzdialenost=0):#posunie robota o vzdialenost dopredu, natocenie si robot pamata
        vektor=np.array([vzdialenost*np.sin(2*np.pi-self.gyro.get_gyro_angle()),vzdialenost*np.cos(2*np.pi-self.gyro.get_gyro_angle())])
        x1Tra,y1Tra = poh.translate(np.array([self.ax[0],self.ay[0]]),np.array([self.ax[1],self.ay[1]]),vektor)#lavy bok robota (green)
        
        x2Tra,y2Tra = poh.translate(np.array([self.axz[0],self.ayz[0]]),np.array([self.axz[1],self.ayz[1]]),vektor)#pravy bok robota (blue)
        
        xLkTra,yLkTra = poh.translate(np.array([self.axlk[0],self.aylk[0]]),np.array([self.axlk[1],self.aylk[1]]),vektor)#lave koleso robota
        
        xPkTra,yPkTra = poh.translate(np.array([self.axpk[0],self.aypk[0]]),np.array([self.axpk[1],self.aypk[1]]),vektor)#lave koleso robota

        self.aktualizujPolohu((x1Tra[0],y1Tra[0]),(x1Tra[1],y1Tra[1]),(x2Tra[0],y2Tra[0]),(x2Tra[1],y2Tra[1]),(xLkTra[0],yLkTra[0]),(xLkTra[1],yLkTra[1]),(xPkTra[0],yPkTra[0]),(xPkTra[1],yPkTra[1]))

        return x1Tra,y1Tra,x2Tra,y2Tra,xLkTra,yLkTra,xPkTra,yPkTra

    def setPoint(self,napravo = True,vzdialenost = None):#nastavi bod okolo, ktoreho sa robot otaca pri kruhovom pohybe
        if(vzdialenost == None):
            vzdialenost=self.radius
        ax = self.ax
        ay = self.ay
        x1 = (ax[0]+ay[0])/2. #suradnice stredu laveho boku 
        y1 = (ax[1]+ay[1])/2.
        #alpha = np.arctan((ax[0]-ay[0])/(ax[1]-ay[1]))#uhol medzi y-osou a osou prechadzajucou robotom
        alpha = self.vratUholYos()
        self.gyro.set_gyro_angle(alpha)
        Sx = x1 + vzdialenost * np.cos(alpha) + np.cos(alpha) * (self.d/2.) 
        Sy = y1 + vzdialenost * np.sin(alpha) + np.sin(alpha) * (self.d/2.) 
        S = (Sx,Sy)
        #print(np.degrees(alpha))
        return Sx,Sy

    def getOnlyRadius(self):#vrati polomer po ktorom sa dany robot toci
        if(self.f1==self.f2):
            raise AssertionError("Robot sa netoci, ale ide vpred")
        radius=(self.s/2.)*(float(self.f1+self.f2)/float(self.f2-self.f1))#vzorec na vypocet polomeru otacania
        return radius

    def dajSuradniceStreduAPolomer(self,x1,y1,x2,y2,alpha):#vychadza z 2 bodov a smernice v 1 z nich 
        #priamka a - normala na spojnicu bodov [x1,y1] a [x2,y2]
        #alpha - smernica robota 
        ka = np.tan(np.pi/2.0+np.arctan(float(y1-y2)/float(x1-x2)))#smernica priamky a
        #print(ka)
        #print(alpha)
        ustred = ((x1+x2)/2.0,(y1+y2)/2.0)
        #print(ustred)
        qa = 0.5*(y1+y2-np.tan(np.pi/2.0+np.arctan(float(y1-y2)/float(x1-x2)))*float(x1+x2))
        #print("ka")
        #print(ka)
        #print("qa")
        #print(qa)
        #priamka c - normala na smer natocenia robota
        kc = np.tan(np.pi/2.0+float(alpha))#smernica priamky c
        qc = y1-np.tan(np.pi/2.0+alpha)*x1#ZMENENE + na -
        #print("kc")
        #print(kc)
        #print("qc")
        #print(qc)
        #suradnice stredu kruznice prienik priamky a a c
        sx = (qa-qc)/float(kc-ka)#x-ova suradnica stredu kruznice
        sy = float(kc*sx+float(qc))#y-ova suradnica stredu kruznice
        #print(sy)
        R = np.sqrt((x1-sx)**2+(y1-sy)**2)#polomer danej kruznice
        omega = 2*np.arcsin(np.sqrt((x1-x2)**2+(y1-y2)**2)/float(2*R))#uhol v radianoch o aky sa zatoci okolo bodu Sx Sy
        omegaDeg = omega*180/np.pi#uhol v stupnoch
        return sx,sy,R,omegaDeg,omega

    def aktualizujPolohu(self,b1,b2,b3,b4,b5,b6,b7,b8):#vola sa po translacii a rotacii aby sa aktualizovala akt poloha robota
        self.ax,self.ay,self.axz,self.ayz,self.axlk,self.aylk,self.axpk,self.aypk = b1,b2,b3,b4,b5,b6,b7,b8
        self.astred = ((self.ay[0]+self.axz[0])/2.,(self.ay[1]+self.axz[1])/2.)
        #self.ax,self.ay,self.axz,self.ayz = b1,b2,b3,b4

class RobotSChybou(object):

    def __init__(self, sirka=30, dlzka=30, sirkakolies=2, x=(5,10), y=(5,35), uhol=0,f1 = 0.5,f2 = 1,polomerKolieska=3,opacity=1):
        self.s = sirka
        self.d = dlzka
        self.sk = sirkakolies
        self.opacity = opacity
        
        #lava ciara robota (green)
        self.x = x
        self.y = (x[0],x[1]+self.d)
        #self.y=y

        #prava ciara robota
        self.xz = (self.x[0]+self.s,self.x[1])
        self.yz = (self.y[0]+self.s,self.y[1])
        
        #lave koleso
        self.xlk=(self.x[0]-self.sk,self.x[1]+self.d/3)
        self.ylk=(self.x[0]-self.sk,self.y[1]-self.d/3.)
        #prave koleso
        self.xpk=(self.x[0]+self.sk+self.s,self.xlk[1])
        self.ypk=(self.x[0]+self.sk+self.s,self.ylk[1])
        
        self.dx = x
        self.dy = (x[0],x[1]+self.d)
        #self.y=y

        self.stred =((self.y[0]+self.xz[0])/2.,(self.y[1]+self.xz[1])/2.)
        self.astred = self.stred

        #prava ciara robota
        self.dxz = (self.x[0]+self.s,self.x[1])
        self.dyz = (self.y[0]+self.s,self.y[1])
        
        #lave koleso
        self.dxlk=(self.x[0]-self.sk,self.x[1]+self.d/3)
        self.dylk=(self.x[0]-self.sk,self.y[1]-self.d/3.)
        #prave koleso
        self.dxpk=(self.x[0]+self.sk+self.s,self.xlk[1])
        self.dypk=(self.x[0]+self.sk+self.s,self.ylk[1])

        self.dstred =((self.dy[0]+self.dxz[0])/2.,(self.dy[1]+self.dxz[1])/2.)
        self.adstred = self.dstred


        self.rot = uhol
        self.f1 = f1
        self.f2 = f2
        self.radius = self.getOnlyRadius()
        self.radiusChyba = fun.chybaPolomeru2(self.radius)
        self.polomerKolieska = polomerKolieska
        self.uhlovaRychlostRobota = np.abs((2*np.pi*self.polomerKolieska)*(self.f2-self.f1)/self.s)
 
        #aktualneHodnoty polohy robota
        self.ax = self.x
        self.ay = self.y
        self.axz = self.xz
        self.ayz = self.yz
        self.axlk = self.xlk
        self.aylk = self.ylk
        self.axpk = self.xpk
        self.aypk = self.ypk

        self.bodRotacie = self.setPoint(napravo=True,vzdialenost = self.radius)
        self.bodRotacieChyba = self.setPoint(napravo = True, vzdialenost = self.radiusChyba,chyba=True)
        self.bodRotacieDuch = self.bodRotacieChyba
        self.i=0

        #self.alpha = 0
        #self.Dalpha = 0

        self.gyro = Gyro()
        self.gyro_sum = Gyro()
 
        

    def vratUholYos(self,duch = False):#vrati uhol ktory zvieraju spojnica 2 bodov a y-OS od 0-2PI
        if(duch == False):
            ax = self.ax
            ay = self.ay
        if(duch == True):
            ax = self.dx
            ay = self.dy
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
        return nAlpha

    def translateRobot2(self,vzdialenost=0,chyba = False):#posunie robota o vzdialenost dopredu, natocenie si robot pamata
        if(chyba == False):
            vektor=np.array([vzdialenost*np.sin(2*np.pi-self.gyro.get_gyro_angle()),vzdialenost*np.cos(2*np.pi-self.gyro.get_gyro_angle())])
            x1Tra,y1Tra = poh.translate(np.array([self.ax[0],self.ay[0]]),np.array([self.ax[1],self.ay[1]]),vektor)#lavy bok robota (green)
            x2Tra,y2Tra = poh.translate(np.array([self.axz[0],self.ayz[0]]),np.array([self.axz[1],self.ayz[1]]),vektor)#pravy bok robota (blue)
            xLkTra,yLkTra = poh.translate(np.array([self.axlk[0],self.aylk[0]]),np.array([self.axlk[1],self.aylk[1]]),vektor)#lave koleso robota
            xPkTra,yPkTra = poh.translate(np.array([self.axpk[0],self.aypk[0]]),np.array([self.axpk[1],self.aypk[1]]),vektor)#lave koleso robota
            self.aktualizujPolohu((x1Tra[0],y1Tra[0]),(x1Tra[1],y1Tra[1]),(x2Tra[0],y2Tra[0]),(x2Tra[1],y2Tra[1]),(xLkTra[0],yLkTra[0]),(xLkTra[1],yLkTra[1]),(xPkTra[0],yPkTra[0]),(xPkTra[1],yPkTra[1]))
        else:
            vektor=np.array([vzdialenost*np.sin(2*np.pi-self.gyro_sum.get_gyro_angle()),vzdialenost*np.cos(2*np.pi-self.gyro_sum.get_gyro_angle())])
            x1Tra,y1Tra = poh.translate(np.array([self.dx[0],self.dy[0]]),np.array([self.dx[1],self.dy[1]]),vektor)#lavy bok robota (green)
            x2Tra,y2Tra = poh.translate(np.array([self.dxz[0],self.dyz[0]]),np.array([self.dxz[1],self.dyz[1]]),vektor)#pravy bok robota (blue)
            xLkTra,yLkTra = poh.translate(np.array([self.dxlk[0],self.dylk[0]]),np.array([self.dxlk[1],self.dylk[1]]),vektor)#lave koleso robota
            xPkTra,yPkTra = poh.translate(np.array([self.dxpk[0],self.dypk[0]]),np.array([self.dxpk[1],self.dypk[1]]),vektor)#lave koleso robota
            self.dAktualizujPolohu((x1Tra[0], y1Tra[0]), (x1Tra[1], y1Tra[1]), (x2Tra[0], y2Tra[0]), (x2Tra[1], y2Tra[1]), (xLkTra[0], yLkTra[0]), (xLkTra[1], yLkTra[1]), (xPkTra[0], yPkTra[0]), (xPkTra[1], yPkTra[1]))
        return x1Tra,y1Tra,x2Tra,y2Tra,xLkTra,yLkTra,xPkTra,yPkTra

    def rotateRobot2(self,uhol=0.,chyba=False,okoloStredu=False):
        if(okoloStredu==False):
            if(chyba==False):
                x1Rot,y1Rot = poh.rotate((self.ax[0],self.ay[0]),(self.ax[1],self.ay[1]),uhol,self.bodRotacie)#lavy bok robota (green)
                
                x2Rot,y2Rot = poh.rotate((self.axz[0],self.ayz[0]),(self.axz[1],self.ayz[1]),uhol,self.bodRotacie)#pravy bok robota (blue)
                
                xLkRot,yLkRot = poh.rotate((self.axlk[0],self.aylk[0]),(self.axlk[1],self.aylk[1]),uhol,self.bodRotacie)#lave koleso robota
                
                xPkRot,yPkRot = poh.rotate((self.axpk[0],self.aypk[0]),(self.axpk[1],self.aypk[1]),uhol,self.bodRotacie)#lave koleso robota

                self.aktualizujPolohu((x1Rot[0],y1Rot[0]),(x1Rot[1],y1Rot[1]),(x2Rot[0],y2Rot[0]),(x2Rot[1],y2Rot[1]),(xLkRot[0],yLkRot[0]),(xLkRot[1],yLkRot[1]),(xPkRot[0],yPkRot[0]),(xPkRot[1],yPkRot[1]))
                self.gyro.set_gyro_angle(self.gyro.get_gyro_angle() + uhol)
            else:
                x1Rot,y1Rot = poh.rotate((self.dx[0],self.dy[0]),(self.dx[1],self.dy[1]),uhol,self.bodRotacieChyba)#lavy bok robota (green)
                
                x2Rot,y2Rot = poh.rotate((self.dxz[0],self.dyz[0]),(self.dxz[1],self.dyz[1]),uhol,self.bodRotacieChyba)#pravy bok robota (blue)
                
                xLkRot,yLkRot = poh.rotate((self.dxlk[0],self.dylk[0]),(self.dxlk[1],self.dylk[1]),uhol,self.bodRotacieChyba)#lave koleso robota
                
                xPkRot,yPkRot = poh.rotate((self.dxpk[0],self.dypk[0]),(self.dxpk[1],self.dypk[1]),uhol,self.bodRotacieChyba)#lave koleso robota
                self.dAktualizujPolohu((x1Rot[0],y1Rot[0]),(x1Rot[1],y1Rot[1]),(x2Rot[0],y2Rot[0]),(x2Rot[1],y2Rot[1]),(xLkRot[0],yLkRot[0]),(xLkRot[1],yLkRot[1]),(xPkRot[0],yPkRot[0]),(xPkRot[1],yPkRot[1]))
                self.gyro_sum.set_gyro_angle(self.gyro_sum.get_gyro_angle() + uhol)
        else:
            if(chyba==False):
                x1Rot,y1Rot = poh.rotate((self.ax[0],self.ay[0]),(self.ax[1],self.ay[1]),uhol,self.astred)#lavy bok robota (green)
                
                x2Rot,y2Rot = poh.rotate((self.axz[0],self.ayz[0]),(self.axz[1],self.ayz[1]),uhol,self.astred)#pravy bok robota (blue)
                
                xLkRot,yLkRot = poh.rotate((self.axlk[0],self.aylk[0]),(self.axlk[1],self.aylk[1]),uhol,self.astred)#lave koleso robota
                
                xPkRot,yPkRot = poh.rotate((self.axpk[0],self.aypk[0]),(self.axpk[1],self.aypk[1]),uhol,self.astred)#lave koleso robota

                self.aktualizujPolohu((x1Rot[0],y1Rot[0]),(x1Rot[1],y1Rot[1]),(x2Rot[0],y2Rot[0]),(x2Rot[1],y2Rot[1]),(xLkRot[0],yLkRot[0]),(xLkRot[1],yLkRot[1]),(xPkRot[0],yPkRot[0]),(xPkRot[1],yPkRot[1]))
                self.gyro.set_gyro_angle(self.gyro.get_gyro_angle() + uhol)
            else:
                x1Rot,y1Rot = poh.rotate((self.dx[0],self.dy[0]),(self.dx[1],self.dy[1]),uhol,self.adstred)#lavy bok robota (green)
                
                x2Rot,y2Rot = poh.rotate((self.dxz[0],self.dyz[0]),(self.dxz[1],self.dyz[1]),uhol,self.adstred)#pravy bok robota (blue)
                
                xLkRot,yLkRot = poh.rotate((self.dxlk[0],self.dylk[0]),(self.dxlk[1],self.dylk[1]),uhol,self.adstred)#lave koleso robota
                
                xPkRot,yPkRot = poh.rotate((self.dxpk[0],self.dypk[0]),(self.dxpk[1],self.dypk[1]),uhol,self.adstred)#lave koleso robota
                self.dAktualizujPolohu((x1Rot[0],y1Rot[0]),(x1Rot[1],y1Rot[1]),(x2Rot[0],y2Rot[0]),(x2Rot[1],y2Rot[1]),(xLkRot[0],yLkRot[0]),(xLkRot[1],yLkRot[1]),(xPkRot[0],yPkRot[0]),(xPkRot[1],yPkRot[1]))
                self.gyro_sum.set_gyro_angle(self.gyro_sum.get_gyro_angle() + uhol)
        return x1Rot,y1Rot,x2Rot,y2Rot,xLkRot,yLkRot,xPkRot,yPkRot

    def setPoint(self,napravo = True,vzdialenost = None,chyba = False):
        if(vzdialenost == None):
            vzdialenost=self.radius
        if(chyba==False):
            ax = self.ax
            ay = self.ay
            alpha = self.vratUholYos()
        if(chyba==True):
            ax = self.dx
            ay = self.dy
            alpha = self.vratUholYos(duch=True)
        x1 = (ax[0]+ay[0])/2. #suradnice stredu laveho boku 
        y1 = (ax[1]+ay[1])/2.
        #alpha = np.arctan((ax[0]-ay[0])/(ax[1]-ay[1]))#uhol medzi y-osou a osou prechadzajucou robotom
        
        Sx = x1 + vzdialenost * np.cos(alpha) + np.cos(alpha) * (self.d/2.) 
        Sy = y1 + vzdialenost * np.sin(alpha) + np.sin(alpha) * (self.d/2.) 
        S = (Sx,Sy)
        #print(np.degrees(alpha))
        return Sx,Sy

    def getOnlyRadius(self):#vrati polomer po ktorom sa dany robot toci
        if(self.f1==self.f2):
            raise AssertionError("Robot sa netoci, ale ide vpred")
        radius=(self.s/2.)*(float(self.f1+self.f2)/float(self.f2-self.f1))#vzorec na vypocet polomeru otacania
        return radius

    def dajSuradniceStreduAPolomer(self,x1,y1,x2,y2,alpha):
        #priamka a - normala na spojnicu bodov [x1,y1] a [x2,y2]
        ka = np.tan(np.pi/2.0+np.arctan((y1-y2)/(x1-x2)))#smernica priamky a
        qa = 0.5*(y1+y2-np.tan(np.pi/2.0+np.arctan((y1-y2)/(x1-x2)))*(x1+x2))
        
        #priamka c - normala na smer natocenia robota
        kc = np.tan(np.pi/2.0+alpha)#smernica priamky c
        qc = y1+np.tan(np.pi/2.0+alpha)*x1
        #suradnice stredu kruznice prienik priamky a a c
        sx = (qa-qc)/(kc-ka)#x-ova suradnica stredu kruznice
        sy = kc*sx+qc#y-ova suradnica stredu kruznice
        R = np.sqrt((x1-sx)**2+(y1-sy)**2)#polomer danej kruznice
        omega = 2*np.arcsin(np.sqrt((x1-x2)**2+(y1-y2)**2)/(2*R))#uhol v radianoch o aky sa zatoci okolo bodu Sx Sy
        omegaDeg = omega*180/np.pi#uhol v stupnoch
        return sx,sy,R,omegaDeg,omega

    def aktualizujPolohu(self,b1,b2,b3,b4,b5,b6,b7,b8):
        self.ax,self.ay,self.axz,self.ayz,self.axlk,self.aylk,self.axpk,self.aypk = b1,b2,b3,b4,b5,b6,b7,b8
        self.astred = ((self.ay[0]+self.axz[0])/2.,(self.ay[1]+self.axz[1])/2.)
        #self.ax,self.ay,self.axz,self.ayz = b1,b2,b3,b4
    def dAktualizujPolohu(self,b1,b2,b3,b4,b5,b6,b7,b8):
        self.dx,self.dy,self.dxz,self.dyz,self.dxlk,self.dylk,self.dxpk,self.dypk = b1,b2,b3,b4,b5,b6,b7,b8
        self.adstred = ((self.dy[0]+self.dxz[0])/2.,(self.dy[1]+self.dxz[1])/2.)
