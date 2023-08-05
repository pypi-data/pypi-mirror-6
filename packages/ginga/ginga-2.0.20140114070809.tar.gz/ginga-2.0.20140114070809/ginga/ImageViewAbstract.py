
from ginga import ImageView, Mixins, Bindings


class ImageViewXYZError(ImageView.ImageViewError):
    pass

class ImageViewXYZ(ImageView.ImageViewBase):

    def __init__(self, logger=None, rgbmap=None, settings=None):
        ImageView.ImageViewBase.__init__(self, logger=logger,
                                         rgbmap=rgbmap, settings=settings)

        # XYZ image widget expects 32bit BGRA data for color images
        self._rgb_order = 'BGRA'
        
        self.t_.setDefaults(show_pan_position=False,
                            onscreen_ff='Sans Serif')

        self.message = None
        self.msgtimer = QtCore.QTimer()
        self.msgtimer.timeout.connect(self.onscreen_message_off)
        self.msgfont = QtGui.QFont(self.t_['onscreen_ff'],
                                   pointSize=24)
        self.set_bg(0.5, 0.5, 0.5, redraw=False)
        self.set_fg(1.0, 1.0, 1.0, redraw=False)

        # cursors
        self.cursor = {}

        # For optomized redrawing
        self._defer_task = QtCore.QTimer()
        self._defer_task.setSingleShot(True)
        self._defer_task.timeout.connect(self.delayed_redraw)


    def get_widget(self):
        return self.imgwin

    def render_image(self, rgbobj, dst_x, dst_y):
        """Render the image represented by (rgbobj) at dst_x, dst_y
        in the pixel space.
        """
        self.logger.debug("redraw pixmap=%s" % (self.pixmap))
        if self.pixmap == None:
            return
        self.logger.debug("drawing to pixmap")

        # Prepare array for rendering
        arr = rgbobj.get_array(self._rgb_order)
        (height, width) = arr.shape[:2]

        return self._render_offscreen(self.pixmap, arr, dst_x, dst_y,
                                      width, height)

    def configure(self, width, height):
        self.logger.debug("window size reconfigured to %dx%d" % (
            width, height))
        self.set_window_size(width, height, redraw=True)
        
    def reschedule_redraw(self, time_sec):
        try:
            self._defer_task.stop()
        except:
            pass

        time_ms = int(time_sec * 1000)
        self._defer_task.start(time_ms)

    def update_image(self):
        if (not self.pixmap) or (not self.imgwin):
            return
            
        self.logger.debug("updating window from pixmap")
        if hasattr(self, 'scene'):
            imgwin_wd, imgwin_ht = self.get_window_size()
            self.scene.invalidate(0, 0, imgwin_wd, imgwin_ht,
                                  QtGui.QGraphicsScene.BackgroundLayer)
        else:
            self.imgwin.update()
            #self.imgwin.show()

    def set_cursor(self, cursor):
        if self.imgwin:
            self.imgwin.setCursor(cursor)
        
    def define_cursor(self, ctype, cursor):
        self.cursor[ctype] = cursor
        
    def get_cursor(self, ctype):
        return self.cursor[ctype]
        
    def get_rgb_order(self):
        return self._rgb_order
        
    def switch_cursor(self, ctype):
        self.set_cursor(self.cursor[ctype])
        
    def set_fg(self, r, g, b, redraw=True):
        self.img_fg = self._get_color(r, g, b)
        if redraw:
            self.redraw(whence=3)
        
    def onscreen_message(self, text, delay=None, redraw=True):
        try:
            self.msgtimer.stop()
        except:
            pass
        self.message = text
        if redraw:
            self.redraw(whence=3)
        if delay:
            ms = int(delay * 1000.0)
            self.msgtimer.start(ms)

    def onscreen_message_off(self, redraw=True):
        return self.onscreen_message(None, redraw=redraw)
    
    def show_pan_mark(self, tf, redraw=True):
        self.t_.set(show_pan_position=tf)
        if redraw:
            self.redraw(whence=3)
        

class ImageViewEvent(ImageViewQt):

    def __init__(self, logger=None, rgbmap=None, settings=None):
        ImageViewXYZ.__init__(self, logger=logger, rgbmap=rgbmap,
                              settings=settings)

        # replace the widget our parent provided
        if self.wtype == 'scene':
            imgwin = RenderGraphicsViewZoom()
            imgwin.setScene(self.scene)
        else:
            imgwin = RenderWidgetZoom()
            
        imgwin.fitsimage = self
        self.imgwin = imgwin
        imgwin.setFocusPolicy(QtCore.Qt.FocusPolicy(
                              QtCore.Qt.TabFocus |
                              QtCore.Qt.ClickFocus |
                              QtCore.Qt.StrongFocus |
                              QtCore.Qt.WheelFocus))
        imgwin.setMouseTracking(True)
        imgwin.setAcceptDrops(True)
        
        # last known window mouse position
        self.last_win_x = 0
        self.last_win_y = 0
        # last known data mouse position
        self.last_data_x = 0
        self.last_data_y = 0
        # Does widget accept focus when mouse enters window
        self.follow_focus = True

        # Define cursors
        for curname, filename in (('pan', 'openHandCursor.png'),
                               ('pick', 'thinCrossCursor.png')):
            path = os.path.join(icon_dir, filename)
            cur = make_cursor(path, 8, 8)
            self.define_cursor(curname, cur)

        # @$%&^(_)*&^ qt!!
        self._keytbl = {
            '`': 'backquote',
            '"': 'doublequote',
            "'": 'singlequote',
            '\\': 'backslash',
            ' ': 'space',
            }
        self._fnkeycodes = [QtCore.Qt.Key_F1, QtCore.Qt.Key_F2,
                            QtCore.Qt.Key_F3, QtCore.Qt.Key_F4,
                            QtCore.Qt.Key_F5, QtCore.Qt.Key_F6,
                            QtCore.Qt.Key_F7, QtCore.Qt.Key_F8,
                            QtCore.Qt.Key_F9, QtCore.Qt.Key_F10,
                            QtCore.Qt.Key_F11, QtCore.Qt.Key_F12,
                            ]

        for name in ('motion', 'button-press', 'button-release',
                     'key-press', 'key-release', 'drag-drop', 
                     'scroll', 'map', 'focus', 'enter', 'leave',
                     ):
            self.enable_callback(name)

    def transkey(self, keycode, keyname):
        self.logger.debug("keycode=%d keyname='%s'" % (
            keycode, keyname))
        if keycode in [QtCore.Qt.Key_Control]:
            return 'control_l'
        if keycode in [QtCore.Qt.Key_Shift]:
            return 'shift_l'
        if keycode in [QtCore.Qt.Key_Alt]:
            return 'alt_l'
        # if keycode in [QtCore.Qt.Key_Super_L]:
        #     return 'super_l'
        # if keycode in [QtCore.Qt.Key_Super_R]:
        #     return 'super_r'
        if keycode in [QtCore.Qt.Key_Escape]:
            return 'escape'
        # Conttrol key on Mac keyboards and "Windows" key under Linux
        if keycode in [16777250]:
            return 'meta_right'
        if keycode in self._fnkeycodes:
            index = self._fnkeycodes.index(keycode)
            return 'f%d' % (index+1)

        try:
            return self._keytbl[keyname.lower()]

        except KeyError:
            return keyname
        
    def get_keyTable(self):
        return self._keytbl
    
    def set_followfocus(self, tf):
        self.followfocus = tf
        
    def map_event(self, widget, event):
        rect = widget.geometry()
        x1, y1, x2, y2 = rect.getCoords()
        width = x2 - x1
        height = y2 - y1
       
        self.configure(width, height)
        return self.make_callback('map')
            
    def focus_event(self, widget, event, hasFocus):
        return self.make_callback('focus', hasFocus)
            
    def enter_notify_event(self, widget, event):
        if self.follow_focus:
            widget.setFocus()
        return self.make_callback('enter')
    
    def leave_notify_event(self, widget, event):
        self.logger.debug("leaving widget...")
        return self.make_callback('leave')
    
    def key_press_event(self, widget, event):
        keyname = event.key()
        keyname2 = "%s" % (event.text())
        keyname = self.transkey(keyname, keyname2)
        self.logger.debug("key press event, key=%s" % (keyname))
        return self.make_callback('key-press', keyname)

    def key_release_event(self, widget, event):
        keyname = event.key()
        keyname2 = "%s" % (event.text())
        keyname = self.transkey(keyname, keyname2)
        self.logger.debug("key release event, key=%s" % (keyname))
        return self.make_callback('key-release', keyname)

    def button_press_event(self, widget, event):
        buttons = event.buttons()
        x, y = event.x(), event.y()

        button = 0
        if buttons & QtCore.Qt.LeftButton:
            button |= 0x1
        if buttons & QtCore.Qt.MidButton:
            button |= 0x2
        if buttons & QtCore.Qt.RightButton:
            button |= 0x4
        self.logger.debug("button down event at %dx%d, button=%x" % (x, y, button))
                
        data_x, data_y = self.get_data_xy(x, y)
        return self.make_callback('button-press', button, data_x, data_y)

    def button_release_event(self, widget, event):
        # note: for mouseRelease this needs to be button(), not buttons()!
        buttons = event.button()
        x, y = event.x(), event.y()
        
        button = 0
        if buttons & QtCore.Qt.LeftButton:
            button |= 0x1
        if buttons & QtCore.Qt.MidButton:
            button |= 0x2
        if buttons & QtCore.Qt.RightButton:
            button |= 0x4
            
        data_x, data_y = self.get_data_xy(x, y)
        return self.make_callback('button-release', button, data_x, data_y)

    def get_last_win_xy(self):
        return (self.last_win_x, self.last_win_y)

    def get_last_data_xy(self):
        return (self.last_data_x, self.last_data_y)

    def motion_notify_event(self, widget, event):
        buttons = event.buttons()
        x, y = event.x(), event.y()
        self.last_win_x, self.last_win_y = x, y
        
        button = 0
        if buttons & QtCore.Qt.LeftButton:
            button |= 0x1
        if buttons & QtCore.Qt.MidButton:
            button |= 0x2
        if buttons & QtCore.Qt.RightButton:
            button |= 0x4

        data_x, data_y = self.get_data_xy(x, y)
        self.last_data_x, self.last_data_y = data_x, data_y

        return self.make_callback('motion', button, data_x, data_y)

    def scroll_event(self, widget, event):
        delta = event.delta()
        direction = None
        if delta > 0:
            direction = 'up'
        elif delta < 0:
            direction = 'down'
        self.logger.debug("scroll delta=%f direction=%s" % (
            delta, direction))

        return self.make_callback('scroll', direction)

    def drop_event(self, widget, event):
        dropdata = event.mimeData()
        formats = map(str, list(dropdata.formats()))
        self.logger.debug("available formats of dropped data are %s" % (
            formats))
        if dropdata.hasUrls():
            urls = list(dropdata.urls())
            paths = [ str(url.toString()) for url in urls ]
            event.acceptProposedAction()
            self.logger.debug("dropped filename(s): %s" % (str(paths)))
            self.make_callback('drag-drop', paths)
        

class ImageViewZoom(Mixins.UIMixin, ImageViewEvent):

    # class variables for binding map and bindings can be set
    bindmapClass = Bindings.BindingMapper
    bindingsClass = Bindings.ImageViewBindings

    @classmethod
    def set_bindingsClass(cls, klass):
        cls.bindingsClass = klass
        
    @classmethod
    def set_bindmapClass(cls, klass):
        cls.bindmapClass = klass
        
    def __init__(self, logger=None, settings=None, rgbmap=None,
                 render='widget',
                 bindmap=None, bindings=None):
        ImageViewEvent.__init__(self, logger=logger, settings=settings,
                                rgbmap=rgbmap, render=render)
        Mixins.UIMixin.__init__(self)

        if bindmap == None:
            bindmap = ImageViewZoom.bindmapClass(self.logger)
        self.bindmap = bindmap
        bindmap.register_for_events(self)

        if bindings == None:
            bindings = ImageViewZoom.bindingsClass(self.logger)
        self.set_bindings(bindings)

    def get_bindmap(self):
        return self.bindmap
    
    def get_bindings(self):
        return self.bindings
    
    def set_bindings(self, bindings):
        self.bindings = bindings
        bindings.set_bindings(self)

        
def make_cursor(iconpath, x, y):
    image = QtGui.QImage()
    image.load(iconpath)
    pm = QtGui.QPixmap(image)
    return QtGui.QCursor(pm, x, y)

#END
