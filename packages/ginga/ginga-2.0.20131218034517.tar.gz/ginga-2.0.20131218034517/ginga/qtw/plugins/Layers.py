#
# Layers.py -- Layers plugin for fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from QtHelp import QtGui, QtCore
import QtHelp

import numpy
import re, os
import time

from ginga.gtkw import GtkHelp
from ginga.misc import Bunch
from ginga import BaseImage, LayerImage
from ginga import GingaPlugin
from ginga.qtw import ImageViewCanvasQt

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
        vpaned = QtGui.QSplitter()
        vpaned.setOrientation(QtCore.Qt.Vertical)
        
        sfi = ImageViewCanvasQt.ImageViewCanvas(logger=None)
        sfi.enable_autozoom('on')
        sfi.enable_autocuts('on')
        #sfi.set_zoom_algorithm('rate')
        sfi.enable_draw(False)
        sfi.set_bg(0.4, 0.4, 0.4)
        self.layerimage = sfi

        bd = sfi.get_bindings()
        bd.enable_flip(True)
        bd.enable_rotate(True)
        bd.enable_pan(True)
        bd.enable_zoom(True)
        bd.enable_cuts(True)

        iw = sfi.get_widget()
        self.w.layerimage = iw
        sp = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                               QtGui.QSizePolicy.MinimumExpanding)
        iw.setSizePolicy(sp)
        width, height = 200, 200
        iw.resize(width, height)
        vpaned.addWidget(iw)

        sw = QtGui.QScrollArea()

        twidget = QtHelp.VBox()
        sp = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                               QtGui.QSizePolicy.Fixed)
        twidget.setSizePolicy(sp)
        vbox1 = twidget.layout()
        vbox1.setContentsMargins(4, 4, 4, 4)
        vbox1.setSpacing(2)
        sw.setWidgetResizable(True)
        sw.setWidget(twidget)

        fr = QtHelp.Frame("Compositing")

        captions = (("Combine", 'combobox'),
                    ("New Image", 'button'),
                    ("Layer Name", 'entry'),
                    ("Layer Alpha", 'hscale'),
                    ("Insert Image", 'button'),
                    ("Store Mask", 'button'),
                    ("Insert Color", 'button', "Choose Color", 'button'),
                    ("Bit Plane", 'entry'),
                    ("Decompose", 'button', "Std Greyscale", 'button'),
                    )
        w, b = QtHelp.build_info(captions)
        self.w.update(b)

        fr.layout().addWidget(w, stretch=1, alignment=QtCore.Qt.AlignLeft)
        vbox1.addWidget(fr, stretch=0, alignment=QtCore.Qt.AlignTop)

        combobox = b.combine
        index = 0
        for name in ('Alpha', 'RGB'):
            combobox.addItem(name)
            index += 1
        combobox.setCurrentIndex(0)
        combobox.activated.connect(self.set_combine_cb)

        b.new_image.clicked.connect(lambda w: self.new_cb())
        b.insert_image.clicked.connect(lambda w: self.insert_cb())
        b.insert_color.clicked.connect(lambda w: self.insert_colored_cb2())
        b.choose_color.clicked.connect(lambda w: self.choose_color_cb())
        b.store_mask.clicked.connect(lambda w: self.store_mask_cb())
        b.decompose.clicked.connect(lambda w: self.decompose_cb())
        b.std_greyscale.clicked.connect(lambda w: self.std_greyscale_cb())

        scale = b.layer_alpha
        lower, upper = 0.0, 1.0
        scale.setMinimum(lower)
        scale.setMaximum(upper)
        scale.setValue(1.0)
        scale.setTracking(True)

        fr = QtHelp.Frame("Layers")
        
        self.w.scales = QtHelp.VBox()
        fr.layout().addWidget(self.w.scales, stretch=1,
                              alignment=QtCore.Qt.AlignLeft)
        vbox1.pack_start(fr, padding=4, fill=True, expand=False)

        btns = QtGui.HBox()
        btns.setSpacing(3)

        btn = QtGui.QPushButton("Close")
        btn.clicked.connect(self.close)
        btns.addWidget(btn)

        vbox1.addWidget(hbox, stretch=0, alignment=QtCore.Qt.AlignLeft)

        sw.setWidgetResizable(True)
        sw.setWidget(twidget)

        vpaned.pack2(sw, resize=True, shrink=True)
        vpaned.set_position(280)
        vpaned.show_all()
        
        container.addWidget(vpaned, stretch=1)

    def _config_scale(self, idx):
        adj = QtGui.QScrollBar(QtCore.Qt.Horizontal)
        lower, upper = 0.0, 1.0
        adj.setRange(lower, upper)
        adj.setSingleStep(upper/100.0)
        adj.setPageStep(upper/10.0)
        adj.setValue(0.0)
        scale.set_digits(3)
        scale.set_draw_value(True)
        scale.set_value_pos(gtk.POS_BOTTOM)
        scale.set_update_policy(gtk.UPDATE_DISCONTINUOUS)
        scale.add_mark(lower, gtk.POS_BOTTOM, "%.1f" % lower)
        scale.add_mark(upper, gtk.POS_BOTTOM, "%.1f" % upper)
        scale.sconnect('value-changed', self.set_opacity_cb, idx)
        scale.set_size_request(200, -1)
        return scale

    def _gui_config_layers(self):
        # remove all old scales
        for child in self.w.scales.get_children():
            QtHelp.removeWidget(self.w.scales, child)

        # construct a new vbox of sliders
        vbox = QtHelp.VBox()
        num_layers = self.limage.numLayers()
        for i in xrange(num_layers):
            layer = self.limage.getLayer(i)
            hbox = QtHelp.HBox()
            scale = self._config_scale(i)
            scale.setValue(layer.alpha)
            lbl = QtGui.QLabel("%-12.12s" % (layer.name))
            hbox.layout().addWidget(lbl, stretch=0)
            hbox.layout().addWidget(scale, stretch=1)
            vbox.layout().addWidget(hbox, stretch=0)

        self.w.scales.layout().addWidget(vbox, stretch=1)
        
    def set_combine_cb(self, w):
        if self.limage == None:
            self.new_cb()
        idx = w.get_active()
        combine = ['alpha', 'rgb']
        name = combine[idx]
        self.limage.setComposeType(name)
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
        #self.limage.add_callback('modified', )
        self._gui_config_layers()
        self.limage.set(name=name)

        # Reflect transforms, colormap, etc.
        self.fitsimage.copy_attributes(self.layerimage,
                                       ['transforms', 'cutlevels',
                                        'rgbmap', 'rotation'],
                                       redraw=False)

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
            print "getting metadata"
            metadata = image.get_metadata()
            print "updating metadata"
            self.limage.update_metadata(metadata)
        print "inserting layer"
        self.limage.insertLayer(0, image, name=attrs.name,
                                alpha=attrs.alpha)
        self._gui_config_layers()

        #self.fitsimage.set_image(self.limage)
        name = self.limage.get('name')
        self.layerimage.set_image(self.limage)
        self.fv.add_image(name, self.limage)
        print "insert done"
        
    ## def insert_colored_cb(self):
    ##     image = self.fitsimage.get_image()
    ##     imageclass = image.__class__
    ##     if self.limage == None:
    ##         self.new_cb(imageclass=imageclass)

    ##     klass = self.get_imageclass(imageclass)
    ##     cimage = klass(logger=self.logger)
    ##     color = self.w.clrbtn.get_color()
    ##     cimage.insertLayer(0, image, alpha=color.red_float,
    ##                        name="Red")
    ##     cimage.insertLayer(1, image, alpha=color.green_float,
    ##                        name="Green")
    ##     cimage.insertLayer(2, image, alpha=color.blue_float,
    ##                        name="Blue")
    ##     cimage.setComposeType('rgb')
        
    ##     attrs = self._get_layer_attributes()
    ##     self.limage.insertLayer(0, cimage, name=attrs.name,
    ##                             alpha=attrs.alpha)
    ##     self._gui_config_layers()

    ##     self.layerimage.set_image(self.limage)
    ##     name = self.limage.get('name')
    ##     self.fv.add_image(name, self.limage)
        
    def store_mask_cb(self):
        image = self.fitsimage.get_image()
        self.mask_image = image
        self.mask_data  = image.get_data().astype('uint')
        self.layerimage.onscreen_message("Mask stored", delay=1.0)
        
    def insert_colored_cb2(self):
        imageclass = self.mask_image.__class__
        if self.limage == None:
            self.new_cb(imageclass=imageclass)

        klass = self.get_imageclass(imageclass)
        cimage = klass(logger=self.logger)

        bitplane = self.w.bit_plane.get_text().strip()
        bitmask = 0x1 << int(bitplane)

        # Get the real data values array
        # TODO: cannot assume data is in bottom layer
        idx = self.limage.numLayers() - 1
        layer = self.limage.getLayer(idx)
        klass = self.get_imageclass(layer.image.__class__)
        values = layer.image.get_data()

        # Prepare data array for colored (unmasked) values
        # TODO: I think this can be made more efficient
        data = numpy.zeros(values.shape)
        data[numpy.nonzero(self.mask_data & bitmask)] = 1.0
        #data *= values
        data = data * values
        nimage = klass(data_np=data, logger=self.logger)

        # Prepare a color image
        color = self.w.clrbtn.get_color()
        cimage.insertLayer(0, nimage, alpha=color.red_float,
                           name="Red", compose=False)
        cimage.insertLayer(1, nimage, alpha=color.green_float,
                           name="Green", compose=False)
        cimage.insertLayer(2, nimage, alpha=color.blue_float,
                           name="Blue", compose=False)
        cimage.setComposeType('rgb')

        attrs = self._get_layer_attributes()
        self.limage.insertLayer(0, cimage, alpha=attrs.alpha,
                                name=attrs.name)
        self._gui_config_layers()

        self.layerimage.set_image(self.limage)
        name = self.limage.get('name')
        self.fv.add_image(name, self.limage)
        
    def decompose_cb(self):
        cimage = self.fitsimage.get_image()
        if self.limage == None:
            self.new_cb(imageclass=cimage.__class__)
        self.limage.rgb_decompose(cimage)
        self._gui_config_layers()

        self.layerimage.set_image(self.limage)
        name = self.limage.get('name')
        self.fv.add_image(name, self.limage)
        
    def std_greyscale_cb(self):
        # standard color to greyscale conversion RGB alphas:
        std_cvt = (0.292, 0.594, 0.114)
        self.limage.setAlphas(std_cvt)

        self.layerimage.set_image(self.limage)
        self.fitsimage.set_image(self.limage)
        
    ## def save_image_cb(self):
    ##     image = self.fitsimage.get_image()
    ##     path = image.get('path', None)
    ##     newname = self.w.save_as.get_text().strip()
    ##     if path != None:
    ##         path = os.join(path, newname)
    ##     else:
    ##         path = newname
    ##     image.save_file_as(path)
        
    def set_opacity_cb(self, w, idx):
        print "set opacity %d" % idx
        val = w.get_value()
        self.limage.setAlpha(idx, val)

        self.layerimage.redraw(whence=0)
        self.fitsimage.redraw(whence=0)
        
    def close(self):
        chname = self.fv.get_channelName(self.fitsimage)
        self.fv.stop_operation_channel(chname, str(self))
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
