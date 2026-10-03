from machine import Pin, SPI
import framebuf
class FC16Matrix:
    def __init__(self, spi, cs, num_matrices=4):
        self.spi, self.cs, self.num = spi, cs, num_matrices
        self.cs.init(Pin.OUT, value=1)
        self.width, self.height = num_matrices * 8, 8
        self.buffer = bytearray(self.width * self.height // 8)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_HLSB)
        for cmd, data in [(0x0F,0),(0x0C,1),(0x0B,7),(0x0A,2),(0x09,0)]: self._write_all(cmd,data)
        self.clear()
    def _write_all(self, cmd, data):
        self.cs(0)
        for _ in range(self.num): self.spi.write(bytearray([cmd,data]))
        self.cs(1)
    def fill(self, col): self.fb.fill(col)
    def text(self, s, x, y, col=1): self.fb.text(s,x,y,col)
    def pixel(self, x, y, col=1): return self.fb.pixel(x,y,col)
    def clear(self): self.fill(0); self.show()
    def brightness(self, val): self._write_all(0x0A,max(0,min(15,val)))
    def show(self):
        for row in range(8):
            self.cs(0)
            for m in range(self.num-1,-1,-1):
                col_data=0
                for col in range(8):
                    if self.fb.pixel(m*8+col,7-row): col_data |= 1 << col
                self.spi.write(bytearray([row+1,col_data]))
            self.cs(1)
