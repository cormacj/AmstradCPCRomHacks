import struct
import zlib
from typing import BinaryIO, List, Tuple
from PIL import Image

Pixel = Tuple[int, int, int]
Image = List[List[Pixel]]

BLACK_PIXEL: Pixel = (0, 0, 0)
WHITE_PIXEL: Pixel = (255, 255, 255)

HEADER = b'\x89PNG\r\n\x1A\n'
printermodel="DMP2000"
printerbit=7
def string_to_binary(st : str):
    return [bin(ord(i))[2:].zfill(8) for i in st]


def generate_printer(width: int, height: int, my_file: str) -> Image:

    with open(my_file, 'r') as f:
        ascii_text = f.read()

    #Lets try and build out the printout.
    #So this is a set of bits.
    #Each bit is a pin on the printhead, but it also sweeps across.
    #So We need to move left to right, but also 7 bits down each time.
    #It's mathing time!
    #
    #First lets initialize a bitmap.
    bitmap=[]
    print ((width*(height+8))*8)
    for q in range((width*(height+8))*8):
        bitmap.append(0)
    h=0
    w=0
    skipcount=0
    print (len(bitmap), len(ascii_text))
    dataloc=0
    gfxdata=0

    for printout in range(len(ascii_text)):
        # print ("Printout=",printout)
        #For this next bit, we'll try and add the data.
        b=string_to_binary(ascii_text[printout])
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
                    #This is 9x9 for character or 8x? for bit images
                    #60 dpi (single density)
                    #120 dpi (double density)
                    #240 dpi (faked, printed as 120dpi)
                    #72 (1:1 aspect ratio)
                    #80,90 dpi (for 640/720 pix screenshots)
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
                                skipcount=1
                                skip=1
                                w=w+8 #I dunno. I'm guessing here. TODO
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
                                    case 0x33:
                                        #1B 33	Select n/216 inch line spacing (n=0..255)
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
                                        gfxdata=(ord(ascii_text[printout+3])*127)+ord(ascii_text[printout+2])
                                        print ("Loc:",hex(printout),"has data ",(ord(ascii_text[printout+3])*127)+ord(ascii_text[printout+2])," from ",(ord(ascii_text[printout+2]))," and", ord(ascii_text[printout+3]))
                                        print ("next code should be at ",hex(printout+gfxdata))
                                    case 0x4c:
                                        #1B 4C lo hi Print 8-pin 120-dpi graphics (same as ESC "*" 1, see there) (density of ESC "L" can be redefined via ESC "?")
                                        skip=1
                                        skipcount=4
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
                for bitloop in range(1,printerbit):
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
                h=h+8 #8 because we've written 7 bits down

    #Now take the bitmap and generate the image from it.
    print ("Height:",h)
    #Scale the PNG height to the lenght of the image.
    height=h
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
                row.append(BLACK_PIXEL)
            else:
                row.append(WHITE_PIXEL)
            # print (b)
            # if (i + j) % 2 == 0:
            #     row.append(WHITE_PIXEL)
            # else:
            #     row.append(BLACK_PIXEL)
        # for l in range(1,8):
        #     #print (row[l])
        #     print ("")
        out.append(row)
    return out


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
    width = 480
    height = 600
    img = generate_printer(width, height,'./che-dmp2000.dat')
    save_png(img, 'out.png')
