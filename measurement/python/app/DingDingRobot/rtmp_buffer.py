import cv2
import threading
import time

class rtmp_buffer(threading.Thread):
    def __init__(self, rtmp_str,buffersize):
        super(rtmp_buffer, self).__init__()
        self.rtmp_str = rtmp_str
        self.cap = cv2.VideoCapture(self.rtmp_str)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.size = (self.width, self.height)
        self.buffer=[]
        self.lock=False
        self.sp=1
        self.bufferSize=buffersize

    def run(self):
        ret, image = self.cap.read()
        self.buffer.append(image)
        while ret:
            ret, image = self.cap.read()
            self.sp = (self.sp + 1 + self.bufferSize) % self.bufferSize
            if self.lock:
                self.buffer[self.sp]=image
            else:
                self.buffer.append(image)
                if self.sp==0:
                    self.lock=True

    def read(self):
        while self.lock==False:
            time.sleep(1)
        print(self.sp,len(self.buffer))
        return self.buffer[self.sp]