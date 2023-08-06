import usb.core
# import usb.util
import time
import struct

ldict = {}
for c in range(65,86):
    # print chr(c),
    ldict[chr(c)] = c-65

def util_byteify(row):
    byte = [0,0,0]
    mrow = [0,0,0]
    mrow.extend( reversed( list(row) ) )

    for i in range(0,len(mrow)):
        if mrow[i]:
            mrow[i] = '0' # device spec: 0 is "on". Weird.
        else:
            mrow[i] = '1'

    byte[0] = ''.join(mrow[:8])
    byte[1] = ''.join(mrow[8:16])
    byte[2] = ''.join(mrow[16:])

    for i in range(0,3):
        byte[i] = int( byte[i], 2 )

    return byte

def decode_grid(location):
    if len(location) != 2:
        raise ValueError("Location grid must be in the form A0")

    (col, row) = location.upper()
    col = ldict[col]
    row = int(row)
    return (col,row)

class display():

    # vendorID = 0x1d34
    # deviceID = 0x0013

    def clear(self, state=0):
        self.current_frame = []
        for row in range(0,7):
            a_row = []
            for col in range(0,21):
                a_row.append(state)
            self.current_frame.append(a_row)

    def __init__(self):
        self.clear()

    def connect(self):
        self.device = usb.core.find(idVendor=0x1d34, idProduct=0x0013)
        if self.device == None:
            return 0
        
        self.device.set_configuration()
        return 1

    def is_connected(self):
        if self.device == None:
            return 0
        return 1

    def _pack_current_frame(self):
        cframe = self.current_frame
        packed_frame = []
        
        for start in [0,2,4,6]:
            byterow = [0, start]
            byterow.extend( util_byteify(cframe[start]) )

            if start < 6:
                byterow.extend( util_byteify(cframe[start+1]) )
            else:
                byterow.extend([0,0,0])

            for i in range(0,len(byterow)):
                byterow[i] = chr(byterow[i])

            packed_frame.append(
                struct.pack(
                    'cccccccc',
                    byterow[0],
                    byterow[1],
                    byterow[2],
                    byterow[3],
                    byterow[4],
                    byterow[5],
                    byterow[6],
                    byterow[7],
                    )
                )

        self.packed_frame = packed_frame

    def _send_packed_frame(self):
        for i in range(0,4):
            assert self.device.ctrl_transfer(0x21, 0x09, 0, 0, self.packed_frame[i]) == 8

    def refresh(self):
        self._pack_current_frame()
        self._send_packed_frame()

    def change_light(self, col, row, state):
        self.current_frame[row][col] = state

    def light_on_at(self, location):
        (col,row) = decode_grid(location)
        self.change_light(col, row, 1)

    def light_off_at(self, location):
        (col,row) = decode_grid(location)
        self.change_light(col, row, 0)

    def light_on(self, x, y):
        self.change_light(x, y, 1)

    def light_off(self, x, y):
        self.change_light(x, y, 0)

    def put_sprite(self, x, y, sprite, mode='replace'):
        row = y
        for gridrow in sprite:
            col = x
            for state in gridrow:
                if mode == 'replace':
                    self.current_frame[row][col] = state
                elif mode == 'and':
                    self.current_frame[row][col] = self.current_frame[row][col] & state
                elif mode == 'or':
                    self.current_frame[row][col] = self.current_frame[row][col] | state
                elif mode == 'xor':
                    self.current_frame[row][col] = self.current_frame[row][col] ^ state
                elif mode == 'clear':
                    self.current_frame[row][col] = 0
                elif mode == 'fill':
                    self.current_frame[row][col] = 1
                else:
                    raise ValueError("Mode must be one of: replace, and, or, xor, clear, fill")
                col += 1
            row += 1

        self.current_frame = self.current_frame[:7]
        for r in range(0, len(self.current_frame)):
            self.current_frame[r] = self.current_frame[r][:21]

    def put_sprite_to(self, location, subgrid, mode='replace'):
        (start_col,start_row) = decode_grid(location)
        self.put_sprite(col, row, subgrid, mode)

    def move_right(self, clear_state=0, count=1):
        for row in self.current_frame:
            for c in range(0,count):
                row.insert(0, clear_state)
                row.pop()

    def move_left(self, clear_state=0, count=1):
        for row in self.current_frame:
            for c in range(0,count):
                row.append(clear_state)
                row.pop(0)

    def move_down(self, clear_state=0, count=1):
        new_row = []
        for i in range(0,21):
            new_row.append(clear_state)

        for i in range(0,count):
            self.current_frame.insert(0,new_row)
            self.current_frame.pop()

    def move_up(self, clear_state=0, count=1):
        new_row = []
        for i in range(0,21):
            new_row.append(clear_state)

        for i in range(0,count):
            self.current_frame.append(new_row)
            self.current_frame.pop(0)
        






