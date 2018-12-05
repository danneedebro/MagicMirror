#   -----------------------------
#   |Title                      |
#   -----------------------------
#   |           DATATABLE       |
#   |                           |
#   -----------------------------


from datetime import datetime
import wx
import VastTrafik.VastTrafik


class ModuleVastTrafik:
    def __init__(self, mainPanel, update_freq_graphics, update_freq_data):
        self.mainPanel = mainPanel
        self.update_freq_graphics = update_freq_graphics
        self.update_freq_data = update_freq_data
        self.updated_graphics = datetime.now()
        self.updated_data = datetime.now()
        self.font_departure = wx.FFont(12, wx.FONTFAMILY_MODERN,  flags=wx.FONTFLAG_STRIKETHROUGH)
        self.data = VastTrafik.VastTrafik.VastTrafik('fYzDg69mhe3eytZLUGiTBrFl2cQa', '0e163wTfFJAFteDgl607KhMkb2Ia', 9021014006480000)
        self.update()

    def update(self):
        now = datetime.now()
        self.updated_graphics = now
        self.mainPanel.Freeze()   # Freeze to avoid flickering

        # Delete all objects in main container for this module
        for myobj in self.mainPanel.GetChildren():
            #myobj.DestroyChildren()
            myobj.Destroy()

        # Create a sub panel to main panel that can be deleted next update
        panel = wx.Panel(self.mainPanel, style=wx.EXPAND|wx.ALIGN_CENTER)
        panel.Freeze()    # Freeze to avoid flickering

        LblTitle = wx.StaticText(panel, label='Avgångar från Svingeln {}'.format(self.data.departures['localDateTime'].strftime('%H:%M')), style=wx.ALIGN_LEFT)
        LblTitle.SetForegroundColour('White')
        LblTitle.SetFont(self.font_departure)

        sizerMain = wx.BoxSizer(wx.VERTICAL)

        number_of_rows = len(self.data.departures['Departures'])
        number_of_cols = 7   # 1 Short name, 2 End stop, 3 Departure in, 4 Access., 5 Departure in, 6 Access., 7 Track

        # Define flex grid sizer
        sizerFlexGrid = wx.FlexGridSizer(number_of_rows, number_of_cols, 2, 2)
        cnt = -1

        for departure in self.data.departures['Departures']:
            cnt += 1
            bg_color = departure['fgColor'][0]
            text_color = departure['bgColor'][0]
            track = departure['track'][0]
            time_delta1 = departure['dateTime'][0] - self.data.departures['serverDateTime'] - (now - self.data.departures['localDateTime'])
            time_to_departure1 = str(int(round(time_delta1.seconds/60,0))) if time_delta1.days >= 0 else 'Nu'
            accessibility1 = '\u267f' if departure['accessibility'][0] == 'wheelChair' else ''

            if len(departure['dateTime']) > 2:
                time_delta2 = departure['dateTime'][1] - self.data.departures['serverDateTime'] - (now - self.data.departures['localDateTime'])
                time_to_departure2 = str(int(round(time_delta2.seconds / 60, 0))) if time_delta2.days >= 0 else 'Nu'
                accessibility2 = '\u267f' if departure['accessibility'][1] == 'wheelChair' else ''
            else:
                time_to_departure2 = ''
                accessibility2 = ''

            fields = [None] * 7
            sizer_props = [None] * 4

            fields[0] = wx.StaticText(panel, label="{}".format(departure['sname'][0].center(7, ' ')), style=wx.ALIGN_CENTER)
            fields[0].SetBackgroundColour(bg_color)
            fields[0].SetForegroundColour(text_color)
            fields[1] = wx.StaticText(panel, label="{:15.12}".format(departure['direction'][0]))
            fields[2] = wx.StaticText(panel, label="{:>5}".format(time_to_departure1))
            fields[3] = wx.StaticText(panel, label="{}".format(accessibility1))
            fields[4] = wx.StaticText(panel, label="{:>5}".format(time_to_departure2))
            fields[5] = wx.StaticText(panel, label="{}".format(accessibility2))
            fields[6] = wx.StaticText(panel, label="{:>5}".format(track))
            for i in range(0, 7):
                if i == 0:
                    fields[i].SetBackgroundColour(bg_color)
                    fields[i].SetForegroundColour(text_color)
                else:
                    fields[i].SetForegroundColour('White')
                    #if cnt % 2 == 0: fields[i].SetBackgroundColour(wx.Colour(38, 38, 38, 255))  # Gray if even row

                fields[i].SetFont(self.font_departure)

                sizer_props[0] = fields[i]
                sizer_props[1] = 1
                sizer_props[3] = 0

                if i == 3 or i == 5:   # Accessibility fields
                    fields[i].SetBackgroundColour('Blue')
                    sizer_props[2] = wx.ALIGN_LEFT
                elif i == 0:   # Short name field
                    sizer_props[2] = wx.ALIGN_CENTER
                elif i == 1 or i == 2 or i == 4 or i == 6:
                    sizer_props[2] = wx.ALIGN_RIGHT

                # Add staticText objects to flex grid sizer
                sizerFlexGrid.Add(sizer_props[0], sizer_props[1], sizer_props[2], sizer_props[3])

        sizerFlexGrid.AddGrowableCol(1, 2)

        # Add header staticText and flex grid sizer to main (vertical) boxsizer
        sizerMain.Add(LblTitle, 0, wx.ALL|wx.EXPAND, 5)
        sizerMain.Add(sizerFlexGrid, 0, wx.ALL|wx.EXPAND, 5)

        panel.SetSizer(sizerMain)
        panel.Fit()
        self.mainPanel.Fit()

        panel.Thaw()          # This avoids flickering
        self.mainPanel.Thaw()

    def updateDataSet(self):
        self.updated_data = datetime.now()
        print('Hämtar data från VästTrafik')
        self.data.update()




