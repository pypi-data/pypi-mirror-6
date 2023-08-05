import gtk
import gobject


class CellTextView(gtk.TextView, gtk.CellEditable):

    __gtype_name__ = "CellTextView"

    __gproperties__ = {
         'editing-canceled' : (gobject.TYPE_BOOLEAN,                        # type
                               'editing canceled',                         # nick name
                               'Indicates whether editing on the cell has been canceled.', # description
                               False,                                        # default value
                               gobject.PARAM_READWRITE)                   # flags
    }
    
    def do_editing_done(self, *args):
        self.remove_widget()

    def do_remove_widget(self, *args):
        pass

    def do_start_editing(self, *args):
        pass

    def get_text(self):
        text_buffer = self.get_buffer()
        bounds = text_buffer.get_bounds()
        return text_buffer.get_text(*bounds)

    def set_text(self, text):
        if text:
            self.get_buffer().set_text(text)


class MultilineCellRenderer(gtk.CellRendererText):

    __gtype_name__ = "MultilineCellRenderer"

    def __init__(self, sqlwidget):
        gtk.CellRendererText.__init__(self)
        self._in_editor_menu = False
        self.treeview = sqlwidget.treeview
        self.sqlwidget = sqlwidget
        
    def _on_editor_focus_out_event(self, editor, *args):

        if self._in_editor_menu:
            return
        
    def _on_editor_key_press_event(self, editor, event):

        if event.state & (gtk.gdk.SHIFT_MASK | gtk.gdk.CONTROL_MASK):
            return

        if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter, gtk.keysyms.Tab):
            self.emit("edited", editor.get_data("path"), editor.get_text())
            editor.remove_widget()

            if event.keyval in (gtk.keysyms.Tab,):
                self.treeview.emit('key-press-event', event )

        elif event.keyval == gtk.keysyms.Escape:
            editor.remove_widget()
            self.emit("editing-canceled")

    def _on_editor_populate_popup(self, editor, menu):
        self._in_editor_menu = True
        def on_menu_unmap(menu, self):
            self._in_editor_menu = False
        menu.connect("unmap", on_menu_unmap, self)

    def do_start_editing(self, event, widget, path, bg_area, cell_area, flags):
        editor = CellTextView()
        editor.modify_font(self.props.font_desc)
        editor.set_text(self.props.text)
        editor.set_size_request(cell_area.width *2, cell_area.height * 2)
        editor.set_border_width(min(self.props.xpad, self.props.ypad))
        editor.set_data("path", path)
        editor.connect("focus-out-event", self._on_editor_focus_out_event)
        editor.connect("key-press-event", self._on_editor_key_press_event)
        editor.connect("populate-popup", self._on_editor_populate_popup)
        editor.show()
        self.set_data('editor', editor)
        self.editor = editor
        return editor
