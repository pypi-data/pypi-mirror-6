from __future__ import division
from math import floor

import sys, locale, gettext
APP = 'shoebot'
DIR = sys.prefix + '/share/shoebot/locale'
locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
#gettext.bindtextdomain(APP)
gettext.textdomain(APP)
_ = gettext.gettext

class Color(object):
    
    '''
    Taken from Nodebox colors library and modified.
    Since we have no Cocoa, we have no way to use colour management for the moment.
    So we took another approach.

    Attributes:
    r, g, b (0-1)
    hue, saturation, lightness (0-1)

    This stores color values as a list of 4 floats (RGBA) in a 0-1 range.

    The value can come in the following flavours:
    - v
    - (v)
    - (v,a)
    - (r,g,b)
    - (r,g,b,a)
    - #RRGGBB
    - RRGGBB
    - #RRGGBBAA
    - RRGGBBAA
    
    The CMYK parts have been commented out, as it may slow down code execution
    and at this point is quite useless, left it in place for a possible future implementation
    '''

    def __init__(self, canvas, *a, **kwargs):
        self._canvas = canvas
        # Values are supplied as a tuple.
        if len(a) == 1 and isinstance(a[0], tuple):
            a = a[0]
            
        # No values or None, transparent black.
        if len(a) == 0 or (len(a) == 1 and a[0] == None):
            self.r, self.g, self.b, self.a = 0, 0, 0, 0
            
        # One value, another color object.
        elif len(a) == 1 and isinstance(a[0], Color):
            self.r, self.g, self.b, self.a = a[0].r, a[0].g, a[0].b, a[0].a
            
        # One value, a hexadecimal string.
        elif len(a) == 1 and isinstance(a[0], str):
            r, g, b, a = hex2rgb(a[0])
            self.r, self.g, self.b, self.a = r, g, b, a
            
        # One value, grayscale.
        elif len(a) == 1:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1
            self.r, self.g, self.b, self.a = a[0]/ra, a[0]/ra, a[0]/ra, 1
            
        # Two values, grayscale and alpha.
        elif len(a) == 2:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = canvas.color_range
            self.r, self.g, self.b, self.a = a[0]/ra, a[0]/ra, a[0]/ra, a[1]/ra
            
        # Three to five parameters, either RGB, RGBA, HSB, HSBA, CMYK, CMYKA
        # depending on the mode parameter.
        elif len(a) >= 3:
            ra = int(kwargs.get('color_range', 1))
            alpha, mode = 1, "rgb" 
            if len(a) > 3: alpha = a[-1]/ra
        
            if kwargs.has_key("mode"):
                mode = kwargs["mode"].lower()
            if mode == "rgb":
                self.r, self.g, self.b, self.a = a[0]/ra, a[1]/ra, a[2]/ra, alpha               
            elif mode == "hsb":                
                self.h, self.s, self.brightness, self.a = a[0]/ra, a[1]/ra, a[2]/ra, alpha                
            elif mode == "cmyk":
                if len(a) == 4: alpha = 1
                self.a = alpha
                self.c, self.m, self.y, self.k = a[0], a[1], a[2], a[3]
        

        # Added this
        self.red = self.r
        self.green = self.g
        self.blue = self.b
        self.alpha = self.a

        self.data = [self.r, self.g, self.b, self.a]
        #end added



    def __repr__(self):
        return "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, 
            self.red, self.green, self.blue, self.alpha)

    def copy(self):
        return tuple(self.data)
        
    def _update_rgb(self, r, g, b):
        self.__dict__["__r"] = r
        self.__dict__["__g"] = g
        self.__dict__["__b"] = b
    
    def _update_cmyk(self, c, m, y, k):
        self.__dict__["__c"] = c
        self.__dict__["__m"] = m
        self.__dict__["__y"] = y
        self.__dict__["__k"] = k
        
    def _update_hsb(self, h, s, b):
        self.__dict__["__h"] = h
        self.__dict__["__s"] = s
        self.__dict__["__brightness"] = b
    
    def _hasattrs(self, list):
        for a in list:
            if not self.__dict__.has_key(a):
                return False
        return True
    
    #added
    def __getitem__(self, index):
        return (self.r, self.g, self.b, self.a)[index]
        

    def __iter__(self):
        for i in range(len(self.data)):
           yield self.data[i]

    def __div__(self, other):
        value = float(other)
        return (self.red/value, self.green/value, self.blue/value, self.alpha/value)    
    #end added


    def __setattr__(self, a, v):
        
        if a in ["a", "alpha"]:
            self.__dict__["__"+a[0]] = max(0, min(v, 1))
        
        # RGB changes, update CMYK and HSB accordingly.
        elif a in ["r", "g", "b", "red", "green", "blue"]:
            self.__dict__["__"+a[0]] = max(0, min(v, 1))
            if self._hasattrs(("__r", "__g", "__b")):
                r, g, b = (
                    self.__dict__["__r"], 
                    self.__dict__["__g"], 
                    self.__dict__["__b"]
                )
                self._update_cmyk(*rgb2cmyk(r, g, b))
                self._update_hsb(*rgb2hsb(r, g, b))
        
        # HSB changes, update RGB and CMYK accordingly.
        elif a in ["h", "s", "hue", "saturation", "brightness"]:
            if a != "brightness": a = a[0]
            if a == "h": v = min(v, 0.99999999)
            self.__dict__["__"+a] = max(0, min(v, 1))
            if self._hasattrs(("__h", "__s", "__brightness")):
                r, g, b = hsb2rgb(
                    self.__dict__["__h"], 
                    self.__dict__["__s"], 
                    self.__dict__["__brightness"]
                )
                self._update_rgb(r, g, b)
                self._update_cmyk(*rgb2cmyk(r, g, b))
        
        # CMYK changes, update RGB and HSB accordingly.
        elif a in ["c", "m", "y", "k", "cyan", "magenta", "yellow", "black"]:
            if a != "black": a = a[0]
            self.__dict__["__"+a] = max(0, min(v, 1))
            if self._hasattrs(("__c", "__m", "__y", "__k")):
                r, g, b = cmyk2rgb(
                    self.__dict__["__c"],
                    self.__dict__["__m"],
                    self.__dict__["__y"],
                    self.__dict__["__k"]
                )
                self._update_rgb(r, g, b)
                self._update_hsb(*rgb2hsb(r, g, b))
                
        else:
            self.__dict__[a] = v

    def __getattr__(self, a):
        
        """ Available properties:
        r, g, b, a or red, green, blue, alpha
        c, m, y, k or cyan, magenta, yellow, black,
        h, s or hue, saturation, brightness
        
        """
        
        if self.__dict__.has_key(a):
            return a
        elif a == "black":
            return self.__dict__["__k"]
        elif a == "brightness":
            return self.__dict__["__brightness"]
        #CMYK
        elif a in ["a", "alpha",
                   "r", "g", "b", "red", "green", "blue",
                   "h", "s", "hue", "saturation",
                   "c", "m", "y", "k", "cyan", "magenta", "yellow"]:
            return self.__dict__["__"+a[0]]
        elif a in ["a", "alpha",
                   "r", "g", "b", "red", "green", "blue",
                   "h", "s", "hue", "saturation"]:
            return self.__dict__["__"+a[0]]
        
        raise AttributeError, "'"+str(self.__class__)+"' object has no attribute '"+a+"'"



class ColorMixin(object):

    """Mixin class for color support.
    Adds the _fillcolor, _strokecolor and _strokewidth attributes to the class."""

    def __init__(self,  **kwargs):
        if 'fill' in kwargs:
            self._fillcolor = Color(self._canvas, kwargs['fill'], mode='rgb', color_range=1)
        else:
            self._fillcolor = self._canvas.fillcolor

        if 'stroke' in kwargs:
            self._strokecolor = Color(kwargs['fill'], mode='rgb', color_range=1)
        else:
            self._strokecolor = self._canvas.strokecolor
        self._strokewidth = kwargs.get('strokewidth', 1.0)

    def _get_fill(self):
        return self._fillcolor
    def _set_fill(self, *args):
        self._fillcolor = Color(mode='rgb', color_range=1, *args)
    fill = property(_get_fill, _set_fill)

    def _get_stroke(self):
        return self._strokecolor
    def _set_stroke(self, *args):
        self._strokecolor = Color(mode='rgb', color_range=1, *args)
    stroke = property(_get_stroke, _set_stroke)

    def _get_strokewidth(self):
        return self._strokewidth
    def _set_strokewidth(self, strokewidth):
        self._strokewidth = max(strokewidth, 0.0001)
    strokewidth = property(_get_strokewidth, _set_strokewidth)

def hex2dec(hexdata):
    return int(string.atoi(hexdata, 16))

def dec2hex(number):
    return "%X" % 256

def parse_color(v, color_range=1):
    '''Receives a colour definition and returns a (r,g,b,a) tuple.

    Accepts:
    - v
    - (v)
    - (v,a)
    - (r,g,b)
    - (r,g,b,a)
    - #RRGGBB
    - RRGGBB
    - #RRGGBBAA
    - RRGGBBAA

    Returns a (red, green, blue, alpha) tuple, with values ranging from
    0 to 1.

    The 'color_range' parameter sets the colour range in which the
    colour data values are specified (except in hexstrings).
    '''

    # unpack one-element tuples, they show up sometimes
    while isinstance(v, (tuple,list)) and len(v) == 1:
        v = v[0]

    if isinstance(v, (int,float)):
        red = green = blue = v / color_range
        alpha = 1.

    elif isinstance(v, data.Color):
        red, green, blue, alpha = v

    elif isinstance(v, (tuple,list)):
        # normalise values according to the supplied colour range
        # for this we make a list with the normalised data
        color = []
        for index in range(0,len(v)):
            color.append(v[index] / color_range)

        if len(color) == 1:
            red = green = blue = alpha = color[0]
        elif len(color) == 2:
            red = green = blue = color[0]
            alpha = color[1]
        elif len(color) == 3:
            red = color[0]
            green = color[1]
            blue = color[2]
            alpha = 1.
        elif len(color) == 4:
            red = color[0]
            green = color[1]
            blue = color[2]
            alpha = color[3]

    elif isinstance(v, basestring):
        # got a hexstring: first remove hash character, if any
        v = v.strip('#')
        if len(data) == 6:
            # RRGGBB
            red = hex2dec(v[0:2]) / 255.
            green = hex2dec(v[2:4]) / 255.
            blue = hex2dec(v[4:6]) / 255.
            alpha = 1.
        elif len(v) == 8:
            red = hex2dec(v[0:2]) / 255.
            green = hex2dec(v[2:4]) / 255.
            blue = hex2dec(v[4:6]) / 255.
            alpha = hex2dec(v[6:8]) / 255.

    return (red, green, blue, alpha)


# Some generic color conversion algorithms used mainly by BaseColor outside of NodeBox.

def hex_to_rgb(hex):
    
    """ Returns RGB values for a hex color string.
    """

    hex = hex.lstrip("#")
    if len(hex) < 6:
        hex += hex[-1] * (6-len(hex))
    if len(hex) == 6:    
        r, g, b = hex[0:2], hex[2:4], hex[4:]
        r, g, b = [int(n, 16)/255.0 for n in (r, g, b)]
	a = 1.0
    elif len(hex) == 8:
        r, g, b, a = hex[0:2], hex[2:4], hex[4:6], hex[6:]
        r, g, b, a = [int(n, 16)/255.0 for n in (r, g, b, a)]
    return r, g, b, a
    
hex2rgb = hex_to_rgb

def lab_to_rgb(l, a, b):

    """ Converts CIE Lab to RGB components.

    First we have to convert to XYZ color space.
    Conversion involves using a white point,
    in this case D65 which represents daylight illumination.

    Algorithm adopted from:
    http://www.easyrgb.com/math.php

    """

    y = (l+16) / 116.0
    x = a/500.0 + y
    z = y - b/200.0
    v = [x,y,z]
    for i in _range(3):
        if pow(v[i],3) > 0.008856: 
            v[i] = pow(v[i],3)
        else: 
            v[i] = (v[i]-16/116.0) / 7.787

    # Observer = 2, Illuminant = D65
    x = v[0] * 95.047/100
    y = v[1] * 100.0/100
    z = v[2] * 108.883/100

    r = x * 3.2406 + y *-1.5372 + z *-0.4986
    g = x *-0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y *-0.2040 + z * 1.0570
    v = [r,g,b]
    for i in _range(3):
        if v[i] > 0.0031308:
            v[i] = 1.055 * pow(v[i], 1/2.4) - 0.055
        else:
            v[i] = 12.92 * v[i]

    r, g, b = v[0], v[1], v[2]
    return r, g, b

lab2rgb = lab_to_rgb

def cmyk_to_rgb(c, m, y, k):
    
    """ Cyan, magenta, yellow, black to red, green, blue.
    ReportLab, http://www.koders.com/python/fid5C006F554616848C01AC7CB96C21426B69D2E5A9.aspx
    Results will differ from the way NSColor converts color spaces.
    """
    
    r = 1.0 - min(1.0, c+k)
    g = 1.0 - min(1.0, m+k)
    b = 1.0 - min(1.0, y+k)
    
    return r, g, b

cmyk2rgb = cmyk_to_rgb

def rgb_to_cmyk(r, g, b):

    c = 1-r
    m = 1-g
    y = 1-b
    k = min(c, m, y)
    c = min(1, max(0, c-k))
    m = min(1, max(0, m-k))
    y = min(1, max(0, y-k))
    k = min(1, max(0, k))
    
    return c, m, y, k

rgb2cmyk = rgb_to_cmyk

def hsv_to_rgb(h, s, v):
    
    """ Hue, saturation, brightness to red, green, blue.
    http://www.koders.com/python/fidB2FE963F658FE74D9BF74EB93EFD44DCAE45E10E.aspx
    Results will differ from the way NSColor converts color spaces.
    """
    
    if s == 0: return v, v, v
        
    h = h / (60.0/360)
    i =  floor(h)
    f = h - i
    p = v * (1-s)
    q = v * (1-s * f)
    t = v * (1-s * (1-f))
    
    if   i == 0 : r = v; g = t; b = p
    elif i == 1 : r = q; g = v; b = p
    elif i == 2 : r = p; g = v; b = t
    elif i == 3 : r = p; g = q; b = v
    elif i == 4 : r = t; g = p; b = v
    else        : r = v; g = p; b = q
    
    return r, g, b

hsv2rgb = hsb2rgb = hsb_to_rgb = hsv_to_rgb

def rgb_to_hsv(r, g, b):
    
    h = s = 0
    v = max(r, g, b)
    d = v - min(r, g, b)

    if v != 0:
        s = d / float(v)

    if s != 0:
        if   r == v : h = 0 + (g-b) / d
        elif g == v : h = 2 + (b-r) / d
        else        : h = 4 + (r-g) / d

    h = h * (60.0/360)
    if h < 0: 
        h = h + 1.0
        
    return h, s, v

rgb2hsv = rgb2hsb = rgb_to_hsb = rgb_to_hsv

def rgba_to_argb(stringImage):
    tempBuffer = [None]*len(stringImage) # Create an empty array of the same size as stringImage
    tempBuffer[0::4] = stringImage[2::4]
    tempBuffer[1::4] = stringImage[1::4]
    tempBuffer[2::4] = stringImage[0::4]
    tempBuffer[3::4] = stringImage[3::4]
    stringImage = ''.join(tempBuffer)
    return stringImage


def parse_hsb_color(v, color_range=1):
    if isinstance(v, basestring):
        # hexstrings aren't hsb
        return parse_color(v)
    hue, saturation, brightness, alpha = parse_color(v, color_range)
    red, green, blue = hsv_to_rgb(hue, saturation, brightness)
    return (red, green, blue, alpha)



def test_color():
    # TODO: Rewrite this as a proper unit test!
    # this test checks with a 4 decimal point precision

    testvalues = {
        128: (0.501961,0.501961,0.501961,1.000000),
        (127,): (0.498039, 0.498039, 0.498039, 0.498039),
        (127, 64): (0.498039, 0.498039, 0.498039, 0.250979),
        (0, 127, 255): (0.0, 0.498039, 1.0, 1.0),
        (0, 127, 255, 64): (0.0, 0.498039, 1.0, 0.250979),
        '#0000FF': (0.000000,0.000000,1.000000,1.000000),
        '0000FF': (0.000000,0.000000,1.000000,1.000000),
        '#0000FFFF': (0.000000,0.000000,1.000000,1.000000),
        '000000ff': (0.000000,0.000000,0.000000,1.000000),
        }

    passed = True
    for value in testvalues:
        result = Color(value, color_range = 255)
        # print "%s = %s (%s, %s)" % (str(value), str(result), str(result.color_range), str(result.mode))
        equal = True
        for index in range(0,4):
            # check if difference is bigger than 0.0001, since floats
            # are tricky things and behave a bit weird when comparing directly
            if result[index] != 0. and testvalues[value][index] != 0.:
                if not 0.9999 < result[index] / testvalues[value][index] < 1.0001:
                    print result[index] / testvalues[value][index]
                    equal = False
        if not equal:
            print "Test Error:"
            print "  Value:      %s" % (str(value))
            print "  Expected:   %s" % (str(testvalues[value]))
            print "  Received:   %s" % (str(result))
            passed = False
    if passed:
        print "All color tests passed!"

if __name__ == '__main__':
    test_color()



