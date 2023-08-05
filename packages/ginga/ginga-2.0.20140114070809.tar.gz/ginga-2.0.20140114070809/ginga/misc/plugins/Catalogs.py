#
# Catalogs.py -- Catalogs plugin for Ginga fits viewer
# 
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
from ginga.misc import Widgets, CanvasTypes
from ginga.gtkw import ColorBar
from ginga.misc import Bunch, Future
from ginga.misc.plugins import CatalogsBase

import gobject
import gtk

class Catalogs(CatalogsBase.CatalogsBase):

    def __init__(self, fv, fitsimage):
        super(Catalogs, self).__init__(fv, fitsimage)

    def build_gui(self, container, future=None):
        vbox1 = Widgets.VBox()

        self.msgFont = self.fv.getFont('sansFont', 12)
        tw = Widgets.TextArea(wrap=True, editable=False)
        tw.set_font(self.msgFont)
        self.tw = tw

        fr = Widgets.Frame("Instructions")
        fr.add(tw)
        vbox1.add_widget(fr, padding=4, fill=True, expand=False)
        
        nb = Widgets.TabWidget(tabpos='bottom')
        vbox1.add_widget(nb, stretch=1)

        vbox0 = Widgets.VBox()
        hbox = Widgets.HBox()
        hbox.set_spacing(4)

        vbox = Widgets.VBox()
        fr = Widgets.Frame("Image Server")
        fr.add(vbox)

        captions = (('Server:', 'label'),
                    ('Server', 'combobox'),
                    ('Use DSS channel', 'checkbutton'),
                    ('Get Image', 'button'))
        w, self.w = Widgets.build_info(captions)
        self.w.nb = nb
        self.w.get_image.add_callback('activated', lambda w: self.getimage_cb())
        self.w.use_dss_channel.set_state(self.use_dss_channel)
        self.w.use_dss_channel.add_callback('activated', self.use_dss_channel_cb)

        vbox.add_widget(w, stretch=0)

        self.w.img_params = Widgets.VBox()
        vbox.add_widget(self.w.img_params, stretch=0)
        
        combobox = self.w.server
        index = 0
        self.image_server_options = self.fv.imgsrv.getServerNames(kind='image')
        for name in self.image_server_options:
            combobox.append_text(name)
            index += 1
        index = 0
        combobox.set_index(index)
        combobox.add_callback('value-changed', self.setup_params_image)
        if len(self.image_server_options) > 0:
            self.setup_params_image(combobox, redo=False)

        hbox.add_widget(fr, stretch=1)

        vbox = Widgets.VBox()
        fr = Widgets.Frame("Catalog Server")
        fr.add(vbox)

        captions = (('Server:', 'label'),
                    ('Server', 'combobox'),
                    ('Limit stars to area', 'checkbutton'),
                    ('Search', 'button'))
        w, self.w2 = Widgets.build_info(captions)
        self.w2.search.add_callback('activated', lambda w: self.getcatalog_cb())
        self.w2.limit_stars_to_area.set_state(self.limit_stars_to_area)
        self.w2.limit_stars_to_area.add_callback('activated', self.limit_area_cb)

        vbox.add_widget(w, stretch=0)

        self.w2.cat_params = Widgets.VBox()
        vbox.add_widget(self.w2.cat_params, stretch=0)
        
        combobox = self.w2.server
        index = 0
        self.catalog_server_options = self.fv.imgsrv.getServerNames(kind='catalog')
        for name in self.catalog_server_options:
            combobox.append_text(name)
            index += 1
        index = 0
        combobox.set_index(index)
        combobox.add_callback('value-changed', self.setup_params_catalog)
        if len(self.catalog_server_options) > 0:
            self.setup_params_catalog(combobox, redo=False)

        hbox.add_widget(fr, stretch=1)
        vbox0.add_widget(hbox, stretch=1)

        btns = Widgets.HBox()
        btns.set_spacing(4)

        btn = Widgets.Button("Set parameters from entire image")
        btn.add_callback('activated', lambda w: self.setfromimage())
        btns.add_widget(btn)
        vbox0.add_widget(btns)

        self.w.params = vbox0
        nb.add_widget(vbox0, title="Params")

        vbox = Widgets.VBox()
        self.table = CatalogListing(self.logger, vbox)

        hbox = Widgets.HBox()
        scale = Widgets.Scrollbar(orientation='horizontal')
        scale.set_limits(0, 0, incr_value=1)
        scale.set_tooltip("Choose subset of stars plotted")
        scale.set_tracking(True)
        self.w.plotgrp = scale
        scale.add_callback('value-changed', self.plot_pct_cb)
        hbox.add_widget(scale, stretch=1)

        sb = Widgets.SpinBox(dtype=int)
        sb.set_limits(10, self.plot_max, incr_value=10)
        sb.set_value(self.plot_limit)
        self.w.plotnum = sb
        sb.set_tooltip("Adjust size of subset of stars plotted")
        sb.add_callback('value-changed', self.plot_limit_cb)
        hbox.add_widget(sb, stretch=0)
        vbox.add_widget(hbox, stretch=0)

        #vbox1.add_widget(vbox, stretch=1)
        self.w.listing = vbox
        nb.add_widget(vbox, title="Listing")

        btns = Widgets.HBox()
        btns.set_spacing(4)
        self.w.buttons = btns

        btn = Widgets.Button("Close")
        btn.add_callback('activated', lambda w: self.close())
        btns.add_widget(btn)
        btns.add_widget(Widgets.Label(''), stretch=1)

        if future:
            btn = Widgets.Button('Ok')
            btn.add_callback('activated', lambda w: self.ok())
            btns.add_widget(btn)
            btn = Widgets.Button('Cancel')
            btn.add_callback('activated', lambda w: self.cancel())
            btns.add_widget(btn)
        vbox1.add_widget(btns, stretch=0)

        container.add_widget(vbox1, stretch=1)
        

    def limit_area_cb(self, w):
        self.limit_stars_to_area = w.get_state()
        return True

    def use_dss_channel_cb(self, w):
        self.use_dss_channel = w.get_state()
        return True

    def plot_pct_cb(self, w, val):
        #val = w.get_value()
        self.plot_start = int(val)
        self.replot_stars()
        return True

    def _update_plotscroll(self):
        num_stars = len(self.starlist)
        if num_stars > 0:
            adj = self.w.plotgrp
            #page_size = self.plot_limit
            self.plot_start = min(self.plot_start, num_stars-1)
            adj.set_limits(0, num_stars, incr_value=1)
            adj.set_value(self.plot_start)

        self.replot_stars()

    def plot_limit_cb(self, w, val):
        #val = w.get_value()
        self.plot_limit = int(val)
        self._update_plotscroll()
        return True

    def set_message(self, msg):
        self.tw.set_text(msg)
        #self.tw.set_font(self.msgFont)
        
    def _raise_tab(self, w):
        num = self.w.nb.index_of(w)
        self.w.nb.set_index(num)
        
    def _get_cbidx(self, w):
        return w.get_index()
        
    def _setup_params(self, obj, container):
        params = obj.getParams()
        captions = []
        paramList = sorted(params.values(), key=lambda b: b.order)
        for bnch in paramList:
            text = bnch.name
            if bnch.has_key('label'):
                text = bnch.label
            #captions.append((text, 'entry'))
            captions.append((text+':', 'label', bnch.name, 'entry'))

        # TODO: put RA/DEC first, and other stuff not in random orders
        w, b = Widgets.build_info(captions)

        # remove old widgets
        container.remove_all()

        # add new widgets
        container.add_widget(w, stretch=0)
        return b

    def setup_params_image(self, combobox, redo=True):
        index = combobox.get_index()
        key = self.image_server_options[index]

        # Get the parameter list and adjust the widget
        obj = self.fv.imgsrv.getImageServer(key)
        b = self._setup_params(obj, self.w.img_params)
        self.image_server_params = b

        if redo:
            self.redo()

    def setup_params_catalog(self, combobox, redo=True):
        index = combobox.get_index()
        key = self.catalog_server_options[index]

        # Get the parameter list and adjust the widget
        obj = self.fv.imgsrv.getCatalogServer(key)
        b = self._setup_params(obj, self.w2.cat_params)
        self.catalog_server_params = b

        if redo:
            self.redo()
            
    def instructions(self):
        self.set_message("""TBD.""")

    def _update_widgets(self, d):
        for bnch in (self.image_server_params,
                     self.catalog_server_params):
            if bnch != None:
                for key in bnch.keys():
                    if d.has_key(key):
                        bnch[key].set_text(str(d[key]))

    def get_params(self, bnch):
        params = {}
        for key in bnch.keys():
            params[key] = bnch[key].get_text()
        return params
        
    def __str__(self):
        return 'catalogs'
    

class CatalogListing(CatalogsBase.CatalogListingBase):
    
    def _build_gui(self, container):
        self.mframe = container

        vbox = Widgets.VBox()

        sw = Widgets.ScrollArea()
        self.sw = sw

        vbox.add_widget(sw, stretch=1)

        self.cbar = ColorBar.ColorBar(self.logger)
        self.cbar.set_cmap(self.cmap)
        self.cbar.set_imap(self.imap)

        vbox.add_widget(self.cbar, stretch=0)

        btns = Widgets.HBox()
        btns.set_spacing(4)
        btns.set_border_width(4)

        combobox = Widgets.ComboBox()
        options = []
        index = 0
        for name in self.cmap_names:
            options.append(name)
            combobox.append_text(name)
            index += 1
        cmap_name = self.magcmap
        try:
            index = self.cmap_names.index(cmap_name)
        except Exception:
            index = self.cmap_names.index('ramp')
        combobox.set_index(index)
        combobox.add_callback('activated', self.set_cmap_cb)
        self.btn['cmap'] = combobox
        btns.add_widget(combobox)

        combobox = Widgets.ComboBox()
        options = []
        index = 0
        for name in self.imap_names:
            options.append(name)
            combobox.append_text(name)
            index += 1
        imap_name = self.magimap
        try:
            index = self.imap_names.index(imap_name)
        except Exception:
            index = self.imap_names.index('ramp')
        combobox.set_index(index)
        combobox.add_callback('activated', self.set_imap_cb)
        self.btn['imap'] = combobox
        btns.add_widget(combobox)

        vbox.add_widget(btns, stretch=0)

        btns = Widgets.HBox()
        btns.set_spacing(4)
        btns.set_border_width(4)

        for name in ('Plot', 'Clear', #'Close'
                     ):
            btn = Widgets.Button(name)
            btns.add_widget(btn)
            self.btn[name.lower()] = btn
            
        combobox = Widgets.ComboBox()
        options = []
        index = 0
        for name in ['Mag']:
            options.append(name)
            combobox.append_text(name)
            index += 1
        combobox.set_index(0)
        combobox.add_callback('activated', self.set_field_cb)
        self.btn['field'] = combobox
        btns.add_widget(combobox)

        self.btn.plot.add_callback('activated', lambda w: self.replot_stars())
        self.btn.clear.add_callback('activated', lambda w: self.clear())
        #self.btn.close.add_callback('activated', lambda w: self.close())

        vbox.add_widget(btns, stretch=0)
        
        # create the table
        info = Bunch.Bunch(columns=self.columns, color='Mag')
        self.build_table(info)

        self.mframe.add_widget(vbox, stretch=1)

    def build_table(self, info):
        columns = info.columns
        self.columns = columns
        
        # remove old treeviews, if any
        self.sw.remove_all()

        # create the TreeView
        treeview = gtk.TreeView()
        self.treeview = treeview
        
        self.cell_sort_funcs = []
        for kwd, key in columns:
            self.cell_sort_funcs.append(self._mksrtfnN(key))

        # Set up the field selector
        fidx = 0
        combobox = self.btn['field']
        try:
            combobox.clear()
        except Exception, e:
            self.logger.error("Error clearing field selector: %s" % (
                str(e)))

        # create the TreeViewColumns to display the data
        tvcolumn = [None] * len(columns)
        for n in range(0, len(columns)):
            cell = gtk.CellRendererText()
            cell.set_padding(2, 0)
            header, kwd = columns[n]
            tvc = gtk.TreeViewColumn(header, cell)
            tvc.set_spacing(4)
            tvc.set_resizable(True)
            tvc.connect('clicked', self.sort_cb, n)
            tvc.set_clickable(True)
            tvcolumn[n] = tvc
            fn_data = self._mkcolfnN(kwd)
            tvcolumn[n].set_cell_data_func(cell, fn_data)
            treeview.append_column(tvcolumn[n])

            combobox.insert_text(n, header)
            if header == info.color:
                fidx = n

        combobox.set_active(fidx)
        
        self.sw.add(treeview)
        self.treeview.connect('cursor-changed', self.select_star_cb)
        self.sw.show_all()

        fieldname = self.columns[fidx][1]
        self.mag_field = fieldname

    def _mkcolfnN(self, kwd):
        def fn(*args):
            column, cell, model, iter = args[:4]
            bnch = model.get_value(iter, 0)
            cell.set_property('text', bnch[kwd])
        return fn

    def sort_cb(self, column, idx):
        treeview = column.get_tree_view()
        model = treeview.get_model()
        model.set_sort_column_id(idx, gtk.SORT_ASCENDING)
        fn = self.cell_sort_funcs[idx]
        model.set_sort_func(idx, fn)
        self.replot_stars()
        return True

    def _mksrtfnN(self, key):
        def fn(*args):
            model, iter1, iter2 = args[:3]
            bnch1 = model.get_value(iter1, 0)
            bnch2 = model.get_value(iter2, 0)
            val1, val2 = bnch1[key], bnch2[key]
            if isinstance(val1, str):
                val1 = val1.lower()
                val2 = val2.lower()
            res = cmp(val1, val2)
            return res
        return fn

    def show_table(self, catalog, info, starlist):
        self.starlist = starlist
        self.catalog = catalog
        # info is ignored, for now
        #self.info = info
        self.selected = []

        # rebuild the table
        self.build_table(info)
        
        # Update the starlist info
        listmodel = gtk.ListStore(object)
        for star in starlist:
            # TODO: find mag range
            listmodel.append([star])

        self.treeview.set_model(listmodel)

    def _get_star_path(self, star):
        model = self.treeview.get_model()
        # find path containing this star in the treeview
        # TODO: is there a more efficient way to do this?
        for path in xrange(len(self.starlist)):
            iter = model.get_iter(path)
            cstar = model.get_value(iter, 0)
            if cstar == star:
                return path
        return None

    def get_subset_from_starlist(self, fromidx, toidx):
        model = self.treeview.get_model()
        res = []
        for idx in xrange(fromidx, toidx):
            iter = model.get_iter(idx)
            star = model.get_value(iter, 0)
            res.append(star)
        return res

    def _select_tv(self, star, fromtable=False):
        treeselection = self.treeview.get_selection()
        star_idx = self._get_star_path(star)
        if star_idx == None:
            return
        treeselection.select_path(star_idx)
        if not fromtable:
            # If the user did not select the star from the table, scroll
            # the table so they can see the selection
            self.treeview.scroll_to_cell(star_idx, use_align=True,
                                         row_align=0.5)

    def _unselect_tv(self, star, fromtable=False):
        treeselection = self.treeview.get_selection()
        star_idx = self._get_star_path(star)
        if star_idx == None:
            return
        treeselection.unselect_path(star_idx)

    def select_star_cb(self, treeview):
        """This method is called when the user selects a star from the table.
        """
        path, column = treeview.get_cursor()
        model = treeview.get_model()
        iter = model.get_iter(path)
        star = model.get_value(iter, 0)
        self.logger.debug("selected star: %s" % (str(star)))
        self.mark_selection(star, fromtable=True)
        return True
    
    def set_cmap_cb(self, w):
        index = w.get_active()
        name = self.cmap_names[index]
        self.set_cmap_byname(name)

    def set_imap_cb(self, w):
        index = w.get_active()
        name = self.imap_names[index]
        self.set_imap_byname(name)

    def set_field_cb(self, w):
        index = w.get_active()
        fieldname = self.columns[index][1]
        self.set_field(fieldname)


# END
