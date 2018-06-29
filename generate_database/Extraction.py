import re
from bs4 import BeautifulSoup


def find_times(f):
	times = []
	l = re.findall("\d\d*\:\d\d*\:*\d*",f )
	for i in l:
		times.append(i)
	
	return times

	
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



def return_times(html):
	f = open(html, 'r')
	soup = BeautifulSoup(f.read(),'html.parser')
	tbody = soup.tbody
	x = find_times(str(tbody))
	return converte(x)



