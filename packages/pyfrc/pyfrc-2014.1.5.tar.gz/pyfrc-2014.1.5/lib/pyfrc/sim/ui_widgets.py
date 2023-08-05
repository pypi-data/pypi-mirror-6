
import tkinter as tk


# user drawable widget for tk
class ValueWidget(tk.Frame):
    
    def __init__(self, master, width=80, height=20, clickable=False, default=None):
        
        super().__init__(master)
        
        self.w = width
        self.h = height
        
        self.canvas = tk.Canvas(self, width=width, height=height)
        self.canvas.pack(fill=tk.BOTH)
        self.canvas.create_rectangle(1, 1, self.w, self.h)
        
        self.box = self.canvas.create_rectangle(0, 0, 0, 0, fill='#00ff00')
        self.text = self.canvas.create_text((self.w - 3, self.h/2), anchor=tk.E, text='--')
        
        if clickable:
            self.canvas.bind("<Button 1>", self._on_mouse)
        
        self.updated = False
        
        if default is None:
            self.set_disabled()
        else:
            self.set_value(default)
        
    def _on_mouse(self, event):
        
        # TODO: this needs to be better.. 
        self.updated = True
        
        # pad the value
        if event.x < 5:
            value = 0
        elif event.x > self.w - 5:
            value = self.w - 5
        else:
            value = event.x - 5
        
        # normalize it
        value = 2.0 * (value - (self.w - 10)/2.0) / (self.w - 10) 
        value = min(max(-1.0, value), 1.0)
        
        self.set_value(value)
    
    
    #
    # Public interface
    #
    
    def set_disabled(self):
        self.canvas.itemconfig(self.text, text='--')
        self.canvas.itemconfig(self.box, state=tk.HIDDEN)
        
    def sync_value(self, value):
        if self.updated:
            self.updated = False
            return self.value
        
        self.set_value(value)
    
    def set_value(self, value):
        
        value = float(min(max(value, -1.0), 1.0))
        
        if value < 0:
            color = '#ff0000'
            x2 = int(self.w / 2)
            x1 = x2 - (abs(value) * x2) 
        else:
            color = '#00ff00'
            x1 = int(self.w / 2)
            x2 = x1 + (abs(value)) * x1
            
        self.canvas.itemconfig(self.text, text='%.2f' % value)
        self.canvas.itemconfig(self.box, state=tk.NORMAL, fill=color)
        self.canvas.coords(self.box, x1, 1, x2, self.h)
        
        self.value = value
        
    
    def get_value(self):
        return self.value
    
    
class PanelIndicator(tk.Frame):
    
    def __init__(self, master, width=20, height=20, clickable=False):
        
        super().__init__(master)
        
        self.updated = False
        self.value = False
        
        self.canvas = tk.Canvas(self, width=width, height=height)
        self.light = self.canvas.create_oval(2, 2, 18, 18, fill='#aaaaaa')
        
        self.canvas.pack(fill=tk.BOTH)
         
        if clickable:
            self.canvas.bind("<Button 1>", self._on_mouse)
            
    def _on_mouse(self, event):
        self.updated = True
        self.set_value(not self.value)
        
    def sync_value(self, value):
        if self.updated:
            self.updated = False
            return self.value
        
        self.set_value(value)
        
    def set_value(self, value):
        if value:
            self.set_on()
        else:
            self.set_off()
        
    def set_on(self):
        self.canvas.itemconfig(self.light, fill='#00FF00')
        self.value = True
    
    def set_off(self):
        self.canvas.itemconfig(self.light, fill='#008800')
        self.value = False
    
    def set_disabled(self):
        self.canvas.itemconfig(self.light, fill='#aaaaaa')

