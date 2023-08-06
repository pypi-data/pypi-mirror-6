import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
def zapis_data_do_suboru(data,fname='uhol_z_robota.txt'):
	f = open(fname,'a')
	f.writelines(data) # python will convert \n to os.linesep
	f.writelines('\n')
	f.close()
	return 0
def vykresli():
	m = np.loadtxt('uhol_z_robota.txt')
	x = m[:,0]
	y = m[:,5]
	z = m[:,6]
	plt.xlabel('time [s]',fontsize = 18)
	plt.ylabel('distance/degree',fontsize = 16)
	plt.grid()
	plt.plot(x,y)
	plt.plot(x,z)

def vykresli2():
	m = np.loadtxt('uhol_z_robota.txt')
	x = m[:,0]
	y = m[:,5]
	z = m[:,6]

	plt.figure(1)
	plt.subplot(211)
	plt.plot(x, y, color='blue')
	plt.ylabel('distance [cm]',fontsize = 16)
	plt.grid()


	plt.subplot(212)
	plt.plot(x, z ,color='green')
	plt.ylabel('degrees',fontsize = 16)
	plt.grid()
	plt.xlabel('time [s]',fontsize = 18)
	plt.show()

def vykresli_all():
	m = np.loadtxt('uhol_z_robota.txt')
	x = m[:,0]
	y = m[:,5]
	z = m[:,6]

	delta_x = abs(m[:,1] - m[:,3])
	delta_y = abs(m[:,2] - m[:,4])

	f_1 = m[:,7]
	f_2 = m[:,8]

	#plt.figure(1)
	plt.figure(2)
	plt.subplot(611)
	plt.figure(2)
	plt.plot(x, y, color='blue')
	plt.ylabel('distance [cm]',fontsize = 13)
	plt.grid()


	plt.subplot(612)
	plt.figure(2)
	plt.plot(x, z ,color='green')
	plt.ylabel('degrees',fontsize = 13)
	plt.grid()

	plt.subplot(613)
	plt.figure(2)
	plt.plot(x, delta_x ,color='black')
	plt.ylabel('delta_x [cm]',fontsize = 13)
	plt.grid()

	plt.subplot(614)
	plt.figure(2)
	plt.plot(x, delta_y ,color='black')
	plt.ylabel('delta_y [cm]',fontsize = 13)
	plt.grid()

	plt.subplot(615)
	plt.figure(2)
	plt.plot(x, f_1 ,color='red')
	plt.ylabel('f_1 [Hz]',fontsize = 13)
	plt.grid()

	plt.subplot(616)
	plt.figure(2)
	plt.plot(x, f_2 ,color='red')
	plt.ylabel('f_2 [Hz]',fontsize = 13)
	plt.grid()

	plt.xlabel('time [s]',fontsize = 18)
	plt.figure(2)
	plt.show()

def vykresli_n(n=50):
	m = np.loadtxt('uhol_z_robota.txt')
	x = m[len(m)-n:,0]
	y = m[len(m)-n:,5]
	z = m[len(m)-n:,6]


	delta_x = abs(m[len(m)-n:,1] - m[len(m)-n:,3])
	delta_y = abs(m[len(m)-n:,2] - m[len(m)-n:,4])

	f_1 = m[len(m)-n:,7]
	f_2 = m[len(m)-n:,8]

	#plt.figure(1)
	plt.figure(2)
	plt.subplot(611)
	plt.figure(2)
	plt.plot(x, y, color='blue')
	plt.ylabel('distance [cm]',fontsize = 13)
	plt.grid()


	plt.subplot(612)
	plt.figure(2)
	plt.plot(x, z ,color='green')
	plt.ylabel('degrees',fontsize = 13)
	plt.grid()

	plt.subplot(613)
	plt.figure(2)
	plt.plot(x, delta_x ,color='black')
	plt.ylabel('delta_x [cm]',fontsize = 13)
	plt.grid()

	plt.subplot(614)
	plt.figure(2)
	plt.plot(x, delta_y ,color='black')
	plt.ylabel('delta_y [cm]',fontsize = 13)
	plt.grid()

	plt.subplot(615)
	plt.figure(2)
	plt.plot(x, f_1 ,color='red')
	plt.ylabel('f_1 [Hz]',fontsize = 13)
	plt.grid()

	plt.subplot(616)
	plt.figure(2)
	plt.plot(x, f_2 ,color='red')
	plt.ylabel('f_2 [Hz]',fontsize = 13)
	plt.grid()

	plt.xlabel('time [s]',fontsize = 18)
	plt.figure(2)
	plt.show()

import shutil as sh
import os.path as osp
import filecmp as fcmp
import scipy
def suborManage(input_file_name = 'uhol_z_robota.txt',output_file_name = 'datas/data.txt'):
	i = 0
	flag = False
	if(osp.isfile(output_file_name) == True):
		semi_ult = output_file_name
		while(flag != True):
			i=i+1
			s_output=output_file_name.split('.')
			l = []
			l.append(s_output[0])
			l.append('_')
			inc=str(i)
			l.append(inc)
			l.append('.')
			l.append(s_output[1])
			s_output = ''.join(l)
			if(osp.isfile(s_output)==False):
				flag = True
				sh.copyfile(input_file_name,s_output)
				if(fcmp.cmp(input_file_name,semi_ult)==False):
					print('aaa')
			semi_ult = s_output
		print('New file has been copied and created as '+s_output)
	if(osp.isfile(output_file_name) == False):
		print('New file has been copied and created as datas/data.txt')
		sh.copyfile(input_file_name,output_file_name)
		
	
#sh.copyfile(input_file_name,s_output) aaa

		

