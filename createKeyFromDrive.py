import locker

from random import choice

SYMVOLS = 'qweasd123zxcrty789fghvb456nmjklu0-iopy'
SYMVOLS += SYMVOLS.upper()
SYMVOLS = list(SYMVOLS)

def generate_key(l = 24):
    p = ''
    for _ in range(l):
        p += choice(SYMVOLS)
    return p

usbDevices = locker.get_drive_list()

def get_key_path(caption_usb):
    return locker.join(caption_usb, '\\', locker.FILE_KEY)


def check_key_exists(usb_path):
    return locker.isfile(get_key_path(usb_path))


def create_key(usb_path, key):
    fileKeyPath = get_key_path(usb_path)
    with open(fileKeyPath, 'w') as fk:
        fk.write(key)


def get_usb_select(drivers):
    i = 1
    for d in drivers:
        print(f'{i}). {d} - Memory Flash Cart')
        i += 1
    try:

        res = int(input('Number drivers? (0 from exit)> '))
        return drivers[res - 1]
    except IndexError:
        print(f'Error no match {res}, please correct select drive/')
        return get_usb_select(drivers)
    except:
        return 0

def show_info():
    print('Create drive key.')
    print('Please sekect usb flash drive from create usbKey')


def main():
    show_info()
    drivers = locker.get_drive_list()
    if len(drivers):
        drive_caption = get_usb_select(drivers)
        if drive_caption == 0: return False
        new_key = generate_key(44)
        if not locker.check_reg_key():
            locker.create_reg_key()
        locker.create_reg_value(new_key)
        create_key(drive_caption, new_key)
        print('Creating usb key - success! Please run locker.')
    else:
        print('Не удалось найти флешки!')


if __name__ == "__main__":
    main()
    input('Press enter to exit...')




