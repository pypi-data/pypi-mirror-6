import os
import glob

from base_node import BaseNode

# command codes
CMD_SET_POWER     = 0xA0
CMD_GET_POWER     = 0xA1
CMD_SET_STATE     = 0xA2
CMD_GET_STATE     = 0xA3
CMD_GET_CURRENT   = 0xA4

# H-bridge states
OFF               = 0
ON                = 1
FORWARD           = 2
REVERSE           = 3


def get_sketch_directory():
    '''
    Return directory containing the `electromagnet_controller` Arduino sketch.
    '''
    return os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'Arduino', 'electromagnet_controller')


def get_includes():
    '''
    Return directories containing the `electromagnet_controller` Arduino header
    files.

    Modules that need to compile against `electromagnet_controller` should use
    this function to locate the appropriate include directories.

    Notes
    =====

    For example:

        import electromagnet_controller
        ...
        print ' '.join(['-I%s' % i for i in electromagnet_controller.get_includes()])
        ...

    '''
    return [get_sketch_directory()]


def get_sources():
    '''
    Return `electromagnet_controller` Arduino source file paths.

    Modules that need to compile against `electromagnet_controller` should use
    this function to locate the appropriate source files to compile.

    Notes
    =====

    For example:

        import electromagnet_controller
        ...
        print ' '.join(electromagnet_controller.get_sources())
        ...

    '''
    return glob.glob(os.path.join(get_sketch_directory(), '*.c*'))


class ElectromagnetController(BaseNode):
    def __init__(self, proxy, address):
        BaseNode.__init__(self, proxy, address)

    def power(self):
        self.send_command(CMD_GET_POWER)
        return self.read_uint8()

    def set_power(self, power):
        self.data = []
        self.serialize_uint8(power)
        self.send_command(CMD_SET_POWER)

    def state(self):
        self.send_command(CMD_GET_STATE)
        return self.read_uint8()

    def get_current(self):
        self.send_command(CMD_GET_CURRENT)
        return self.read_uint16()/1024.0*5.0/0.13

    def on(self):
        self._set_state(ON)

    def off(self):
        self._set_state(OFF)

    def forward(self):
        self._set_state(FORWARD)

    def reverse(self):
        self._set_state(REVERSE)

    def _set_state(self, state):
        self.data = []
        self.serialize_uint8(state)
        self.send_command(CMD_SET_STATE)
