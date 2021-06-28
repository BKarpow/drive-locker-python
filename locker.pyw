import ctypes
import hashlib
import win32com.client
import sys

from pathlib import Path
from os.path import join, isfile
from loguru import logger
from time import sleep
from winregistry import WinRegistry as Reg

logger.add('DriveLocker.log')


reg = Reg()
FILE_KEY = 'DriveLocker.key'
ACC_CONTENT = 'c8524dbce0b244b02915bbe38a87586e'
TIMEOUT_LOOP = 1
AUTIRUN = True
REGISTRY_AUTIRUN = r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
REGISTRY_VALUE_KEY_NAME = 'key_lock'
REGISTRY_KEY = r'DriveLocker'
REGISTRY_SOFTWARE = r'HKLM\SOFTWARE'
AUTORUN_NAME = 'DriveLockerPy'
ENCODING = 'utf8'


def get_md5(string):
    return hashlib.md5(bytes(string, ENCODING)).hexdigest()


def check_reg_key():
    return True if REGISTRY_KEY in reg.read_key(REGISTRY_SOFTWARE)['keys'] else False


def get_registry_key_path():
    return REGISTRY_SOFTWARE + '\\' + REGISTRY_KEY


def create_reg_key():
    reg.create_key(get_registry_key_path())


def create_reg_value(value_string):
    reg.write_value(get_registry_key_path(), REGISTRY_VALUE_KEY_NAME, value_string, 'REG_SZ')


def get_reg_value_key():
    try:
       return reg.read_value(get_registry_key_path(), REGISTRY_VALUE_KEY_NAME)['data']
    except KeyError:
        return False



def get_path_windows():
    p = Path(__file__).resolve()
    logger.debug('File path: ' + str(p))
    return str(p)


def create_autorun():
    if AUTIRUN:
        reg.write_value(REGISTRY_AUTIRUN, AUTORUN_NAME, get_path_windows(), 'REG_SZ')
        logger.debug(f'Create autorun {AUTORUN_NAME} reg value in {REGISTRY_AUTIRUN}')


def check_autorun_windows():
    res = reg.read_key(REGISTRY_AUTIRUN)
    if type(res.get('values')) is list:
        for val in res['values']:
            if val['value'] == AUTORUN_NAME:
                logger.debug(f'Key "{AUTORUN_NAME}" autorun exists')
                return True
        else:
            logger.debug('Ключ автозагрузки не найден')
    else:
        logger.debug('не удалось получить список автозагрузок виндовс')
    return False


def block():
    # logger.info('Block desctop!')
    ctypes.windll.user32.LockWorkStation()


def get_obj_items():
    try:
        strComputer = sys.argv[1]
    except IndexError:
        strComputer = "."
    objWMIService = win32com.client.Dispatch( "WbemScripting.SWbemLocator" )
    objSWbemServices = objWMIService.ConnectServer( strComputer, "root/CIMV2" )
    return objSWbemServices.ExecQuery( "SELECT * FROM Win32_LogicalDisk" )


def get_drive_list():
    driversUSB = []
    for dr in get_obj_items():
        try:
            if dr.DriveType == 2:
                driversUSB.append(dr.Caption)
            else:
                continue
        except:
            return driversUSB
    return driversUSB


def scan_usbDrive_from_key():
    # logger.debug('Start scan devices usb')
    for dr in get_obj_items():
        try:
            if dr.DriveType == 2:
                fileKeyPath = join(dr.Caption, '\\', FILE_KEY)
                # logger.debug('File key path: ' + str(fileKeyPath))
                if isfile(fileKeyPath):
                    # logger.debug('File key exists!!')
                    return fileKeyPath
                else:
                    logger.debug('Non search key file in ' + str(dr.Caption))
            else:
                continue
        except:
            return False




def locker():
    k = scan_usbDrive_from_key()
    access_key = get_reg_value_key()
    if not access_key:
        logger.error("Please create usb key using utilit createKeyFromDrive!!!!")
        return False
    if k:
        with open(k ,'r') as fk:
            if fk.read() != access_key:
                block()
    else:
        block()


def autorun_handle():
    if not check_autorun_windows():
        create_autorun()


def loop():
    logger.info('Start Drive locker!')
    while True:
        sleep(TIMEOUT_LOOP)
        locker()


if __name__ == '__main__':
    autorun_handle()

    loop()
    
    