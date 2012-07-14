
import configobj
try:
    from PySide import QtCore, QtGui
except ImportError:
    print "Could not load PySide (Qt) librairies, exiting."
    sys.exit(1)
    
#~ class Config(configobj.ConfigObj):
    #~ """ 
    #~ 
    #~ config.get('section') => config.section
    #~ """
    #~ email = ""
    #~ password = ""
    #~ 
    #~ def __getattr__(self, key):
        #~ return self.get(key)
#~ 
#~ class Section(configobj.Section):
    #~ pass

from gui.configwindow import Ui_Dialog
    
class ConfigUI(QtGui.QDialog):
    def __init__(self, config=None):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        if config:
            self.populate(config)
            
        self.ui.emailLine.setFocus()
    
    def populate(self, config):
        # account tab
        self.ui.emailLine.setText(config['user']['email'])
        self.ui.passwdLine.setText(config['user']['password'])
        self.ui.connectBox.setChecked(config['user'].as_bool('auto_connect'))
        
        # data tab
        self.ui.saveCsvBox.setChecked(config['data'].as_bool('save_csv'))
        self.ui.csvPathLine.setText(config['data']['csv_path'])
        self.ui.csvFormatLine.setText(config['data']['csv_format'])
        
        self.ui.saveXmlBox.setChecked(config['data'].as_bool('save_xml'))
        self.ui.xmlPathLine.setText(config['data']['xml_path'])
        
config = configobj.ConfigObj('micoach-backup.conf')
