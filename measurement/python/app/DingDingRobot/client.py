import cv2
import torch
import threading
import time
import os
import shutil
import DingDingRobot as ddr
# import win32gui,win32con

image_path=os.path.join(os.getcwd(),"images")
picBufferSize=1
I=10

def Mark(image,box):
    ptLeftTop=(int(box[0]),int(box[1]))
    ptRightBottom=(int(box[2]),int(box[3]))
    point_color = (0, 255, 0)  # BGR
    thickness = 10
    lineType = 4
    cv2.rectangle(image, ptLeftTop, ptRightBottom, point_color, thickness, lineType)
    return image

class UniTag:
    def __init__(self,cap):
        self.mat=[]
        self.sp=0
        self.cap=cap
        for i in range(cap):
            self.mat.append("0")
            self.sp=(self.sp+1+self.cap)%self.cap

    def getId(self):
        ans=str(hash(time.time()))
        d=self.mat[self.sp]
        self.mat[self.sp]=ans
        self.sp=(self.sp+1+self.cap)%self.cap
        return ans,d


class Producer(threading.Thread):
    """docstring for Producer"""
    def __init__(self, rtmp_str):
        super(Producer, self).__init__()
        self.rtmp_str = rtmp_str
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.cap = cv2.VideoCapture(self.rtmp_str)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        # print(self.fps)
        # 获取cap视频流的每帧大小
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.size = (self.width, self.height)
        self.tag=UniTag(200)
        # print(self.size)
        try:
            shutil.rmtree(image_path)
            os.makedirs(image_path)
        except :
            os.makedirs(image_path)

    def run(self):
        print('in producer')
        ret, image = self.cap.read()
        id =0
        while ret:
            personInfo={"confidence":[],"position":[]}
            result = self.model(image)

            for i, (im, pred) in enumerate(zip(result.imgs, result.pred)):
                s = f'image {i + 1}/{len(result.pred)}: {im.shape[0]}x{im.shape[1]} '  # string
                if pred.shape[0]:
                    for c in pred[:, -1].unique():
                        n = (pred[:, -1] == c).sum()  # detections per class
                        s += f"{n} {result.names[int(c)]}{'s' * (n > 1)}, "  # add to string
                else:
                    s += '(no detections)'
                print(s)
                for *box, conf, cls in reversed(pred):
                    if int(cls) == 0:   ## 人的classId为0
                        personInfo["confidence"].append(float(conf))
                        personInfo["position"].append(list(box))
                        image = Mark(image, box)


            a,d=self.tag.getId()
            if d!="0":
                os.remove(os.path.join(image_path,d+".png"))
            picPath = os.path.join(image_path, a+ ".png")
            cv2.imwrite(picPath, image)
            time.sleep(3)



            ddr.dd.send_msg("有人头在动", ddr.phraseUrl(a))
            print(ddr.phraseUrl(a))
            time.sleep(3)
            ret, image = self.cap.read()


if __name__ == '__main__':
    print('run program')
    rtmp_str = 'rtmp://10.214.131.230:11935/live/cam0'
    producer = Producer(rtmp_str)  # 开个线程
    producer.start()