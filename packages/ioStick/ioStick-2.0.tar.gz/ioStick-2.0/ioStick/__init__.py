import serial
HIGH='HIGH'
LOW='LOW'
INPUT='INPUT'
OUTPUT='OUTPUT'
class ioStick:
     port="/dev/ttyS0"
     def __init__(self, serport="/dev/ttyACM0"):
          self.port=serport
          self.ser=serial.Serial(serport,9600)
     def pinMode(self,pin,inout):
          x=convert(pin)
          y=x[0]+x[1]
          if (inout == INPUT):
               self.ser.write("i"+y)
          else:
               self.ser.write("o"+y)
     def analogRead(self,pin):
          x=convert(pin)
          y=x[0]+x[1]
          self.ser.write("a"+y)
          output=self.ser.readline().strip()
          return output
     def digitalWrite(self,pin,status):
          x=convert(pin)
          y=x[0]+x[1]
          if(status == HIGH):
               self.ser.write("h"+y)
          else:
               self.ser.write("l"+y)
     def digitalRead(self,pin):
          x=convert(pin)
          y=x[0]+x[1]
          self.ser.write("r"+y)
          z=self.ser.read()
          if (z == '1'):
               return(HIGH)
          else:
               return(LOW)
def convert(numb):
     a=['0','1']
     if (numb <= 9):
             a[0]=str(numb)
             a[1]='0'
     else:
             a[0]='9'
             a[1]=str(numb-9)
     return a
