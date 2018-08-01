import sys
from tensorflow.python.client import device_lib


def get_available_gpus():
    local_device_protos = device_lib.list_local_devices()
    return [x.name for x in local_device_protos]


def main():
    print(get_available_gpus())

if __name__ == "__main__":
    print(get_available_gpus())
    sys.exit(int(main() or 0))



