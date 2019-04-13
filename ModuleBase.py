import wx
from datetime import datetime
from datetime import timedelta
import logging

logger = logging.getLogger("MagicMirror")

class ModuleBase(wx.Panel):
    '''
    Class for a base module consisting of a wx.Panel. Saves some boiler plate code

    Args:
        parent: a wx python window object
        *args: Not used...
        **kwargs: Keyword arguments are used for settings:
            updateFreqData (int): the time in seconds between data updates
            updateFreqGraphics (int): The time in seconds between updating graphics
        
    Key Attributes/Properties:
        temperature (float): Temperature in celsius
    '''
    def __init__(self, parent, *args, **kwargs):
        """Creates a panel with black background"""
        wx.Panel.__init__(self, parent, -1)
        self.SetBackgroundColour("Black")
        self.updateFreqData = kwargs.get("updateFreqData", 60)
        self.updateFreqGraphics = kwargs.get("updateFreqGraphics", 30)
        self.lastUpdateGraphics = datetime.now() - timedelta(days=1)
        self.lastUpdateData = datetime.now() - timedelta(days=1)

    def UpdateCheck(self, **kwargs):
        """Check if enough time has passed to update either data or graphics"""
        now = datetime.now()
        
        updateDataNow = (now - self.lastUpdateData).total_seconds() > self.updateFreqData
        updaupdateGraphicsNow = (now - self.lastUpdateGraphics).total_seconds() > self.updateFreqGraphics

        updateDataNow = kwargs.get("updateDataNow", updateDataNow)
        updateGraphicsNow = kwargs.get("updateGraphicsNow", updaupdateGraphicsNow)

        if updateDataNow is True:
            try:
                logger.debug("{}: Update data".format(type(self).__name__))
                self.UpdateData()
            except Exception as e:
                logger.error("Unexpected error updating dataset: {}".format(e), exc_info=True)

        if updateGraphicsNow is True:
            try:
                logger.debug("{}: Update graphics".format(type(self).__name__))
                self.UpdateGraphics()
            except Exception as e:
                logger.error("Unexpected error updating graphics: {}".format(e), exc_info=True)  

    def UpdateGraphics(self):
        """Update graphics. Remember to end with self.Thaw"""
        self.lastUpdateGraphics = datetime.now()

        self.Freeze()

        # Delete all objects in main container for this module
        for child in self.GetChildren():
            child.Destroy()

    def UpdateData(self):
        """Update data"""
        self.lastUpdateData = datetime.now()



class ClassName:
    '''
    Class to store a temperature in celsius

    Args:
        temperature (float): The temperature in celsius > -273
        *args: The variable arguments are used for...
        **kwargs: The keyword arguments are used for...

    Key Attributes/Properties:
        temperature (float): Temperature in celsius
    '''
    def __init__(self, temperature = 0, *args, **kwargs):
        self._temperature = temperature

    def ToFahrenheit(self):
        '''Converts current temperature in celsius to fahrenheit

        Args:
            None

        Returns:
            (float): The temperature in fahrenheit
        '''
        return (self.temperature * 1.8) + 32

    @property
    def temperature(self):
        """Gets and sets the temperature"""
        print("Getting value")
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if value < -273:
            raise ValueError("Temperature below -273 is not possible")
        print("Setting value")
        self._temperature = value
