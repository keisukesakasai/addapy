import collections
import libaddapy

ADS1256_VAR_T = collections.namedtuple('ADS1256_VAR_T',
                                       ['ADS1256_GAIN_E',
                                        'ADS1256_DRATE_E',
                                        'AdcNow',
                                        'Channel',
                                        'ScanMode'])

ADS1256_GAIN_E = {'ADS1256_GAIN_1':1,
                  'ADS1256_GAIN_2':2,
                  'ADS1256_GAIN_4':4,
                  'ADS1256_GAIN_8':8,
                  'ADS1256_GAIN_16':16,
                  'ADS1256_GAIN_32':32,
                  'ADS1256_GAIN_64':64}

ADS1256_DRATE_E = {'ADS1256_30000SPS':0,
                   'ADS1256_15000SPS':1,
                   'ADS1256_7500SPS':2,
                   'ADS1256_3750SPS':3,
                   'ADS1256_2000SPS':4,
                   'ADS1256_1000SPS':5,
                   'ADS1256_500SPS':6,
                   'ADS1256_100SPS':7,
                   'ADS1256_60SPS':8,
                   'ADS1256_50SPS':9,
                   'ADS1256_30SPS':10,
                   'ADS1256_25SPS':11,
                   'ADS1256_15SPS':12,
                   'ADS1256_10SPS':13,
                   'ADS1256_5SPS':14,
                   'ADS1256_2d5SPS':15,
                   'ADS1256_DRATE_MAX':16}

def configure():
    libaddapy.init()
    libaddapy.spi_begin()
    libaddapy.spi_setBitOrder(libaddapy.BCM2835_SPI_BIT_ORDER_LSBFIRST)
    libaddapy.spi_setDataMode(libaddapy.BCM2835_SPI_MODE1)
    libaddapy.spi_setClockDivider(libaddapy.BCM2835_SPI_CLOCK_DIVIDER_1024)
    libaddapy.gpio_fsel(libaddapy.SPICS, libaddapy.BCM2835_GPIO_FSEL_OUTP)
    libaddapy.gpio_write(libaddapy.SPICS, libaddapy.HIGH)
    libaddapy.gpio_fsel(libaddapy.DRDY, libaddapy.BCM2835_GPIO_FSEL_INPT)
    libaddapy.gpio_set_pud(libaddapy.DRDY, libaddapy.BCM2835_GPIO_PUD_UP)
    return

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
    
def ads1256_cfgadc(_gain=ADS1256_GAIN_1['ADS1256_GAIN_1'], _drate=ADS1256_DRATE_E['ADS1256_15SPS']):
    ADS1256_VAR_T.ADS1256_GAIN_E = _gain
    ADS1256_VAR_T.ADS1256_DRATE_E = _drate

    # ads1256_wait_drdy()

    buf = [[], [], [], []]
    buf[0] = (0 << 3) | (1 << 2) | (0 << 1)
    buf[1] = 0x08
    buf[2] = (0 << 5) | (0 << 3) | (_gain << 0)
    buf[3] = s_tabDataRate[_drate]

    cs_0()
    ads1256_send8bit(libaddapy.CMD_WREG | 0)
    ads1256_send8bit(0x03)

    ads1256_send8bit(buf[0])
    ads1256_send8bit(buf[1])
    ads1256_send8bit(buf[2])
    ads1256_send8bit(buf[3])

    cs_1()

    # bsp_delayus(50)

def ads1256_startscan(_ucstanmode=0):
    ADS1256_VAR_T.ScanMode = _ucstanmode
    ADS1256_VAR_T.Channel = 0
    ADS1256_VAR_T.AdcNow = []

    for i in range(8):
        ADS1256_VAR_T.AdcNow.append(0)

def ads1256_scan():
    if drdy_is_low:
        ads1256_isr()

        return 1

    return0

def ads1256_isr():
    if ADS1256_VAR_T.ScanMode == 0:
        ads1256_setchannel(ADS1256_VAR_T.Channel)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_SYNC)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_WAKEUP)
        # bsp_delayus(25)

        if ADS1256_VAR_T.Channel == 0:
            ADS1256_VAR_T.AdcNow[7] = ads1256_readdata()

        else:
            ADS1256_VAR_T.AdcNow[ADS1256_VAR_T.Channel-1] = ADS1256_readdata()

        if ADS1256_VAR_T.Channel >= 8:
            ADS1256_VAR_T.Channel = 0

    else:
        ADS1256_setdiffchannel(ADS1256_VAR_T.Channel)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_SYNC)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_WAKEUP)
        # bsp_delayus(25)

        if ADS1256_VAR_T.Channel == 0:
            ADS1256_VAR_T.AdcNow[3] = ads1256_readdata()

        else:
            ADS1256_VAR_T.AdcNow[ADS1256_VAR_T.Channel-1] = ADS1256_readdata()

        if ADS1256_VAR_T.Channel >= 4:
            ADS1256_VAR_T.Channel = 0

    return
    
def ads1256_setchannel(_ch=0):
    if _ch > 7:
        return
    ads1256_writereg(libaddapy.REG_MUX, (_ch << 4) | (1 << 3))

def ads1256_readdata():
    read = 0
    buf = [[], [], []]

    cs_0()
    
    ads1256_send8bit(libaddapy.CMD_RDATA)
    # ads1256_delaydata()

    buf[0] = ads1256_recive8bit()
    buf[1] = ads1256_recive8bit()
    buf[2] = ads1256_recive8bit()

    read = (buf[0] << 16) & 0x00FF0000
    read |= (buf[1] << 8)
    read |= buf[2]

    cs_1()

    if read & 0x800000: read |= 0xFF000000
        return read
        

def ads1256_setdiffchannel(_ch):
    if _ch == 0:
        ads1256_writereg(libaddapy.REG_MUX, (0 << 4) | 1)

    elif _ch == 1:
        ads1256_writereg(libaddapy.REG_MUX, (2 << 4) | 3)

    elif _ch == 2:
        ads1256_writereg(libaddapy.REG_MUX, (4 << 4) | 5)

    elif _ch == 3:
        ads1256_writereg(libaddapy.REG_MUX, (6 << 4) | 7)
        
    return

def ads1256_writereg(_regid, _regvalue):
    cs_0()
    ads1256_send8bit(libaddapy.CMD_WREG | _regid)
    ads1256_send8bit(0x00)

    ads1256_send8bit(_regvalue)
    cs_1()

def ads1256_getadc(_ch):
    iTemp = 0

    if _ch > 7: return 0

    iTemp = ADS1256_VAR_T.AdcNow[_ch]

    return iTemp

if __init__ = '__main__':
    ch_num = 8
    adc = [_ for _ in range(8)]
    volt = [_ for _ in range(8)]
    iTemp = 0
    buf = [[], [], []]
    
    if configure(): return
    # else: raise InvalidAccessError
    id = ads1256_readchipid

    if id == 0x11:
        ads1256_cfgadc(_gain=ADS1256_GAIN_E['ADS1256_GAIN_1'], _drate=ADS1256_DRATE_E['ADS126_15SPS'])
        ads1256_startscan(0)

        while 1:
            while ads1256_scan() == 0:
                for i in range(ch_num):
                    adc[i] = ads1256_getadc(i)
                volt[i] = adc[i] * 100 / 167

                for i in range(ch_num):
                    buf[0] = (adc[i] >> 16) & 0xFF
                    buf[1] = (adc[i] >> 8) & 0xFF
                    buf[2] = (adc[i] >> 0) & 0xFF

                    print('{0}={1}{2}{3}, {4}'.format(i,
                                                      round(buf[0], 2),
                                                      round(buf[1], 2),
                                                      round(buf[2], 2),
                                                      round(adc[i], 8)))
                    iTemp = volt[i]

                    if iTemp < 0: iTemp = -iTemp
                        print('(-{0}.{1} {2} V) \r\n'.format(iTemp/1000000, (iTemp%1000000)/1000, iTemp%1000))
                    else: print('{0}.{1} {2} V) \r\n'.format(iTemp/1000000, (iTemp%1000000)/1000, iTemp%1000))

                bsp_delayus(100000)

    libaddapy.spi.end()
    libaddapy.spi.close()

    return
