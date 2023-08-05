#!/usr/bin/python
"""
wxmplot ImageFrame: a wx.Frame for image display, using matplotlib
"""
import os
import wx
import numpy
from   matplotlib.cm import get_cmap
import matplotlib.cm as mpl_colormap
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg

from .imagepanel import ImagePanel
from .imageconf import ColorMap_List, Interp_List
from .baseframe import BaseFrame
from .colors import rgb2hex
from .utils import Closure, LabelEntry
from .contourdialog import ContourDialog

 

CURSOR_MENULABELS = {'zoom':  ('Zoom to Rectangle\tCtrl+B',
                               'Left-Drag to zoom to rectangular box'),
                     'lasso': ('Select Points\tCtrl+X',
                               'Left-Drag to select points freehand'),
                     'prof':  ('Select Line Profile\tCtrl+K',
                               'Left-Drag to select like for profile')}

class ImageFrame(BaseFrame):
    """
    MatPlotlib Image Display ons a wx.Frame, using ImagePanel
    """

    help_msg =  """Quick help:

Left-Click:   to display X,Y coordinates and Intensity
Left-Drag:    to zoom in on region
Right-Click:  display popup menu with choices:
               Zoom out 1 level
               Zoom all the way out
               --------------------
               Rotate Image
               Save Image

Keyboard Shortcuts:   (For Mac OSX, replace 'Ctrl' with 'Apple')
  Saving Images:
     Ctrl-S:     Save image to file
     Ctrl-C:     Copy image to clipboard
     Ctrl-P:     Print Image

  Zooming:
     Ctrl-Z:     Zoom all the way out
  
  Rotating/Flipping:
     Ctrl-R:     Rotate Clockwise
     Ctrl-T:     Flip Top/Bottom
     Ctrl-F:     Flip Left/Right     

  Image Enhancement:
     Ctrl-L:     Log-Scale Intensity
     Ctrl-E:     Enhance Contrast

  
"""
    

    def __init__(self, parent=None, size=None,
                 lasso_callback=None, mode='intensity',
                 show_xsections=True, cursor_labels=None,
                 output_title='Image', subtitles=None,  **kws):
        if size is None: size = (550, 450)
        self.lasso_callback = lasso_callback
        self.cursor_menulabels =  {}
        self.cursor_menulabels.update(CURSOR_MENULABELS)
        if cursor_labels is not None:
            self.cursor_menulabels.update(cursor_labels)

        BaseFrame.__init__(self, parent=parent,
                           title  = 'Image Display Frame',
                           output_title=output_title,
                           size=size, **kws)

        self.cmap_lo = {}
        self.cmap_hi = {}
        self.cmap_img = {}
        self.cmap_dat = {}
        self.cmap_canvas = {}
        self.wids_subtitles = {}
        self.subtitles = {}
        self.config_mode = None
        if subtitles is not None:
            self.subtitles = subtitles
        sbar = self.CreateStatusBar(2, wx.CAPTION|wx.THICK_FRAME)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(10)
        sbar.SetFont(sfont)

        self.SetStatusWidths([-2, -1])
        self.SetStatusText('', 0)

        mids = self.menuIDs
        mids.SAVE_CMAP = wx.NewId()
        mids.LOG_SCALE = wx.NewId()
        mids.AUTO_SCALE = wx.NewId()
        mids.ENHANCE   = wx.NewId()
        mids.FLIP_H    = wx.NewId()
        mids.FLIP_V    = wx.NewId()
        mids.FLIP_O    = wx.NewId()
        mids.ROT_CW    = wx.NewId()
        mids.CUR_ZOOM  = wx.NewId()
        mids.CUR_LASSO = wx.NewId()
        mids.CUR_PROF  = wx.NewId()

        self.BuildCustomMenus()
        self.BuildMenu()

        self.bgcol = rgb2hex(self.GetBackgroundColour()[:3])
        # self.bgcol
        self.panel = ImagePanel(self, data_callback=self.onDataChange,
                                size=(650, 450), dpi=100,
                                lasso_callback=self.onLasso,
                                output_title=self.output_title)

        self.SetBackgroundColour('#F8F8F4')
        
        self.config_panel = wx.Panel(self)
        if mode.lower().startswith('int'):
            self.config_mode = 'int'
            self.Build_ConfigPanel_Int()
        elif mode.lower().startswith('rgb'):
            self.config_mode = 'rgb'
            self.Build_ConfigPanel_RGB()
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        mainsizer.Add(self.config_panel, 0,
                      wx.LEFT|wx.ALIGN_LEFT|wx.TOP|wx.ALIGN_TOP|wx.EXPAND)

        self.panel.messenger = self.write_message
        # self.panel.fig.set_facecolor(self.bgcol)

        mainsizer.Add(self.panel, 1, wx.ALL|wx.GROW)

        self.BindMenuToPanel(panel=self.panel)

        # self.SetAutoLayout(True)
        self.SetSizer(mainsizer)
        self.Fit()

    def display(self, img, title=None, colormap=None, style='image',
                subtitles=None, **kw):
        """plot after clearing current plot
        """
        if title is not None:
            self.SetTitle(title)
        if subtitles is not None:
            self.subtitles = subtitles
        if len(img.shape) == 3:
            if not self.config_mode.lower().startswith('rgb'):
                for comp in self.config_panel.Children:
                    comp.Destroy()
                self.config_mode = 'rgb'
                self.Build_ConfigPanel_RGB()
        else:
            if not self.config_mode.lower().startswith('int'):
                for comp in self.config_panel.Children:
                    comp.Destroy()
                self.config_mode = 'int'
                self.Build_ConfigPanel_Int()
        self.panel.display(img, style=style, **kw)

        if subtitles is not None:
            for key, val in subtitles.items():
                if key in self.wids_subtitles:
                    self.wids_subtitles[key].SetLabel(val)
        
        self.panel.conf.title = title
        if colormap is not None:
            self.set_colormap(name=colormap)
        contour_value = 0
        if style == 'contour':
            contour_value = 1
        self.panel.redraw()
        self.config_panel.Refresh()
        self.SendSizeEvent()
        wx.CallAfter(self.EnableMenus)

    def EnableMenus(self, evt=None):
        isIntMap = True
        if self.panel.conf.data is not None:
            isIntMap = {True:1, False:0}[len(self.panel.conf.data.shape) == 2]
        self.opts_menu.Enable(self.menuIDs.SAVE_CMAP,  isIntMap)
        self.opts_menu.Enable(self.menuIDs.CONTOUR,    isIntMap)
        self.opts_menu.Enable(self.menuIDs.CONTOURLAB, isIntMap)
        # self.onInt_Autoscale(event=None, val=False)

    def BuildMenu(self):
        mids = self.menuIDs
        m0 = wx.Menu()
        mids.EXPORT = wx.NewId()
        m0.Append(mids.SAVE,   '&Save Image\tCtrl+S',  'Save PNG Image of Plot')
        m0.Append(mids.CLIPB,  '&Copy Image\tCtrl+C',  'Copy Image to Clipboard')
        m0.Append(mids.EXPORT, 'Export Data to ASCII', 'Export to ASCII file')
        m0.AppendSeparator()
        m0.Append(mids.PSETUP,  'Page Setup...',    'Printer Setup')
        m0.Append(mids.PREVIEW, 'Print Preview...', 'Print Preview')
        m0.Append(mids.PRINT,   '&Print\tCtrl+P',   'Print Plot')
        m0.AppendSeparator()
        m0.Append(mids.EXIT, 'E&xit\tCtrl+Q', 'Exit the 2D Plot Window')

        self.top_menus['File'] = m0

        mhelp = wx.Menu()
        mhelp.Append(mids.HELP, 'Quick Reference',  'Quick Reference for WXMPlot')
        mhelp.Append(mids.ABOUT, 'About', 'About WXMPlot')
        self.top_menus['Help'] = mhelp

        mbar = wx.MenuBar()

        mbar.Append(self.top_menus['File'], 'File')
        for m in self.user_menus:
            title,menu = m
            mbar.Append(menu, title)
        mbar.Append(self.top_menus['Help'], '&Help')


        self.SetMenuBar(mbar)
        self.Bind(wx.EVT_MENU, self.onHelp,            id=mids.HELP)
        self.Bind(wx.EVT_MENU, self.onAbout,           id=mids.ABOUT)
        self.Bind(wx.EVT_MENU, self.onExit ,           id=mids.EXIT)
        self.Bind(wx.EVT_CLOSE,self.onExit)
        # print 'done with BuildMenu'

    def BuildCustomMenus(self):
        'build menus'
        m = self.opts_menu = wx.Menu()
        mids = self.menuIDs
        m.Append(mids.UNZOOM, 'Zoom Out\tCtrl+Z',
                 'Zoom out to full data range')
        m.Append(mids.SAVE_CMAP, 'Save Image of Colormap')
        m.AppendSeparator()

        m.Append(mids.ROT_CW, 'Rotate clockwise\tCtrl+R', '')
        m.Append(mids.FLIP_V, 'Flip Top/Bottom\tCtrl+T', '')
        m.Append(mids.FLIP_H, 'Flip Left/Right\tCtrl+F', '')
        # m.Append(mids.FLIP_O, 'Flip to Original', '')
        m.AppendSeparator()
        m.Append(wx.NewId(), 'Cursor Modes : ',
                 'Action taken on with Left-Click and Left-Drag')

        clabs = self.cursor_menulabels
        m.AppendRadioItem(mids.CUR_ZOOM,  clabs['zoom'][0],  clabs['zoom'][1])
        m.AppendRadioItem(mids.CUR_LASSO, clabs['lasso'][0], clabs['lasso'][1])
        # m.AppendRadioItem(mids.CUR_PROF,  clabs['prof'][0],  clabs['prof'][1])
        m.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_H)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_V)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.FLIP_O)
        self.Bind(wx.EVT_MENU, self.onFlip,       id=mids.ROT_CW)
        self.Bind(wx.EVT_MENU, self.onCursorMode, id=mids.CUR_ZOOM)
        self.Bind(wx.EVT_MENU, self.onCursorMode, id=mids.CUR_LASSO)
        mids.CONTOUR  = wx.NewId()
        m.Append(mids.CONTOUR, 'As Contour', 'Show as contour map', kind=wx.ITEM_CHECK)
        m.Check(mids.CONTOUR, False)
        self.Bind(wx.EVT_MENU, self.onContourToggle, id=mids.CONTOUR)

        mids.CONTOURLAB  = wx.NewId()
        m.Append(mids.CONTOURLAB, 'Configure Contours', 'Configure Contours')
        self.Bind(wx.EVT_MENU, self.onContourConfig, id=mids.CONTOURLAB)

        em = wx.Menu()
        em.Append(mids.LOG_SCALE,  'Log Scale Intensity\tCtrl+L',
                  'use logarithm to set intensity scale', wx.ITEM_CHECK)
        em.Append(mids.ENHANCE,    'Enhance Contrast\tCtrl+E',
                  'use 1% / 99% levels to set intensity scale', wx.ITEM_CHECK)
        em.Append(mids.AUTO_SCALE, 'Auto Scale Intensity\tCtrl+A',
                  'reset intensity scale from data range', wx.ITEM_CHECK)
        
        sm = wx.Menu()
        for itype in Interp_List:
            wid = wx.NewId()
            sm.AppendRadioItem(wid, itype, itype)
            self.Bind(wx.EVT_MENU, Closure(self.onInterp, name=itype), id=wid)
        self.user_menus  = [('&Options', m), ('Contrast', em), ('Smoothing', sm)]
        # print 'done Build Custom Menus'

    def onInterp(self, evt=None, name=None):
        if name not in Interp_List:
            name = Interp_List[0]
        self.panel.conf.interp = name
        self.panel.redraw()

    def onCursorMode(self, event=None):
        wid = event.GetId()
        self.panel.cursor_mode = 'zoom'
        if wid == self.menuIDs.CUR_PROF:
            self.panel.cursor_mode = 'profile'
        elif wid == self.menuIDs.CUR_LASSO:
            self.panel.cursor_mode = 'lasso'

    def onFlip(self, event=None):
        conf = self.panel.conf
        wid = event.GetId()
        mids = self.menuIDs

        if wid == mids.FLIP_H:
            conf.flip_lr = not conf.flip_lr
        elif wid == mids.FLIP_V:
            conf.flip_ud = not conf.flip_ud
        elif wid == mids.FLIP_O:
            conf.flip_lr, conf.flip_ud = False, False
        elif wid == mids.ROT_CW:
            conf.rot = True
        self.panel.unzoom_all()

    def BindMenuToPanel(self, panel=None):
        if panel is None: panel = self.panel
        BaseFrame.BindMenuToPanel(self, panel=panel)
        mids = self.menuIDs

        self.Bind(wx.EVT_MENU, self.onCMapSave, id=mids.SAVE_CMAP)
        self.Bind(wx.EVT_MENU, self.onLogScale, id=mids.LOG_SCALE)
        self.Bind(wx.EVT_MENU, self.onEnhanceContrast, id=mids.ENHANCE)
        self.Bind(wx.EVT_MENU, self.onInt_Autoscale, id=mids.AUTO_SCALE)
        self.Bind(wx.EVT_MENU, self.panel.exportASCII, id=mids.EXPORT)

    def Build_ConfigPanel_RGB(self):
        """config panel for left-hand-side of frame: RGB Maps"""
        self.imin_val = {}
        self.imax_val = {}
        conf = self.panel.conf
        lpanel = self.config_panel
        lsizer = wx.GridBagSizer(7, 4)
        
        labstyle = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        s = wx.StaticText(lpanel, label='Zero Intensity Color:', size=(120, -1))
        lsizer.Add(s, (0, 0), (1, 2), labstyle, 2)

        bg_choice = wx.Choice(lpanel, size=(75, -1), choices=('black', 'white'))
        bg_choice.Bind(wx.EVT_CHOICE,  self.onTriColorBG)
        bg_choice.SetSelection(0)
        
        lsizer.Add(bg_choice, (0, 2), (1, 2), labstyle, 2)

        irow = 0

        for col in ('red', 'green', 'blue'):
            stitle = self.subtitles.get(col, '')
            lab = "%s: %s" % (col.title(), stitle)
            s = wx.StaticText(lpanel, label=lab, size=(100, -1))
            irow += 1
            lsizer.Add(s, (irow, 0), (1, 4), labstyle, 0)
            self.wids_subtitles[col] = s
            
            cm_wid   = 1.00
            cm_ratio = 0.07
            cmax = 100.0
            self.cmap_dat[col]   = numpy.outer(numpy.ones(cmax*cm_ratio),
                                               numpy.linspace(0, 1, cmax))

            fig  = Figure((cm_wid, cm_wid*cm_ratio), dpi=150)

            ax  = fig.add_axes([0, 0, 1, 1])
            ax.set_axis_off()
            self.cmap_canvas[col] = FigureCanvasWxAgg(lpanel, -1, figure=fig)

            cmap = get_cmap(col)
            conf.cmap[col] = cmap
            conf.cmap_lo[col] = 0
            conf.cmap_hi[col] = 100
            self.cmap_img[col] = ax.imshow(self.cmap_dat[col],
                                           cmap=cmap,
                                           interpolation='bilinear')

            self.cmap_lo[col] = wx.Slider(lpanel, -1, 0, 0, 100,
                                            style=wx.SL_HORIZONTAL)
            self.cmap_hi[col] = wx.Slider(lpanel, -1, 100, 0, 100,
                                            style=wx.SL_HORIZONTAL)
            self.cmap_lo[col].Bind(wx.EVT_SCROLL,  Closure(self.onStretchLow, col=col))
            self.cmap_hi[col].Bind(wx.EVT_SCROLL,  Closure(self.onStretchHigh, col=col))

            #         self.cmap_hi_val.Bind(wx.EVT_SCROLL,  self.onStretchHigh)
            irow += 1
            lsizer.Add(self.cmap_hi[col],    (irow, 0), (1, 4), labstyle, 0)
            irow += 1
            lsizer.Add(self.cmap_canvas[col],  (irow, 0), (1, 4), wx.ALIGN_CENTER, 0)
            irow += 1
            lsizer.Add(self.cmap_lo[col],     (irow, 0), (1, 4), labstyle, 0)

            self.imin_val[col] = LabelEntry(lpanel, conf.int_lo[col],
                                            size=65, labeltext='Range:',
                                            action = Closure(self.onThreshold,
                                                             argu='lo', col=col))
            self.imax_val[col] = LabelEntry(lpanel, conf.int_hi[col],
                                            size=65, labeltext=':',
                                            action = Closure(self.onThreshold,
                                                             argu='hi', col=col))
            irow += 1
            lsizer.Add(self.imin_val[col].label, (irow, 0), (1, 1), labstyle, 1)
            lsizer.Add(self.imin_val[col],       (irow, 1), (1, 1), labstyle, 0)
            lsizer.Add(self.imax_val[col].label, (irow, 2), (1, 1), labstyle, 0)
            lsizer.Add(self.imax_val[col],       (irow, 3), (1, 1), labstyle, 0)

            irow += 1
            lsizer.Add(wx.StaticLine(lpanel, size=(50, 2), style=wx.LI_HORIZONTAL),
                       (irow, 0), (1, 4), labstyle, 0)
        irow += 1
        self.CustomConfig(lpanel, lsizer, irow)

        lpanel.SetSizer(lsizer)
        lpanel.Fit()

        return lpanel

    
    def CustomConfig(self, lpanel, lsizer, irow):
        """ override to add custom config panel items
        to bottom of config panel
        """
        pass

    def Build_ConfigPanel_Int(self):
        """config panel for left-hand-side of frame"""
        self.imin_val = {}
        self.imax_val = {}
        conf = self.panel.conf
        lpanel = self.config_panel
        lsizer = wx.GridBagSizer(7, 4)

        labstyle = wx.ALIGN_LEFT|wx.LEFT|wx.TOP|wx.EXPAND

        s = wx.StaticText(lpanel, label=' Color Table:', size=(100, -1))
        lsizer.Add(s, (0, 0), (1, 4), labstyle, 2)

        col = 'int'
        # color map
        cmap_choice =  wx.Choice(lpanel, size=(150, -1), choices=ColorMap_List)
        cmap_choice.Bind(wx.EVT_CHOICE,  self.onCMap)
        cmap_name = conf.cmap[col].name
        if cmap_name.endswith('_r'):
            cmap_name = cmap_name[:-2]
        cmap_choice.SetStringSelection(cmap_name)
        self.cmap_choice = cmap_choice

        cmap_reverse = wx.CheckBox(lpanel, label='Reverse Table',
                                  size=(140, -1))
        cmap_reverse.Bind(wx.EVT_CHECKBOX, self.onCMapReverse)
        cmap_reverse.SetValue(conf.cmap_reverse)
        self.cmap_reverse = cmap_reverse

        cmax = conf.cmap_range
        self.bgcol = rgb2hex(lpanel.GetBackgroundColour()[:3])

        cm_wid   = 1.00
        cm_ratio = 0.12
        col = 'int'
        self.cmap_dat[col] = numpy.outer(numpy.ones(cmax*cm_ratio),
                                       numpy.linspace(0, 1, cmax))

        fig = Figure((cm_wid, cm_wid*cm_ratio), dpi=150)

        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_axis_off()
        self.cmap_canvas[col] = FigureCanvasWxAgg(lpanel, -1, figure=fig)

        self.cmap_img[col] = ax.imshow(self.cmap_dat[col],
                                       cmap=conf.cmap[col],
                                       interpolation='bilinear')

        self.cmap_lo[col] = wx.Slider(lpanel, -1, conf.cmap_lo[col], 0,
                                        conf.cmap_range,
                                        style=wx.SL_HORIZONTAL)

        self.cmap_hi[col] = wx.Slider(lpanel, -1, conf.cmap_hi[col], 0,
                                     conf.cmap_range,
                                     style=wx.SL_HORIZONTAL)

        self.cmap_lo[col].Bind(wx.EVT_SCROLL,  self.onStretchLow)
        self.cmap_hi[col].Bind(wx.EVT_SCROLL,  self.onStretchHigh)
        irow = 1
        lsizer.Add(self.cmap_choice,  (1, 0), (1, 4), labstyle, 2)
        lsizer.Add(self.cmap_reverse, (2, 0), (1, 4), labstyle, 2)
        lsizer.Add(self.cmap_hi[col],  (3, 0), (1, 4), labstyle, 2)
        lsizer.Add(self.cmap_canvas[col],  (4, 0), (1, 4), wx.ALIGN_CENTER, 0)
        lsizer.Add(self.cmap_lo[col],  (5, 0), (1, 4), labstyle, 2)
        irow = 5

        self.imin_val[col] = LabelEntry(lpanel, conf.int_lo[col],
                                   size=65, labeltext='Range:',
                                   action = Closure(self.onThreshold, argu='lo'))
        self.imax_val[col] = LabelEntry(lpanel, conf.int_hi[col],
                                   size=65, labeltext=':',
                                   action = Closure(self.onThreshold, argu='hi'))

        irow += 1
        lsizer.Add(self.imin_val[col].label, (irow, 0), (1, 1), labstyle, 1)
        lsizer.Add(self.imin_val[col],       (irow, 1), (1, 1), labstyle, 0)
        lsizer.Add(self.imax_val[col].label, (irow, 2), (1, 1), labstyle, 0)
        lsizer.Add(self.imax_val[col],       (irow, 3), (1, 1), labstyle, 0)

        irow += 1
        lsizer.Add(wx.StaticLine(lpanel, size=(50, 2), style=wx.LI_HORIZONTAL),
                   (irow, 0), (1, 4), labstyle, 1)
        irow += 1
        self.CustomConfig(lpanel, lsizer, irow)
        lpanel.SetSizer(lsizer)
        lpanel.Fit()
        return lpanel

    def onContourConfig(self, event=None):
        panel = self.panel
        conf = panel.conf
        dlg = ContourDialog(parent=self, conf=conf)
        dlg.CenterOnScreen()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            pass
        dlg.Destroy()
        if conf.style != 'contour':
            return
        self.set_colormap()
        panel.axes.cla()
        panel.display(conf.data, x=panel.xdata, y = panel.ydata,
                      xlabel=panel.xlab, ylabel=panel.ylab,
                      contour_labels=conf.contour_labels,
                      nlevels=conf.ncontour_levels, style='contour')
        panel.redraw()

    def onContourToggle(self, event=None):
        if len(self.panel.conf.data.shape) > 2:
            return
        panel = self.panel
        conf  = panel.conf
        conf.style = 'image'
        if event.IsChecked():
            conf.style = 'contour'
        nlevels = int(conf.ncontour_levels)
        self.set_colormap()
        panel.axes.cla()
        panel.display(conf.data, x=panel.xdata, y = panel.ydata,
                      nlevels=nlevels, contour_labels=conf.contour_labels,
                      xlabel=panel.xlab, ylabel=panel.ylab,
                      style=conf.style)
        panel.redraw()

    def onTriColorBG(self, event=None):
        col = event.GetString()
        conf = self.panel.conf        
        if col == conf.tricolor_bg:
            return
        
        conf.tricolor_bg = col
        cmaps = ('red', 'green', 'blue')
        if col.startswith('wh'):
            cmaps = ('Reds', 'Greens', 'Blues')
        
        self.set_colormap(name=cmaps[0], col='red')
        self.set_colormap(name=cmaps[1], col='green')
        self.set_colormap(name=cmaps[2], col='blue')
        self.panel.redraw()
        
    def onCMap(self, event=None):
        self.set_colormap(name=event.GetString())
        self.panel.redraw()

    def onLasso(self, data=None, selected=None, mask=None, **kws):
        if hasattr(self.lasso_callback , '__call__'):
            self.lasso_callback(data=data, selected=selected, mask=mask, **kws)

    def onDataChange(self, data, x=None, y=None, col='int', **kw):
        conf = self.panel.conf
        if len(data.shape) == 2: # intensity map
            imin, imax = data.min(), data.max()
            self.imin_val[col].SetValue('%.4g' % imin)
            self.imax_val[col].SetValue('%.4g' % imax)
            conf.int_lo['int'] = imin
            conf.int_hi['int'] = imax
        else:
            for ix, cnam in ((0, 'red'), (1, 'green'), (2, 'blue')):
                imin, imax = data[:,:,ix].min(), data[:,:,ix].max()
                conf.int_lo[cnam] = imin
                conf.int_hi[cnam] = imax
                self.imin_val[cnam].SetValue('%.4g' % imin)
                self.imax_val[cnam].SetValue('%.4g' % imax)
        for ix, iwid in self.imax_val.items():
            try:
                iwid.Enable()
            except pyDeadObjectError:
                pass
        for ix, iwid in self.imin_val.items():
            try:
                iwid.Enable()
            except pyDeadObjectError:
                pass

    def onEnhanceContrast(self, event=None):
        """change image contrast, using scikit-image exposure routines"""
        enhance = event.IsChecked()
        conf = self.panel.conf
        data = self.panel.conf.data
        if len(data.shape) == 2: # intensity map        
            imin, imax = data.min(), data.max()
            if enhance:  
                imin, imax = numpy.percentile(data, [1, 99])
            conf.int_lo['int'] = imin
            conf.int_hi['int'] = imax
            self.imin_val['int'].SetValue('%.4g' % imin)
            self.imax_val['int'].SetValue('%.4g' % imax)
        if len(data.shape) == 3: # rgb map        
            for ix, cnam in ((0, 'red'), (1, 'green'), (2, 'blue')):
                imin, imax = data[:,:,ix].min(), data[:,:,ix].max()
                if enhance:  
                    imin, imax = numpy.percentile(data[:,:,ix], [1, 99])
                conf.int_lo[cnam] = imin
                conf.int_hi[cnam] = imax
                self.imin_val[cnam].SetValue('%.4g' % imin)
                self.imax_val[cnam].SetValue('%.4g' % imax)

        self.panel.redraw()
        
    def onThreshold(self, event=None, argu='hi', col='int'):
        if (wx.EVT_TEXT_ENTER.evtType[0] == event.GetEventType()):
            try:
                val =  float(str(event.GetString()).strip())
            except:
                return
        elif (wx.EVT_KILL_FOCUS.evtType[0] == event.GetEventType()):
            val = float(self.imax_val[col].GetValue())
            if argu == 'lo':
                val = float(self.imin_val[col].GetValue())
        if argu == 'lo':
            self.panel.conf.int_lo[col] = val
        else:
            self.panel.conf.int_hi[col] = val
        self.panel.redraw()

    def onInt_Autoscale(self, event=None, val=None):
        self.panel.conf.auto_intensity = event.IsChecked()
        if event.IsChecked():
            try:
                self.onDataChange(self.panel.conf.data)
            except:
                pass
            self.panel.redraw()

    def onCMapReverse(self, event=None):
        self.set_colormap()
        self.panel.redraw()

    def set_colormap(self, name=None, col='int'):
        conf = self.panel.conf
        try:
            if name is None:
                name = self.cmap_choice.GetStringSelection()
        except:
            return
        conf.cmap_reverse = False
        try:
            conf.cmap_reverse = (1 == int(self.cmap_reverse.GetValue()))
        except:
            pass
        if conf.cmap_reverse and not name.endswith('_r'):
            name = name + '_r'
        elif not conf.cmap_reverse and name.endswith('_r'):
            name = name[:-2]
        cmap_name = name
        try:
            conf.cmap[col] = getattr(mpl_colormap, name)
        except:
            conf.cmap[col] = get_cmap(name)
        if hasattr(conf, 'contour'):
            xname = 'gray'
            if cmap_name == 'gray_r':
                xname = 'Reds_r'
            elif cmap_name == 'gray':
                xname = 'Reds'
            elif cmap_name.endswith('_r'):
                xname = 'gray_r'
            conf.contour.set_cmap(getattr(mpl_colormap, xname))
        if hasattr(conf, 'image'):
            conf.image.set_cmap(conf.cmap[col])
        self.redraw_cmap(col=col)

        if hasattr(conf, 'highlight_areas'):
            if hasattr(conf.cmap[col], '_lut'):
                rgb  = [int(i*240)^255 for i in conf.cmap[col]._lut[0][:3]]
                col  = '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])
                for area in conf.highlight_areas:
                    for w in area.collections + area.labelTexts:
                        w.set_color(col)

    def redraw_cmap(self, col='int'):
        conf = self.panel.conf
        if not hasattr(conf, 'image'):
            return
        # conf.image.set_cmap(conf.cmap)
        self.cmap_img[col].set_cmap(conf.cmap[col])
        lo = conf.cmap_lo[col]
        hi = conf.cmap_hi[col]
        cmax = 1.0 * conf.cmap_range
        self.cmap_dat[col][:, :lo] = 0
        self.cmap_dat[col][:, lo:hi]  = numpy.linspace(0., 1., hi-lo)
        self.cmap_dat[col][:, hi:] = 1
        self.cmap_img[col].set_data(self.cmap_dat[col])
        self.cmap_canvas[col].draw()

    def onStretchLow(self, event=None, col='int'):
        high = self.cmap_hi[col].GetValue()
        self.StretchCMap(event.GetInt(), high, col=col)

    def onStretchHigh(self, event=None, col='int'):
        low = self.cmap_lo[col].GetValue()
        self.StretchCMap(low, event.GetInt(), col=col)

    def StretchCMap(self, low, high, col='int'):
        lo, hi = min(low, high), max(low, high)
        if (hi-lo)<2:
            hi = min(hi, self.panel.conf.cmap_range)
            lo = max(lo, 0)
        self.cmap_lo[col].SetValue(lo)
        self.cmap_hi[col].SetValue(hi)
        self.panel.conf.cmap_lo[col] = lo
        self.panel.conf.cmap_hi[col] = hi
        self.redraw_cmap(col=col)
        self.panel.redraw(col=col)

    def onLogScale(self, event=None):
        self.panel.conf.log_scale = not self.panel.conf.log_scale
        self.panel.redraw()

    def onCMapSave(self, event=None, col='int'):
        """save color table image"""
        file_choices = 'PNG (*.png)|*.png'
        ofile = 'Colormap.png'

        dlg = wx.FileDialog(self, message='Save Colormap as...',
                            defaultDir = os.getcwd(),
                            defaultFile=ofile,
                            wildcard=file_choices,
                            style=wx.SAVE|wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.cmap_canvas[col].print_figure(dlg.GetPath(), dpi=600)

    def save_figure(self,event=None, transparent=True, dpi=600):
        """ save figure image to file"""
        if self.panel is not None:
            self.panel.save_figure(event=event,
                                   transparent=transparent, dpi=dpi)

