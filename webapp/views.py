from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import  StreamingHttpResponse
import cv2
import os
import re
import pandas as pd
import nltk
import numpy as np
import face_recognition
from datetime import datetime
from webapp.models import attendance



casecade=r'haarcascade_frontalface_default.xml'
print(casecade)
face_encods=[]
names=[]
# Create your views here.
attendance_count=[]
attendance_time=[]


def home(request):
    return  render(request,'index.html')

def cam(request):
    return render(request, "camera.html")


class videocamera():
    def __init__(self):
        self.cap=cv2.VideoCapture(0)
    def __del__(self):
        self.cap.release()
    def for_capture(self):
        _,scenes=self.cap.read()
        return scenes
    def get_frame(self):
        _,img=self.cap.read()
        #cv2.putText(img, 'new_txt', (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        ret,jpeg=cv2.imencode('.jpg',img)##convert image into streaming data
        return jpeg.tobytes()##string willbe converted into bytes



def capture(request):
    obj=videocamera()
    frm=obj.for_capture()
    nme=request.GET['name']
    path=r'facesmaindir/'+nme

    haar=cv2.CascadeClassifier(casecade)
    faces=haar.detectMultiScale(frm)
    if len(faces) !=0:
        os.makedirs(r'facesmaindir/' + nme)

        cv2.imwrite(path+'/'+nme+'.jpg',frm)

        txt='success'
    else:
        txt="no face found"
    return render(request,'camera.html',{'text':txt,'name':nme})

    
def gen(camera):
    while True:
        frame=camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')##yield can return somethong from the function without destroying it


def video_feed(request):
    return StreamingHttpResponse(gen(videocamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')





class videocamerav2():
    def __init__(self):
        self.cap=cv2.VideoCapture(0)
        self.forattendance()


    def __del__(self):
        self.cap.release()


    def forattendance(self):
        print("uploading to the names is working")
        path = r'facesmaindir'
        nme = os.listdir(r'facesmaindir')#/praveen kumar/praveen kumar.jpg


        for i in range(len(nme)):
            names.append(nme[i])
            image_path = path + '/' + nme[i] + '/' + nme[i] + '.jpg'
            img = cv2.imread(image_path)

            try:
                encs=face_recognition.face_encodings(img)[0]
                face_encods.append(encs)
            except:
                print("image is not clear")



    def get_frame(self):
        txt="fetching"
        _,img=self.cap.read()
        #
        haar = cv2.CascadeClassifier(casecade)
        faces = haar.detectMultiScale(img)
        li = []
        if len(faces) != 0:
            enc=face_recognition.face_encodings(img)


            if len(enc)!=0:
                count=0
                for i in face_encods:
                    count=count+1

                    li.append(face_recognition.compare_faces(i,enc))
                li=nltk.flatten(li)
                if True in li:
                    ind=li.index(True)
                    txt=names[ind]

                    if txt not in attendance_count:
                        attendance_count.append(txt)
                        now = datetime.now()
                        tim=now.strftime("%H:%M")
                        attendance_time.append(tim)
                        value=attendance(name=txt,time=tim)

                        dbname=attendance.objects.filter(name=txt)
                        if len(dbname) ==0:
                            value.save()


                else:
                    txt="unknown"

                if len(li)==len(names):
                    li=[]

            print(attendance_count,attendance_time)

        else:
            txt="noface"

        cv2.putText(img, txt, (0, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        ret,jpeg=cv2.imencode('.jpg',img)##convert image into streaming data
        return jpeg.tobytes()##string willbe converted into bytes


def genv2(camera):
    while True:

        frame=camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')##yield can return somethong from the function without destroying it


def video_feedv2(request):
    return StreamingHttpResponse(gen(videocamerav2()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def attend(request):

    return render(request,'takeattendance.html')


def export(request):
    df=pd.DataFrame()
    value=attendance.objects.all().values()
    names=[]
    time=[]
    for i in value:
        names.append(i['name'])
        time.append(i['time'])

    df['names']=names
    df['time']=time
    now=datetime.now()
    date=str(now.strftime("%D:%M")[:8])
    file=re.sub(r'[^0-9]+'," ",date)+'.csv'
    #
    df.to_csv(r'attendancelist/'+file)

    return HttpResponse("SUCCESSFULLY EXPORTED")


def clear(request):
    attendance.objects.all().delete()
    return HttpResponse("Database clear")
