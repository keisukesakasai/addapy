import os
import ctypes

DRDY = 17 # RPI_GPIO_P1_11
SPICS = 22 # RPI_GPIO_P1_15

CMD_RREG = 0x10

REG_STATUS =0

HIGH = 1
LOW = 0


SO_DIR = '/usr/local/lib'
SO_NAME = 'libbcm2835.so'
SO_PATH = os.path.join(SO_DIR, SO_NAME)

lib = ctypes.cdll.LoadLibrary(SO_PATH)

_int = ctypes.c_int
_uint = ctypes.c_int

# int bcm2835_init(  );
# ---------------------
init = lib.bcm2835_init
init.restype = _int

# void bcm2835_spi_begin(  );
# ---------------------------

# void bcm2835_spi_setBitOrder( uint16_t );
# -----------------------------------------
setBitOrder = lib.bcm2835_spi_setBitOrder
setBitOrder.argtypes = {_uint}

# void bcm2835_spi_setClockDivider( uint16_t );
setClockDivider = lib.bcm2835_spi_setClockDivider
setClockDivider.argtypes = {_uint}


# void bcm2835_gpio_fsel( uint8_t, uint8_t );
gpio_fsel = lib.bcm2835_gpio_fsel
gpio_fsel.argtypes = {_uint, _uint}

# void bcm2835_gpio_write( uint8_t, uint8_t );
gpio_write = lib.bcm2835_gpio_write
gpio_write.argtypes = {_uint, _uint}

# void bcm2835_gpio_set_pud( uint8_t, uint8_t );
gpio_set_pud = lib.bcm2835_gpio_set_pud
gpio_set_pud.argtypes = {_uint, _uint}

# uint8_t bcm2835_gpio_lev ( uint8_t );
gpio_lev = lib.bcm2835_gpio_lev
gpio_lev.restype = _uint
gpio_lev.argtypes = {_uint}

# void bcm2835_delayMicroseconds ( uint64_t )
delayMicroseconds = lib.bcm2835_delayMicroseconds
delayMicroseconds.argtypes = {_uint}

# uint8_t bcm2835_spi_transfer ( uint8_t )
spi_transfer = lib.bcm2835_spi_transfer
spi_transfer.restype = _uint
spi_transfer.argtypes = {_uint}

