#!/usr/bin/python
#
# simple example of MPlot
import sys
if not hasattr(sys, 'frozen'):
    try:
        import wxversion
        wxversion.ensureMinimal('2.8')
    except:
        pass
import wx
import numpy
import wxmplot

x   = numpy.arange(0.0,10.0,0.1)
y   = numpy.sin(2*x)/(x+2)
app = wx.App()

pframe = wxmplot.PlotFrame(output_title='simple')
pframe.plot(x, y, title='Test Plot',
            xlabel=r'  ${ R \mathrm{(\AA)}}$  ')

pframe.write_message('WXMPlot PlotFrame example: Try Help->Quick Reference')
pframe.Show()
#
app.MainLoop()


