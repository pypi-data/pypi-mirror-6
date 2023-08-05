#
# Layers.py -- Layers plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import numpy
import re, os
import time

from ginga.misc import Widgets, CanvasTypes, Bunch
from ginga import BaseImage, LayerImage
from ginga import GingaPlugin

class Layers(GingaPlugin.LocalPlugin):

    def __init__(self, fv, fitsimage):
        # superclass defines some variables for us, like logger
        super(Layers, self).__init__(fv, fitsimage)

        self.lidx = 0
        self.limage = None
        self.naxispath = []
        self.compositing = 'alpha'

    def build_gui(self, container):
        # Splitter is just to provide a way to size the graph
        # to a reasonable size
        vpaned = Widgets.Splitter(orientation='vertical')
        
        width, height = 200, 200
        sfi = CanvasTypes.ImageViewCanvas(logger=self.logger)
        sfi.set_desired_size(width, height)
        sfi.enable_autozoom('on')
        sfi.enable_autocuts('on')
        #sfi.set_zoom_algorithm('rate')
        sfi.enable_draw(False)
        sfi.set_bg(0.4, 0.4, 0.4)
        self.layerimage = sfi

        bd = sfi.get_bindings()
        bd.enable_all(True)

        iw = sfi.get_widget()
        self.w.layerimage = Widgets.wrap(iw)
        vpaned.add_widget(self.w.layerimage)

        sw = Widgets.ScrollArea()

        vbox1 = Widgets.VBox()
        vbox1.set_border_width(4)
        vbox1.set_spacing(2)
        sw.set_widget(vbox1)

        fr = Widgets.Frame("Compositing")

        captions = (("Combine:", 'label', "Combine", 'combobox'),
                    ("New Image", 'button'),
                    ("Layer Name:", 'label', "Layer Name", 'entry'),
                    ("Layer Alpha:", 'label', "Layer Alpha", 'hscale'),
                    ("Insert Image", 'button'),
                    #("Insert Color", 'button', "Choose Color", 'button'),
                    ("Decompose", 'button', "Std Greyscale", 'button'),
                    )
        w, b = Widgets.build_info(captions)
        self.w.update(b)

        fr.set_widget(w)
        vbox1.add_widget(fr, stretch=0)

        combobox = b.combine
        index = 0
        for name in ('Alpha', 'RGB'):
            combobox.append_text(name)
            index += 1
        combobox.set_index(0)
        combobox.add_callback('activated', self.set_combine_cb)

        b.new_image.add_callback('activated', lambda w: self.new_cb())
        b.insert_image.add_callback('activated', lambda w: self.insert_cb())
        #b.insert_color.add_callback('activated', lambda w: self.insert_colored_cb())
        #b.choose_color.add_callback('activated', lambda w: self.choose_color_cb())
        b.decompose.add_callback('activated', lambda w: self.decompose_cb())
        b.std_greyscale.add_callback('activated', lambda w: self.std_greyscale_cb())

        scale = b.layer_alpha
        lower, upper = 0.0, 1.0
        scale.set_limits(lower, upper, incr_value=0.01)
        scale.set_value(1.0)
        #scale.setTracking(True)

        fr = Widgets.Frame("Layers")
        self.w.scales = fr
        vbox1.add_widget(fr, stretch=0)

        btns = Widgets.HBox()
        btns.set_border_width(4)
        btns.set_spacing(4)

        btn = Widgets.Button("Compose")
        btn.add_callback('activated', lambda w: self.compose_cb())
        btns.add_widget(btn)
        btn = Widgets.Button("Add to channel")
        btn.add_callback('activated', lambda w: self.add_to_channel_cb())
        btns.add_widget(btn)
        btns.add_widget(Widgets.Label(''), stretch=1)

        vbox1.add_widget(btns, stretch=0)

        btns = Widgets.HBox()
        btns.set_border_width(4)
        btns.set_spacing(4)

        btn = Widgets.Button("Close")
        btn.add_callback('activated', lambda w: self.close())
        btns.add_widget(btn)
        btns.add_widget(Widgets.Label(''), stretch=1)

        vbox1.add_widget(btns, stretch=0)

        vpaned.add_widget(sw)
        
        container.add_widget(vpaned, stretch=1)

    def _gui_config_layers(self):
        # remove all old scales
        self.w.scales.remove_all()

        # construct a new vbox of alpha controls
        captions = []
        num_layers = self.limage.num_layers()
        for i in xrange(num_layers):
            layer = self.limage.get_layer(i)
            captions.append((layer.name+':', 'label', 'layer_%d' % i, 'hscale'))

        w, b = Widgets.build_info(captions)
        self.w.update(b)
        for i in xrange(num_layers):
            layer = self.limage.get_layer(i)
            adj = b['layer_%d' % (i)]
            lower, upper = 0, 100
            adj.set_limits(lower, upper, incr_value=1)
            #adj.set_decimals(2)
            adj.set_value(int(layer.alpha * 100.0))
            #adj.set_tracking(True)
            adj.add_callback('value-changed', self.set_opacity_cb, i)

        self.logger.debug("adding layer alpha controls")
        self.w.scales.set_widget(w)
        
    def set_combine_cb(self, w, idx):
        if self.limage == None:
            self.new_cb()
        idx = w.get_index()
        combine = ['alpha', 'rgb']
        name = combine[idx]
        self.limage.set_compose_type(name)
        #self.fitsimage.redraw(whence=0)

    def get_imageclass(self, imageclass):
        # create a dynamic image class that has the LayerImage mixin
        class klass(imageclass, LayerImage.LayerImage):
            def __init__(self, *args, **kwdargs):
                imageclass.__init__(self, *args, **kwdargs)
                LayerImage.LayerImage.__init__(self)
        return klass
    
    def new_cb(self, imageclass=BaseImage.BaseImage):
        klass = self.get_imageclass(imageclass)
        name = str(time.time())
        self.limage = klass(logger=self.logger)
        self.limage.add_callback('modified', self.layerimage_modified_cb)
        self._gui_config_layers()
        self.limage.set(name=name)

        # Reflect transforms, colormap, etc.
        self.fitsimage.copy_attributes(self.layerimage,
                                       ['transforms', 'cutlevels',
                                        'rgbmap', 'rotation'],
                                       redraw=False)
        self.layerimage.set_image(self.limage)

    def _get_layer_attributes(self):
        # Get layer name
        s = self.w.layer_name.get_text().strip()
        if len(s) > 0:
            name = s
        else:
            name = None

        # Get alpha
        alpha = self.w.layer_alpha.get_value()
        bnch = Bunch.Bunch(name=name, alpha=alpha)
        return bnch

    def insert_cb(self):
        image = self.fitsimage.get_image()
        attrs = self._get_layer_attributes()
        if self.limage == None:
            self.new_cb(imageclass=image.__class__)
            metadata = image.get_metadata()
            self.limage.update_metadata(metadata)
        self.limage.insert_layer(0, image, name=attrs.name,
                                alpha=attrs.alpha)
        self._gui_config_layers()
        
    def insert_colored_cb(self):
        image = self.fitsimage.get_image()
        imageclass = image.__class__
        if self.limage == None:
            self.new_cb(imageclass=imageclass)

        klass = self.get_imageclass(imageclass)
        cimage = klass(logger=self.logger)
        color = self.w.clrbtn.get_color()
        cimage.insert_layer(0, image, alpha=color.red_float,
                           name="Red")
        cimage.insert_layer(1, image, alpha=color.green_float,
                           name="Green")
        cimage.insert_layer(2, image, alpha=color.blue_float,
                           name="Blue")
        cimage.set_compose_type('rgb')
        
        attrs = self._get_layer_attributes()
        self.limage.insert_layer(0, cimage, name=attrs.name,
                                alpha=attrs.alpha)
        self._gui_config_layers()

        self.layerimage.set_image(self.limage)
        name = self.limage.get('name')
        self.fv.add_image(name, self.limage)
        
    def decompose_cb(self):
        cimage = self.fitsimage.get_image()
        self.new_cb(imageclass=cimage.__class__)
        self.limage.rgb_decompose(cimage)
        self._gui_config_layers()
        
    def std_greyscale_cb(self):
        # standard color to greyscale conversion RGB alphas:
        std_cvt = (0.292, 0.594, 0.114)
        self.limage.set_alphas(std_cvt)
        
    ## def save_image_cb(self):
    ##     image = self.fitsimage.get_image()
    ##     path = image.get('path', None)
    ##     newname = self.w.save_as.get_text().strip()
    ##     if path != None:
    ##         path = os.join(path, newname)
    ##     else:
    ##         path = newname
    ##     image.save_file_as(path)
        
    def set_opacity_cb(self, w, val, idx):
        #val = w.get_value()
        alpha = val / 100.0
        self.limage.set_alpha(idx, alpha)
        
    def _alphas_controls_to_layers(self):
        print "updating layers in %s from controls" % self.limage
        num_layers = self.limage.num_layers()
        vals = []
        for i in xrange(num_layers):
            alpha = self.w['layer_%d' % i].get_value() / 100.0
            vals.append(alpha)
            print "%d: alpha=%f" % (i, alpha)
            i += 1
        self.limage.set_alphas(vals)

    def _alphas_layers_to_controls(self):
        print "updating controls from %s" % self.limage
        num_layers = self.limage.num_layers()
        for i in xrange(num_layers):
            layer = self.limage.get_layer(i)
            print "%d: alpha=%f" % (i, layer.alpha)
            ctrlname = 'layer_%d' % (i)
            if self.w.has_key(ctrlname):
                self.w[ctrlname].set_value(layer.alpha * 100.0)
            i += 1

    def layerimage_modified_cb(self, image, *args):
        print "image %s modified" % image
        try:
            self._alphas_layers_to_controls()
        except:
            pass
        #self.layerimage.redraw(whence=0)
        
    def compose_cb(self):
        self._alphas_controls_to_layers()
        #self.layerimage.redraw(whence=0)

    def add_to_channel_cb(self):
        image = self.limage.copy()
        name = str(time.time())
        image.set(name=name)
        self.fv.add_image(name, image)
        
    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_local_plugin(chname, str(self))
        return True
        
    def start(self):
        self.resume()

    def pause(self):
        pass
        
    def resume(self):
        self.redo()
        
    def stop(self):
        self.fv.showStatus("")
        
        
    def redo(self):
        pass
    
    def __str__(self):
        return 'layers'
    
#END
