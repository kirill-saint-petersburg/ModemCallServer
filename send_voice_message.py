import serial
import wave
import time
import sys, getopt
import subprocess

def textToWav(text,file):
    print text
    subprocess.call(["espeak", "-vru", "-w " + file, "-s 90", text])

def sendATCmd(phone,cmd):
    phone.write(('AT'+cmd+'\r\n').encode())
    time.sleep(1)
    phone_response_echo = phone.readline()
    phone_response      = phone.readline()
    print 'COMMAND: ' + phone_response_echo + 'RESPONSE: ' + phone_response

def initializePhone():
    phone = serial.Serial(port='/dev/ttyUSB0',baudrate=115200,timeout=10,rtscts=0,xonxoff=0)
    sendATCmd(phone, '+FCLASS=8')
    sendATCmd(phone, '+VSM=4,9600')
    sendATCmd(phone, '+VLS=2')
    return phone

def call(phone, number):
    sendATCmd(phone, 'DT' + number + ';')
    time.sleep(15)

def sendMusic(phone, music):
    sendATCmd(phone, '+VTX')
    chunk = 1024
    cont = True
    while cont:
        frame = music.readframes(chunk)
        if frame == '':
            cont = False
            music.close()
            continue
        phone.write(chunk)
        time.sleep(0.12)
        phone.write(("<DLE><ETX>" + "\r\n").encode())
        # 15 sec Time Out
        timeout = time.time() + 15
        while 1:
            modem_data = phone.readline()
            if "OK" in modem_data:
                break
            if time.time() > timeout:
                break

def sendFile(phone, file):
    sendATCmd(phone, '+VTX')
    in_file = open(file, 'rb')
    cont = True
    while cont:
        frame = in_file.read(1)
        if frame == '':
            cont = False
            in_file.close()
        phone.write(b"".join(frame))

def hangUp(phone):
    sendATCmd(phone, 'H0')

def main(argv):
    text = ''
    try:
        opts, args = getopt.getopt(argv,"ht:")
    except getopt.GetoptError:
        print 'send_voice_message.py -t <Text>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'send_voice_message.py -t <Text>'
            sys.exit()
        elif opt in ("-t"):
            text = arg
    textToWav(text, 'message.wav')
    phone = initializePhone()
    #call(phone, '5524085')
    #music = wave.open('message.wav','rb')
    #music = wave.open('message-new.wav','rb')
    #sendMusic(phone, music)
    #sendFile(phone, 'message-new.wav')
    #time.sleep(5)
    hangUp(phone)
    phone.close()

if __name__=='__main__':
    main(sys.argv[1:])
