import numpy as np
import random
import scipy as sc
def uholYOS(x_1,y_1,x2,y2):
    alpha = np.arctan(float(x_1-x2)/float(y_1-y2))
    nAlpha=15
    if(x2>=x_1 and y2>=y_1):
        nAlpha = alpha
    if(x_1>=x2 and y2>=y_1):
        nAlpha = alpha
    if(x_1<=x_1 and y2<=y_1):
        nAlpha = np.pi + alpha
    if(x_1>=x2 and y_1>=y2):
        nAlpha = -(np.pi - alpha)
    return nAlpha
def chybaPolomeru(radius):
    return (2*random.random()*radius)-radius

def chybaPolomeru2(radius,percentoChyby=0.7):
    return ((2*random.random()*radius*percentoChyby-radius*percentoChyby)+radius)

def chybaUhla(uhol):
    return ((2*random.random()*uhol)-uhol)

def kvant_angle_error(angle,kvant = 8):
    error = (2*random.random()*angle)-angle
    index = int(np.round(sc.random.random()*8))
    kvantization = angle/(kvant/2.)
    kvantization_help = kvantization
    kvantlist = [0]
    while(kvantization_help<=angle):
        kvantlist.append(kvantization_help)
        kvantlist.append(-kvantization_help)
        kvantization_help = kvantization_help + kvantization
    return kvantlist[index]

def dajSuradniceStreduAPolomer(x1,y1,x2,y2,alpha):#vychadza z 2 bodov a smernice v 1 z nich 
    #priamka a - normala na spojnicu bodov [x1,y1] a [x2,y2]
    #alpha - smernica robota 
    ka = np.tan(np.pi/2.0+np.arctan(float(y1-y2)/float(x1-x2)))#smernica priamky a
    #print(ka)
    #print(alpha)
    ustred = ((x1+x2)/2.0,(y1+y2)/2.0)
    #print(ustred)
    qa = 0.5*(y1+y2-np.tan(np.pi/2.0+np.arctan(float(y1-y2)/float(x1-x2)))*float(x1+x2))
    #priamka c - normala na smer natocenia robota
    kc = np.tan(np.pi/2.0+float(alpha))#smernica priamky c
    qc = y1-np.tan(np.pi/2.0+alpha)*x1#ZMENENE + na -
    #suradnice stredu kruznice prienik priamky a a c
    sx = (qa-qc)/float(kc-ka)#x-ova suradnica stredu kruznice
    sy = float(kc*sx+float(qc))#y-ova suradnica stredu kruznice
    #print(sy)
    R = np.sqrt((x1-sx)**2+(y1-sy)**2)#polomer danej kruznice
    omega = 2*np.arcsin(np.sqrt((x1-x2)**2+(y1-y2)**2)/float(2*R))#uhol v radianoch o aky sa zatoci okolo bodu Sx Sy
    omegaDeg = omega*180/np.pi#uhol v stupnoch
    return sx,sy,R,omegaDeg,omega
    
def vzdialenost_2_bodov_v_rovine(x1,y1,x2,y2):
    return np.sqrt((x1-x2)**2+(y1-y2)**2)

def zaokruhli(cislo):
    '''
    ak zaporne vrati floor
    ak kladne vrati ceil
    '''
    if(cislo<=0):
        cislo = np.floor(cislo)
    if(cislo>0):
        cislo = np.ceil(cislo)
    return cislo

def point_check(meno_zoznamu):
    '''
    kontrola bodov ci vyhovuju
    '''
    change = 0
    lenght = len(meno_zoznamu)
    for x in xrange(0,lenght-2):
        if(meno_zoznamu[x][0]==meno_zoznamu[x+1][0]):
            meno_zoznamu[x+1][0]=meno_zoznamu[x][0]+1
            change=change+1
        if(meno_zoznamu[x][1]==meno_zoznamu[x+1][1]):
            meno_zoznamu[x+1][1]=meno_zoznamu[x][1]+1
            change=change+1
    return change #vrati pocet zmien
def generate_points(N = 10, start = -150,end = 150):
    '''
    generate N points from start to end as an numpy array
    '''
    zoznamBodov = np.array([(0,0)])
    print("Prebieha nahodne generovanie bodov.")
    for x in xrange(1,N):
        pom_x = (np.random.rand()*(end - start))
        pom_xa = pom_x - abs(start)
        pom_y = (np.random.rand()*(end - start))
        pom_ya = pom_y - abs(start)
        zoznamBodov=np.append(zoznamBodov,[(pom_xa,pom_ya)],axis = 0)
    print("{} {}".format(N, "nahodnych bodov uspesne vygenerovanych"))

    return zoznamBodov
        