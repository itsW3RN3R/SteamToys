import sys
import winreg
import psutil
import vdf
import yaml
import os
from PyQt5.QtWidgets import QApplication ,QMainWindow 
from PyQt5.QtCore import QUrl , Qt
from PyQt5.QtGui import QPixmap , QDesktopServices , QIcon
from PyQt5.uic import loadUi


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()


        loadUi("Ui.ui" , self)
        
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon("assets/logo.png"))
        

        self.stackedWidget.setCurrentWidget(self.pgPortal1)

        self.stackedWidget.setCurrentWidget(self.pgPortal1)
        self.navigate_to_portal_page()

        self.btnPortal.clicked.connect(self.navigate_to_portal_page)
        self.btnFee.clicked.connect(self.navigate_to_fee_page)
        self.btnTeleport.clicked.connect(self.set_login_user)
        self.cbUsers1.currentTextChanged.connect(self.yaml_data)
        self.exitIcon.mousePressEvent = self.exit_app
        self.steamProfile.mousePressEvent = self.steam_profile
        self.githubProfile.mousePressEvent = self.github_profile

        self.drag_position = None
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.drag_position is not None:
                self.move(event.globalPos() - self.drag_position)
                event.accept()


    def navigate_to_portal_page(self):
        global steam_registry_key ,user_names , path,steam_id , steamPath

        self.stackedWidget.setCurrentWidget(self.pgPortal1)
        #clearing combobox so it does not keep showing duplicated items
        self.cbUsers1.clear()


        #getting steam path
        steam_registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        steamPath, _ = winreg.QueryValueEx(steam_registry_key, "SteamPath")

        path = f"{steamPath}/config/avatarcache"
        files = os.listdir(path)
        for file in files:
            steam_id, file_ext = os.path.splitext(file)
            with open(f"{steamPath}/config/loginusers.vdf", "r",encoding='utf-8') as file:
                data = file.read()
                vdf_data = vdf.loads(data)
                user_names = vdf_data['users'][steam_id]['AccountName']
            try:
                self.cbUsers1.addItem(user_names)
                self.yaml_data()
            except:
                pass

    def yaml_data(self):
        # Add the new data
        new_data = {f'{user_names}': f'{steam_id}'}
        try:
            if os.stat('ids.yaml').st_size == 0:
                with open('ids.yaml', 'w') as file:
                    yaml.dump(new_data, file)
            else:
                with open('ids.yaml', 'r') as file:
                    data = yaml.safe_load(file)
                    if user_names in data:
                        pass
                    else:
                        data.update(new_data)
                        with open('ids.yaml', 'w') as file:
                            yaml.dump(data, file)
        
        except FileNotFoundError:
            with open('ids.yaml', 'w') as file:
                yaml.dump(new_data, file)
        except TypeError:
            data = {}
        
        get_user = self.cbUsers1.currentText()
        self.set_avatar(path, data.get(get_user))




    def set_avatar(self, path , steam_id):
        avatar_path = f"{path}/{steam_id}.png"
        avatar = QPixmap(avatar_path)
        self.lbAvatar.setPixmap(avatar)


           

    
    def set_login_user(self):

        # store the combobox value in variable so we can get it as string and not a Qstring if we were to use str()
        user_str = self.cbUsers1.currentText()
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\\Valve\\Steam', 0,winreg.KEY_ALL_ACCESS)as key: 
            winreg.SetValueEx(key, "AutoLoginUser", 0, winreg.REG_SZ, user_str)

        for proc in psutil.process_iter(): 
            if 'steam' in proc.name(): # filter all steam process 
                os.system("taskkill /f /im " + str(proc.pid)) # closing the filtered process
            else :
                pass

        os.startfile(f"{steamPath}/steam.exe")
        
        


    def navigate_to_fee_page(self):
        self.stackedWidget.setCurrentWidget(self.pgFee1)

        self.lePriceInput.textChanged.connect(self.priceInput)

    def priceInput(self):
        price = self.lePriceInput.text()
        try:
            if price.isdigit() or type(float(price)) == float: 
                self.calculator(price)
        except ValueError :
            self.lbYourCut.setText("ENTER DIGIT")

    def calculator(self , price):
            ur_cut = float(price) / 1.15
            price_to_sting = round(ur_cut , 2)
            self.lbYourCut.setText(f"Your Cut is \n {str(price_to_sting)} $")
    
    def steam_profile(self , event):
        link = "https://steamcommunity.com/id/SGOUM/"
        QDesktopServices.openUrl(QUrl(link))

    def github_profile(self , event):
        link = "https://github.com/itsW3RN3R"
        QDesktopServices.openUrl(QUrl(link))

    def exit_app(self , event):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
