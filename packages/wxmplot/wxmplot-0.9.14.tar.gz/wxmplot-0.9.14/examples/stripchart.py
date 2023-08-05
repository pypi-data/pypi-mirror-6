#!/usr/bin/python
import time
import numpy as np
import sys
if not hasattr(sys, 'frozen'):
    import wxversion
    wxversion.ensureMinimal('2.8')

import wx
from wx.lib import masked
from floatcontrol import FloatCtrl
from wxmplot import PlotPanel

def next_data():
    "simulated data"
    t0 = time.time()
    lt = time.localtime(t0)
    tmin, tsec = lt[4],lt[5]
    x = np.sin(tmin/12.0) + tsec/30. + np.random.random()/5.0
    return t0, x

class StripChartFrame(wx.Frame):
    def __init__(self, parent, ID, **kws):
        kws["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL

        wx.Frame.__init__(self, parent, ID, '',
                         wx.DefaultPosition, wx.Size(-1,-1), **kws)
        self.SetTitle("wxmplot StripChart Demo")

        self.tmin = 15.0

        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        menu = wx.Menu()
        ID_EXIT  = wx.NewId()
        ID_TIMER = wx.NewId()

        menu.Append(ID_EXIT, "E&xit", "Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
        self.SetMenuBar(menuBar)

        wx.EVT_MENU(self, ID_EXIT,  self.OnExit)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        sbar = self.CreateStatusBar(2,wx.CAPTION|wx.THICK_FRAME)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(11)
        sbar.SetFont(sfont)
        self.SetStatusWidths([-3,-1])
        self.SetStatusText('',0)

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        btnpanel = wx.Panel(self, -1)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)

        b_on  = wx.Button(btnpanel, -1, 'Start',   size=(-1,-1))
        b_off = wx.Button(btnpanel, -1, 'Stop',    size=(-1,-1))

        b_on.Bind(wx.EVT_BUTTON, self.onStartTimer)
        b_off.Bind(wx.EVT_BUTTON, self.onStopTimer)

        tlabel = wx.StaticText(btnpanel, -1, '  Time range:')
        self.time_range = FloatCtrl(btnpanel,  size=(75, -1),
                                    value=abs(self.tmin), precision=1)

        btnsizer.Add(b_on,   0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        btnsizer.Add(b_off,  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        btnsizer.Add(tlabel, 1, wx.GROW|wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        btnsizer.Add(self.time_range, 1, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)

        btnpanel.SetSizer(btnsizer)
        btnsizer.Fit(btnpanel)

        self.plotpanel = PlotPanel(self, messenger=self.write_message)
        self.plotpanel.BuildPanel()
        self.plotpanel.set_xlabel('Time from Present (s)')
        mainsizer.Add(btnpanel,       0, wx.GROW|wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)

        mainsizer.Add(self.plotpanel, 1, wx.GROW|wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)

        wx.EVT_TIMER(self, ID_TIMER, self.onTimer)
        self.timer = wx.Timer(self, ID_TIMER)
        self.Refresh()

    def write_message(self, msg, panel=0):
        """write a message to the Status Bar"""
        self.SetStatusText(msg, panel)

    def onStartTimer(self,event=None):
        self.count    = 0
        t0,y0 = next_data()
        self.ylist = [y0]
        self.tlist = [t0]
        self.tmin_last = -10000
        self.time0    = time.time()
        self.timer.Start(50)

    def onStopTimer(self,event=None):
        self.timer.Stop()

    def onTimer(self, event):
        self.count += 1
        etime = time.time() - self.time0
        self.tmin = float(self.time_range.GetValue())
        t1, y1 = next_data()
        self.tlist.append(t1)
        self.ylist.append(y1)
        tdat = np.array(self.tlist) - t1
        mask = np.where(tdat > -abs(self.tmin))
        ydat = np.array(self.ylist)

        n = len(self.ylist)
        if n <= 2:
            self.plotpanel.plot(tdat, ydat)
        else:
            self.plotpanel.update_line(0, tdat, ydat, draw=True)
            self.write_message(" %i points in %8.4f s" % (n,etime))

        lims = self.plotpanel.get_viewlimits()
        try:
            ymin, ymax = ydat[mask].min(), ydat[mask].max()
        except:
            ymin, ymax = ydat.min(), ydat.max()
        tmin = max(int(min(tdat)) - 1.0, -self.tmin)
        if (ymin < lims[2] or ymax >  lims[3] or
            tmin != self.tmin_last or time.time()-self.last_update > 2):
            self.tmin_last = tmin
            self.last_update = time.time()
            self.plotpanel.set_xylims((tmin, 0, ymin, ymax))

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "wxmplot example: stripchart app",
                              "About WXMPlot test", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Destroy()

app = wx.App()
f = StripChartFrame(None,-1)
f.Show(True)
app.MainLoop()
#
