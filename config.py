
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
        self.accepted.connect(self.saveFromUI)
        
        if config:
            self.config = config
            self.populateUI()
            
        self.ui.emailLine.setFocus()
    
    def populateUI(self):
        # account tab
        self.ui.emailLine.setText(self.config['user']['email'])
        self.ui.passwdLine.setText(self.config['user']['password'])
        self.ui.connectBox.setChecked(self.config['user'].as_bool('auto_connect'))
        
        # data tab
        self.ui.saveCsvBox.setChecked(self.config['data'].as_bool('save_csv'))
        self.ui.csvPathLine.setText(self.config['data']['csv_path'])
        self.ui.csvFormatLine.setText(self.config['data']['csv_format'])
        
        self.ui.saveXmlBox.setChecked(self.config['data'].as_bool('save_xml'))
        self.ui.xmlPathLine.setText(self.config['data']['xml_path'])
        
    def saveFromUI(self):
        # account tab
        self.config['user']['email'] = self.ui.emailLine.text()
        self.config['user']['password'] = self.ui.passwdLine.text()
        self.config['user']['auto_connect'] = self.ui.connectBox.isChecked()
        
        # data tab
        self.config['data']['save_csv'] = self.ui.saveCsvBox.isChecked()
        self.config['data']['csv_path'] = self.ui.csvPathLine.text()
        self.config['data']['csv_format'] = self.ui.csvFormatLine.text()
        
        self.config['data']['save_xml'] = self.ui.saveXmlBox.isChecked()
        self.config['data']['xml_path'] = self.ui.xmlPathLine.text()
        
        self.config.write()
        
        self.config.reload()
        
        
config = configobj.ConfigObj('micoach-backup.conf')
