
import configobj
try:
    from PySide import QtCore, QtGui
except ImportError:
    print "Could not load PySide (Qt) librairies, exiting."
    sys.exit(1)

from gui.configwindow import Ui_Dialog
    
DEFAULT_CONFIG_FILENAME = "micoach-backup.conf"

DEFAULT_CONFIG_CONTENT = """# miCoach backup
# configuration file

[user]
# if empty, will be asked at launch
email = ""
password = ""
# connect at launch (works only if email/passwd already set)
auto_connect = False

[data]
# CSV
save_csv = True
# csv lines format 
# available: {time} {hr} {calories} {pace}
csv_format = {time}; {hr}; {calories}; {pace};
# storage path
# available: {username} {date} {name}
csv_path = data/{username}/{date} - {name}.csv

# XML
save_xml = True
# storage path
# available: {username} {date} {name}
xml_path = data/{username}/xml/{date} - {name}.xml

[network]
# 
#use_https = false

# 
#timeout = 0
"""

format_comment = lambda a: '\n'.join(a).replace("# ", "").strip()

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
        self.ui.emailLine.setToolTip(format_comment(config['user'].comments['email']))
        
        self.ui.passwdLine.setText(self.config['user']['password'])
        self.ui.passwdLine.setToolTip(format_comment(config['user'].comments['password']))
        
        self.ui.connectBox.setChecked(self.config['user'].as_bool('auto_connect'))
        self.ui.connectBox.setToolTip(format_comment(config['user'].comments['auto_connect']))
        
        # data tab
        self.ui.saveCsvBox.setChecked(self.config['data'].as_bool('save_csv'))
        self.ui.saveCsvBox.setToolTip(format_comment(config['data'].comments['save_csv']))
        
        self.ui.csvPathLine.setText(self.config['data']['csv_path'])
        self.ui.csvPathLine.setToolTip(format_comment(config['data'].comments['csv_path']))
        
        self.ui.csvFormatLine.setText(self.config['data']['csv_format'])
        self.ui.csvFormatLine.setToolTip(format_comment(config['data'].comments['csv_format']))
        
        self.ui.saveXmlBox.setChecked(self.config['data'].as_bool('save_xml'))
        self.ui.saveXmlBox.setToolTip(format_comment(config['data'].comments['save_xml']))
        
        self.ui.xmlPathLine.setText(self.config['data']['xml_path'])
        self.ui.xmlPathLine.setToolTip(format_comment(config['data'].comments['xml_path']))
        
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


try:
    config = configobj.ConfigObj(DEFAULT_CONFIG_FILENAME, file_error=True)
except IOError: 
    # config file doesn't exist, creating one
    with open(DEFAULT_CONFIG_FILENAME, 'w') as f:
        f.write(DEFAULT_CONFIG_CONTENT)
    config = configobj.ConfigObj(DEFAULT_CONFIG_FILENAME, file_error=True)
