# [注] 需要保存文件的示例程序在部分环境下需以管理员权限执行，否则会有异常
# [PS] Sample programs that need to save files need to be executed with administrator privileges \
#      in some environments, otherwise there will be exceptions
     

import sys
import threading
import msvcrt
import numpy as np
import inspect
import csv
import codecs
import cv2
import os
from datetime import datetime
import subprocess
import serial
import time
import requests
from ultralytics import YOLO
import yolov9.detect_dual as detect


from ctypes import *

sys.path.append("../MvImport")
from MVFGControl_class import *
from PyQt5.QtWidgets import *
from PyUIBasicDemo import Ui_Form

ser = serial.Serial()
ser.port = 'COM5'
ser.baudrate = 38400
ser.open()

hThreadHandle = None
nFrameNum = 0                          #存图id
Buf_Lock = threading.Lock()            #取图和存图的锁
stImageInfo = MV_FG_INPUT_IMAGE_INFO()
Save_Image_Buf = None
Save_Image_Buf_Size = c_uint(0)

TIMEOUT         = 1000
nInterfaceNum   = c_uint(0)
IsOpenIF        = False
IsOpenDevice    = False
IsStartGrabbing = False
nTriggerMode    = c_uint(0)
TRIGGER_MODE_ON = c_uint(1)
TRIGGER_MODE_OFF = c_uint(0)

TRIGGER_SOURCE_LINE0 = c_uint(0)                     # ch:Line0 | en:Line0
TRIGGER_SOURCE_LINE1 = c_uint(1)                     # ch:Line1 | en:Line1
TRIGGER_SOURCE_LINE2 = c_uint(2)                     # ch:Line2 | en:Line2
TRIGGER_SOURCE_LINE3 = c_uint(3)                     # ch:Line3 | en:Line3
TRIGGER_SOURCE_COUNTER0 = c_uint(4)                  # ch:Conuter0 | en:Conuter0
TRIGGER_SOURCE_SOFTWARE = c_uint(7)                  # ch:软触发 | en:Software
TRIGGER_SOURCE_FrequencyConverter = c_uint(8)        # ch:变频器 | en:Frequency Converter

Delay_Shutter = 0

a = 0
b = 0
round = 0
changecolor = 0
banana = 11
capFrame = 0

def calculate_checksum(data):
        return '{:02X}'.format(sum(data.encode('ascii')) % 256)
def check_database():
    url = 'http://localhost:4000/readsendweight'
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None
    return response

def save_frame_on_rgb():
    global a
    global b
    global round
    global changecolor
    global banana
    global name_setting
    global name_banana
    global capFrame
    response = check_database()
    if response.status_code == 200:
        capFrame +=1
        if a == 0:
            a = 1
            b = 0
            print(a)
            data = response.json() 
            print(data)
            uuid = data.get('uuid', 'N/A')
            weight = data.get('weight', 'N/A')
            state = data.get('state', 'N/A')
            print(weight)
            ui.label_uuid.setText(f"UUID: {uuid}")
            ui.label_weight.setText(f"WEIGHT: {weight}")
            ui.label_state.setText(f"STATE: {state}")
                    
            ser.write(b'@FFL100A9\r\n')
        if 7 <= capFrame <= 21:
            SaveJpeg()            
    else:
        capFrame = 0
        if b == 0:
                b = 1
                ui.label_uuid.setText(f"UUID: None")
                ui.label_weight.setText(f"WEIGHT: None")
                ui.label_state.setText(f"STATE: None")
                    
                ser.write(b'@FFL000A8\r\n')

                r_value = [str(val).zfill(3) for val in [0,255,0,0,255,255,0,0,255]]
                g_value = [str(val).zfill(3) for val in [0,0,255,0,255,0,255,0,255]]
                b_value = [str(val).zfill(3) for val in [0,0,0,255,255,0,0,255,255]]
                name_setting = ['NO','RO','GO','BO','WO','RC','GC','BC','WC']
                name_banana = ['banana01','banana02','banana03','banana04','banana05','banana06','banana07','banana08','banana09','banana10','banana11']
                if round == banana:
                    round = 1
                    changecolor += 1
                    if changecolor == 9:
                        changecolor = 0

                    print('arraycolor',changecolor)
                    checksum_r = calculate_checksum(f'@00F{r_value[changecolor]}00')
                    checksum_g = calculate_checksum(f'@01F{g_value[changecolor]}00')
                    checksum_b = calculate_checksum(f'@02F{b_value[changecolor]}00')

                else :
                    round += 1
                    checksum_r = calculate_checksum(f'@00F{r_value[changecolor]}00')
                    checksum_g = calculate_checksum(f'@01F{g_value[changecolor]}00')
                    checksum_b = calculate_checksum(f'@02F{b_value[changecolor]}00')


                time.sleep(0.1)
                ser.write(f'@00F{r_value[changecolor]}00{checksum_r}\r\n'.encode())
                time.sleep(0.1)
                ser.write(f'@01F{g_value[changecolor]}00{checksum_g}\r\n'.encode())
                time.sleep(0.1)
                ser.write(f'@02F{b_value[changecolor]}00{checksum_b}\r\n'.encode())
                print(f'@00F{r_value[changecolor]}00{checksum_r}\r\n'.encode())
                print(f'@01F{g_value[changecolor]}00{checksum_g}\r\n'.encode())
                print(f'@02F{b_value[changecolor]}00{checksum_b}\r\n'.encode())

                a = 0
                print('round',round)
                print(f"Finish")



def OpenServerGetData1():
    script_path = r'F:\proend\server\train.js'
    try:
        subprocess.run(['start', 'cmd', '/k', 'node', script_path],shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Node.js script: {e}")
    except FileNotFoundError:
        print("Node.js executable not found. Please provide the correct path.")

def OpenServerGetData2():
    script_path = r'F:\proend\server\index.js'
    try:
        subprocess.run(['start', 'cmd', '/k', 'node', script_path],shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Node.js script: {e}")
    except FileNotFoundError:
        print("Node.js executable not found. Please provide the correct path.")

# 将返回的错误码转换为十六进制显示
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr

# 强制关闭线程
def Async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

# 停止线程
def Stop_thread(thread):
    Async_raise(thread.ident, SystemExit)

def EnableControls(IsCameraReady):
    ui.BtnEnumInterface.setEnabled(not IsOpenIF)
    ui.BtnOpenInterface.setEnabled(not IsOpenIF and nInterfaceNum.value > 0)
    ui.BtnCloseInterface.setEnabled(IsOpenIF and not IsOpenDevice)
    ui.ComboInterface.setEnabled(not IsOpenIF and nInterfaceNum.value > 0)

    ui.BtnEnumDevice.setEnabled(not IsOpenDevice and IsOpenIF)
    ui.BtnOpenDevice.setEnabled(not IsOpenDevice and IsCameraReady)
    ui.BtnCloseDevice.setEnabled(IsOpenDevice and IsCameraReady)
    ui.ComboDevice.setEnabled(not IsOpenDevice and IsCameraReady)

    ui.BtnStart.setEnabled(not IsStartGrabbing and IsOpenDevice and IsCameraReady)
    ui.BtnStop.setEnabled(IsStartGrabbing)

    ui.RadioContinuousMode.setEnabled(IsOpenDevice)
    ui.RadioTriggerMode.setEnabled(IsOpenDevice)
    ui.CheckTriggerbySoftware.setEnabled(IsOpenDevice)
    ui.BtnTriggerOnce.setEnabled(IsStartGrabbing and ui.CheckTriggerbySoftware.isChecked() and ui.RadioTriggerMode.isChecked())


def GrabbingThread(Stream=0, winHandle=0):
    global hThreadHandle
    global Save_Image_Buf
    global Save_Image_Buf_Size
    stFrameInfo = MV_FG_BUFFER_INFO()
    stDisplayInfo = MV_FG_DISPLAY_FRAME_INFO()
    memset(byref(stFrameInfo), 0, sizeof(stFrameInfo))
    ret = MV_FG_SUCCESS

    nFrame_text = ui.lineEdit_nFrame.text()
    try:
        nFrame = int(nFrame_text)
    except ValueError:
        print("Invalid input for nFrame. Please enter a valid integer.")
        return
    countFrame = 0
    while True:
        countFrame = countFrame+1
        #ui.BtnGetData3.setEnabled(False)
        #ui.BtnGetData4.setEnabled(False)
        ret = Stream.GetFrameBuffer(stFrameInfo, TIMEOUT)
        if MV_FG_SUCCESS != ret:
            if nTriggerMode is TRIGGER_MODE_OFF:
                strError = "Get Frame Buffer Failed! ret:" + ToHexStr(ret)
                print(strError)
            continue
        else:
            Buf_Lock.acquire()
            memset(byref(stImageInfo), 0, sizeof(stImageInfo))
            if Save_Image_Buf is None or stFrameInfo.nFilledSize > Save_Image_Buf_Size:
                if Save_Image_Buf is not None:
                    del Save_Image_Buf
                    Save_Image_Buf = None
                Save_Image_Buf = (c_ubyte * stFrameInfo.nFilledSize)()
                Save_Image_Buf_Size = stFrameInfo.nFilledSize
            memset(byref(Save_Image_Buf), 0, Save_Image_Buf_Size)
            cdll.msvcrt.memcpy(byref(Save_Image_Buf), cast(stFrameInfo.pBuffer, POINTER(c_ubyte * stFrameInfo.nFilledSize)),
                               stFrameInfo.nFilledSize)
            stImageInfo.nWidth = stFrameInfo.nWidth
            stImageInfo.nHeight = stFrameInfo.nHeight
            stImageInfo.enPixelType = stFrameInfo.enPixelType
            stImageInfo.pImageBuf = cast(stFrameInfo.pBuffer, POINTER(c_ubyte))
            stImageInfo.nImageBufLen = stFrameInfo.nFilledSize
            global nFrameNum
            nFrameNum = stFrameInfo.nFrameID
            Buf_Lock.release()


            memset(byref(stDisplayInfo), 0, sizeof(stDisplayInfo))
            stDisplayInfo.nWidth = stFrameInfo.nWidth
            stDisplayInfo.nHeight = stFrameInfo.nHeight
            stDisplayInfo.enPixelType = stFrameInfo.enPixelType
            stDisplayInfo.pImageBuf = cast(stFrameInfo.pBuffer, POINTER(c_ubyte))
            stDisplayInfo.nImageBufLen = stFrameInfo.nFilledSize
            ret = ImgProc.DisplayOneFrame(winHandle, stDisplayInfo)
            if countFrame == nFrame :
                save_frame_on_rgb()
                countFrame = 0

            ret = Stream.ReleaseFrameBuffer(stFrameInfo)
            if MV_FG_SUCCESS != ret:
                strError = "Release Frame Buffer Failed! ret:" + ToHexStr(ret)
                QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
                break

        if not IsStartGrabbing:
            break

    return ret

# ch:枚举采集卡 | en:Enum interface
def EnumInterface():
    bChanged = c_bool(False)
    ret = FGSystem.UpdateInterfaceList(MV_FG_CXP_INTERFACE | MV_FG_GEV_INTERFACE | MV_FG_CAMERALINK_INTERFACE | MV_FG_XoF_INTERFACE, bChanged)
    if MV_FG_SUCCESS != ret:
        strError = "Enum Interfaces Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    ret = FGSystem.GetNumInterfaces(nInterfaceNum)
    if MV_FG_SUCCESS != ret:
        strError = "Get Num Interfaces Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    if 0 == nInterfaceNum.value:
        strError = "No Interface!"
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    if True == bChanged.value:
        ui.ComboInterface.clear()
        for i in range(0, nInterfaceNum.value):
            stInterfaceInfo = MV_FG_INTERFACE_INFO()
            memset(byref(stInterfaceInfo), 0, sizeof(stInterfaceInfo))
            ret = FGSystem.GetInterfaceInfo(i, stInterfaceInfo)
            if MV_FG_SUCCESS != ret:
                strError = "Get Interface Info Failed! ret:" + ToHexStr(ret)
                QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
                return

            if MV_FG_CAMERALINK_INTERFACE == stInterfaceInfo.nTLayerType:
                chDisplayName = ""
                for per in stInterfaceInfo.IfaceInfo.stCMLIfaceInfo.chDisplayName:
                    chDisplayName = chDisplayName + chr(per)
                chInterfaceID = ""
                for per in stInterfaceInfo.IfaceInfo.stCMLIfaceInfo.chInterfaceID:
                    chInterfaceID = chInterfaceID + chr(per)
                chSerialNumber = ""
                for per in stInterfaceInfo.IfaceInfo.stCMLIfaceInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strIFInfo = "CML[" + str(i) + "]" + chDisplayName + "|" + chInterfaceID + "|" + chSerialNumber
                
            ui.ComboInterface.addItem(strIFInfo)

    if nInterfaceNum.value > 0:
        ui.ComboInterface.setCurrentIndex(0)

    EnableControls(False)


# ch:打开采集卡 | en:Open Interface
def OpenInterface():
    global IsOpenIF
    nInterfaceIndex = ui.ComboInterface.currentIndex()
    if nInterfaceIndex < 0 or nInterfaceIndex >= ui.ComboInterface.count():
        strError = "Please select valid index!"
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    ret = Iface.OpenInterface(nInterfaceIndex)
    if MV_FG_SUCCESS != ret:
        strError = "Open Interface Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    IsOpenIF = True
    EnableControls(False)

# ch；关闭采集卡 | en:Close interface
def CloseInterface():
    global IsOpenIF
    if True == IsOpenDevice:
        CloseDevice()
    ret = Iface.CloseInterface()
    if MV_FG_SUCCESS != ret:
        strError = "Close Interface Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    IsOpenIF = False

    EnableControls(False)

# ch:枚举设备 | en:Enum device
def EnumDevice():
    bChanged   = c_bool(False)
    nDeviceNum = c_uint(0)

    ret = Iface.UpdateDeviceList(bChanged)
    if MV_FG_SUCCESS != ret:
        strError = "Enum Devices Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    ret = Iface.GetNumDevices(nDeviceNum)
    if MV_FG_SUCCESS != ret:
        strError = "Get Num Devices Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    if 0 == nDeviceNum.value:
        strError = "No Device!"
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    if True == bChanged.value:
        ui.ComboDevice.clear()
        for i in range(0, nDeviceNum.value  ):
            stDeviceInfo = MV_FG_DEVICE_INFO()
            memset(byref(stDeviceInfo), 0, sizeof(stDeviceInfo))
            ret = Iface.GetDeviceInfo(i, stDeviceInfo)
            if MV_FG_SUCCESS != ret:
                strError = "Get Device Info Failed! ret:" + ToHexStr(ret)
                QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
                return

            if MV_FG_CAMERALINK_DEVICE == stDeviceInfo.nDevType:
                chUserDefinedName = ""
                for per in stDeviceInfo.DevInfo.stCMLDevInfo.chUserDefinedName:
                    chUserDefinedName = chUserDefinedName + chr(per)
                chModelName = ""
                for per in stDeviceInfo.DevInfo.stCMLDevInfo.chModelName:
                    chModelName = chModelName + chr(per)
                chSerialNumber = ""
                for per in stDeviceInfo.DevInfo.stCMLDevInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strDevInfo = "CML[" + str(i) + "]" + chUserDefinedName + "|" + chModelName + "|" + chSerialNumber

            ui.ComboDevice.addItem(strDevInfo)

    if nDeviceNum.value > 0:
        ui.ComboDevice.setCurrentIndex(0)

    EnableControls(True)

# ch:打开设备 | en:Open device
def OpenDevice():
    global IsOpenDevice
    ui.BtnGetData1.setEnabled(True)
    ui.BtnGetData2.setEnabled(True)
    ui.lineEdit_nFrame.setEnabled(True)
    ui.lineEdit_amountBanana.setEnabled(True)

    if True == IsOpenDevice:
        return
    nIndex = ui.ComboDevice.currentIndex()
    if nIndex < 0 or nIndex >= ui.ComboDevice.count():
        strError = "Please select valid index!"
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    ret = Dev.OpenDevice(Iface, nIndex)
    if MV_FG_SUCCESS != ret:
        strError = "Open Device Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    IsOpenDevice = True
    global DevGeneral
    DevGeneral = FGGeneral(Dev)
    ret = GetTriggerMode()
    if MV_FG_SUCCESS != ret:
        strError = "Get Trigger Mode Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    ret = GetTriggerSource()
    if MV_FG_SUCCESS != ret:
        strError = "Get Trigger Source Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    EnableControls(True)

# ch:关闭设备 | en:Close device
def CloseDevice():
    global IsOpenDevice
    ui.BtnGetData1.setEnabled(False)
    ui.BtnGetData2.setEnabled(False)
    ui.lineEdit_nFrame.setEnabled(False)
    ui.lineEdit_amountBanana.setEnabled(False)

    if True == IsStartGrabbing:
        StopGrabbing()
    if True == IsOpenDevice:
        ret = Dev.CloseDevice()
        if MV_FG_SUCCESS != ret:
            strError = "Close Device Failed! ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    IsOpenDevice = False

    EnableControls(True)




# ch:获取触发模式 | en:Get trigger mode
def GetTriggerMode():
    stEnumValue = MV_FG_ENUMVALUE()
    memset(byref(stEnumValue), 0, sizeof(stEnumValue))
    ret = DevGeneral.GetEnumValue("TriggerMode", stEnumValue)
    if MV_FG_SUCCESS != ret:
        return ret
    global nTriggerMode
    nTriggerMode = stEnumValue.nCurValue
    if TRIGGER_MODE_ON == nTriggerMode:
        StartTriggerMode()
    else:
        StartContinuousMode()

    return MV_FG_SUCCESS

# ch:获取触发源 | en:Get trigger source
def GetTriggerSource():
    stEnumValue = MV_FG_ENUMVALUE()
    memset(byref(stEnumValue), 0, sizeof(stEnumValue))
    ret = DevGeneral.GetEnumValue("TriggerSource", stEnumValue)
    if MV_FG_SUCCESS == ret:
        return ret
    if TRIGGER_SOURCE_SOFTWARE != stEnumValue.nCurValue:
       ui.CheckTriggerbySoftware.setChecked(True)
    else:
       ui.CheckTriggerbySoftware.setChecked(False)
    return ret

# ch:设置触发模式 | en:Set trigger mode
def SetTriggerMode(nTriggerMode = 0):
    return DevGeneral.SetEnumValue("TriggerMode", nTriggerMode)

# ch:设置触发源 | en:Set trigger source
def SetTriggerSource():
    if True == ui.CheckTriggerbySoftware.isChecked():
        ret = DevGeneral.SetEnumValue("TriggerSource", TRIGGER_SOURCE_SOFTWARE)
        if MV_FG_SUCCESS != ret:
            strError = "Set Software Trigger Failed! ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            return
    else:
        ret = DevGeneral.SetEnumValue("TriggerSource", TRIGGER_SOURCE_LINE0)
        if MV_FG_SUCCESS != ret:
            strError = "Set Hardware Trigger Failed! ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
            return


# ch:开启连续模式 | en:Start continuous mode
def StartContinuousMode():
    ui.RadioTriggerMode.setChecked(False)
    ui.RadioContinuousMode.setChecked(True)
    global nTriggerMode
    nTriggerMode = TRIGGER_MODE_OFF
    ret = SetTriggerMode(nTriggerMode)
    if MV_FG_SUCCESS != ret:
        strError = "Set Continuous Mode Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return


# ch:开启触发模式 | en:Start trigger mode
def StartTriggerMode():
    ui.RadioTriggerMode.setChecked(True)
    ui.RadioContinuousMode.setChecked(False)
    global nTriggerMode
    nTriggerMode = TRIGGER_MODE_ON
    ret = SetTriggerMode(nTriggerMode)
    if MV_FG_SUCCESS != ret:
        strError = "Set Trigger Mode Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        ui.RadioTriggerMode.setAutoExclusive(False)
        ui.RadioTriggerMode.setChecked(False)
        return

# ch:软触发 | en:Software trigger
def SoftwareTrigger():
    if True != IsStartGrabbing:
        return
    ret = DevGeneral.SetCommandValue("TriggerSoftware")
    if MV_FG_SUCCESS != ret:
        strError = "Software Trigger Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)

    EnableControls(True)


# ch:开始采集 | en:Start grabbing
def StartGrabbing():
    global IsStartGrabbing
    global hThreadHandle
    global a
    global b
    global round
    global changecolor
    global banana
    if False == IsOpenDevice or True == IsStartGrabbing:
        return

    nStreamNum = c_uint(0)
    ret = Dev.GetNumStreams(nStreamNum)
    if MV_FG_SUCCESS != ret:
        strError = "Get Num Streams Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    ret = Stream.OpenStream(Dev, c_uint(0))
    if MV_FG_SUCCESS != ret:
        strError = "Open Stream Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    global ImgProc
    ImgProc = FGImageProcess(Stream)
    nBufferNum = c_uint(3)
    ret = Stream.SetBufferNum(nBufferNum)
    if MV_FG_SUCCESS != ret:
        strError = "Set Buffer Num Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    ret = Stream.StartAcquisition()
    if MV_FG_SUCCESS != ret:
        strError = "Start Acquisition Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    IsStartGrabbing = True
    try:
        hThreadHandle = threading.Thread(target=GrabbingThread, args=(Stream, int(ui.label_3.winId())))
        hThreadHandle.start()
    except:
        strError = "Start Thread Failed!"
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    EnableControls(True)        
    if not round == 0 : 
        round = 0
        changecolor = 0
        b = 0
        save_frame_on_rgb()
        ui.banana = int(ui.lineEdit_amountBanana.text())
        print('test',ui.lineEdit_nFrame.text(),ui.banana)

# ch:停止采集 | en:Stop grabbing
def StopGrabbing():
    global IsStartGrabbing
    global hThreadHandle
    if False == IsOpenDevice or False == IsStartGrabbing:
        return
    IsStartGrabbing = False
    #hThreadHandle.join()
    Stop_thread(hThreadHandle)

    ret = Stream.StopAcquisition()
    if MV_FG_SUCCESS != ret:
        strError = "Stop Acquisition Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    ret = Stream.CloseStream()
    if MV_FG_SUCCESS != ret:
        strError = "Close Stream Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return

    EnableControls(True)

# ch:保存JPEG图像 | en:Save JPEG
def SaveJpeg():
    global file_path
    global stImageInfo
    if 0 == Save_Image_Buf:
        return

    Buf_Lock.acquire()
    for i in range(1):
        current_dateTime = datetime.now()
        year = current_dateTime.year
        month = current_dateTime.month
        day = current_dateTime.day
        hour = current_dateTime.hour
        min = current_dateTime.minute
        sec = current_dateTime.second
        microsec = current_dateTime.microsecond // 10000
        response = check_database()
        if response.status_code == 200:
            setnamebanana = name_banana[round-1]
            setnamesetting = name_setting[changecolor]
        else :
            setnamesetting = 'None'
            setnamebanana = 'None'
        file_path = 'F:\\proend\\Python\\BasicDemo\\img\\test\\' + str(year) + "-" + str(month)  + "-" + str(day) +" " + str(hour) + ";" + str(min)  + ";" + str(sec)  + ";" + str(microsec) + ' ' + str(setnamebanana) +  " " + str(setnamesetting) + " " + str(nFrameNum) + "p.jpg"
        stJpegInfo = MV_FG_SAVE_JPEG_INFO()
        memset(byref(stJpegInfo), 0, sizeof(MV_FG_SAVE_JPEG_INFO))
        JpegBuffer = (c_ubyte * (Save_Image_Buf_Size * 4 + 1028))()
        JpegBufferSize = Save_Image_Buf_Size * 4 + 1028

        stJpegInfo.stInputImageInfo = stImageInfo
        stJpegInfo.pJpgBuf = JpegBuffer
        stJpegInfo.nJpgBufSize = JpegBufferSize
        stJpegInfo.nJpgQuality = 100                              # JPG编码质量(0 - 100]
        stJpegInfo.enCfaMethod = MV_FG_CFA_METHOD_OPTIMAL
        
        ret = ImgProc.SaveJpeg(stJpegInfo)
        if MV_FG_SUCCESS != ret:
            break
        file = open(file_path.encode('ascii'), 'wb+')
        file.write(JpegBuffer)
        file.close()
        threading.Thread(target=ocv, args=(file_path)).start()

    Buf_Lock.release()

    if MV_FG_SUCCESS != ret:
        strError = "Save Jpeg Failed! ret:" + ToHexStr(ret)
        QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return
    
def ocv(file_path):
    global capFrame
    print(capFrame)
    detect.run(weights='F:/proend/Python/BasicDemo/train/te/exp21/weights/last.pt', 
           source=file_path,
           save_crop=True,
           save_conf=True,
           save_txt=True,
           device='cpu')
    
if __name__ == '__main__':
    Iface = FGInterface()
    Dev = FGDevice()
    Stream = FGStream()

    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    mainWindow.setFixedSize(787, 632)
    ui = Ui_Form()
    ui.setupUi(mainWindow)
    EnableControls(False)
    ui.BtnEnumInterface.clicked.connect(EnumInterface)
    ui.BtnOpenInterface.clicked.connect(OpenInterface)
    ui.BtnCloseInterface.clicked.connect(CloseInterface)
    ui.BtnEnumDevice.clicked.connect(EnumDevice)
    ui.BtnOpenDevice.clicked.connect(OpenDevice)
    ui.BtnCloseDevice.clicked.connect(CloseDevice)
    ui.RadioContinuousMode.clicked.connect(StartContinuousMode)
    ui.RadioTriggerMode.clicked.connect(StartTriggerMode)
    ui.CheckTriggerbySoftware.clicked.connect(SetTriggerSource)
    ui.BtnTriggerOnce.clicked.connect(SoftwareTrigger)
    ui.BtnStart.clicked.connect(StartGrabbing)
    ui.BtnStop.clicked.connect(StopGrabbing)
    ui.BtnGetData1.clicked.connect(OpenServerGetData1)
    ui.BtnGetData2.clicked.connect(OpenServerGetData2)

    mainWindow.show()
    app.exec_()

    if True == IsOpenDevice:
        CloseDevice()
    if True == IsOpenIF:
        CloseInterface()

    sys.exit()


