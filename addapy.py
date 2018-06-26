import libaddapy

def drdy_is_low():
    libaddapy.gpio_lev(libaddapy.DRDY)
    return

def ads1256_wait_drdy():
    drdy_is_low()
    return

def ads1256_readreg(_regid):
    cs_0()
    ads1256_send8bit(libaddapy.CMD_RREG | _regid)
    ads1256_send8bit(0x00)

    # ads1256_delaydata()

    read = ads1256_recive8bit()
    cs_1()

    return read

def ads1256_readchipid():
    ads1256_wait_drdy()
    id = ads1256_readreg(libaddapy.REG_STATUS)
    return id >> 4

def cs_0():
    libaddapy.gpio_write(libaddapy.SPICS, libaddapy.LOW)

def cs_1():
    libaddapy.gpio_write(libaddapy.SPICS, libaddapy.HIGH)

def ads1256_send8bit(_data):
    # bsp_delayus(2)
    libaddapy.spi_transfer(_data)

def bsp_delayus(micros):
    libaddapy.delayMicroseconds(micros)

def ads1256_delaydata():
    bsp_delayus(10)

def ads1256_recive8bit():
    read = libaddapy.spi_transfer(0xff)
    return read
    
