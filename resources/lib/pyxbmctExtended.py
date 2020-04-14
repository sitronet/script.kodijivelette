#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

'''
import os

import xbmc
import xbmcgui
import xbmcaddon
import pyxbmct

ADDON = xbmcaddon.Addon()
ADDONID = ADDON.getAddonInfo('id')
ADDONNAME = ADDON.getAddonInfo('name')
ADDONVERSION = ADDON.getAddonInfo('version')
ARTWORK = xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media'))


class MySkin(pyxbmct.Skin):
    '''
    original source is :
    @property
    def main_bg_img(self):
        return os.path.join(self.images, 'AddonWindow', 'SKINDEFAULT.jpg')

    @property
    def background_img(self):
        return os.path.join(self.images, 'AddonWindow', 'ContentPanel.png')
    '''

    @property
    def background_img(self):
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_allegro.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_encore.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_harmony.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_nocturne.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_quartet.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_sonata.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_symphony.png'))
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'pcp_vibrato.png'))
        #return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media', 'fond-noir.jpg'))

    @property
    def title_background_img(self):
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_vibrato.png'))

    @property
    def main_bg_img(self):
        return xbmc.translatePath(os.path.join(ADDON.getAddonInfo('path'), 'resources', 'skins', 'Default', 'media','pcp_vibrato.png'))


skin = MySkin()


class AddonWindowWithoutTitle(pyxbmct.AbstractWindow):
    """
    copy/paste then modify from class pyxbmct.AddonWindow
    Top-level control window.
    The control windows serves as a parent widget for other XBMC UI controls
    much like ``Tkinter.Tk`` or PyQt ``QWidget`` class.
    This is an abstract class which is not supposed to be instantiated directly
    and will raise exeptions. It is designed to be implemented in a grand-child class
    with the second inheritance from ``xbmcgui.Window`` or ``xbmcgui.WindowDialog``
    in a direct child class.
    This class provides a control window with a background
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
        self.background_img = skin.background_img
        # xbmcgui.ControlImage(x, y, width, height, filename, aspectRatio=0, colorDiffuse=None)
        # Background for a window header
        #Parameters: x – integer - x coordinate of control.
        # y – integer - y coordinate of control.
        # width – integer - width of control.
        # height – integer - height of control.
        # filename – string - image filename.
        # aspectRatio – [opt] integer - (values 0 = stretch (default), 1 = scale up(crops), 2 = scale down(black bar)
        # colorDiffuse – hexString - (example, ‘0xC0FF0000’ (red tint))
        self.background = xbmcgui.ControlImage( -10 , -10 , 1, 1, self.background_img)
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

        self._width = width_
        self._height = height_
        self.rows = rows_
        self.columns = columns_
        self.win_padding = padding
        if pos_x > 0 and pos_y > 0:
            self.x = pos_x
            self.y = pos_y
        else:
            self.x = 640 - width_ // 2
            self.y = 360 - height_ // 2

        super(AddonWindowWithoutTitle, self).setGeometry(width_, height_, rows_, columns_, pos_x, pos_y)

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
        return val + skin.x_margin

    def getGridY(self):
        # type: () -> int
        try:
            val = self.y + self.win_padding
        except AttributeError:
            self._raiseSetGeometryNotCalledError()
        return val + skin.y_margin

    def getGridWidth(self):
        # type: () -> int
        try:
            val = self._width - 2 * self.win_padding
        except AttributeError:
            self._raiseSetGeometryNotCalledError()
        return val - 2 * skin.x_margin

    def getGridHeight(self):
        # type: () -> int
        try:
            val = self._height - 2 * self.win_padding
        except AttributeError:
            self._raiseSetGeometryNotCalledError()
        return val

class BackgroundFullWindow(AddonWindowWithoutTitle, xbmcgui.Window):
    """
    Same as AddonFullWindow(title='') without Title and title-bar
    Addon UI container with a solid background.
    ``BackgroundFullWindow`` instance is displayed on top of the main background image --
    ``self.main_bg`` -- and can hide behind a fullscreen video or music viaualisation.
    Minimal example::
        addon = BackgroundFullWindow('My Cool Addon')
        addon.setGeometry(400, 300, 4, 3)
        addon.doModal()
    """

    def __new__(cls, *args, **kwargs):
        return super(BackgroundFullWindow, cls).__new__(cls, *args, **kwargs)

        #def _setFrame(self):
        """
        Set the image for for the fullscreen background.
        """
        # type: (str) -> None
        # Image for the fullscreen background.
        #self.main_bg_img = skin.main_bg_img
        # Fullscreen background image control.
        #self.main_bg = xbmcgui.ControlImage(1, 1, 1280, 720, self.main_bg_img)
        #self.addControl(self.main_bg)
        #super(BackgroundFullWindow, self)._setFrame()
        #pass

    def setBackground(self, image=''):
        """
        Set the main bacground to an image file.
        :param image: path to an image file as str.
        Example::
            self.setBackground('/images/bacground.png')
        """
        # type: (str) -> None
        self.background_img.setImage(image)


class BackgroundDialogWindow(AddonWindowWithoutTitle, xbmcgui.WindowDialog):
    """
    cpoy/paste of AddonDialogWindow(title='')

    Addon UI container with a transparent background.

    .. note:: ``AddonDialogWindow`` instance is displayed on top of XBMC UI,
        including fullscreen video and music visualization.

    Minimal example::

        addon = AddonDialogWindow('My Cool Addon')
        addon.setGeometry(400, 300, 4, 3)
        addon.doModal()
    """