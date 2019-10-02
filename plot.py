"""
HPGL plotter buffer script

This script provides a buffer for when your poor cheap chinese import
(vinyl)-cutter has an issue with receiving to many commands at once.
"""

__author__ = 'Jan klopper <jan@underdark.nl>'
__version__ = 0.1



import serial
import time
import math
import optparse


def plot(options):
  # configure the serial connections (the parameters differs on the device you are connecting to)
  ser = serial.Serial(options.device,
	  baudrate=options.baudrate,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,
    xonxoff=1,
    rtscts=1
  )

  speed = int(options.speed)
  units = 40

  ser.setDTR(True)

  inputfile = open(options.inputfile)
  inputstring = inputfile.readline()
  pos = [0,0]
  for line in inputstring.split(';'):
    ser.write('%s;' % line)
    if options.verbose:
      print '%s;' % line
    sleeptime = 0.05 # default sane wait period
    if line[0:2] in ('PU', 'PD'): # pen movement
      newpos = line[2:].split(',')
      posdelta = abs(pos[0] - int(newpos[0])), abs(pos[1] - int(newpos[1]))
      pos = int(newpos[0]), int(newpos[1])
      distance = math.sqrt((posdelta[0] * posdelta[0]) +
                           (posdelta[1] * posdelta[1]))
      sleeptime = (distance / units) / speed
      if options.verbose:
        print '%d units, %f mm in %f sec.' % (
          distance, distance / units, sleeptime)
    elif line[0:2] == 'CI': # other movements
      sleeptime = (((int(line[2:]) * 2) * math.Pi) / units) / speed
    time.sleep(sleeptime * 2) # allow some stepper motor acceleration an deceleration time

def main():
  parser = optparse.OptionParser()
  parser.add_option("-i", "--input", dest="inputfile",
                    help="Input file")
  parser.add_option("-d", "--debug",
                    action="store_true", dest="verbose", default=False,
                    help="print distances to stdout")
  parser.add_option("-t", "--tty",
                    dest="device", default='/dev/ttyUSB0', help="tty device")
  parser.add_option("-r", "--rate",
                    dest="baudrate", default=9600, help="baudrate")
  parser.add_option("-s", "--speed",
                    dest="speed", default=300, help="speed in mm/s")

  (options, args) = parser.parse_args()

  if not options.inputfile:
    parser.print_help()
  else:
    plot(options)

if __name__ == '__main__':
  main()
