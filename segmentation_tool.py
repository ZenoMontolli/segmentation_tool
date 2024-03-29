#!/usr/bin/env python
# coding: utf-8

# # Tool for segment images pyxelwise

# This tool can be used to create training set of image segment and is used on the Intcatch project to create a training set, for pixelwise water detection
#

# In[1]:


#!/usr/bin/env python
from tkinter import *
import tkinter as tk
from PIL import Image, ImageEnhance
from PIL import ImageTk
from tkinter import filedialog
import cv2
from skimage.segmentation import felzenszwalb, slic, quickshift
from skimage.segmentation import mark_boundaries
from skimage.segmentation import find_boundaries
from scipy.misc import toimage
import numpy as np
import glob
import matplotlib.pyplot as plt

import os


# In[10]:


class SegmentationGUI(Frame):

    def __init__(self,master):

        self.root=master
        #the name of the window
        self.root.title("Segmentation Tool")
        self.panelA = None
        #vector of all images in the same folder
        self.images = None
        #index of the image opened
        self.index_image=None
        #image opened
        self.image=None
        #path to the image
        self.path=None
        #image original before segmentation
        self.image_original=None
        self.image_original_2x=None
        self.image_original_3x=None
        self.image_original_4x=None
        self.height_original=None
        self.width_original=None
        self.mask=None


        #trace the actual zoom of the image
        self.zoomCycle = 0
        self.segment_type_choice=None
        self.mask_type_choice=None
        self.segments=None
        self.slider1=None
        self.slider2=None
        self.slider3=None

        self.panel_height = None
        self.panel_width = None

        self.intro_window()
        #self.main_window()

    def intro_window(self):

        self.panel0 = Canvas(self.root, width=500, height=400, background="lightblue")

        self.T = Text(self.root, height=10, width=50)
        self.T.insert(END, "SEGMENTATION TOOL \n \n" +
                           "This is a tool used to label to a pixelwise level an image\n\n" +
                           "main comands: \n \n" +
                           "1- Drag and drop right mouse to select areas \n" +
                           "2- mouse wheel to zoom the image \n" +
                           "3- left click to drag the image in the window \n" +
                           "\n \n First step select a resolution in this window in the commands below \n and press continue")

        self.panel0.grid(row=1,column=1,columnspan=4,rowspan=5)
        self.T.grid(row=1,column=1,columnspan=4,sticky='WE')

        self.panel_width=IntVar()
        self.panel_width.set(800)
        RadioButtonChoiceTheWidthResolution1=Radiobutton(self.root, text="width -> 800", padx = 20, variable=self.panel_width, value=800)
        RadioButtonChoiceTheWidthResolution2=Radiobutton(self.root, text="width -> 1200", padx = 20, variable=self.panel_width, value=1200)
        RadioButtonChoiceTheWidthResolution3=Radiobutton(self.root, text="width -> 1900", padx = 20, variable=self.panel_width, value=1900)

        RadioButtonChoiceTheWidthResolution1.grid(row=2,column=1,columnspan=1,sticky='WE')
        RadioButtonChoiceTheWidthResolution2.grid(row=3,column=1,columnspan=1,sticky='WE')
        RadioButtonChoiceTheWidthResolution3.grid(row=4,column=1,columnspan=1,sticky='WE')


        self.panel_height=IntVar()
        self.panel_height.set(450)
        RadioButtonChoiceTheHeightResolution1=Radiobutton(self.root, text="height -> 450", padx = 20, variable=self.panel_height, value=450)
        RadioButtonChoiceTheHeightResolution2=Radiobutton(self.root, text="height -> 600", padx = 20, variable=self.panel_height, value=600)
        RadioButtonChoiceTheHeightResolution3=Radiobutton(self.root, text="height -> 700", padx = 20, variable=self.panel_height, value=700)
        RadioButtonChoiceTheHeightResolution4=Radiobutton(self.root, text="height -> 900", padx = 20, variable=self.panel_height, value=900)

        RadioButtonChoiceTheHeightResolution1.grid(row=2,column=2,columnspan=1,sticky='WE')
        RadioButtonChoiceTheHeightResolution2.grid(row=3,column=2,columnspan=1,sticky='WE')
        RadioButtonChoiceTheHeightResolution3.grid(row=4,column=2,columnspan=1,sticky='WE')
        RadioButtonChoiceTheHeightResolution4.grid(row=5,column=2,columnspan=1,sticky='WE')

        btnContinue = Button(self.root, text="Continue", command=self.main_window)
        btnContinue.grid(row=3,column=3,columnspan=1)


    def main_window(self):
        # create a button, then when pressed, will trigger a file chooser
        # dialog and allow the user to select an input image; then add the
        # button the GUI
        btnSelectImage = Button(self.root, text="Select an image", command=self.open_image)
        btnReset = Button(self.root, text="Reset", command=self.reset_image)
        btnOpenMask = Button(self.root, text="Open a Mask", command=self.open_mask)
        #Next image button
        btnNext = Button(self.root, text='Next', command=self.Next)
        #Previous image button
        btnPrevious = Button(self.root, text='Previous', command=self.Previous)
        #Zoom + button
        btnZoomP = Button(self.root, text='Zoom +', command=self.zoomerPiuBtn)
        #Zoom - button
        btnZoomM = Button(self.root, text='Zoom -', command=self.zoomerMenoBtn)




        self.panelA = Canvas(self.root, width=self.panel_width.get(), height=self.panel_height.get(), background="bisque")
        self.segment_type_choice=IntVar()
        self.segment_type_choice.set(1)
        RadioButton1=Radiobutton(self.root, text="SLIC", padx = 20, variable=self.segment_type_choice, value=1,command=self.radioBtn_refresh)
        RadioButton2=Radiobutton(self.root, text="felzenszwalb", padx = 20, variable=self.segment_type_choice, value=2,command=self.radioBtn_refresh)
        RadioButton3=Radiobutton(self.root, text="quickshift(slow)", padx = 20, variable=self.segment_type_choice, value=3,command=self.radioBtn_refresh)
        self.mask_type_choice=IntVar()
        self.mask_type_choice.set(1)
        RadioButtonChoiceTheMask1=Radiobutton(self.root, text="Water", padx = 20, variable=self.mask_type_choice, value=1)
        RadioButtonChoiceTheMask2=Radiobutton(self.root, text="sky", padx = 20, variable=self.mask_type_choice, value=2)
        RadioButtonChoiceTheMask3=Radiobutton(self.root, text="Undo", padx = 20, variable=self.mask_type_choice, value=3)
        RadioButtonChoiceTheMask4=Radiobutton(self.root, text="nature", padx = 20, variable=self.mask_type_choice, value=4)
        RadioButtonChoiceTheMask5=Radiobutton(self.root, text="obstacle in the water", padx = 20, variable=self.mask_type_choice, value=5)

        btnShow = Button(self.root, text='Show', command=self.slider_refresh)
        self.slider1 = Scale(self.root, from_=0, to=5000, orient=HORIZONTAL)
        self.slider2 = Scale(self.root, from_=0, to=100, orient=HORIZONTAL)
        self.slider3 = Scale(self.root, from_=0, to=30, orient=HORIZONTAL, resolution =   0.5)
        self.slider1.set(150)
        self.slider2.set(20)
        self.slider3.set(1)
        # Save Mask Button
        btnSave = Button(self.root, text='Save Mask', command=self.save_mask)
        # Adjust the Mask
        btnAdjust = Button(self.root, text='Adjust the Mask', command=self.adjust_mask)
        self.text = Text(self.root,width=100, height=1)


        #set the position of the widget in the window
        btnSelectImage.grid(row=0,column=0,columnspan=2)
        btnReset.grid(row=0,column=2,columnspan=2)
        btnOpenMask.grid(row=0,column=4,columnspan=2)
        self.panelA.grid(row=1,column=1,columnspan=4,rowspan=4)
        self.text.grid(row=5,column=1,columnspan=3,sticky='WE')
        btnZoomP.grid(row=2,column=5)
        btnZoomM.grid(row=3,column=5)
        RadioButtonChoiceTheMask1.grid(row=1,column=6)
        RadioButtonChoiceTheMask2.grid(row=2,column=6)
        RadioButtonChoiceTheMask3.grid(row=3,column=6)
        RadioButtonChoiceTheMask4.grid(row=4,column=6)
        RadioButtonChoiceTheMask5.grid(row=5,column=6)
        btnNext.grid(row=2,column=0)
        btnPrevious.grid(row=3,column=0)
        RadioButton1.grid(row=6,column=1)
        RadioButton2.grid(row=6,column=2)
        RadioButton3.grid(row=6,column=3)
        self.slider1.grid(row=7,column=1,columnspan=3,sticky='WE')
        self.slider2.grid(row=8,column=1,columnspan=3,sticky='WE')
        self.slider3.grid(row=9,column=1,columnspan=3,sticky='WE')
        btnShow.grid(row=8,column=4)
        btnAdjust.grid(row=10,column=2,columnspan=2)
        btnSave.grid(row=11,column=2,columnspan=2)

        #set the keybord and mouse events
        self.panelA.bind("<Button-1>", self.select_segment)
        self.panelA.bind("<B1-Motion>", self.select_segment)
        # This is what enables using the mouse for move the image in the window
        self.panelA.bind("<ButtonPress-3>",self.move_start)
        self.panelA.bind("<B3-Motion>",self.move_move)
        #linux scroll zoom
        self.panelA.bind("<Button-4>", self.zoomerPiu)
        self.panelA.bind("<Button-5>", self.zoomerMeno)
        #windows scroll zoom
        self.panelA.bind("<MouseWheel>", self.zoomer)



    def adjust_mask(self):
        if(self.path!=None):
            self.t = Toplevel()
            self.t.wm_title("adjust the mask")
            self.mask=cv2.resize(self.mask,(self.width_original, self.height_original), interpolation = cv2.INTER_CUBIC)
            self.image=self.image_original
            height,width=self.image.shape[:2]
            self.panelB = Canvas(self.t, width=self.panel_width.get(), height=self.panel_height.get(), background="bisque")
            imageOUT = cv2.bitwise_or(self.image,self.mask)
            #imageOUT = cv2.addWeighted(self.image,0.6,self.mask,0.3,0)
            #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
            imageOUT=toimage(imageOUT)
            imageOUT = ImageTk.PhotoImage(imageOUT)
            self.panelB.create_image(0, 0, image = imageOUT, anchor = NW)
            self.panelB.image = imageOUT
            RadioButtonChoiceTheMask1=Radiobutton(self.t, text="Water", padx = 20, variable=self.mask_type_choice, value=1)
            RadioButtonChoiceTheMask2=Radiobutton(self.t, text="sky", padx = 20, variable=self.mask_type_choice, value=2)
            RadioButtonChoiceTheMask3=Radiobutton(self.t, text="Undo", padx = 20, variable=self.mask_type_choice, value=3)
            RadioButtonChoiceTheMask4=Radiobutton(self.t, text="nature", padx = 20, variable=self.mask_type_choice, value=4)
            RadioButtonChoiceTheMask5=Radiobutton(self.t, text="obstacles in the water", padx = 20, variable=self.mask_type_choice, value=5)
            self.pen_size=IntVar()
            self.pen_size.set(3)
            RadioButtonPenSize1=Radiobutton(self.t, text="small", padx = 20, variable=self.pen_size, value=1)
            RadioButtonPenSize2=Radiobutton(self.t, text="normal", padx = 20, variable=self.pen_size, value=2)
            RadioButtonPenSize3=Radiobutton(self.t, text="big", padx = 20, variable=self.pen_size, value=3)
            btnCloseAdjustMask = Button(self.t, text='Confirm Modification', command=self.close_adjust_mask)



            self.panelB.grid(row=0,column=0,columnspan=3)
            RadioButtonChoiceTheMask1.grid(row=1,column=0)
            RadioButtonChoiceTheMask2.grid(row=1,column=1)
            RadioButtonChoiceTheMask3.grid(row=1,column=2)
            RadioButtonChoiceTheMask4.grid(row=1,column=3)
            RadioButtonChoiceTheMask5.grid(row=1,column=4)
            RadioButtonPenSize1.grid(row=2,column=0)
            RadioButtonPenSize2.grid(row=2,column=1)
            RadioButtonPenSize3.grid(row=2,column=2)
            btnCloseAdjustMask.grid(row=3,column=1)

            #set the keybord and mouse events
            self.panelB.bind("<B1-Motion>", self.draw)
            self.panelB.bind("<ButtonPress-3>",self.move_start_adjust_mask)
            self.panelB.bind("<B3-Motion>",self.move_move_adjust_mask)

            #linux scroll zoom
            self.panelB.bind("<Button-4>", self.zoomerPiuB)
            self.panelB.bind("<Button-5>", self.zoomerMenoB)
            #windows scroll zoom
            self.panelB.bind("<MouseWheel>", self.zoomerB)


    def move_start_adjust_mask(self,event):
        self.panelB.scan_mark(event.x, event.y)

    def move_move_adjust_mask(self,event):
        self.panelB.scan_dragto(event.x, event.y, gain=1)


    def draw(self,event):
        x=int(self.panelB.canvasx(event.x))#event.x
        y=int(self.panelB.canvasy(event.y))#event.y
        if(self.mask_type_choice.get() == 1): color = np.float64([100,100,255])
        if(self.mask_type_choice.get() == 2): color = np.float64([100,255,100])
        if(self.mask_type_choice.get() == 3): color = np.float64([0,0,0])
        if(self.mask_type_choice.get() == 4): color = np.float64([0,255,0])
        if(self.mask_type_choice.get() == 5): color = np.float64([255,0,0])
        height,width=self.image.shape[:2]
        if(self.pen_size.get()==1):
            if(x>=5): x1=x-5
            else: x1=0
            if(y>=5): y1=y-5
            else: y1=0
            if(x<=width-5): x2=x+5
            else: x2=width
            if(y<=height-5): y2=y+5
            else: y2=height
        if(self.pen_size.get()==2):
            if(x>=15): x1=x-15
            else: x1=0
            if(y>=15): y1=y-15
            else: y1=0
            if(x<=width-15): x2=x+15
            else: x2=width
            if(y<=height-15): y2=y+15
            else: y2=height
        if(self.pen_size.get()==3):
            if(x>=25): x1=x-25
            else: x1=0
            if(y>=25): y1=y-25
            else: y1=0
            if(x<=width-25): x2=x+25
            else: x2=width
            if(y<=height-25): y2=y+25
            else: y2=height
        if(self.pen_size.get()==4):
            if(x>=35): x1=x-35
            else: x1=0
            if(y>=35): y1=y-35
            else: y1=0
            if(x<=width-35): x2=x+35
            else: x2=width
            if(y<=height-35): y2=y+35
            else: y2=height
        if(self.pen_size.get()==5):
            if(x>=50): x1=x-50
            else: x1=0
            if(y>=50): y1=y-50
            else: y1=0
            if(x<=width-50): x2=x+50
            else: x2=width
            if(y<=height-50): y2=y+50
            else: y2=height

        self.mask[y1:y2,x1:x2]=color

        imageOUT = cv2.bitwise_or(self.image,self.mask)
        #imageOUT = cv2.addWeighted(self.image,0.3,self.mask,0.7,0)
        #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
        imageOUT = toimage(imageOUT)
        imageOUT = ImageTk.PhotoImage(imageOUT)

        self.panelB.create_image(0, 0, image = imageOUT, anchor = NW)
        self.panelB.image = imageOUT




    def close_adjust_mask(self):
        self.t.destroy()
        self.mask=cv2.resize(self.mask,(self.width_original, self.height_original), interpolation = cv2.INTER_CUBIC)
        self.image=self.image_original

        imageOUT = cv2.bitwise_or(self.image,self.mask)
        #imageOUT = cv2.addWeighted(self.image,0.3,self.mask,0.7,0)
        #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
        imageOUT = toimage(imageOUT)
        imageOUT = ImageTk.PhotoImage(imageOUT)

        self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
        self.panelA.image = imageOUT

    def open_mask(self):
        if(self.path!=None):
            path=self.path_to_image()
            mask = cv2.imread(path)
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)
            self.mask=mask

            imageOUT = cv2.bitwise_or(self.image,self.mask)
            #imageOUT = cv2.addWeighted(self.image,0.3,self.mask,0.7,0)
            #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
            imageOUT = toimage(imageOUT)
            imageOUT = ImageTk.PhotoImage(imageOUT)

            self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
            self.panelA.image = imageOUT

    def open_image(self):
        path=self.path_to_image()
        self.path=path
        # ensure a file path was selected
        if len(path) > 0:
            #get the self.root of the path
            pathroot=path[:path.rfind('/')] + '/*'+path[path.rfind('.'):]
            #open all the images in the path
            self.images = glob.glob(pathroot)
            #find the index of the image selected for trace the previous and next images
            self.index_image=self.find_index_selected(self.images,path)
            image = cv2.imread(path)
            image = self.increase_contrast_image(image)
            #convert to RGB from BGR
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.height_original,self.width_original=image.shape[:2]
            self.image_original=image
            self.image_original_2x = cv2.resize(image,(self.width_original*2, self.height_original*2), interpolation = cv2.INTER_CUBIC)
            self.image_original_3x = cv2.resize(image,(self.width_original*3, self.height_original*3), interpolation = cv2.INTER_CUBIC)
            self.image_original_4x = cv2.resize(image,(self.width_original*4, self.height_original*4), interpolation = cv2.INTER_CUBIC)
            #init the mask for the image
            self.mask = np.zeros(self.image_original.shape[:3], dtype = "uint8")
            self.image=image
            # convert the images to PIL format...
            image=toimage(image)
            # ...and then to ImageTk format
            imageOUT = ImageTk.PhotoImage(image)
            self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
            self.panelA.image = imageOUT
            self.text.delete(1.0,END)
            self.text.insert(INSERT,self.path)

    def reset_image(self):
        if(self.path!=None):
            path=self.path
            if len(path) > 0:
                #get the self.root of the path
                pathroot=path[:path.rfind('/')] + '/*'+path[path.rfind('.'):]
                #open all the images in the path
                self.images = glob.glob(pathroot)
                #find the index of the image selected for trace the previous and next images
                self.index_image=self.find_index_selected(self.images,path)
                image = cv2.imread(path)
                image = self.increase_contrast_image(image)
                #convert to RGB from BGR
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.height_original,self.width_original=image.shape[:2]
                self.image_original=image
                self.image_original_2x = cv2.resize(image,(self.width_original*2, self.height_original*2), interpolation = cv2.INTER_CUBIC)
                self.image_original_3x = cv2.resize(image,(self.width_original*3, self.height_original*3), interpolation = cv2.INTER_CUBIC)
                self.image_original_4x = cv2.resize(image,(self.width_original*4, self.height_original*4), interpolation = cv2.INTER_CUBIC)
                #init the mask for the image
                self.mask = np.zeros(self.image_original.shape[:3], dtype = "uint8")
                self.image=image
                # convert the images to PIL format...
                image=toimage(image)
                # ...and then to ImageTk format
                imageOUT = ImageTk.PhotoImage(image)
                self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
                self.panelA.image = imageOUT
                self.text.delete(1.0,END)
                self.text.insert(INSERT,self.path)

    #increase the contrast of the image
    def increase_contrast_image(self,image):
        lab= cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        image_high_contrast = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        return image_high_contrast

    #dialog window to choose the path to images
    def path_to_image(self):
        path = filedialog.askopenfilename()
        return path

    #find the index of the actual image selected
    def find_index_selected(self,images,path):
        i=0
        for pathImage in self.images:
            if(path==pathImage):
                indexSelected=i
            i=i+1
        return indexSelected

    def select_segment(self,event):
        if(self.path!=None):
            #true_x = panelA.canvasx(event.x)
            #true_y = panelA.canvasy(event.y)
            x=int(self.panelA.canvasx(event.x))#event.x
            y=int(self.panelA.canvasy(event.y))#event.y
            height,width=self.image.shape[:2]
            if(x>0 and x<width and y>0 and y<height):
                #print(x,"-",y,"-",true_x,"-",true_y)
                clicked_segment = self.segments[y,x]
                if(self.mask_type_choice.get() == 1): color = np.float64([100,100,255])
                if(self.mask_type_choice.get() == 2): color = np.float64([255,0,255])
                if(self.mask_type_choice.get() == 3): color = np.float64([0,0,0])
                if(self.mask_type_choice.get() == 4): color = np.float64([0,255,0])
                if(self.mask_type_choice.get() == 5): color = np.float64([255,0,0])
                self.mask[self.segments == clicked_segment] = color
                #image2=np.copy(self.image)
                #for x in range (self.width_original):
                #    for y in range (self.height_original):
                #        tmp=self.mask.item(x,y)
                #        if(np.array_equal(tmp, (0,0,0))==False):
                #            image2[y,x]=self.mask[y,x]
                #imageOUT = cv2.bitwise_or(self.image,self.mask)
                #idx = (self.mask==color)
                #image2[idx] = self.mask[idx]
                #image2=np.copy(self.image)

                imageOUT = cv2.bitwise_or(self.image,self.mask)
                #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
                #imageOUT = cv2.addWeighted(self.image,0.3,self.mask,0.7,0)
                imageOUT = toimage(mark_boundaries(imageOUT, self.segments))
                imageOUT = ImageTk.PhotoImage(imageOUT)

                self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
                self.panelA.image = imageOUT



    def slider_pack(self):
        if(self.segment_type_choice.get()==1):
            self.slider1.configure(from_=0, to=5000)
            self.slider2.configure(from_=0, to=100)
            self.slider3.configure(from_=0, to=30)
            self.slider1.set(150)
            self.slider2.set(20)
            self.slider3.set(1)

        if(self.segment_type_choice.get()==2):
            self.slider1.configure(from_=0, to=1000)
            self.slider2.configure(from_=1, to=400)
            self.slider3.configure(from_=0, to=1, resolution=0.05)
            self.slider1.set(100)
            self.slider2.set(50)
            self.slider3.set(0.95)

        if(self.segment_type_choice.get()==3):
            self.slider1.configure(from_=3, to=31)
            self.slider2.configure(from_=1, to=400)
            self.slider3.configure(from_=0, to=1, resolution=0.05)
            self.slider1.set(3)
            self.slider2.set(6)
            self.slider3.set(0.5)

    def radioBtn_refresh(self):
        self.slider_pack()
        if(self.segment_type_choice.get()==1):
            numSeg=self.slider1.get()
            comp= self.slider2.get()
            sigma=float(self.slider3.get())
            self.segments = slic(self.image, n_segments=numSeg, compactness=comp, sigma=sigma,slic_zero=True)

        if(self.segment_type_choice.get()==2):
            scale=self.slider1.get()
            min_size=self.slider2.get()
            sigma=self.slider3.get()
            self.segments = felzenszwalb(self.image, scale=scale, sigma=sigma, min_size=min_size)

        if(self.segment_type_choice.get()==3):
            kernel_size=self.slider1.get()
            max_dist= self.slider2.get()
            ratio=self.slider3.get()
            self.segments = quickshift(self.image, kernel_size=3, max_dist=6, ratio=0.5)

        imageOUT = cv2.bitwise_or(self.image,self.mask)
        #imageOUT = cv2.addWeighted(self.image,0.3,self.mask,0.7,0)
        #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
        imageOUT = toimage(mark_boundaries(imageOUT, self.segments))
        imageOUT = ImageTk.PhotoImage(imageOUT)

        self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
        self.panelA.image = imageOUT


    def slider_refresh(self):
        if(self.segment_type_choice.get()==1):
            numSeg=self.slider1.get()
            comp= self.slider2.get()
            sigma=self.slider3.get()
            self.segments = slic(self.image, n_segments=numSeg, compactness=comp, sigma=sigma,slic_zero=True)

        if(self.segment_type_choice.get()==2):
            scale=self.slider1.get()
            min_size= self.slider2.get()
            sigma=self.slider3.get()
            self.segments = felzenszwalb(self.image, scale=scale, sigma=sigma, min_size=min_size)

        if(self.segment_type_choice.get()==3):
            kernel_size=self.slider1.get()
            max_dist= self.slider2.get()
            ratio=self.slider3.get()
            self.segments = quickshift(self.image, kernel_size=3, max_dist=6, ratio=0.5)

        imageOUT = np.where(self.mask==(0,0,0),self.image,self.mask)
        imageOUT = toimage(mark_boundaries(imageOUT, self.segments))
        imageOUT = ImageTk.PhotoImage(imageOUT)

        self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
        self.panelA.image = imageOUT

    def Next(self):
        if(self.path!=None):
            if(self.index_image<len(self.images)-1):
                self.index_image=self.index_image+1
                self.path=self.images[self.index_image]
                image = cv2.imread(self.path)
                image = self.increase_contrast_image(image)
                #convert to RGB from BGR
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.height_original,self.width_original=image.shape[:2]
                self.image_original=image
                self.image_original_2x = cv2.resize(image,(self.width_original*2, self.height_original*2), interpolation = cv2.INTER_CUBIC)
                self.image_original_3x = cv2.resize(image,(self.width_original*3, self.height_original*3), interpolation = cv2.INTER_CUBIC)
                self.image_original_4x = cv2.resize(image,(self.width_original*4, self.height_original*4), interpolation = cv2.INTER_CUBIC)
                #init the mask for the image
                self.mask = np.zeros(self.image_original.shape[:3], dtype = "uint8")
                self.image=image
                # convert the images to PIL format...
                image=toimage(image)
                # ...and then to ImageTk format
                imageOUT = ImageTk.PhotoImage(image)
                self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
                self.panelA.image = imageOUT
                self.text.delete(1.0,END)
                self.text.insert(INSERT,self.path)



    def Previous(self):
        if(self.path!=None):
            if(self.index_image>=0):
                self.index_image=self.index_image-1
                self.path=self.images[self.index_image]
                image = cv2.imread(self.path)
                image = self.increase_contrast_image(image)
                #convert to RGB from BGR
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.height_original,self.width_original=image.shape[:2]
                self.image_original=image
                self.image_original_2x = cv2.resize(image,(self.width_original*2, self.height_original*2), interpolation = cv2.INTER_CUBIC)
                self.image_original_3x = cv2.resize(image,(self.width_original*3, self.height_original*3), interpolation = cv2.INTER_CUBIC)
                self.image_original_4x = cv2.resize(image,(self.width_original*4, self.height_original*4), interpolation = cv2.INTER_CUBIC)
                #init the mask for the image
                self.mask = np.zeros(self.image_original.shape[:3], dtype = "uint8")
                self.image=image
                # convert the images to PIL format...
                image=toimage(image)
                # ...and then to ImageTk format
                imageOUT = ImageTk.PhotoImage(image)
                self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
                self.panelA.image = imageOUT
                self.text.delete(1.0,END)
                self.text.insert(INSERT,self.path)


    #move the image in the window
    def move_start(self,event):
        self.panelA.scan_mark(event.x, event.y)

    def move_move(self,event):
        self.panelA.scan_dragto(event.x, event.y, gain=1)

    #windows zoom
    def zoomer(self,event):
        if (event.delta > 0):
                if self.zoomCycle != 4: self.zoomCycle += 1
        elif (event.delta < 0):
                if self.zoomCycle != 0: self.zoomCycle -= 1
        self.zoom()
    #linux zoom
    def zoomerPiu(self,event):
        if self.zoomCycle != 4: self.zoomCycle += 1
        self.zoom()

    def zoomerMeno(self,event):
        if self.zoomCycle != 0: self.zoomCycle -= 1
        self.zoom()


    #windows zoom
    def zoomerB(self,event):
        if (event.delta > 0):
                if self.zoomCycle != 4: self.zoomCycle += 1
        elif (event.delta < 0):
                if self.zoomCycle != 0: self.zoomCycle -= 1
        self.zoomB()
    #linux zoom
    def zoomerPiuB(self,event):
        if self.zoomCycle != 4: self.zoomCycle += 1
        self.zoomB()

    def zoomerMenoB(self,event):
        if self.zoomCycle != 0: self.zoomCycle -= 1
        self.zoomB()

    #zoom with button
    def zoomerPiuBtn(self):
        if self.zoomCycle != 4: self.zoomCycle += 1
        self.zoom()

    def zoomerMenoBtn(self):
        if self.zoomCycle != 0: self.zoomCycle -= 1
        self.zoom()


    def zoom(self):
        if(self.path!=None):

            if (self.zoomCycle) != 0:
                if self.zoomCycle == 1:
                    self.mask=cv2.resize(self.mask,(self.width_original, self.height_original), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original

                elif self.zoomCycle == 2:
                    self.mask=cv2.resize(self.mask,(self.width_original*2, self.height_original*2), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original_2x

                elif self.zoomCycle == 3:
                    self.mask=cv2.resize(self.mask,(self.width_original*3, self.height_original*3), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original_3x

                elif self.zoomCycle == 4:
                    self.mask=cv2.resize(self.mask,(self.width_original*4, self.height_original*4), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original_4x

                imageOUT = cv2.bitwise_or(self.image,self.mask)
                #imageOUT = cv2.addWeighted(self.image,0.3,self.mask,0.7,0)
                #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
                imageOUT=toimage(imageOUT)
                imageOUT = ImageTk.PhotoImage(imageOUT)

                self.panelA.create_image(0, 0, image = imageOUT, anchor = NW)
                self.panelA.image = imageOUT

    def zoomB(self):
        if(self.path!=None):

            if (self.zoomCycle) != 0:
                if self.zoomCycle == 1:
                    self.mask=cv2.resize(self.mask,(self.width_original, self.height_original), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original

                elif self.zoomCycle == 2:
                    self.mask=cv2.resize(self.mask,(self.width_original*2, self.height_original*2), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original_2x

                elif self.zoomCycle == 3:
                    self.mask=cv2.resize(self.mask,(self.width_original*3, self.height_original*3), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original_3x

                elif self.zoomCycle == 4:
                    self.mask=cv2.resize(self.mask,(self.width_original*4, self.height_original*4), interpolation = cv2.INTER_CUBIC)
                    self.image=self.image_original_4x

                imageOUT = cv2.bitwise_or(self.image,self.mask)
                #imageOUT = cv2.addWeighted(self.image,0.3,self.mask,0.7,0)
                #imageOUT=np.where(self.mask==(0,0,0),self.image,self.mask)
                imageOUT=toimage(imageOUT)
                imageOUT = ImageTk.PhotoImage(imageOUT)

                self.panelB.create_image(0, 0, image = imageOUT, anchor = NW)
                self.panelB.image = imageOUT

    def save_mask(self):
        if(self.path!=None):
            mask=cv2.resize(self.mask,(self.width_original, self.height_original), interpolation = cv2.INTER_CUBIC)
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)
            mask2saveWater=mask

            #mask2saveWater = np.zeros(self.image_original.shape[:2], dtype = "uint8")
            #mask2saveOther = np.zeros(self.image_original.shape[:3], dtype = "uint8")
            #for x in range (self.width_original):
            #    for y in range (self.height_original):
            #        tmp=mask[y,x]
            #        if(np.array_equal(tmp, (100,100,255))):
            #            mask2saveWater[y,x] = 1
                    #elif(mask [x,y] == (255,255,255)):
                        #mask2saveOther[x,y] = (255,255,255)

            Fname=(self.path[self.path.rfind('/')+1 : self.path.rfind('.')] + '-annotation.png')

            f =  filedialog.asksaveasfile(mode='wb',initialfile=Fname, defaultextension=".png", filetypes=(("PNG file", "*.png"),("All Files", "*.*")))

            if f:
                abs_path = os.path.abspath(f.name)
                cv2.imwrite(abs_path,mask2saveWater)
                #maskOUT=toimage(mask2saveWater)
                #maskOUT.save(abs_path)


#The master of the GUI
root=Tk()

#call the class for the SegmentationGUI
app=SegmentationGUI(root)
#start the GUI loop
root.mainloop()



# In[ ]:





# In[ ]:
