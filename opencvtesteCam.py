import cv2
import numpy as np
import matplotlib.pyplot as plt
import cv2
import customtkinter 
from PIL import Image, ImageTk
from openalpr import Alpr




DARK_MODE = "dark"
customtkinter.set_appearance_mode(DARK_MODE)
customtkinter.set_default_color_theme("dark-blue")

minScoreToSend = 0.30

class App(customtkinter.CTk):

    def initialize_alpr():
        alpr = Alpr("br", "openalpr.conf", "runtime_data")
        alpr.set_top_n(10)
        alpr.set_default_region("br")
        return alpr
    
    alpr = initialize_alpr()
    
    def exibeImagem(self):
        frame = cv2.imread("ixf.jpg")

        xmax = frame.shape[1] 
        ymax = frame.shape[0] 
        print("xmax: "+ str(xmax))
        print("ymax: "+ str(ymax))
        src = np.array([ 
                        [0, 0],  
                        [0, ymax], 
                        [xmax, ymax],  
                        [xmax, 0] 
                    ], dtype='float32') 
        
        dst = np.array( 
                [ 
                    [xmax*float(self.value1.get()), ymax*float(self.value2.get())], 
                    [xmax*float(self.value3.get()), ymax*float(self.value4.get())], 
                    [xmax*float(self.value5.get()), ymax*float(self.value6.get())], 
                    [xmax*float(self.value7.get()), ymax*float(self.value8.get())] 
                ],  
                dtype='float32')

        # Apply Perspective Transform Algorithm
        matrix = cv2.getPerspectiveTransform(src, dst)
        result = cv2.warpPerspective(frame, matrix, (xmax, ymax))
        resized_image = cv2.resize(result, (300, 150))
        imgArray = Image.fromarray(resized_image)
        imgtk = ImageTk.PhotoImage(image=imgArray)
        self.plateImgLabelFrame1.imageTk = imgtk
        self.plateImgLabelFrame1.configure(image=imgtk, text="")
        
        results = App.alpr.recognize_array(result)

        if(license_plate_text_score is None):
            license_plate_text_score = 0

        if(license_plate_text is None):
            license_plate_text = "nothing"
            
        self.plateTxtLabelFrame1.configure(text=license_plate_text+ " - score: " + str(license_plate_text_score))
        
        
    def __init__(self):
        super().__init__()
        # self.state('withdraw')
        self.title("teste Prewarp")

        self.geometry("{0}x{0}+0+0".format(800, 800))
        """
        ixf.jpg
        
        0.03
        0.2
        0
        0.9
        1
        1
        1
        0.3
        """
        self.value1 = customtkinter.StringVar(value="0")
        self.value2 = customtkinter.StringVar(value="0")
        self.value3 = customtkinter.StringVar(value="0")
        self.value4 = customtkinter.StringVar(value="1")
        self.value5 = customtkinter.StringVar(value="1")
        self.value6 = customtkinter.StringVar(value="1")
        self.value7 = customtkinter.StringVar(value="1")
        self.value8 = customtkinter.StringVar(value="0")

        self.text1 = customtkinter.CTkEntry(self, textvariable=self.value1)
        self.text1.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.05)
        
        self.text2 = customtkinter.CTkEntry(self, textvariable=self.value2)
        self.text2.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.1)
        
        self.text3 = customtkinter.CTkEntry(self, textvariable=self.value3)
        self.text3.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.15)
        
        self.text4 = customtkinter.CTkEntry(self, textvariable=self.value4)
        self.text4.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.20)
        
        self.text5 = customtkinter.CTkEntry(self, textvariable=self.value5)
        self.text5.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.25)
        
        self.text6 = customtkinter.CTkEntry(self, textvariable=self.value6)
        self.text6.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.30)
        
        self.text7 = customtkinter.CTkEntry(self, textvariable=self.value7)
        self.text7.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.35)
        
        self.text8 = customtkinter.CTkEntry(self, textvariable=self.value8)
        self.text8.place(relwidth=0.70, relheight=0.05, relx=0.025, rely=0.40)

        self.plateTxtLabelFrame1 = customtkinter.CTkLabel(self, text="AAA0000", font=("Roboto", 12))
        self.plateTxtLabelFrame1.place(relwidth=0.70, relheight=0.1,relx=0.05, rely=0.5)
        
        self.plateImgLabelFrame1 = customtkinter.CTkLabel(self, text="Image Plate")
        self.plateImgLabelFrame1.place(relwidth=0.70, relheight=0.28,relx=0.1, rely=0.68)
        
        self.streamStopBtnFrame2 = customtkinter.CTkButton(self, text="MakeImg", command=self.exibeImagem, state="normal",  fg_color="red")
        self.streamStopBtnFrame2.place(relwidth=0.30, relheight=0.05, relx=0.025, rely=0.95)
        
        ## END
if __name__ == "__main__":
    a = App()
    a.mainloop()