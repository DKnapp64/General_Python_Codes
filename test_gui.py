#!/usr/bin/python

# simple python GUI

import wx

app = wx.App()

frame = wx.Frame(None, -1, 'test_gui.py')
frame.Show()

app.MainLoop()
