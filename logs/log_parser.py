import sys

def main(filename):
	times = []
	tasktimes = []
	fo = open(filename, 'r')
	
	for line in fo.readlines():
		
		if "INFO" in line:
			timestr = line[11:23]
			
			hours = int(timestr[0:2])
			minutes = int(timestr[3:5])
			seconds = int(timestr[6:8])
			milliseconds = int(timestr[9:])

			time = 60*minutes + seconds + 0.001*milliseconds
			times.append(time)

	print(times)

	i = 0
	while i < len(times) - 1:
		tasktimes.append(times[i+1] - times[i])
		i += 1

	print(tasktimes)

	print(len(tasktimes))

if __name__ == "__main__":
	main(sys.argv[1])