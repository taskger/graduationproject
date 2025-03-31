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

            if MV_FG_CXP_INTERFACE == stInterfaceInfo.nTLayerType:
                chDisplayName = ""
                for per in stInterfaceInfo.IfaceInfo.stCXPIfaceInfo.chDisplayName:
                    chDisplayName = chDisplayName + chr(per)
                chInterfaceID = ""
                for per in stInterfaceInfo.IfaceInfo.stCXPIfaceInfo.chInterfaceID:
                    chInterfaceID = chInterfaceID + chr(per)
                chSerialNumber = ""
                for per in stInterfaceInfo.IfaceInfo.stCXPIfaceInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strIFInfo = "CXP[" + str(i) + "]" + chDisplayName + "|" + chInterfaceID + "|" + chSerialNumber

            elif MV_FG_GEV_INTERFACE == stInterfaceInfo.nTLayerType:
                chDisplayName = ""
                for per in stInterfaceInfo.IfaceInfo.stGEVIfaceInfo.chDisplayName:
                    chDisplayName = chDisplayName + chr(per)
                chInterfaceID = ""
                for per in stInterfaceInfo.IfaceInfo.stGEVIfaceInfo.chInterfaceID:
                    chInterfaceID = chInterfaceID + chr(per)
                chSerialNumber = ""
                for per in stInterfaceInfo.IfaceInfo.stGEVIfaceInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strIFInfo = "GEV[" + str(i) + "]" + chDisplayName + "|" + chInterfaceID + "|" + chSerialNumber

            elif MV_FG_CAMERALINK_INTERFACE == stInterfaceInfo.nTLayerType:
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
                
            elif MV_FG_XoF_INTERFACE == stInterfaceInfo.nTLayerType:
                chDisplayName = ""
                for per in stInterfaceInfo.IfaceInfo.stXoFIfaceInfo.chDisplayName:
                    chDisplayName = chDisplayName + chr(per)
                chInterfaceID = ""
                for per in stInterfaceInfo.IfaceInfo.stXoFIfaceInfo.chInterfaceID:
                    chInterfaceID = chInterfaceID + chr(per)
                chSerialNumber = ""
                for per in stInterfaceInfo.IfaceInfo.stXoFIfaceInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strIFInfo = "XoF[" + str(i) + "]" + chDisplayName + "|" + chInterfaceID + "|" + chSerialNumber

            ui.ComboInterface.addItem(strIFInfo)

    if nInterfaceNum.value > 0:
        ui.ComboInterface.setCurrentIndex(0)

    EnabelControls(False)


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
    EnabelControls(False)

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

    EnabelControls(False)

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

            if MV_FG_CXP_DEVICE == stDeviceInfo.nDevType:
                chUserDefinedName = ""
                for per in stDeviceInfo.DevInfo.stCXPDevInfo.chUserDefinedName:
                    chUserDefinedName = chUserDefinedName + chr(per)
                chModelName = ""
                for per in stDeviceInfo.DevInfo.stCXPDevInfo.chModelName:
                    chModelName = chModelName + chr(per)
                chSerialNumber = ""
                for per in stDeviceInfo.DevInfo.stCXPDevInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strDevInfo = "CXP[" + str(i) + "]" + chUserDefinedName + "|" + chModelName + "|" + chSerialNumber

            elif MV_FG_GEV_DEVICE == stDeviceInfo.nDevType:
                chUserDefinedName = ""
                for per in stDeviceInfo.DevInfo.stGEVDevInfo.chUserDefinedName:
                    chUserDefinedName = chUserDefinedName + chr(per)
                chModelName = ""
                for per in stDeviceInfo.DevInfo.stGEVDevInfo.chModelName:
                    chModelName = chModelName + chr(per)
                chSerialNumber = ""
                for per in stDeviceInfo.DevInfo.stGEVDevInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strDevInfo = "GEV[" + str(i) + "]" + chUserDefinedName + "|" + chModelName + "|" + chSerialNumber

            elif MV_FG_CAMERALINK_DEVICE == stDeviceInfo.nDevType:
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
                
            elif MV_FG_XoF_DEVICE == stDeviceInfo.nDevType:
                chUserDefinedName = ""
                for per in stDeviceInfo.DevInfo.stXoFDevInfo.chUserDefinedName:
                    chUserDefinedName = chUserDefinedName + chr(per)
                chModelName = ""
                for per in stDeviceInfo.DevInfo.stXoFDevInfo.chModelName:
                    chModelName = chModelName + chr(per)
                chSerialNumber = ""
                for per in stDeviceInfo.DevInfo.stXoFDevInfo.chSerialNumber:
                    chSerialNumber = chSerialNumber + chr(per)
                strDevInfo = "XoF[" + str(i) + "]" + chUserDefinedName + "|" + chModelName + "|" + chSerialNumber

            ui.ComboDevice.addItem(strDevInfo)

    if nDeviceNum.value > 0:
        ui.ComboDevice.setCurrentIndex(0)

    EnabelControls(True)

# ch:打开设备 | en:Open device
def OpenDevice():
    global IsOpenDevice
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

    EnabelControls(True)

# ch:关闭设备 | en:Close device
def CloseDevice():
    global IsOpenDevice
    if True == IsStartGrabbing:
        StopGrabbing()
    if True == IsOpenDevice:
        ret = Dev.CloseDevice()
        if MV_FG_SUCCESS != ret:
            strError = "Close Device Failed! ret:" + ToHexStr(ret)
            QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    IsOpenDevice = False

    EnabelControls(True)