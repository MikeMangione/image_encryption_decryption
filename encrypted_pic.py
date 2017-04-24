#!/usr/bin/env python

import cv2
import numpy as np
import os.path
from Crypto.Cipher import DES,DES3,AES
from Crypto import Random
from binascii import hexlify

def block_maker(int_vals):
    assert(len(int_vals)%8==0)
    assert(all(item < 256 for item in int_vals))
    out = ""
    for x in int_vals:
        t = hex(x)[2:]
        out += chr(int("0x" + "0" * (2 - len(t)) + t,16))
    return out

def block_breaker(str_val):
    assert(all(item in "0123456789abcdef" for item in str_val))
    out = []
    for x in range(len(str_val)/2):
         out.append(int("0x"+str_val[x*2:(x+1)*2],16))
    return out

class EncryptedImage:
    def __init__(self,scheme,mode,key,im_src_in):
        self.tmp_img = cv2.imread(im_src_in)
        self.mode = mode
        self.scheme = scheme
        self.iv = Random.new().read(self.scheme.block_size)
        self.cipher = self.scheme.new(key, self.mode, self.iv)

    def enc(self):
        h,w,d = self.tmp_img.shape
        new_new = self.tmp_img.flatten().tolist()
        self.val_enc = block_breaker(hexlify(self.cipher.encrypt(block_maker(new_new))))
        self.enc_img = np.asarray(self.val_enc[:h*w*d]).reshape((h,w,d))
        return self.enc_img

    def dec(self):
        h,w,d = self.enc_img.shape
        new_new = self.enc_img.flatten().tolist()
        self.val_dec = block_breaker(hexlify(self.cipher.decrypt(block_maker(new_new))))
        self.dec_img = np.asarray(self.val_dec[:h*w*d]).reshape((h,w,d))
        return self.dec_img

if __name__ == '__main__':
    im_src_in = raw_input("Which photo would you like to use for encryption/decryption? ")
    if im_src_in is '' or not os.path.isfile(str(im_src_in)):
        print("\nImage not found\n")
        if not os.path.isfile("eve.png"):
            print("\nand you moved the eve photo! Run the script again and choose another photo\n")
        else:
            print("Defaulting to eve.png")
            im_src_in = "eve.png"
    sch = raw_input("Which cipher? (choose from the numbers below)\nDES = 0\nDES3 = 1\nAES = 2\n")
    if sch is '' or not (int(sch) <=2 and int(sch) >=0):
        print("\nNot a valid choice, defaulting to AES\n")
        sch = 2
    scheme = [DES,DES3,AES][int(sch)]
    mode_ = raw_input("Which mode? (choose from the numbers below)\nECB = 1\nCBC = 2\nCFB = 3\n")
    if mode_ is '' or int(mode_) not in [1,2,3]:
        print("\nNot a valid choice, defaulting to CBC\n")
        mode_ = 2
    if sch != 1:
        key = raw_input("Choose a key with 16 letters or numbers\n")
    else:
        key = raw_input("Choose a key with "+str(scheme.block_size)+" letters or numbers\n")
    if key is '' or len(str(key))!= scheme.block_size:
        if int(sch) == 0:
            print("\nNot a valid key length, defaulting to \'Sixteen \'\n")
            key='Sixteen '
        else:
            print("\nNot a valid key length, defaulting to \'Sixteen byte key\'\n")
            key='Sixteen byte key'
    im = EncryptedImage(scheme,int(mode_),key,im_src_in)
    print("\nEncrypting image\n")
    cv2.imwrite(str(["DES","DES3","AES"][int(sch)])+"_"+str(["ECB","CBC","CFB"][int(mode_)])+"_enc.jpeg",im.enc())
    print("\nEncryption done\n")
    print("\nDecrypting image\n")
    cv2.imwrite("dec.jpeg",im.dec())
    print("\nDecryption done\n")
