
import cv2
import torch
import threading
import time
import os
import shutil
import DingDingRobot as ddr
import rtmp_buffer

image_path=os.path.join(os.getcwd(),"images")
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

class robot(threading.Thread):
    def __init__(self,rtmp_str):
        super(robot, self).__init__()
        self.rtmp_buffer = rtmp_buffer.rtmp_buffer(rtmp_str,50)
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        self.tag = UniTag(200)
        self.rtmp_buffer.start()
        try:
            shutil.rmtree(image_path)
            os.makedirs(image_path)
        except:
            os.makedirs(image_path)

    def run(self):
        print('in producer')
        while True:
            personDetect = False
            image = self.rtmp_buffer.read()
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
                        personDetect=True

            a,d=self.tag.getId()
            if d!="0":
                try:
                    os.remove(os.path.join(image_path,d+".png"))
                except:
                    pass
            if personDetect:
                picPath = os.path.join(image_path, a + ".png")
                cv2.imwrite(picPath, image)
                time.sleep(3)
                ddr.dd.send_msg("有人头在动", ddr.phraseUrl(a))
                print(ddr.phraseUrl(a))
                time.sleep(3)


if __name__ == '__main__':
    print('run program')
    rtmp_str = 'rtmp://10.214.131.230:11935/live/cam0'
    producer = robot(rtmp_str)  # 开个线程
    producer.start()