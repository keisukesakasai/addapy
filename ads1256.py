import time
import sys
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

ADS1256_DRATE_E = {'ADS1256_30000SPS':0xf0,
                   'ADS1256_15000SPS':0xe0,
                   'ADS1256_7500SPS':0xd0,
                   'ADS1256_3750SPS':0xc0,
                   'ADS1256_2000SPS':0xb0,
                   'ADS1256_1000SPS':0xa1,
                   'ADS1256_500SPS':0x92,
                   'ADS1256_100SPS':0x82,
                   'ADS1256_60SPS':0x72,
                   'ADS1256_50SPS':0x63,
                   'ADS1256_30SPS':0x53,
                   'ADS1256_25SPS':0x43,
                   'ADS1256_15SPS':0x33,
                   'ADS1256_10SPS':0x20,
                   'ADS1256_5SPS':0x13,
                   'ADS1256_2d5SPS':0x03}

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

def ussleep(_t = 0):
    t = _t * 10 ** (-6)
    time.sleep(t)
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
    ussleep(2000)

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
    ussleep(2000)
    
    libaddapy.spi_transfer(_data)

def bsp_delayus(micros):
    libaddapy.delayMicroseconds(micros)

def ads1256_delaydata():
    bsp_delayus(100000)

def ads1256_recive8bit():
    read = libaddapy.spi_transfer(0xff)
    return read
    
def ads1256_cfgadc(_gain=ADS1256_GAIN_E['ADS1256_GAIN_1'], _drate=ADS1256_DRATE_E['ADS1256_15SPS']):
    d = {}
    d['ADS1256_GAIN_E'] = _gain
    d['ADS1256_DRATE_E'] = _drate
    d['ScanMode'] = None
    d['Channel'] = None
    d['AdcNow'] = None
    config = ADS1256_VAR_T(**d)
    
    '''
    ADS1256_VAR_T.ADS1256_GAIN_E = _gain
    ADS1256_VAR_T.ADS1256_DRATE_E = _drate
    '''

    # ads1256_wait_drdy()

    buf = [[], [], [], []]
    buf[0] = (0 << 3) | (1 << 2) | (0 << 1)
    buf[1] = 0x08
    buf[2] = (0 << 5) | (0 << 3) | (_gain << 0)
    buf[3] = _drate

    cs_0()
    ads1256_send8bit(libaddapy.CMD_WREG | 0)
    ads1256_send8bit(0x03)

    ads1256_send8bit(buf[0])
    ads1256_send8bit(buf[1])
    ads1256_send8bit(buf[2])
    ads1256_send8bit(buf[3])

    cs_1()

    return config

    # bsp_delayus(50)
    ussleep(50000)

def ads1256_startscan(_ucscanmode=0, _ch=0, config={}):
    d = {}
    d['ADS1256_GAIN_E'] = config.ADS1256_GAIN_E
    d['ADS1256_DRATE_E'] = config.ADS1256_DRATE_E
    d['ScanMode'] = _ucscanmode
    # d['Channel'] = 0
    d['Channel'] = _ch
    d['AdcNow'] = [0 for i in range(8)]
    config = ADS1256_VAR_T(**d)

    return config

    '''
    ADS1256_VAR_T.ScanMode = _ucscanmode
    ADS1256_VAR_T.Channel = 0
    ADS1256_VAR_T.AdcNow = []

    for i in range(8):
        ADS1256_VAR_T.AdcNow.append(0)
    '''

def ads1256_scan(config={}):
    if drdy_is_low:
        config = ads1256_isr(config)

        return config

    return 0

def ads1256_isr(config={}):
    if config.ScanMode == 0:
        ads1256_setchannel(config.Channel)
        # bsp_delayus(5)
        ussleep(5000)

        ads1256_writecmd(libaddapy.CMD_SYNC)
        # bsp_delayus(5)
        ussleep(50000)

        ads1256_writecmd(libaddapy.CMD_WAKEUP)
        # bsp_delayus(25)
        ussleep(250000)

        if config.Channel == 0:
            config.AdcNow[7] = ads1256_readdata()

        else:
            config.AdcNow[config.Channel-1] = ads1256_readdata()

        '''
        elif config.Channel >= 8:
            config.Channel = 0
        '''
        return config
            

    else:
        ads1256_setdiffchannel(config.Channel)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_SYNC)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_WAKEUP)
        # bsp_delayus(25)

        if config.Channel == 0:
            config.AdcNow[3] = ads1256_readdata()

        else:
            config.AdcNow[config.Channel-1] = ads1256_readdata()
        '''
        elif config.Channel >= 4:
            config.Channel = 0
        '''
        return config

    '''
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
        ads1256_setdiffchannel(ADS1256_VAR_T.Channel)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_SYNC)
        # bsp_delayus(5)

        ads1256_writecmd(libaddapy.CMD_WAKEUP)
        # bsp_delayus(25)

        if ADS1256_VAR_T.Channel == 0:
            ADS1256_VAR_T.AdcNow[3] = ads1256_readdata()

        else:
            ADS1256_VAR_T.AdcNow[ADS1256_VAR_T.Channel-1] = ads1256_readdata()

        if ADS1256_VAR_T.Channel >= 4:
            ADS1256_VAR_T.Channel = 0
    '''
    
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
    ussleep(10000)

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

def ads1256_getadc(_ch, config={}):
    iTemp = 0

    if _ch > 7: return 0

    iTemp = config.AdcNow[_ch]
    # iTemp = ADS1256_VAR_T.AdcNow[_ch]

    return iTemp

def ads1256_writecmd(_cmd):
    cs_0()
    ads1256_send8bit(_cmd)
    cs_1()

def ads1256_adc():
    d = {}
    ch_num = 8
    adc = [0 for _ in range(8)]
    volt = [0 for _ in range(8)]
    iTemp = 0
    buf = [[], [], []]
    _val = [0 for _ in range(8)]

    configure()

    for i in range(ch_num):
        config = ads1256_cfgadc(_gain=ADS1256_GAIN_E['ADS1256_GAIN_1'], _drate=ADS1256_DRATE_E['ADS1256_15SPS'])
        config = ads1256_startscan(_ucscanmode=0, _ch=i, config=config)
        config = ads1256_scan(config)
        if i == 0: _val[i] = config.AdcNow[7]
        else: _val[i] = config.AdcNow[i-1]
    val = [round(_*100/167/2/1000000, 4) for _ in _val]

    for i in range(ch_num):
        d['CH{0}'.format(i+1)] = val[i]
    
    libaddapy.spi_end()
    libaddapy.close()

    return d
    
if __name__ == '__main__':
    ch_num = 8
    adc = [_ for _ in range(8)]
    volt = [_ for _ in range(8)]
    iTemp = 0
    buf = [[], [], []]
    val = []
    
    configure()
    # else: raise InvalidAccessError
    id = ads1256_readchipid()
    print('id = {}'.format(id))

    if id == 0x03:
        print('Valid Chip ID...\n' \
                         'Satrt ADC...\n\n\n')
        try:
            while True:
                d = ads1256_adc()
                '''
                sys.stdout.write('\rCH1 : {0} V'.format(d['CH1']))
                sys.stdout.write('\rCH2 : {0} V'.format(d['CH2']))
                sys.stdout.write('\rCH3 : {0} V'.format(d['CH3']))
                sys.stdout.write('\rCH4 : {0} V'.format(d['CH4']))
                sys.stdout.write('\rCH5 : {0} V'.format(d['CH5']))
                sys.stdout.write('\rCH6 : {0} V'.format(d['CH6']))
                sys.stdout.write('\rCH7 : {0} V'.format(d['CH7']))
                sys.stdout.write('\rCH8 : {0} V'.format(d['CH8']))                
                '''
                sys.stdout.write('\n'
                                 '====== ADC VALUE ======\n'
                                 'CH1 : {0} V\n'
                                 'CH2 : {1} V\n'
                                 'CH3 : {2} V\n'
                                 'CH4 : {3} V\n'
                                 'CH5 : {4} V\n'
                                 'CH6 : {5} V\n'
                                 'CH7 : {6} V\n'
                                 'CH8 : {7} V\n'
                                 '========================\n\n'.format(d['CH1'], d['CH2'], d['CH3'], d['CH4'], d['CH5'], d['CH6'], d['CH7'], d['CH8']))
                sys.stdout.flush()
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        '''
        config = ads1256_cfgadc(_gain=ADS1256_GAIN_E['ADS1256_GAIN_1'], _drate=ADS1256_DRATE_E['ADS1256_15SPS'])
        config = ads1256_startscan(0, config=config)

        while 1:
            # while ads1256_scan(config) == 1:
            config = ads1256_scan(config)
            for i in range(ch_num):
                adc[i] = ads1256_getadc(i, config)
                volt[i] = adc[i] * 100 / 167 / 2
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

                if iTemp < 0:
                    iTemp = -iTemp
                    print('(-{:.5f} V) \r\n'.format(iTemp/1000000))
                else: print('({:.5f} V) \r\n'.format(iTemp/1000000))
        '''


