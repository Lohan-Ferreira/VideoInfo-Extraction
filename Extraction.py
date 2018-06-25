import re
from bs4 import BeautifulSoup

f = open('DeepLearn.html', 'r')
soup = BeautifulSoup(f.read(),'html.parser')
tbody = soup.tbody

def find_times(f):
	times = []
	l = re.findall("\d\d*\:\d\d*\:*\d*",f )
	for i in l:
		times.append(i)
		
	return times

x = find_times(str(tbody))

def converte(time):
	segundos = []
	for i in time:
		aux = i.split(":")
		if(len(aux) == 3):
			horas = int(aux[0])*3600
			minutos = int(aux[1])*60
			segundos.append(horas + minutos + int(aux[2]))
		else:
			minutos = int(aux[0])*60
			segundos.append(minutos + int(aux[1]))
	return segundos

print(converte(x))
f.close()
