import struct
import zlib

from ephex_charset import chars, widths
from typing import BinaryIO, List, Tuple
#from PIL import Image
from PIL import Image, ImageDraw


Pixel = Tuple[int, int, int]
# Image = List[List[Pixel]]

BLACK_PIXEL: Pixel = (0, 0, 0)
WHITE_PIXEL: Pixel = (255, 255, 255)

HEADER = b'\x89PNG\r\n\x1A\n'
printermodel="DMP2000"
printerbit=8
pinsize=1 #pixels
debug=False
bitmap=[]

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
                bitmap[((y+(bl*2))*width)+x]=1
                #print("*", end="")
                # print ("X",end="")
            else:
                # print (h,w,bitloop,((h+bitloop)*height)+w)
                bitmap[((y+(bl*2))*width)+x]=0
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
    for q in range((width*(height+8))*8):
        bitmap.append(0)
    #h and w below are basically the print head position
    h=0 #initial height
    w=0 #initial width
    skipcount=0 #How many bytes to ignore if we find a control code
    #print (len(bitmap), len(ascii_text))
    gfxdata=0 #Counter for how much graphics data is upcoming

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
                                    gfxdata=(ord(ascii_text[printout+2])*127)+ord(ascii_text[printout+3])
                        case 0x1c:
                            #chr(1Ch,num,gfx)      Repetition of one byte of graphic print data
                            skip=1
                            amt=ord(ascii_text[printout+1])
                            gfx=ord(ascii_text[printout+2])
                            b=string_to_binary(ascii_text[gfx])
                            for l in range(amt):
                                for bitloop in range(printerbut,1,-1):
                                    #print (b[0])
                                    tmp=b[0][bitloop]
                                    # So each bit is a row down.
                                    if (tmp=="1"):
                                        bitmap[((h+bitloop)*width)+w]=1
                                        #print("*", end="")
                                    else:
                                        #print (h,w,bitloop,((h+bitloop)*height)+w)
                                        bitmap[((h+bitloop)*width)+w]=0
                                        #print(".", end="")
                                w=w+1
                case "DMP2000":
                    linesize=9
                    #This is 9x9 for character or 8x? for bit images
                    #60 dpi (single density)
                    #120 dpi (double density)
                    #240 dpi (faked, printed as 120dpi)
                    #72 (1:1 aspect ratio)
                    #80,90 dpi (for 640/720 pix screenshots)
                    #Not sure how much of this we actually need to worry about.
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
                                skipcount=1
                                skip=1
                                w=0
                                h=h+linesize #8 because we've written 7 bits down
                            case 0x0d:
                                #CR or CR+LF (selectable)
                                skipcount=2
                                skip=1
                                w=0
                            case 0x14:
                                #14 	20 	DC4 	Text Style 	Cancel one line double width mode (unlike ESC W 0/1 continous)
                                skipcount=1
                                skip=1
                            case 0x0c:
                                skip=1
                                #May have to figure out what to do here.
                                h=h+120
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
                                        skipcount=2
                                    case 0x40:
                                        #1B 40  Initialize printer (Reset)
                                        #Probably will ignore this
                                        skip=1
                                        skipcount=2
                                    case 0x41:
                                        #1B 41 n 	Select n/72 inch line spacing (n=0..85)
                                        skip=1
                                        skipcount=4
                                    case 0x4b:
                                        #1B 4B Graphics 	Print 8-pin 60-dpi graphics (same as ESC "*" 0, see there) (density of ESC "K" can be redefined via ESC "?")
                                        skip=1
                                        skipcount=4
                                        #Some 7 bit math to see how much we should ignore before we process more data
                                        gfxdata=(ord(ascii_text[printout+3])*128)+ord(ascii_text[printout+2])
                                        if debug:
                                            print ("Loc:",hex(printout),"has data",gfxdata,"bytes from ",hex(ord(ascii_text[printout+2])))," and", hex(ord(ascii_text[printout+3]))
                                            print ("next code should be at ",hex(printout+gfxdata))
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
                                            bitmap[((h+bitloop)*width)+w]=1
                                            #print("*", end="")
                                        else:
                                            #print (h,w,bitloop,((h+bitloop)*height)+w)
                                            bitmap[((h+bitloop)*width)+w]=0
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
                            tmp=b[0][printerbit-bitloop]
                        case "DMP2000":
                            tmp=b[0][bitloop]
                    # So each bit is a row down.
                    if (tmp=="1"):
                        bitmap[((h+bitloop)*width)+w]=1
                        #print("*", end="")
                    else:
                        # print (h,w,bitloop,((h+bitloop)*height)+w)
                        bitmap[((h+bitloop)*width)+w]=0
                        #print(".", end="")
            w=w+1
            if (w>width):
                w=0
                h=h+linesize #8 because we've written 7 bits down
    c=0
    h=h+16
    w=0
    for lookup in range(33,33+80):
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
        if (w>width):
            w=0
            h=h+linesize+1 #8 because we've written 7 bits down
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
            #print (headloc,fsize)
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
    width = 960
    height = 12600
    shape = [(40, 40), (10,10)]
    img = Image.new("RGB", (width, height))
    img = generate_printer(width, height,'./che-dmp2000.dat')
    # img = generate_printer(width, height,'./dumpetest.dat')
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
