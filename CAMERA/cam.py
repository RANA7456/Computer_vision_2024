from pypylon import pylon
import cv2 as cv
import random
import numpy as np
import neoapi

class camera_streams:
    capture = None
    mode = None
    IP = None
    path = None

    def __init__(self, mode, IP=None, path=None):
        self.IP = IP
        self.mode = mode
        self.path = path
        if mode == 'Industrial':

            self.capture = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.capture.Open()
            self.capture.ExposureTime.SetValue(50000)
            self.capture.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
            self.converter = pylon.ImageFormatConverter()
            self.converter.OutputPixelFormat = pylon.PixelType_RGB16packed
            self.converter.OutputBitAlignment = pylon.OutputBitAlignment_LsbAligned
            self.bgr_img = self.frame = np.ndarray(shape=(self.capture.Height.Value, self.capture.Width.Value, 3),
                                                   dtype=np.uint8)
            
        
        elif mode == "Baumer_Cam":
            self.capture = neoapi.Cam()
            self.capture.Connect()
            self.capture.f.PixelFormat.SetString('RGB8') # for 3 channel otherwise remove it
            self.capture.f.ExposureTime.Set(50000)

        elif mode == "Gigi_Cam":
            self.capture = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.capture.Open()

            # if trigger is true
            # self.capture.TriggerSelector.SetValue("FrameStart")
            # self.capture.TriggerMode.SetValue("On")
            # self.capture.TriggerSource.SetValue('Line1')
            # self.capture.TriggerActivation.SetValue("RisingEdge")
            # ===================================
            self.capture.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        elif mode == "IP cam":
            self.capture = cv.VideoCapture(self.IP)
            if self.capture.isOpened():
                print("IP Camera Connected.")
            else:
                print("Please check the host address/network connectivity")

        elif mode == "fromfile":
            self.capture = cv.VideoCapture(self.path)
            if self.capture.isOpened():
                print("Video File Ready to Read.")
            else:
                print("Path may be incorrect. Please check again.")

        else:
            for cameraID in range(0, 200):
                print("Looking for open camera device.")
                self.capture = cv.VideoCapture(cameraID)
                if self.capture.isOpened():
                    print("Working camID: ", cameraID)
                    break
                if cameraID == 200:
                    print("No camera ID is found working")

    def get_frame(self, size=None):
        if self.mode == "Industrial":
            grabResult = self.capture.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                image = self.converter.Convert(grabResult)
                frame = np.ndarray(buffer=image.GetBuffer(), shape=(image.GetHeight(), image.GetWidth(), 3),
                                   dtype=np.uint16)
                self.bgr_img[:, :, 0] = frame[:, :, 2]
                self.bgr_img[:, :, 1] = frame[:, :, 1]
                self.bgr_img[:, :, 2] = frame[:, :, 0]
                self.frame = self.bgr_img.copy()
                
            else:
                print("Error in frame grabbing.")
            grabResult.Release()

        elif self.mode == "Baumer_Cam":
            image = self.capture.GetImage()
            if not image.IsEmpty():
                self.frame = image.GetNPArray()
                self.frame = cv.cvtColor(self.frame,cv.COLOR_RGB2BGR) # for 3 channel otherwise remove it
            else:
                print("Error in frame grabbing.")

        elif self.mode == "Gigi_Cam":
            grabResult = self.capture.RetrieveResult(100000, pylon.TimeoutHandling_Return)
            if grabResult.GrabSucceeded():
                image = self.converter.Convert(grabResult)
                self.frame = image.GetArray()
            else:
                print("Error in frame grabbing.")

            grabResult.Release()

        else:
            ret, self.frame = self.capture.read()
            if ret:
                # self.frame = cv.resize(self.frame, size)
                pass
            else:
                print("Error in frame grabbing.")

        if size is not None:
            self.frame = cv.resize(self.frame, size)

        return self.frame

    def __del__(self):
        self.capture.release()

if __name__ == "__main__":

    cap=camera_streams(mode="fjdsjf")
    
    while True:
        frame=cap.get_frame()
        print(frame.shape)

        key=cv.waitKey(1)
        
        cv.namedWindow("Basler",cv.WINDOW_NORMAL)
        cv.imshow('Basler', frame)

        if key==ord("q"):
            break
        
    cv.destroyAllWindows()
        
