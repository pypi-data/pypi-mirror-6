#!/usr/bin/env python2

# This file is part of Shoebot.
# Copyright (C) 2007-2009 the Shoebot authors
# See the COPYING file for the full license text.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED
#   WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#   MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
#   EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import cairo
import pango
import pangocairo
## from shoebot.data import Grob, BezierPath, TransformMixin, ColorMixin, _copy_attrs
from shoebot.data import Grob, BezierPath, ColorMixin, _copy_attrs
from shoebot.util import RecordingSurfaceA8
from cairo import PATH_MOVE_TO, PATH_LINE_TO, PATH_CURVE_TO, PATH_CLOSE_PATH

class Text(Grob, ColorMixin):
    
    # several reference docs can be found at http://www.pygtk.org/docs/pygtk/class-pangofontdescription.html

    def __init__(self, bot, text, x=0, y=0, width=None, height=None, outline=False, ctx=None, enableRendering=True, **kwargs):
        self._canvas = canvas = bot._canvas
        Grob.__init__(self, bot)
        ColorMixin.__init__(self, **kwargs)
        
        ###self._transform = canvas.transform # TODO remove - this is in grob

        self._ctx = ctx
        self._pang_ctx = None
        
        self._doRender = enableRendering
                
        self.text = unicode(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self._outline = outline

        self._fontfile = kwargs.get('font', canvas.fontfile)
        self._fontsize = kwargs.get('fontsize', canvas.fontsize)
        self._lineheight = kwargs.get('lineheight', canvas.lineheight)
        self._align = kwargs.get('align', canvas.align)
        self._indent = kwargs.get("indent")

        # we use the pango parser instead of trying this by hand
        self._fontface = pango.FontDescription(self._fontfile)
                                                      
        # then we set fontsize (multiplied by pango.SCALE)
        self._fontface.set_absolute_size(self._fontsize*pango.SCALE)

        # the style
        self._style = pango.STYLE_NORMAL
        if kwargs.has_key("style"):
            if kwargs["style"]=="italic" or kwargs["style"]=="oblique":
                self._style = pango.STYLE_ITALIC
        self._fontface.set_style(self._style)
        
        #we need to pre-render some stuff to enable metrics sizing
        self._pre_render()
        
        if (self._doRender): #this way we do not render if we only need to create metrics
          if bool(ctx):
              self._render(self._ctx)
          else:
              # Normal rendering, can be deferred
              self._deferred_render()
            
    # pre rendering is needed to measure the metrics of the text, it's also useful to get the path, without the need to call _render()
    def _pre_render(self):
        #we use a new CairoContext to pre render the text
        self._pang_ctx = pangocairo.CairoContext(cairo.Context(RecordingSurfaceA8(0, 0)))
        self.layout = self._pang_ctx.create_layout()
        # layout line spacing
        # TODO: the behaviour is not the same as nodebox yet
        self.layout.set_spacing(int(((self._lineheight-1)*self._fontsize)*pango.SCALE)) #pango requires an int casting
        # we pass pango font description and the text to the pango layout
        self.layout.set_font_description(self._fontface)
        self.layout.set_text(self.text)
        # check if max text width is set and pass it to pango layout
        # text will wrap, meanwhile it checks if and indent has to be applied
        # indent is subordinated to width because it makes no sense on a single-line text block
        if self.width:
            self.layout.set_width(int(self.width)*pango.SCALE)
            if self._indent:
                self.layout.set_indent(self._indent*pango.SCALE)                
        # set text alignment    
        if self._align == "right":
            self.layout.set_alignment(pango.ALIGN_RIGHT)
        elif self._align == "center":
            self.layout.set_alignment(pango.ALIGN_CENTER)
        elif self._align == "justify":
            self.layout.set_alignment(pango.ALIGN_LEFT)
            self.layout.set_justify(True)
        else:
            self.layout.set_alignment(pango.ALIGN_LEFT)
            

    def _get_context(self):
        self._ctx = self._ctx or cairo.Context(RecordingSurfaceA8(0, 0))
        return self._ctx

    def _render(self, ctx = None):
        if (not self._doRender):
          return
        ctx = ctx or self._get_context()
        # we build a PangoCairo context linked to cairo context
        # then we create a pango layout
        
        # we update the context as we already used a null one on the pre-rendering
        # supposedly there should not be a big performance penalty 
        self._pang_ctx = pangocairo.CairoContext(ctx)
        self._pang_ctx.update_layout(self.layout)

        if self._fillcolor is not None:
            # Go to initial point (CORNER or CENTER):
            transform = self._call_transform_mode(self._transform)
            ctx.set_matrix(self._transform)

            ctx.translate(self.x,self.y-self.baseline)
            
            if self._outline is False:
                ctx.set_source_rgba(*self._fillcolor)
            self._pang_ctx.show_layout(self.layout)
            self._pang_ctx.update_layout(self.layout)
        


    # This version is probably more pangoesque, but the layout iterator
    # caused segfaults on some system
    #def _get_baseline(self):
        #self.iter = self.layout.get_iter()
        #baseline_y = self.iter.get_baseline()
        #baseline_delta = baseline_y/pango.SCALE
        #return (baseline_delta)
    #baseline = property(_get_baseline)

    def _get_baseline(self):
        # retrieves first line of text block
        first_line = self.layout.get_line(0)
        # get the logical extents rectangle of first line
        first_line_extent = first_line.get_extents()[1]
        # get the descent value, in order to calculate baseline position
        first_line_descent = pango.DESCENT(first_line.get_extents()[1])
        # gets the baseline offset from the top of thext block
        baseline_delta = (first_line_extent[3]-first_line_descent)/pango.SCALE
        return (baseline_delta)
    baseline = property(_get_baseline)

    
    def _get_metrics(self):
        w,h = self.layout.get_pixel_size()
        return (w,h)
    metrics = property(_get_metrics)

    # this function is quite computational expensive 
    # there should be a way to make it faster, by not creating a new context each time it's called
    def _get_path(self):
        if not self._pang_ctx:
            self._pre_render()
            
        # here we create a new cairo.Context in order to hold the pathdata
        tempCairoContext = cairo.Context(RecordingSurfaceA8(1, 1))
        tempCairoContext.move_to(self.x,self.y-self.baseline)
        # in here we create a pangoCairoContext in order to display layout on it
        tempPangoCairoContext = pangocairo.CairoContext(tempCairoContext)
        
        # supposedly showlayout should work, but it fills the path instead,
        # therefore we use layout_path instead to render the layout to pangoCairoContext
        #tempPangoCairoContext.show_layout(self.layout) 
        tempPangoCairoContext.layout_path(self.layout)
        #here we extract the path from the temporal cairo.Context we used to draw on the previous step
        pathdata = tempCairoContext.copy_path()
        
        #print tempCairoContext
        
        # creates a BezierPath instance for storing new shoebot path
        p = BezierPath(self._bot)
       
        # parsing of cairo path to build a shoebot path
        for item in pathdata:
            cmd = item[0]
            args = item[1]
            if cmd == PATH_MOVE_TO:
                p.moveto(*args)
            elif cmd == PATH_LINE_TO:
                p.lineto(*args)
            elif cmd == PATH_CURVE_TO:
                p.curveto(*args)
            elif cmd == PATH_CLOSE_PATH:
                p.closepath()
        # cairo function for freeing path memory
        return p
    path = property(_get_path)

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        w,h = self.layout.get_pixel_size()
        x = (self.x+w/2)
        y = (self.y+h/2)
        return (x,y)
    center = property(_get_center)

    def copy(self):
        new = self.__class__(self._bot, self.text)
        _copy_attrs(self, new,
            ('x', 'y', 'width', 'height', '_transform', '_transformmode',
            '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight'))
        return new

