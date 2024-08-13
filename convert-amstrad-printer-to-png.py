import struct
import zlib

#from ephex_charset import chars, widths
from typing import BinaryIO, List, Tuple
#from PIL import Image
from PIL import Image, ImageDraw


Pixel = Tuple[int, int, int]
# Image = List[List[Pixel]]

BLACK_PIXEL: Pixel = (0, 0, 0)
WHITE_PIXEL: Pixel = (255, 255, 255)
#bitmaps of the printer font
chars = [[4, 10, 32, 138, 96, 10, 32, 28, 2], [28, 34, 8, 162, 72, 34, 8, 34, 24], [0, 60, 0, 130, 64, 2, 0, 60, 2], [0, 28, 34, 128, 98, 0, 34, 28, 0], [0, 18, 128, 94, 0, 2, 0, 0, 0], [0, 0, 64, 160, 0, 160, 64, 0, 0], [18, 0, 126, 128, 18, 128, 2, 128, 66], [0, 0, 0, 0, 79, 0, 0, 0, 0], [6, 0, 9, 0, 81, 0, 1, 0, 2], [94, 128, 16, 128, 8, 64, 4, 64, 158], [64, 158, 0, 144, 64, 16, 78, 128, 0], [146, 40, 68, 0, 68, 0, 68, 40, 146], [254, 0, 160, 0, 72, 0, 30, 0, 10], [6, 8, 84, 160, 4, 160, 84, 8, 6], [4, 10, 32, 10, 160, 10, 32, 28, 2], [56, 68, 1, 68, 1, 70, 0, 68, 0], [0, 80, 170, 0, 170, 0, 170, 20, 0], [126, 128, 0, 128, 18, 128, 18, 108, 0], [62, 64, 144, 0, 254, 0, 146, 0, 146], [44, 2, 40, 2, 28, 32, 10, 32, 26], [58, 68, 0, 138, 16, 162, 0, 68, 184], [2, 8, 20, 34, 8, 34, 20, 8, 32], [0, 0, 128, 0, 0, 0, 128, 0, 0], [6, 136, 20, 32, 68, 32, 20, 136, 6], [28, 162, 0, 34, 0, 34, 0, 162, 28], [60, 130, 0, 2, 0, 2, 0, 130, 60], [4, 10, 160, 10, 32, 10, 160, 28, 2], [0, 28, 162, 0, 34, 0, 162, 28, 0], [0, 60, 128, 2, 0, 2, 128, 60, 2], [62, 0, 42, 0, 106, 128, 42, 0, 34], [28, 34, 8, 34, 72, 162, 8, 34, 24], [168, 0, 104, 0, 62, 0, 104, 0, 168], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 242, 0, 0, 0, 0], [0, 0, 224, 0, 0, 0, 224, 0, 0], [40, 0, 254, 0, 40, 0, 254, 0, 40], [36, 0, 84, 0, 254, 0, 84, 0, 72], [192, 2, 196, 8, 16, 32, 70, 128, 6], [76, 160, 18, 160, 74, 0, 4, 8, 18], [0, 0, 0, 0, 64, 128, 0, 0, 0], [0, 0, 0, 0, 56, 68, 130, 0, 0], [0, 0, 130, 68, 56, 0, 0, 0, 0], [16, 0, 84, 40, 16, 40, 84, 0, 16], [16, 0, 16, 0, 124, 0, 16, 0, 16], [0, 0, 0, 12, 1, 14, 0, 0, 0], [16, 0, 16, 0, 16, 0, 16, 0, 16], [0, 0, 6, 0, 6, 0, 0, 0, 0], [0, 2, 4, 8, 16, 32, 64, 128, 0], [56, 68, 0, 130, 0, 130, 0, 68, 56], [0, 0, 66, 0, 254, 0, 2, 0, 0], [66, 128, 6, 128, 10, 128, 18, 128, 98], [132, 0, 130, 0, 162, 0, 210, 0, 140], [8, 16, 40, 64, 136, 0, 254, 0, 8], [228, 2, 160, 2, 160, 2, 160, 2, 156], [12, 18, 32, 82, 128, 18, 0, 18, 12], [128, 0, 130, 4, 136, 16, 160, 64, 128], [108, 146, 0, 146, 0, 146, 0, 146, 108], [96, 144, 0, 144, 2, 148, 8, 144, 96], [0, 0, 54, 0, 54, 0, 0, 0, 0], [0, 0, 109, 0, 110, 0, 0, 0, 0], [16, 0, 40, 0, 68, 0, 130, 0, 0], [40, 0, 40, 0, 40, 0, 40, 0, 40], [0, 0, 130, 0, 68, 0, 40, 0, 16], [64, 128, 0, 128, 10, 128, 16, 128, 96], [56, 68, 130, 16, 170, 0, 170, 0, 122], [30, 32, 72, 128, 8, 128, 72, 32, 30], [130, 124, 130, 16, 130, 16, 130, 16, 108], [124, 130, 0, 130, 0, 130, 0, 130, 68], [130, 124, 130, 0, 130, 0, 130, 68, 56], [254, 0, 146, 0, 146, 0, 146, 0, 130], [254, 0, 144, 0, 144, 0, 144, 0, 128], [124, 130, 0, 130, 16, 130, 16, 130, 92], [254, 0, 16, 0, 16, 0, 16, 0, 254], [0, 0, 130, 0, 254, 0, 130, 0, 0], [12, 2, 0, 130, 0, 130, 124, 128, 0], [254, 0, 16, 0, 40, 0, 68, 0, 130], [254, 0, 2, 0, 2, 0, 2, 0, 2], [254, 0, 64, 32, 16, 32, 64, 0, 254], [254, 0, 64, 32, 16, 8, 4, 0, 254], [124, 130, 0, 130, 0, 130, 0, 130, 124], [254, 0, 144, 0, 144, 0, 144, 0, 96], [124, 130, 0, 130, 8, 130, 4, 128, 122], [254, 0, 144, 0, 144, 0, 152, 4, 98], [100, 146, 0, 146, 0, 146, 0, 146, 76], [128, 0, 128, 0, 254, 0, 128, 0, 128], [252, 2, 0, 2, 0, 2, 0, 2, 252], [224, 16, 8, 4, 2, 4, 8, 16, 224], [252, 2, 4, 8, 48, 8, 4, 2, 252], [0, 130, 68, 40, 16, 40, 68, 130, 0], [128, 64, 32, 16, 14, 16, 32, 64, 128], [0, 130, 4, 138, 16, 162, 64, 130, 0], [0, 0, 254, 0, 130, 0, 130, 0, 0], [0, 128, 64, 32, 16, 8, 4, 2, 0], [0, 0, 130, 0, 130, 0, 254, 0, 0], [32, 0, 64, 0, 128, 0, 64, 0, 32], [1, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 128, 64, 0, 0, 0, 0], [4, 10, 32, 10, 32, 10, 32, 28, 2], [254, 0, 34, 0, 34, 0, 34, 28, 0], [28, 34, 0, 34, 0, 34, 0, 34, 0], [28, 34, 0, 34, 0, 34, 0, 254, 0], [28, 34, 8, 34, 8, 34, 8, 34, 24], [16, 0, 16, 110, 144, 0, 144, 0, 0], [56, 68, 1, 68, 1, 68, 1, 126, 0], [254, 0, 32, 0, 32, 0, 32, 30, 0], [0, 34, 0, 190, 0, 2, 0, 0, 0], [0, 1, 0, 1, 32, 1, 190, 0, 0], [0, 254, 0, 8, 0, 20, 0, 34, 0], [0, 130, 0, 254, 0, 2, 0, 0, 0], [30, 32, 0, 32, 30, 32, 0, 32, 30], [62, 0, 32, 0, 32, 0, 32, 30, 0], [28, 34, 0, 34, 0, 34, 0, 34, 28], [127, 0, 68, 0, 68, 0, 68, 56, 0], [0, 56, 68, 0, 68, 0, 68, 0, 127], [62, 0, 16, 32, 0, 32, 0, 32, 0], [16, 42, 0, 42, 0, 42, 0, 42, 4], [32, 0, 252, 2, 32, 2, 32, 2, 0], [60, 2, 0, 2, 0, 2, 0, 60, 2], [32, 16, 8, 4, 2, 4, 8, 16, 32], [60, 2, 4, 8, 16, 8, 4, 2, 60], [34, 20, 0, 8, 0, 20, 34, 0, 0], [64, 32, 17, 10, 4, 8, 16, 32, 64], [34, 4, 34, 8, 34, 16, 34, 0, 0], [0, 0, 16, 0, 108, 130, 0, 130, 0], [0, 0, 0, 0, 238, 0, 0, 0, 0], [0, 130, 0, 130, 108, 0, 16, 0, 0], [64, 128, 0, 128, 64, 32, 0, 32, 64], [124, 130, 4, 138, 16, 162, 64, 130, 124], [4, 10, 32, 138, 96, 10, 36, 26, 0], [12, 18, 40, 130, 104, 2, 40, 16, 0], [12, 50, 0, 130, 64, 2, 12, 50, 0], [12, 18, 0, 160, 66, 0, 36, 24, 0], [0, 2, 0, 22, 136, 82, 0, 0, 0], [0, 0, 64, 160, 0, 160, 64, 0, 0], [18, 0, 30, 96, 18, 128, 18, 128, 64], [0, 1, 2, 4, 8, 16, 0, 128, 0], [6, 1, 8, 1, 16, 33, 128, 2, 0], [6, 88, 128, 8, 132, 64, 6, 88, 128], [18, 76, 128, 16, 128, 80, 2, 76, 128], [2, 24, 36, 128, 68, 2, 72, 48, 128], [6, 56, 192, 32, 136, 38, 216, 2, 8], [2, 4, 8, 20, 64, 164, 0, 190, 64], [4, 10, 32, 10, 32, 138, 36, 26, 0], [0, 24, 33, 4, 65, 6, 64, 4, 64], [2, 16, 106, 0, 170, 0, 172, 16, 128], [6, 24, 96, 0, 130, 16, 130, 108, 0], [14, 48, 64, 144, 14, 112, 130, 16, 130], [4, 34, 8, 34, 28, 34, 8, 34, 16], [26, 36, 66, 8, 146, 32, 132, 72, 176], [12, 17, 2, 44, 18, 32, 68, 24, 0], [0, 0, 128, 0, 0, 0, 128, 0, 0], [2, 4, 8, 20, 128, 36, 0, 62, 128], [12, 18, 0, 162, 0, 34, 0, 164, 24], [12, 50, 0, 130, 0, 2, 0, 140, 48], [4, 10, 32, 138, 32, 10, 36, 154, 0], [12, 18, 0, 160, 2, 0, 36, 152, 0], [12, 50, 128, 2, 0, 2, 12, 178, 0], [6, 24, 34, 8, 34, 72, 34, 128, 32], [12, 18, 40, 2, 104, 2, 168, 16, 0], [8, 32, 136, 102, 24, 32, 72, 32, 128], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 2, 0, 8, 16, 32, 64, 128, 0], [0, 32, 64, 128, 0, 32, 64, 128, 0], [40, 6, 56, 192, 40, 6, 56, 192, 40], [0, 36, 16, 70, 56, 196, 16, 72, 0], [64, 130, 68, 136, 16, 34, 68, 130, 4], [12, 16, 66, 160, 18, 168, 68, 10, 16], [0, 0, 0, 0, 64, 128, 0, 0, 0], [0, 0, 0, 28, 34, 64, 0, 128, 0], [0, 2, 0, 4, 136, 112, 0, 0, 0], [16, 4, 80, 40, 16, 40, 20, 64, 16], [16, 0, 20, 8, 16, 32, 80, 0, 16], [0, 0, 1, 4, 10, 4, 8, 0, 0], [16, 0, 16, 0, 16, 0, 16, 0, 16], [0, 0, 2, 4, 2, 4, 0, 0, 0], [0, 2, 4, 8, 16, 32, 64, 128, 0], [28, 32, 66, 0, 130, 0, 132, 8, 112], [0, 2, 0, 70, 24, 98, 128, 0, 0], [2, 64, 6, 128, 10, 128, 18, 128, 96], [4, 0, 130, 0, 146, 0, 178, 76, 128], [8, 16, 8, 32, 8, 70, 56, 192, 8], [4, 96, 130, 32, 130, 32, 132, 24, 128], [12, 16, 34, 16, 66, 16, 130, 12, 0], [128, 2, 132, 8, 144, 32, 128, 64, 128], [12, 98, 16, 130, 16, 130, 16, 140, 96], [96, 2, 144, 4, 144, 8, 144, 96, 0], [0, 0, 2, 20, 34, 20, 32, 0, 0], [0, 0, 1, 4, 42, 68, 40, 64, 0], [0, 16, 8, 36, 2, 64, 0, 128, 0], [8, 32, 8, 32, 8, 32, 8, 32, 0], [0, 2, 0, 4, 128, 72, 32, 16, 0], [64, 2, 128, 8, 128, 16, 128, 96, 0], [28, 32, 66, 128, 18, 136, 34, 136, 112], [2, 4, 8, 16, 40, 64, 136, 0, 254], [6, 152, 98, 128, 18, 128, 18, 140, 96], [28, 34, 64, 130, 0, 130, 0, 132, 64], [6, 152, 98, 128, 2, 128, 4, 136, 112], [6, 56, 194, 16, 130, 16, 130, 0, 128], [6, 56, 192, 16, 128, 16, 128, 0, 128], [28, 34, 64, 130, 0, 146, 4, 152, 64], [6, 56, 192, 16, 0, 16, 6, 56, 192], [0, 2, 0, 134, 24, 226, 0, 128, 0], [12, 2, 0, 2, 128, 4, 152, 96, 128], [6, 56, 192, 16, 32, 8, 68, 2, 128], [0, 6, 24, 98, 128, 2, 0, 2, 0], [6, 56, 192, 0, 48, 0, 70, 56, 192], [6, 56, 192, 32, 16, 8, 6, 56, 192], [12, 50, 64, 130, 0, 130, 4, 152, 96], [6, 24, 96, 144, 0, 144, 0, 144, 96], [28, 32, 66, 0, 138, 0, 132, 10, 112], [6, 24, 96, 128, 16, 136, 20, 130, 96], [4, 98, 0, 146, 0, 146, 0, 140, 64], [128, 0, 134, 24, 224, 0, 128, 0, 128], [12, 50, 192, 2, 0, 2, 12, 48, 192], [0, 254, 0, 4, 8, 16, 32, 64, 128], [6, 56, 196, 8, 16, 8, 6, 56, 192], [2, 132, 72, 32, 24, 36, 2, 64, 128], [128, 64, 38, 24, 0, 32, 0, 64, 128], [2, 4, 138, 0, 146, 0, 162, 64, 128], [0, 6, 24, 98, 128, 2, 128, 0, 128], [0, 0, 192, 48, 12, 2, 0, 0, 0], [2, 0, 2, 128, 6, 152, 96, 128, 0], [0, 32, 0, 64, 0, 128, 64, 32, 0], [1, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 128, 64, 0, 0, 0, 0], [4, 10, 32, 10, 32, 10, 36, 26, 0], [6, 24, 226, 0, 34, 0, 36, 24, 0], [12, 16, 2, 32, 2, 32, 2, 32, 0], [12, 16, 2, 32, 2, 32, 6, 56, 192], [12, 18, 40, 2, 40, 2, 40, 16, 0], [32, 0, 38, 24, 96, 0, 160, 0, 128], [0, 24, 37, 0, 69, 0, 70, 24, 96], [6, 24, 224, 0, 32, 0, 38, 24, 0], [0, 2, 0, 38, 24, 34, 128, 0, 0], [1, 0, 1, 0, 38, 24, 160, 0, 0], [6, 24, 96, 136, 4, 18, 0, 32, 0], [0, 2, 0, 6, 152, 98, 128, 0, 0], [38, 24, 32, 6, 56, 0, 38, 24, 0], [38, 24, 32, 0, 32, 6, 24, 0, 0], [12, 18, 0, 32, 2, 0, 36, 24, 0], [3, 28, 96, 4, 64, 4, 72, 48, 0], [0, 24, 36, 0, 68, 0, 71, 24, 96], [6, 56, 0, 16, 32, 0, 32, 0, 0], [2, 16, 2, 40, 2, 40, 4, 32, 0], [0, 32, 12, 50, 192, 34, 0, 32, 0], [12, 50, 0, 2, 0, 2, 12, 50, 0], [0, 62, 0, 4, 0, 8, 16, 32, 0], [14, 48, 4, 0, 24, 4, 0, 6, 56], [2, 0, 36, 16, 8, 4, 18, 0, 32], [0, 64, 33, 18, 4, 8, 16, 32, 64], [2, 0, 38, 0, 42, 0, 50, 0, 32], [0, 16, 4, 26, 96, 130, 0, 128, 0], [0, 2, 4, 8, 32, 64, 128, 0, 0], [0, 2, 0, 130, 12, 176, 64, 16, 0], [64, 128, 0, 128, 64, 32, 0, 32, 64], [26, 36, 66, 8, 146, 32, 132, 72, 176]]

HEADER = b'\x89PNG\r\n\x1A\n'
# printermodel="DMP2000"
printerbit=8
pinsize=1 #pixels
debug=False
# debug=True
bitmap=[]

def update_bitmap(location, value):
    #update the bitmap, and extend it if the requested location is out of bounds.
    global bitmap
    diff=location-len(bitmap)
    # if debug:
        # print ("Diff is",diff)
        # print (len(bitmap),location)
    if location>=len(bitmap):
        for q in range(len(bitmap),location+128):
            bitmap.append(0)
        # print("bitmap bumped")
    bitmap[location]=value

def string_to_binary(st : str):
    return [bin(ord(i))[2:].zfill(8) for i in st]

def printchar(ascii_code,y,x):
    global bitmap

    l=chars[ascii_code]
    for l2 in l:
        # print (l, "-",end="")
        b=string_to_binary(chr(l2))
        for bl in range(0,8):
            # print (bl)
            tmp=b[0][bl]
            if (tmp=="1"):
                update_bitmap(((y+(bl*2))*width)+x,1)
                #print("*", end="")
                # print ("X",end="")
            else:
                # print (h,w,bitloop,((h+bitloop)*height)+w)
                update_bitmap(((y+(bl*2))*width)+x,0)
                #print(".", end="")
                # print(".",end="")
        # print (l)
        # print (widths[71])
        #
        #Make wrapping someone elses problem
        x=x+1
        # if (x>width):
        #     x=0
        #     h=h+linesize+1 #8 because we've written 7 bits down
    x=x+(3)
    return x

def generate_printer(width: int, height: int, my_file: str) -> Image:
    global bitmap
    with open(my_file, 'r') as f:
        ascii_text = f.read()

    #Lets try and build out the printout.
    #So this is a set of bits.
    #Each bit is a pin on the printhead, but it also sweeps across.
    #So We need to move left to right, but also several bits down each time.
    #It's mathing time!
    #
    #First lets initialize a bitmap and zero it
    print ("Rendering as ",printermodel)
    print ("Available print space: ",(width*(height+8))*8,"bytes")
    print ("Data size:",len(ascii_text),"bytes")
    print ("Bitmap size:",len(bitmap))
    # for q in range((width*(height+8))*8):
    #     bitmap.append(0)
    #h and w below are basically the print head position
    h=0 #initial height
    w=0 #initial width
    skipcount=0 #How many bytes to ignore if we find a control code
    #print (len(bitmap), len(ascii_text))
    gfxdata=0 #Counter for how much graphics data is upcoming
    linesize=12

    for printout in range(len(ascii_text)):
        # print ("Printout=",printout)
        #For this next bit, we'll try and add the data.
        b=string_to_binary(ascii_text[printout]) #convert the data to binary
        skip=0
        if gfxdata==0: #If we're handling graphics data don't process anything
            #Most of this is considered a #TODO
            #Right now it's more about just not processing control codes as data
            match printermodel:
                case "DMP1":
                    #This is a 7x5 print head
                    #60 dpi
                    printerbit=8 #Technically 7, but py range starts at upperlimit-1
                    match ord(ascii_text[printout]):
                        case 0x0:
                            #Sometimes it seems like programs dump extra zeros, or maybe its an emulator.
                            #in any case, we're going to ignore it
                            skip=1
                            skipcount=1
                        case 0x0a:
                            #CR+LF
                            skipcount=1
                            skip=1
                            w=0
                            h=h+7 #8 because we've written 7 bits down
                        case 0x0d:
                            #CR or CR+LF (selectable)
                            skipcount=2
                            skip=1
                            w=0
                        case 0x14:
                            #Also CR, oddly enough
                            skipcount=2
                            skip=1
                            w=0
                            h=h+8
                        case 0x0e:
                            #Double width mode
                            skipcount=2
                            skip=1
                        case 0x0f:
                            #Normal width mode
                            skipcount=2
                            skip=1
                        case 0x16:
                            #Takes 2 bytes after 0x16
                            #Print Position in character units (NN = two-digit ASCII, "00..79")
                            skip=1
                            skipcount=3
                        case 0x1b:
                            next=ord(ascii_text[printout+1])
                            match next:
                                case 0x10:
                                    #Print Position in dot units (hi:lo = 9bit binary, 0..479) (lo=lower 7bit, hi=upper 2bit)
                                    skip=1
                                    skipcount=4
                                case 0x4b:
                                    #chr(1Bh,4Bh,hi,lo,gfx0,gfx1,..) Graphics Mode (hi:lo = 9bit count, 0..479) (followed by as many bytes, with bit0=upper pixel .. bit6=lower pixel)
                                    skip=1
                                    skipcount=4
                                    #Some 7 bit math to see how much we should ignore before we process more data
                                    #Epson/DMP2000 actually works as 8 bit on this. We'll use 128 as our multiplier here
                                    gfxdata=(ord(ascii_text[printout+2])*128)+ord(ascii_text[printout+3])
                        case 0x1c:
                            #chr(1Ch,num,gfx)      Repetition of one byte of graphic print data
                            skip=1
                            amt=ord(ascii_text[printout+1])
                            gfx=ord(ascii_text[printout+2])
                            b=string_to_binary(ascii_text[gfx])
                            for l in range(amt):
                                for bitloop in range(printerbit-1,0,-1):
                                    #print (b[0])
                                    tmp=b[0][bitloop]
                                    # So each bit is a row down.
                                    if (tmp=="1"):
                                        update_bitmap(((h+bitloop)*width)+w,1)
                                        #print("*", end="")
                                    else:
                                        #print (h,w,bitloop,((h+bitloop)*height)+w)
                                        update_bitmap(((h+bitloop)*width)+w,0)
                                        #print(".", end="")
                                w=w+1
                case "DMP2000":
                    #This is 9x9 for character or 8x? for bit images
                    #60 dpi (single density)
                    #120 dpi (double density)
                    #240 dpi (faked, printed as 120dpi)
                    #72 (1:1 aspect ratio)
                    #80,90 dpi (for 640/720 pix screenshots)
                    #Not sure how much of this we actually need to worry about.
                    #n/216
                    #A4=210 x 297 mm
                    #Dot matrix paper is 279 x 241mm (11 x 9.5")
                    #DMP2000 is 60 dpi, 480 pix per 8 inch, single density graphics default
                    #9.5" wide * 60 dpi = 570 dots
                    #11" * 60 dpi = 660
                    #Standard font is 10 characters per inch, 80 characters per line
                    #Mini (elite) is 12 CPI/96 pl
                    #Condensed is 17 cpi/137 pl
                    #double standard is 5CPI/4 pl (Note, can just do a second loop on character to do that!)
                    #other doubles are literally just double what the font is
                    #Each line is 1/6th inch.
                    #Each page should be 66 lines.

                    #Ref: https://files.support.epson.com/pdf/fx80__/fx80__uv.pdf

                    printerbit=8 #Technically 8, but py range starts at upperlimit-1
                    #This is an 8 bit printer (DMP1 is 7 bit)
                    if skipcount==0:
                        match ord(ascii_text[printout]):
                            case 0x0:
                                #Sometimes it seems like programs dump extra zeros, or maybe its an emulator.
                                #in any case, we're going to ignore it
                                skip=1
                                skipcount=1
                            case 0x08:
                                #Backspace
                                skipcount=1
                                skip=1
                                w=w-1
                            case 0x09:
                                #09 	9 	HT 	Tab 	Horizontal tab (see ESC "D")
                                skipcount=1
                                skip=1
                                w=w+8 #I dunno. I'm guessing here. TODO
                            case 0x0a:
                                #CR+LF
                                if debug:
                                    print ("CR/LF, gfxdata=",gfxdata,", linesize=",linesize)
                                skipcount=1
                                skip=1
                                w=0
                                h=h+linesize #8 because we've written 7 bits down
                            case 0x0d:
                                #CR or CR+LF (selectable)
                                skipcount=2
                                skip=1
                                w=0
                                if debug:
                                    print ("Newline, linesize=",linesize)
                            case 0x14:
                                #14 	20 	DC4 	Text Style 	Cancel one line double width mode (unlike ESC W 0/1 continous)
                                skipcount=1
                                skip=1
                            case 0x0c:
                                skip=1
                                #May have to figure out what to do here.
                                h=h+120 #lets just do a bunch
                            case 0x0e:
                                #Double width mode
                                skipcount=2
                                skip=1
                            case 0x0f:
                                #Normal width mode
                                skipcount=2
                                skip=1
                            case 0x16:
                                #Takes 2 bytes after 0x16
                                #Print Position in character units (NN = two-digit ASCII, "00..79")
                                skip=1
                                skipcount=3
                            case 0x1b:
                                next=ord(ascii_text[printout+1])
                                if (debug):
                                    print ("Loc:",hex(printout),"Processing: 0x1b,",hex(next))
                                match next:
                                    case 0x10:
                                        #Print Position in dot units (hi:lo = 9bit binary, 0..479) (lo=lower 7bit, hi=upper 2bit)
                                        skip=1
                                        skipcount=4
                                    case 0x33:
                                        #1B 33	Select n/216 inch line spacing (n=0..255)
                                        skip=1
                                        skipcount=3
                                        if debug:
                                            print ("Linesize=",linesize," and requested ",next)
                                            print ("Line spacing n/216",hex(next))
                                            print ("New linesize=",int(216/(next)*2))
                                        linesize=int(216/(next)*2)
                                    case 0x40:
                                        #1B 40  Initialize printer (Reset)
                                        skip=1
                                        skipcount=2
                                        linesize=12 #default linesize
                                    case 0x41:
                                        #1B 41 n 	Select n/72 inch line spacing (n=0..85)
                                        skip=1
                                        skipcount=4
                                        #if debug:
                                        ls=int(next/8)
                                        print ("Linesize=",linesize," and requested ",next)
                                        print ("Line spacing n/72",hex(next))
                                        print ("New linesize=",ls)
                                        linesize=ls #int(72/(next)*2)
                                        #linesize=8
                                    case 0x4b:
                                        #1B 4B Graphics 	Print 8-pin 60-dpi graphics (same as ESC "*" 0, see there) (density of ESC "K" can be redefined via ESC "?")
                                        skip=1
                                        skipcount=4
                                        #Some 7 bit math to see how much we should ignore before we process more data
                                        gfxdata=(ord(ascii_text[printout+3])*256)+ord(ascii_text[printout+2])
                                        if debug:
                                            print (hex(ord(ascii_text[printout+2])))
                                            print (hex(ord(ascii_text[printout+3])))
                                            print ("->Loc:",hex(printout),"has data ",gfxdata,end="")
                                            print ("bytes from ",hex(ord(ascii_text[printout+2])))," and ",hex(ord(ascii_text[printout+3]))
                                            print ("    next code should be at ",hex(printout+gfxdata))
                                    case 0x4c:
                                        #1B 4C lo hi Print 8-pin 120-dpi graphics (same as ESC "*" 1, see there) (density of ESC "L" can be redefined via ESC "?")
                                        skip=1
                                        skipcount=4
                                        width=960 #If we're using 120dpi, we need to double the default "paper" we setup (was 480)
                                        #Some 7 bit math to see how much we should ignore before we process more data
                                        gfxdata=(ord(ascii_text[printout+3])*256)+ord(ascii_text[printout+2])
                                        if debug:
                                            print ("Loc:",hex(printout),"has data ",gfxdata,"bytes  from ",hex(ord(ascii_text[printout+2]))," and", hex(ord(ascii_text[printout+3])))
                                            print ("next code should be at ",hex(printout+gfxdata))
                                    case 0x5a:
                                        #1B 5A lo hi Print 8-pin 240/2-dpi graphics (same as ESC "*" 3, see there) (density of ESC "Z" can be redefined via ESC "?")
                                        skip=1
                                        skipcount=4
                                        width=1920 #If we're using 240dpi, we need to quadruple the default "paper" we setup (was 480)
                                        #Some 7 bit math to see how much we should ignore before we process more data
                                        gfxdata=(ord(ascii_text[printout+3])*256)+ord(ascii_text[printout+2])
                                        if debug:
                                            print ("Loc:",hex(printout),"has data ",gfxdata,"bytes  from ",hex(ord(ascii_text[printout+2]))," and", hex(ord(ascii_text[printout+3])))
                                            print ("next code should be at ",hex(printout+gfxdata))
                                    case 0x5e:
                                        print ("WARNING!!! 9 bit print mode enabled, but this is not yet implemented")
                                    case _:
                                        print ("Unimplemented 0x1b function found: 0x1b,",hex(ord(ascii_text[printout+1])))
                            case 0x1c:
                                #chr(1Ch,num,gfx)      Repetition of one byte of graphic print data
                                skip=1
                                amt=ord(ascii_text[printout+1])
                                gfx=ord(ascii_text[printout+2])
                                b=string_to_binary(ascii_text[gfx])
                                for l in range(amt):
                                    for bitloop in range(1,printerbit):
                                        #print (b[0])
                                        tmp=b[0][bitloop]
                                        # So each bit is a row down.
                                        if (tmp=="1"):
                                            update_bitmap(((h+bitloop)*width)+w,1)
                                            #print("*", end="")
                                        else:
                                            #print (h,w,bitloop,((h+bitloop)*height)+w)
                                            update_bitmap(((h+bitloop)*width)+w,0)
                                            #print(".", end="")
                                    w=w+1
                            case _:
                                print ("Unimplemented function found: ",hex(ord(ascii_text[printout]))," at around ",hex(printout))

        # print ("outer Skipcount=",skipcount)
        if skipcount>0:
            skipcount=skipcount-1
            # print ("Skipcount=",skipcount)
        else:
            if skip==0:
                if gfxdata>0:
                    gfxdata=gfxdata-1 #count down if we're process graphics
                for bitloop in range(0,printerbit):
                    #print (b[0])
                    # tmp=b[0][printerbit-bitloop]
                    match printermodel:
                        #DMP1 seems to work from bits 8 to 1
                        #DMP2000 works bits 1 to 8
                        case "DMP1":
                            #print (bitloop)
                            #the printerbit-1 is a fixup to make it go 7 to 0 instead of 8 to 1
                            tmp=b[0][(printerbit-1)-bitloop]
                        case "DMP2000":
                            tmp=b[0][bitloop]
                    # So each bit is a row down.
                    if (tmp=="1"):
                        update_bitmap((((h+bitloop)*width)+w),1)
                        #print("*", end="")
                    else:
                        # print (h,w,bitloop,((h+bitloop)*height)+w)
                        # print (((h+bitloop)*width)+w)
                        update_bitmap((((h+bitloop)*width)+w),0)
                        #print(".", end="")
            w=w+1
            if (w>width):
                w=0
                h=h+linesize #8 because we've written 7 bits down
    c=0
    h=h+linesize
    w=0
    for lookup in range(33,33+160):
        # l=chars[lookup]
        # c=c+1
        # if c>80:
        #     h=h+linesize
        #     c=0
        #     w=0
        # for l2 in l:
        #     # print (l, "-",end="")
        #     b=string_to_binary(chr(l2))
        #     for bl in range(0,8):
        #         # print (bl)
        #         tmp=b[0][bl]
        #         if (tmp=="1"):
        #             bitmap[((h+(bl*2))*width)+w]=1
        #             #print("*", end="")
        #             # print ("X",end="")
        #         # else:
        #         #     # print (h,w,bitloop,((h+bitloop)*height)+w)
        #         #     bitmap[((h+bl)*width)+w]=0
        #         #     #print(".", end="")
        #         #     # print(".",end="")
        #     # print (l)
        #     # print (widths[71])
            # w=w+1
        w=printchar(lookup,h,w)
        if (w>(width-12)):
            w=0
            h=h+(linesize*2)+1 #8 because we've written 7 bits down
        # w=w+3
    h=h+32


    #Now take the bitmap and generate the image from it.
    print ("Height:",h)
    #Scale the PNG height to the length of the image.
    height=h
    page = Image.new("RGB", (width, height),"white")
    page1 = ImageDraw.Draw(page)
    #page1.ellipse(shape, fill ="#ffff33", outline ="red")
    out = []
    fsize = len(ascii_text)
    headloc=0
    for y in range(height):
        # Generate a single row of white/black pixels
        row = []
        for x in range(width):
            # print (headloc,len(bitmap))
            if headloc>=len(bitmap):
                #fill out the bitmap so the image doesn't look odd.
                update_bitmap(headloc,0)
            headpin=bitmap[headloc]
            headloc=headloc+1
            if headpin==1:
                #row.append(BLACK_PIXEL)
                shape = [(x, y), (x + pinsize, y + pinsize)]
                page1.ellipse(shape, fill ="black", outline ="black")

            # else:
            #     shape = [(x, y), (x + 2, y +2)]
            #     page1.ellipse(shape, fill ="black", outline ="black")

                #row.append(WHITE_PIXEL)
        # out.append(row)
    return page


def get_checksum(chunk_type: bytes, data: bytes) -> int:
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(data, checksum)
    return checksum


def chunk(out: BinaryIO, chunk_type: bytes, data: bytes) -> None:
    out.write(struct.pack('>I', len(data)))
    out.write(chunk_type)
    out.write(data)

    checksum = get_checksum(chunk_type, data)
    out.write(struct.pack('>I', checksum))


def make_ihdr(width: int, height: int, bit_depth: int, color_type: int) -> bytes:
    return struct.pack('>2I5B', width, height, bit_depth, color_type, 0, 0, 0)


def encode_data(img: Image) -> List[int]:
    ret = []

    for row in img:
        ret.append(0)

        color_values = [
            color_value
            for pixel in row
            for color_value in pixel
        ]
        ret.extend(color_values)

    return ret


def compress_data(data: List[int]) -> bytes:
    data_bytes = bytearray(data)
    return zlib.compress(data_bytes)


def make_idat(img: Image) -> bytes:
    encoded_data = encode_data(img)
    compressed_data = compress_data(encoded_data)
    return compressed_data


def dump_png(out: BinaryIO, img: Image) -> None:
    out.write(HEADER)  # start by writing the header

    assert len(img) > 0  # assume we were not given empty image data
    width = len(img[0])
    height = len(img)
    bit_depth = 8  # bits per pixel
    color_type = 2  # pixel is RGB triple

    ihdr_data = make_ihdr(width, height, bit_depth, color_type)
    chunk(out, b'IHDR', ihdr_data)

    compressed_data = make_idat(img)
    chunk(out, b'IDAT', data=compressed_data)

    chunk(out, b'IEND', data=b'')


def save_png(img: Image, filename: str) -> None:
    with open(filename, 'wb') as out:
        dump_png(out, img)


if __name__ == '__main__':
    #A4=210 x 297 mm
    #Dot matrix paper is 279 x 241mm (11 x 9.5")
    #DMP2000 is 60 dpi, 480 pix per 8 inch, single density graphics default
    #9.5" wide * 60 dpi = 570 dots
    #11" * 60 dpi = 660
    #Standard font is 10 characters per inch, 80 characters per line
    #Mini (elite) is 12 CPI/96 pl
    #Condensed is 17 cpi/137 pl
    #double standard is 5CPI/4 pl (Note, can just do a second loop on character to do that!)
    #other doubles are literally just double what the font is
    #Ref: https://files.support.epson.com/pdf/fx80__/fx80__uv.pdf
    width = 960
    height = 12600
    shape = [(40, 40), (10,10)]
    img = Image.new("RGB", (width, height))
    #img = generate_printer(width, height,'./graph-epson.dat')
    # img = generate_printer(width, height,'./dumpetest.dat')
    # img = generate_printer(width, height,'./che-dmp2000.dat')

    # printermodel="DMP1"
    # img = generate_printer(width, height,'./graph-dmp1.dat')
    printermodel="DMP2000"
    img = generate_printer(width, height,'./graph-dmp2000.dat')
    img.show()
    # for l in chars:
    #     for l2 in l:
    #         print ("->",l, end="")
    #
    # # img.ellipse((25, 50, 175, 200), fill="red")
    # image = Image.new("RGB", (400, 400), "white")
    # #ellipse(self, xy, fill=None, outline=None, width=1):
    # #
    # image.ellipse(image,(25, 50), fill="red")

    # w, h = 220, 190
    # shape = [(40, 40), (w - 10, h - 10)]

    # creating new Image object
    # img = Image.new("RGB", (w, h))

    # create ellipse image
    # img1 = ImageDraw.Draw(img)
    # img1.ellipse(shape, fill ="#ffff33", outline ="red")
    # img.show()
    # save_png(image, 'out.png')
    # print (chars)
