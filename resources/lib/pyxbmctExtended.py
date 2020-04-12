'''

'''

import xbmc
import xbmcgui
import xbmcaddon
import pyxbmct


class AddonWindowWithoutTitle(pyxbmct.AbstractWindow):
    """
    Top-level control window.
    The control windows serves as a parent widget for other XBMC UI controls
    much like ``Tkinter.Tk`` or PyQt ``QWidget`` class.
    This is an abstract class which is not supposed to be instantiated directly
    and will raise exeptions. It is designed to be implemented in a grand-child class
    with the second inheritance from ``xbmcgui.Window`` or ``xbmcgui.WindowDialog``
    in a direct child class.
    This class provides a control window with a background and a header
    similar to top-level widgets of desktop UI frameworks.
    .. warning:: This is an abstract class and is not supposed to be instantiated directly!
    """

    def __init__(self):
        """Constructor method."""
        # type: (str) -> None
        super(AddonWindowWithoutTitle, self).__init__()
        self._setFrame()

    def onControl(self, control):
        """
        Catch activated controls.
        :param control: is an instance of :class:`xbmcgui.Control` class.
        """
        # type: (xbmcgui.Control) -> None
        if (hasattr(self, 'window_close_button') and
                control.getId() == self.window_close_button.getId()):
            self.close()  # pytype: disable=attribute-error
        else:
            super(AddonWindowWithoutTitle, self).onControl(control)

    def _setFrame(self):
        """
        Set window frame
        Define paths to images for window background and title background textures,
        and set control position adjustment constants used in setGrid.
        This is a helper method not to be called directly.
        """
        # type: (str) -> None
        # Window background image
        self.background_img = pyxbmct.skin.background_img
        # Background for a window header
        self.background = xbmcgui.ControlImage(-10, -10, 1, 1, self.background_img)
        self.addControl(self.background)
        self.setAnimation(self.background)
        # let's see later the close_button
        #self.window_close_button = xbmcgui.ControlButton(-100, -100, skin.close_btn_width, skin.close_btn_height, '',
        #                                                 focusTexture=skin.close_button_focus,
        #                                                 noFocusTexture=skin.close_button_no_focus)
        #self.addControl(self.window_close_button)
        #self.setAnimation(self.window_close_button)

    def setGeometry(self, width_, height_, rows_, columns_, pos_x=-1, pos_y=-1, padding=5):
        """
        Set width, height, Grid layout, and coordinates (optional) for a new control window.
        :param width_: new window width in pixels.
        :param height_: new window height in pixels.
        :param rows_: # of rows in the Grid layout to place controls on.
        :param columns_: # of colums in the Grid layout to place controls on.
        :param pos_x: (optional) x coordinate of the top left corner of the window.
        :param pos_y: (optional) y coordinate of the top left corner of the window.
        :param padding: (optional) padding between outer edges of the window
        and controls placed on it.
        If ``pos_x`` and ``pos_y`` are not privided, the window will be placed
        at the center of the screen.
        Example::
            self.setGeometry(400, 500, 5, 4)
        """
        # type: (int, int, int, int, int, int, int) -> None
        self.win_padding = padding
        super(AddonWindow, self).setGeometry(width_, height_, rows_, columns_, pos_x, pos_y)
        self.background.setPosition(self.x, self.y)
        self.background.setWidth(self._width)
        self.background.setHeight(self._height)

        # self.window_close_button.setPosition(self.x + self._width - skin.close_btn_x_offset,
        #                                     self.y + skin.y_margin + skin.close_btn_y_offset)

    def _raiseSetGeometryNotCalledError(self):
        """
        Helper method that raises an AddonWindowError  that states that setGeometry needs to be called. Used by methods
        that will fail if the window geometry is not defined.
        :raises AddonWindowError
        """
        # type: () -> None
        raise pyxbmct.AddonWindowError('Window geometry is not defined! Call setGeometry first.')

    def getGridX(self):
        # type: () -> int
        try:
            val = self.x + self.win_padding
        except AttributeError:
            self._raiseSetGeometryNotCalledError()
        return val + pyxbmct.skin.x_margin

    def getGridY(self):
        # type: () -> int
        try:
            val = self.y + self.win_padding
        except AttributeError:
            self._raiseSetGeometryNotCalledError()
        return val + pyxbmct.skin.y_margin + pyxbmct.skin.title_back_y_shift + pyxbmct.skin.header_height

    def getGridWidth(self):
        # type: () -> int
        try:
            val = self._width - 2 * self.win_padding
        except AttributeError:
            self._raiseSetGeometryNotCalledError()
        return val - 2 * pyxbmct.skin.x_margin

    def getGridHeight(self):
        # type: () -> int
        try:
            val = self._height - 2 * self.win_padding
        except AttributeError:
            self._raiseSetGeometryNotCalledError()
        return val - pyxbmct.skin.header_height - pyxbmct.skin.title_back_y_shift - 2 * pyxbmct.skin.y_margin

class AddonFullWindowWT(AddonWindowWithoutTitle, xbmcgui.Window):
    """
    AddonFullWindow(title='')without Title and title-bar
    Addon UI container with a solid background.
    ``AddonFullWindow`` instance is displayed on top of the main background image --
    ``self.main_bg`` -- and can hide behind a fullscreen video or music viaualisation.
    Minimal example::
        addon = AddonFullWindow('My Cool Addon')
        addon.setGeometry(400, 300, 4, 3)
        addon.doModal()
    """

    def __new__(cls, *args, **kwargs):
        return super(AddonFullWindowWT, cls).__new__(cls, *args, **kwargs)

    def _setFrame(self):
        """
        Set the image for for the fullscreen background.
        """
        # type: (str) -> None
        # Image for the fullscreen background.
        self.main_bg_img = pyxbmct.skin.main_bg_img
        # Fullscreen background image control.
        self.main_bg = xbmcgui.ControlImage(1, 1, 1280, 720, self.main_bg_img)
        self.addControl(self.main_bg)
        super(AddonFullWindowWT, self)._setFrame()

    def setBackground(self, image=''):
        """
        Set the main bacground to an image file.
        :param image: path to an image file as str.
        Example::
            self.setBackground('/images/bacground.png')
        """
        # type: (str) -> None
        self.main_bg.setImage(image)
