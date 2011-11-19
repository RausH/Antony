#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2009, 2010, 2011 Reinhard Fritsch
#    Copyright (C) 2010 Marc Fahrner et al. (French translation)
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################

# For License and Copyright of EXIF.py please refer to the header in the EXIF.py file

# This is going to be the 21th release candidate of the Kronstorf Scout Image DB it 
# it is based on Antony.py RC20
# It aims to provide a means to associate metadata to images (year, event, 
# photographer, people on the image and some comments). Most importantly 
# it enables a rather small group of people who can meet physically to share and
# syncronize their archives, images and associated information (e.g. by storing
# them on an external hd). Moreover it allows to export Images out of the db for
# uses in presentations or compilations.
# It is implemented using python and platform independent toolkits to ensure future
# usability.
#
# TODO 
#    statusbar: alle messages die wichtig sind, oder den eindruck vermitteln, dass das program arbeitet in der statusbar anzeigen (überlgen wegen der sql statements); ERLEDIGT
#    möglichkeit nach bildern zu suchen, bei denen keine weiteren daten eingetragen sind (die sonst nicht auffindbar sind) ERLEDIGT (bei Suche mit leeren feldern wird nach bildern gesucht, die kein Jahr, kein Ereignis und keinen Author haben)
#    PEP8 naming conventions durcharbeiten. die Class und attribute namen danach ausrichten (auch PyQt4 beachten)
#   die diversen verzeichnisse, die zur zeit noch fest einprogramiert sind (das db verzeichnis, das bilder verzeichnis etc.) abh von variablen machen (zB als basis verzeichnis jenes der db heranziehen, und dann das merken, aus dem das letzte bild geladen wurde) - ERLEDIGT: durch eingabe eine "" wird immer das aktuelle arbeitsverzeichnis herangezogen (also so wie ich es geplant hätte)
#    anbieten von ein paar Standard Kommentaren zum anhackerln (checkbox) zB 
#    [] Gruppenfoto     [] Kochen
#    [] Lagerfeuer      [] Aufbau
#    ev. schönere lösung fürs syncen, keine tabula rasa, sondern das sync zeugs für die angezeigten bilder in das md5TOimdata dic dazu schreiben
#    EXIF data einfügen
#    beautify program exit upon closure of start dialog, todate it exits because of an error. however it would be nice to make it quit because the dialog is closed without specifing any db and not because this fact causes an error (see below Dialog return value) DONE
#    ERLEDIGT: close dbs: after db sync close the sync db connection to be ready for loading another sync db
#    DONE: unifiy duplicate functionality in export_singleImage/export_allImages and update_singleImage/update_allImages to functions (e.g. def update_Image(md5) and export_Image(item)) DONE: as suggested in the todo
#    DONE: add drag and drop support for adding images to the database (draging images from the filemanager to the images display area of antony) - in order to get drag and drop support the ImLoad method has to be rewritten (esp. the things happening in the for loop should go to a new function (e.g. def show_fresh_images(filename) in order to access the database insertion mechanisms for both, the dialog and drag and drop (in case i get the filename out of this drag and drop event))) DONE: drop with help from: http://tech.xster.net/tips/pyqt-drag-images-into-list-widget-for-thumbnail-list/
#    DONE: change the window title to "antony - The decentralized image database" 
#      DONE: changed to Antony
#    add help system
#    add Drag from Antony to filemanager (image and metadata) is copied to folder
#    encode exported metadata according to locale.getdefaultlocale()[1]
#    part. DONE: implement the startDia with return values (if no filename -> quit()) and load 
#      the db outside of the dialog (part. DONE because now i have return values and i quit the app i case the dialog has been closed, but i still load the db from within the dialog)
#    implement image view functionality (e.g. double click on image starts fullscreen
#      view of this image; navigation by cursor keys through all images loaded; due to thumbnailing it might be necessary to load images sequentially from the filesystem -> add address of image in filesystem to Image Object (ist schon dort fs_fname); attention for images allready in db drag and drop or loading results in a wrong fs_fname) lsg: bild immer von original position laden (wird schwierig, wenn bild gesucht wurde, da werden auch die original position und der fs filename eingetragen, allerdings kann es sein, dass das original nicht mehr existiert, also nur der fs stimmt -> müßte dann der richtige fs name eingetragen werden (falls md5 schon in db fs filename mit dem aus der db überschreiben)
#         PROGRESS: in object SingleIm the fs_filename referres to the name of the image in the fs in all cases (search, load new image and load existing image); found an example for an imageviewer on the internet (http://www.riverbankcomputing.com/pipermail/pyqt/2010-March/026116.html) and saved it ot /Prog/weitere_downloads/image_viewer.py; implemented a viewer GUI according to the example; single click on image updates db double click shows the viewer GUI; for the single vs double click system i used code from http://www.mail-archive.com/pyqt@riverbankcomputing.com/msg14531.html.
#    DONE: add .tif to IMAGE_FORMATS
#    DONE (but not hard tested): Prevent overwriting of images by copying from sync to master during sync (check if filename allready in master and increase image number in this case; like in the general image addition process) line 528ff
#      DONE: implemented a separate function file_in_fs_check (because this functionality is needed twice)
#    TODO: bei image viewer die resize fkt mit timer connecten und erst nach ablauf der zeit die bilder größe neu berechnen (unnötig)
#   DONE: TODO: bei image viewer die v_max und die h_max separat berechnen und die bilder entsprechend skalieren (damit auch breite bilder bis an den rand gehen)
#    DONE: TODO: check image orientation in exif and rotate them in the viewer 
#    DONE: TODO: make the rotate_image method (in Viewer) a "global" function and rotate the images for the imagedisplay area (liwi) too. (get the tags around line 220 and rotate image around line 249 and 282; the images that have been searched are not opened "rb" so i have to get the tags septerately ~at line 453 and rotate at line 455
#     Partiall DONE: TODO: use left and right key in viewer to navigate and r and l to rotate the image-> rewrite the rotation routines to accept the rotation and not the tags dict, otherwise i would have to generate a dic in the navigation ... (see class ViewerDialog); DONE: r and l key rotate image (but no left and right key functionality and no rewrite of rotation routine due to practical reasons
#     DONE: TODO: automatically append new entered data to the respective comboBoxes (not just after pressing "enter") added a new method "add_cb(self)" at about line 340
#     DONE: TODO: reset the viewer after clicking "Clear display" (or close it), this should help to avoid that the viewer displays different images than on the image display area; added a call to viewer.close() to ImClear at about line 310
#     Done: TODO: Sort filenames before loading files into the image view area to preserve chronology as files in digital cameras are named chronologically ascending.
#	ADDED: closeEvent to StartGui to be able to do someting when the mainwindow is closed (e.g. close the viewer)
#       CHANGED: The event metadata has been splitt into event name, event type, event location;

import locale
import datetime
import codecs
import hashlib
import sys
from PyQt4 import QtGui, QtCore
#from PyQt4.QtCore import QString as qstr
#from pysqlite2 import dbapi2 as sqlite3
import sqlite3 #was ist der unterschied zwischen dem internen modul und pysqlite2
from zlib import adler32
from shutil import copy2
import os
import os.path
import EXIF
from FotoDB import Ui_MainWindow 
from SelectStartDB_dialogue import Ui_Dialog
from ViewerUI import Ui_Dialog as Ui_Viewer

# TODO die sache mit dem encoding aus der windows version übernehmen. ERLEDIGT:
# section to set the encoding right in the py2exe windows version. does no harm in the other versions...
#reload(sys) 
#if hasattr(sys,"setdefaultencoding"):
#    sys.setdefaultencoding("utf8")


ICON_SIZE=250   # Global Variable to set the image scaling and icon size
IMAGE_FORMATS= ["BMP","bmp","GIF","gif","JPG","jpg","PEG","peg","PNG","png","IFF","iff","TIF","tif"] #PEG...JPEG and IFF ...TIFF; global variable to identify imagefiles upon drag and drop

def uniDEcode(string): # using utf8 encoding in all strings (better than modifying site.py)
    if string is None: # should only be the case in db_sync
        return string
    elif not isinstance(string,unicode) and not isinstance(string,QtCore.QString) and isinstance(string,str):
        #print("From UTF-8 TO UNICODE")
        return unicode(string,"utf8")
    elif isinstance(string, QtCore.QString):
        #print("__MELDUNG: QString conversion!__")
        string=string.toUtf8()
        #print(type(string))
        return unicode(string,"utf8")
    elif isinstance(string,unicode):
        #print("__________found an unicode string oh surprize__________")
        return string
    elif isinstance(string,long) or isinstance(string,int):
        return unicode(string)
    else:
        print("not handelt string type")
        print(type(string))
        
def uniENcode(string):
    if isinstance(string,unicode):
        return string.encode("utf8")
    elif isinstance(string, QtCore.QString):
        string=string.toUtf8()
        return str(string)
    elif isinstance(string,long):
        return str(string)
    elif isinstance(string, str):
        return string
    else:
        print("you want to get a str from that???")
        print(type(string))

def file_in_fs_check(proposed_fn): # function that checks whether or not a filename exist in the fs
    while os.path.exists(uniDEcode(os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir), uniDEcode(proposed_fn)))):
        proposed_fn=QtCore.QString(proposed_fn)
        name=proposed_fn.split(".")[0]
        ending=proposed_fn.split(".")[1]
        if name[-3] =="_":
            try:
                num=name[-2:]
                num=int(num)+1
                if num<10:
                    num="0"+str(num)
                name=name[:-2]
                name.append(str(num))
            except ValueError:
                name.append("_01")
        else:
                name.append("_01")    
        
        proposed_fn=name
        proposed_fn.append(".") 
        proposed_fn.append(ending)
    return uniDEcode(proposed_fn)
    
def rotate_image(work_image,tags):
    try:
        if tags['Image Orientation'].printable == "Rotated 90 CW":
            return work_image.transformed(QtGui.QTransform().rotate(90.0))
        elif tags['Image Orientation'].printable == "Rotated 90 CCW":
            return work_image.transformed(QtGui.QTransform().rotate(270.0))
        else:
            return work_image
    except KeyError:  # for all those images where there is no orientation EXIF tag
        return work_image

class StartGui (QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.liwi=ThumbListWidget(self.ui.centralwidget)
        self.ui.ImDisplay.addWidget(self.liwi)

        self.md5TOimdata={} # dictionary um die md5 eines bildes mit den bildaten zu verbinden /dictionary relating md5 to data associated with an image using the class SingleIm
        self.timer = QtCore.QTimer()  # part of single vs double click detection system
        self.timer.setInterval(500)
        self.timer.setSingleShot(True)
        
        self.connect(self.timer,QtCore.SIGNAL("timeout()"), self.update_export_decide) # take it as single click
        self.connect(self.ui.ImLoad_button, QtCore.SIGNAL("clicked()"),self.ImLoad)
        self.connect(self.ui.ImClear_button, QtCore.SIGNAL("clicked()"),self.ImClear)
        self.connect(self.ui.People_comboBox, QtCore.SIGNAL("activated(const QString&)"), self.people2list)
        self.connect(self.ui.ClearPeopleList_button, QtCore.SIGNAL("clicked()"), self.clear_piwili)
        self.connect(self.ui.RemovePeople_button, QtCore.SIGNAL("clicked()"), self.remove_single_name)
        #self.connect(self.liwi,QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.start_viewer) # so richtig fkt die unterscheidung der einfach und doppel klicks nicht (auch bei doppelklick wird in die db eingertragen)
        #self.connect(self.liwi,QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.update_export_decide) #self.update_singleImage)
        self.connect(self.liwi,QtCore.SIGNAL("itemClicked(QListWidgetItem*)"), self.double_click_detect)
        self.connect(self.ui.AllInsert_button, QtCore.SIGNAL("clicked()"), self.update_allImages)
        self.connect(self.ui.SearchDB_button, QtCore.SIGNAL("clicked()"),self.search_btn_DB)
        self.connect(self.ui.ExportAll_button, QtCore.SIGNAL("clicked()"), self.export_allImages)
        self.connect(self.ui.dbSync_pushButton, QtCore.SIGNAL("clicked()"), self.db_sync)
        self.connect(self.liwi, QtCore.SIGNAL("dropped"), self.load_Images)
        
    def closeEvent(self,event): # close the viewer too if the main window is closed
        viewer.close()
        event.accept()
    
    def double_click_detect(self): # if no double click then the timer will emmit the timeout() signal and call the single click action (update_export_decide())
        if not self.timer.isActive():
            self.timer.start() 
        else:
            self.timer.stop()
            self.start_viewer()
            
    def update_export_decide(self):
        if self.ui.insertRadioButton.isChecked():
            self.update_singleImage()
        else:
            self.export_singleImage()
    
    def start_viewer(self):
        #self.viewer=ViewerDialog() # ob das nicht ins Hauptprogram (ganz unten gehört) und hier nur das show() so kann der dialog nicht mehrmals geöffnet werden
        #self.viewer.showViewer()
        row=self.liwi.currentRow()
        fileList=[]
        for index in range(row, self.liwi.count()):
            fileList.append(uniDEcode(self.liwi.item(index).data(32).toString()))
        for index in range(row):
            fileList.append(uniDEcode(self.liwi.item(index).data(32).toString()))
        viewer.set_view(fileList)
        viewer.showViewer() #this is the version inititalization in the main prog.
    
    def ImLoad(self):
        """ This method is called by clicking on the "load images" button. It loads the 
            selected images from the source and copies them to the db filesystem.
            Of course it is checked whether the image is allready in the db (no insertion
            happens) or if its is even loaded (not going to be loaded twice) (the last part
            is moved to a new function def load_Images(fileNames) to be able to implement 
            drag and drop features """
        fileNames = QtGui.QFileDialog.getOpenFileNames(self,
         self.tr("Load Image(s)"), "", self.tr("Image files (*.png *.jpg *.bmp *.tif)"))
        #insert check for image filenames - i don't think this is necessary because only imagefiles are presented for selection
        fileNames.sort()
        self.load_Images(fileNames) 

    def load_Images(self,fileNames):
        for fileName in fileNames:  
            fs_fname=QtCore.QString("")
            self.liwiit=QtGui.QListWidgetItem() # ob das ein self sein muss?
    
            im_file=open(uniDEcode(fileName),'rb')
            imdata=im_file.read()
            hs=hashlib.md5()
            hs.update(imdata)
            im_file.seek(0)
            tags = EXIF.process_file(im_file, details=False)
            day=datetime.date.today()
            fs_fname.append(str(day))
            fs_fname.replace("-","")
            fs_fname.append("_")
            fs_fname.append(os.path.split(os.path.split(os.path.split(uniDEcode(fileName))[0])[0])[1])
            fs_fname.append("_")
            fs_fname.append(os.path.split(os.path.split(uniDEcode(fileName))[0])[1])
            fs_fname.append("_")
            fs_fname.append(os.path.split(uniDEcode(fileName))[1])
            # following: an insurance against overwriting files in the filesystem
            fs_fname=file_in_fs_check(fs_fname)
                           
            self.Image=SingleIm(uniDEcode(hs.hexdigest()),fileName,fs_fname) #Constructor of Single Image; TODO sollte das nicht erst dann erfolgen, wenn sichergestellt ist, dass das image noch nicht geladen ist (in den untenstehenden if und elif stmts) Nicht notwendig oder nützlich/ this todo questions the place in the code for this constructor; conclusion this place seems right
            im_file.close()
    
            search_dic={"md5":self.Image.md5check}
            row=master_db.search_ImageDB(search_dic) # check: image allready in db
            for i in range(len(row)):
                print(row[i][0])
    
            if not row:   # image not in db
                self.set_statusbar(uniDEcode(self.tr("Insert, copy and display new picture")))
                self.md5TOimdata[self.Image.md5check]=self.Image  # dictionary containing all images now shown in the window, the key is the md5 of the image
                #pixmp=rotate_image(QtGui.QPixmap(fileName),tags)
                pixmp=rotate_image(QtGui.QImage(fileName),tags)
                #icon=QtGui.QIcon(pixmp.scaledToHeight(ICON_SIZE)) #scaledToHeight spart massiv speicherplatz
                icon=QtGui.QIcon(QtGui.QPixmap(pixmp.scaledToHeight(ICON_SIZE)))
                self.liwiit.setIcon(icon)
                self.liwiit.setToolTip(self.Image.generateToolTip())
                self.liwiit.setData(32,uniDEcode(os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir), uniDEcode(self.Image.fs_filename))))
                self.liwi.addItem(self.liwiit) 
                self.Image.db_insert()
                copy2(uniDEcode(fileName),uniDEcode(os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir), uniDEcode(self.Image.fs_filename)))) # file copied to the DB filesystem
       
            elif row and not self.Image.md5check in self.md5TOimdata.keys(): # image in db but not shown in window -> show it (and all its metadata)
                self.set_statusbar(uniDEcode(self.tr("Picture already in database, loading to display")))
                
                self.Image.cksum=row[0][0]
                self.Image.people_check=row[0][9]
                self.Image.addyear(row[0][2])
                self.Image.addEvent_name(row[0][3])
                self.Image.addEvent_type(row[0][10])
                self.Image.addEvent_loc(row[0][11])
                auth_ok=self.Image.addauth(row[0][4])
                self.Image.fs_filename=row[0][7] #reset fs_filename (to be able to load image from, fs; damit neu eingefügte, bereits vorhandene und gesuchte bilder für image view von der gleichen quelle geladen werden können

                if row[0][5] is None:
                    comment=""
                else:
                    comment=row[0][5]
    
                self.Image.addcomment(comment)

                prow=master_db.search_People(self.Image.md5check)
                for name in prow:
                    self.Image.addperson(name)

                self.md5TOimdata[self.Image.md5check]=self.Image 

                pixmp=rotate_image(QtGui.QImage(fileName),tags)  # replaced QPixmap by QImage
                icon=QtGui.QIcon(QtGui.QPixmap(pixmp.scaledToHeight(ICON_SIZE)))
                self.liwiit.setIcon(icon)
                self.liwiit.setToolTip(self.Image.generateToolTip())
                self.liwiit.setData(32,uniDEcode(os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir), uniDEcode(self.Image.fs_filename))))
                self.liwi.addItem(self.liwiit)
            self.set_statusbar(uniDEcode(self.tr("New pictures loaded: Ready")))
    
    def ImClear(self): # clears the image show and sets all relevant input fields to the initital conditions, moreover clears the dictionary
        self.liwi.clear()
        self.md5TOimdata={}
        self.populate_cb()
        viewer.close()
        self.set_statusbar(uniDEcode(self.tr("Tabula rasa: Ready")))

    def clear_piwili(self):
        self.ui.people_listWidget.clear()
        self.ui.People_comboBox.setCurrentIndex(0)

    def remove_single_name(self):
        nix=self.ui.people_listWidget.takeItem(self.ui.people_listWidget.currentRow())
        self.ui.People_comboBox.setCurrentIndex(0)

    def populate_cb(self): # befüllen der comboBoxen aus der db/ Setting and resetting comboBoxes using the database
        self.ui.year_comboBox.clear()
        self.ui.event_comboBox.clear()
        self.ui.etype_comboBox.clear()
        self.ui.loc_comboBox.clear()
        self.ui.Author_cb.clear()
        self.ui.People_comboBox.clear()
        self.ui.Comment_cb.clear()
        self.ui.CommentInput_text.clear()
        years=master_db.search_distinct({"year":"images"})
        years.insert(0,"")
        self.ui.year_comboBox.addItems(years)

        events=master_db.search_distinct({"event":"images"})
        events.insert(0,"")
        self.ui.event_comboBox.addItems(events)
        
        e_types=master_db.search_distinct({"future1":"images"}) # event type is stored in the future1 column in the db 
        e_types.insert(0,"")
        self.ui.etype_comboBox.addItems(e_types)
        
        locs=master_db.search_distinct({"future2":"images"}) # event location is stored in future2 in the db
        locs.insert(0,"")
        self.ui.loc_comboBox.addItems(locs)

        authors=master_db.search_distinct({"author":"images"})
        authors.insert(0,"")
        self.ui.Author_cb.addItems(authors)
        
        comments_li=master_db.search_distinct({"comment":"images"})
        com_cb_li=[""]
        for comment_str in comments_li:
            com_li=QtCore.QString(comment_str).split(";",QtCore.QString.SkipEmptyParts)
            for com in com_li:
                com=com.trimmed()
                if not com in com_cb_li:
                    com_cb_li.append(com)
        com_cb_li.sort()
        self.ui.Comment_cb.addItems(com_cb_li)

        persons=master_db.search_distinct({"pers":"Im2People"})
        persons.insert(0,"")
        self.ui.People_comboBox.addItems(persons)
        self.clear_piwili()
        
    def add_cb(self):  # add newly added content to comboBoxes;
        if self.ui.year_comboBox.findText(self.ui.year_comboBox.\
                currentText().replace("'","`"))==-1 or\
                self.ui.year_comboBox.findText(self.ui.year_comboBox.\
                currentText())==-1:
            self.ui.year_comboBox.addItem(self.ui.year_comboBox.
                                          currentText().replace("'","`"))
        if self.ui.event_comboBox.findText(self.ui.event_comboBox.\
                currentText().replace("'","`"))==-1 or\
                self.ui.event_comboBox.findText(self.ui.event_comboBox.\
                currentText())==-1:
            self.ui.event_comboBox.addItem(self.ui.event_comboBox.
                                           currentText().replace("'","`"))
        
        if self.ui.etype_comboBox.findText(self.ui.etype_comboBox.\
                currentText().replace("'","`"))==-1 or\
                self.ui.etype_comboBox.findText(self.ui.etype_comboBox.\
                currentText())==-1:
            self.ui.etype_comboBox.addItem(self.ui.etype_comboBox.
                                           currentText().replace("'","`"))
                                           
        if self.ui.loc_comboBox.findText(self.ui.loc_comboBox.\
                currentText().replace("'","`"))==-1 or\
                self.ui.loc_comboBox.findText(self.ui.loc_comboBox.\
                currentText())==-1:
            self.ui.loc_comboBox.addItem(self.ui.loc_comboBox.
                                           currentText().replace("'","`"))
        
        if self.ui.Author_cb.findText(self.ui.Author_cb.\
                currentText().replace("'","`"))==-1 or\
                self.ui.Author_cb.findText(self.ui.Author_cb.currentText())==-1:
            self.ui.Author_cb.addItem(self.ui.Author_cb.currentText().replace("'","`"))
            
        name_ok=1
        if self.ui.People_comboBox.currentText():
            name_ok=self.people2list(self.ui.People_comboBox.currentText())
            
        if self.ui.Comment_cb.findText(self.ui.Comment_cb.\
                currentText().replace("'","`"))==-1 or\
                self.ui.Comment_cb.findText(self.ui.Comment_cb.currentText())==-1:
            self.ui.Comment_cb.addItem(self.ui.Comment_cb.currentText().replace("'","`"))
        
        return name_ok
        

    def people2list(self,name): # eintragen der personen die in der comboBox ausgewählt wurden in die widget liste die die namen tragen sollen
        if name.count(";") is 2:
            if not self.ui.people_listWidget.findItems(name,QtCore.Qt.MatchExactly) or not\
                    self.ui.people_listWidget.findItems(name.replace("'","`"),QtCore.Qt.MatchExactly):
                piliwiit=QtGui.QListWidgetItem()
                piliwiit.setText(name.replace("'","`"))
                self.ui.people_listWidget.addItem(piliwiit)
            if self.ui.People_comboBox.findText(self.ui.People_comboBox.\
                   currentText().replace("'","`"))==-1 or\
                   self.ui.People_comboBox.findText(self.ui.People_comboBox.currentText())==-1:
                self.ui.People_comboBox.addItem(self.ui.People_comboBox.currentText().replace("'","`"))
            self.set_statusbar(uniDEcode(self.tr("Name o.k.")))
            return 1
        else:
            self.set_statusbar(uniDEcode(self.tr("WARNING: Only names containing two ; are accepted")))
            return 0

    def update_allImages(self): 
        auth_ok=1
        self.set_statusbar(uniDEcode(self.tr("Recording data for all displayed pictures to database")))
        name_ok=self.add_cb()
        for row in range(self.liwi.count()):
            item=self.liwi.item(row)
            auth_ok=self.update_Image(item)
        if auth_ok==1 and name_ok==1:
            self.set_statusbar(uniDEcode(self.tr("All data recorded: Ready")))
        else:
            self.set_statusbar(uniDEcode(self.tr("WARNING: Only names containing two ; are accepted")))
        # TODO check ob fürs update des images uniDEcode notwendig ist (siehe update_singleImage) oder obs nicht gebraucht wird (siehe update_allImages)    

    def update_singleImage(self):
        auth_ok=1
        name_ok=self.add_cb()
        item=self.liwi.currentItem()
        auth_ok=self.update_Image(item)
        if auth_ok==1 and name_ok==1:
            self.set_statusbar(uniDEcode(self.tr("Recorded data for single picuture: Ready")))
        else:
            self.set_statusbar(uniDEcode(self.tr("WARNING: Only names containing two ; are accepted")))
        
    def update_Image(self,item):
        md5=item.toolTip()#.split("<")[0]
        md5=uniDEcode(md5.split("<")[0])
        self.md5TOimdata[md5].addyear(self.ui.year_comboBox.currentText().replace("'","`"))
        self.md5TOimdata[md5].addEvent_name(self.ui.event_comboBox.currentText().replace("'","`"))
        self.md5TOimdata[md5].addEvent_type(self.ui.etype_comboBox.currentText().replace("'","`"))
        self.md5TOimdata[md5].addEvent_loc(self.ui.loc_comboBox.currentText().replace("'","`"))
        auth_ok=self.md5TOimdata[md5].addauth(self.ui.Author_cb.currentText().replace("'","`"))
        #comment=self.ui.CommentInput_text.toPlainText().replace("'","`")  #delete after test
        self.md5TOimdata[md5].addcomment(self.ui.Comment_cb.currentText().replace("'","`"))

        for i in range(self.ui.people_listWidget.count()):
            pitem=self.ui.people_listWidget.item(i)
            name=pitem.text().replace("'","`")
            self.md5TOimdata[md5].addperson(name)

        item.setToolTip(self.md5TOimdata[md5].generateToolTip())
        self.liwi.setCurrentItem(item) 
        self.md5TOimdata[md5].update_DB()
        return auth_ok

    def export_allImages(self):
        export_dir=QtGui.QFileDialog.getExistingDirectory(self, uniDEcode(self.tr("Export Folder")), "")
        if export_dir:
            for row in range(self.liwi.count()):
                item=self.liwi.item(row)
                self.export_Image(item,export_dir)
               
            self.set_statusbar(uniDEcode(self.tr("Exporting finished: Ready")))
        else:
            self.set_statusbar(uniDEcode(self.tr("Export failed: Ready")))

    def export_singleImage(self):
        export_dir=QtGui.QFileDialog.getExistingDirectory(self, uniDEcode(self.tr("Export Folder")), "")

        if export_dir:
            item=self.liwi.currentItem()
            self.export_Image(item,export_dir)
          
            self.set_statusbar(uniDEcode(self.tr("Export finished: Ready")))
        else:
            self.set_statusbar(uniDEcode(self.tr("Export failed: Ready")))
    
    def export_Image(self,item,export_dir):
        tt=item.toolTip()
        md5=uniDEcode(tt.split("<")[0])

        src_f=os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir),
         uniDEcode(self.md5TOimdata[md5].fs_filename))
        dst_f=os.path.join(uniDEcode(export_dir),
         uniDEcode(self.md5TOimdata[md5].fs_filename))
 
        copy2(src_f,dst_f)
        meta_fn=QtCore.QString(self.md5TOimdata[md5].fs_filename.split(".")[0])
        meta_fn.append(".txt")
        meta_fn=os.path.join(uniDEcode(export_dir),uniDEcode(meta_fn))
        tt.replace("<br>","\n")
        tt.replace("<i>","")
        tt.replace("</i>","")
        tt.replace("&nbsp;"," ")
        tt.append("\n")
        f = open(meta_fn,'w')
        f.write(tt)
        f.close()

    def search_btn_DB(self):  # searching the db and displaying the resulting images 
        self.set_statusbar(uniDEcode(self.tr("Searching database")))
        search_dic={}
        if self.ui.year_comboBox.currentText():
            search_dic["year"]=self.ui.year_comboBox.currentText().replace("'","`")
        if self.ui.event_comboBox.currentText():
            search_dic["e_name"]=self.ui.event_comboBox.currentText().replace("'","`")
        if self.ui.etype_comboBox.currentText():
            search_dic["e_type"]=self.ui.etype_comboBox.currentText().replace("'","`")
        if self.ui.loc_comboBox.currentText():
            search_dic["e_loc"]=self.ui.loc_comboBox.currentText().replace("'","`")
        if self.ui.Author_cb.currentText():
            search_dic["author"]=self.ui.Author_cb.currentText().replace("'","`")
       # if self.ui.CommentInput_text.toPlainText():  # delete after test
        #    search_dic["comment"]=self.ui.CommentInput_text.toPlainText().replace("'","`")
        if self.ui.Comment_cb.currentText():
            search_dic["comment"]=self.ui.Comment_cb.currentText().replace("'","`")
        if self.ui.people_listWidget.count():
            name=[]
            for i in range(self.ui.people_listWidget.count()):
                pitem=self.ui.people_listWidget.item(i)
                name.append(pitem.text().replace("'","`"))
            search_dic["pers"]=name
    
        rows=master_db.search_ImageDB(search_dic)
        if not rows:
            self.set_statusbar(self.tr("Your search parameters did not fit for any picture in the database"))
        for row in rows:
            if not row[1] in self.md5TOimdata.keys(): 
                self.set_statusbar(row[7])
                self.liwiit=QtGui.QListWidgetItem()
                self.Image=SingleIm(row[1],row[8],row[7])
                self.Image.cksum=row[0]
                self.Image.people_check=row[9]
                self.Image.addyear(row[2])
                self.Image.addEvent_name(row[3])
                self.Image.addEvent_type(row[10])
                self.Image.addEvent_loc(row[11])
                self.Image.addauth(row[4])
            
                if row[5] is None:
                    comment=""
                else:
                    comment=row[5]
    
                self.Image.addcomment(comment)

                prow=master_db.search_People(self.Image.md5check)
                for name in prow:
                    self.Image.addperson(name)
            
                self.md5TOimdata[self.Image.md5check]=self.Image 
                #Oldstyle icon via qpixmap lets test it without the slow qpixmap
                #Newest style: rotate images according to EXIF data
                f=open(os.path.join(uniDEcode(location.pathName), uniDEcode(self.Image.fs_path), uniDEcode(self.Image.fs_filename)), 'rb')  # according to EXIF.py
                tags = EXIF.process_file(f, details=False)
                f.close()
                # replaced QPixmap by QImage
                pixmp=rotate_image(QtGui.QImage(os.path.join(uniDEcode(location.pathName), uniDEcode(self.Image.fs_path), uniDEcode(self.Image.fs_filename))),tags)
                icon=QtGui.QIcon(QtGui.QPixmap(pixmp.scaledToHeight(ICON_SIZE)))
                """ New style it got even worse ... so back to the old one
                icon=QtGui.QIcon()
                icon.addFile(os.path.join(uniDEcode(location.pathName), uniDEcode(self.Image.fs_path), uniDEcode(self.Image.fs_filename)), QtCore.QSize(ICON_SIZE,ICON_SIZE))"""
                
                self.liwiit.setIcon(icon)
                self.liwiit.setToolTip(self.Image.generateToolTip())
                self.liwiit.setData(32,uniDEcode(os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir), uniDEcode(self.Image.fs_filename))))
                self.liwi.addItem(self.liwiit)
        if rows:    
            self.set_statusbar(self.tr("Search finished: Ready"))
    

    def db_sync(self): # major feature of the program: comparison of two image databases and appending data to the allready loaded db, the sync db remains unchanged
    # die funktion zum synchronisieren von zwei datenbanken, der bereits geladenen master_db und einer neuen.
        fileName = QtGui.QFileDialog.getOpenFileName(self, uniDEcode(self.tr("Open database")), "", self.tr("Database (*.sqlite)"));
        
        if uniDEcode(fileName) == os.path.join(uniDEcode(location.pathName),uniDEcode(location.fName)):
            self.set_statusbar(uniDEcode(self.tr("Selected database and current database are identical, select another one."))) 
            
        elif fileName:   
            sync_db=database()
            sync_db.get_cur(fileName)
            sync_combikey=sync_db.search_distinct({"chksum, md5":"images"})
            master_combikey=master_db.search_distinct({"chksum, md5":"images"})
            print(len(sync_combikey))
            print(len(master_combikey))
            sli=[]
            sync_combikey_copy=sync_combikey[:]
            for sync_combi in sync_combikey_copy:  
                print(uniDEcode("sync_combi= ")+sync_combi[0])
                if sync_combi in master_combikey:
                    master_combikey.remove(sync_combi)
                    sync_combikey.remove(sync_combi)
                else:
                    sli.append(sync_combi[1])    # immerhin bekomme ich jetzt diese liste / list containing images that are differnt in the sync db (either sync has additional infos or it is not in master at all)
            print(len(sync_combikey))
            print(len(master_combikey))
            self.set_statusbar(uniDEcode(len(sync_combikey))+uniDEcode(self.tr(" data records to be added or updated")))
           
            mli=[]
            for master_combi in master_combikey:
                mli.append(master_combi[1])
            print(sli)
            print(mli)
            k=1
            for smd5 in sli:
                pili=[]
                #people_check=0
                if smd5 in mli:   # file already in db but metadata different
                    sync_db.curs.execute("SELECT * from images WHERE md5=?",(smd5,))
                    s_row=sync_db.curs.fetchone()
                    sync_db.curs.execute("SELECT pers from Im2People WHERE md5=?",(smd5,))
                    s_prows=sync_db.curs.fetchall()
                    master_db.curs.execute("SELECT * from images WHERE md5=?", (smd5,))
                    m_row=master_db.curs.fetchone()
                    
                    cksum=0
                    for name in s_prows:
                        pili.append(name[0])
                    
                    up_dic={}
                    
                    #if pili:
                    people_check=master_db.insert_Peop(smd5,pili)
                    if people_check:
                        people_check=uniDEcode(people_check)
                        up_dic["people_checksum"]=people_check
                        people_check=uniENcode(people_check)
                        cksum=adler32(people_check,cksum)&0xffffffff
                        
                    
                    cksum=adler32(smd5,cksum)&0xffffffff
                    
                    if m_row[3] is None and not s_row[3] is None:
                        up_dic["e_name"]=s_row[3]
                        cksum=adler32(uniENcode(s_row[3]),cksum)&0xffffffff
                    elif not m_row[3] is None:
                        cksum=adler32(uniENcode(m_row[3]),cksum)&0xffffffff
                        
                    if m_row[10] is None and not s_row[10] is None:
                        up_dic["e_type"]=s_row[10]
                        cksum=adler32(uniENcode(s_row[10]),cksum)&0xffffffff
                    elif not m_row[10] is None:
                        cksum=adler32(uniENcode(m_row[10]),cksum)&0xffffffff
                        
                    if m_row[11] is None and not s_row[11] is None:
                        up_dic["e_loc"]=s_row[11]
                        cksum=adler32(uniENcode(s_row[11]),cksum)&0xffffffff
                    elif not m_row[11] is None:
                        cksum=adler32(uniENcode(m_row[11]),cksum)&0xffffffff

                    if m_row[4] is None and not s_row[4] is None:
                        up_dic["author"]=s_row[4]
                        cksum=adler32(uniENcode(s_row[4]),cksum)&0xffffffff
                    elif not m_row[4] is None:
                        cksum=adler32(uniENcode(m_row[4]),cksum)&0xffffffff
                    
                    if m_row[2] is None and not s_row[2] is None:
                        up_dic["year"]=s_row[2]
                        cksum=adler32(uniENcode(s_row[2]),cksum)&0xffffffff
                    elif not m_row[2] is None:
                        cksum=adler32(uniENcode(m_row[2]),cksum)&0xffffffff
                    
                    if s_row[5]:
                        s_com_li=QtCore.QString(s_row[5]).split("; ",QtCore.QString.SkipEmptyParts)
                        if m_row[5]:
                            m_com_li=QtCore.QString(m_row[5]).split("; ",QtCore.QString.SkipEmptyParts)
                        else:
                            m_com_li=QtCore.QStringList()
                                                     
                        for s_com in s_com_li:
                            if s_com not in m_com_li: #and s_com is not unicode(""):
                                m_com_li.append(s_com)
                        
                        m_com_str=m_com_li.join(";")
                        #print(m_com_str)
                        m_com_str.append(";")
                        #print(m_com_str)
                        m_com_str.replace("; ",";")
                        #print(m_com_str)
                        m_com_str.replace(";","; ")
                        #print(m_com_str)
                        up_dic["comment"]=m_com_str
                        cksum=adler32(uniENcode(m_com_str),cksum)&0xffffffff
                        
                    elif m_row[5]:
                        cksum=adler32(uniENcode(m_row[5]),cksum)&0xffffffff
                    
                    #if people_check:
                        
                     #   cksum=adler32(people_check,cksum)&0xffffffff
                    
                    up_dic["chksum"]=uniDEcode(cksum)
                    master_db.update_table(smd5,up_dic)
                
                elif not smd5 in mli:  # file not in master db 
                    sync_db.curs.execute("SELECT * from images WHERE md5=?",(smd5,))
                    s_row=sync_db.curs.fetchone()
                    name_in_master=uniENcode(file_in_fs_check(s_row[7]))
                    sync_db.curs.execute("SELECT pers from Im2People WHERE md5=?",(smd5,))
                    s_prows=sync_db.curs.fetchall()
                    
                    master_db.curs.execute("insert into images (chksum, md5, year, event, author, comment, relPath, fileName, sourceFileName, people_checksum, future1, future2) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (uniDEcode(s_row[0]),uniDEcode(s_row[1]),uniDEcode(s_row[2]),uniDEcode(s_row[3]), uniDEcode(s_row[4]),uniDEcode(s_row[5]), uniDEcode(location.fs_dir),uniDEcode(name_in_master),uniDEcode(s_row[8]),uniDEcode(s_row[9]),uniDEcode(s_row[10]),uniDEcode(s_row[11]),))
                    master_db.con.commit()
                    
                    fn_src=os.path.split(uniENcode(fileName))[0]
                    copy2(uniDEcode(os.path.join(fn_src,s_row[6],s_row[7])),uniDEcode(os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir), uniDEcode(name_in_master))))
                    pili=[]
                    for name in s_prows:
                        pili.append(name[0])  

                    if pili:
                        master_db.insert_Peop(smd5,pili)
                self.set_statusbar(uniDEcode(len(sync_combikey)-k)+uniDEcode(self.tr(" data records to be added or updated")))
                k=k+1 
            self.ImClear() # tabula rasa of the image display to avoid db inconsistensies
            sync_db.close_db()
            
     
    def set_statusbar(self, message,t=0):
        self.ui.statusbar.showMessage(uniDEcode(message),t)
               

class StartDialog (QtGui.QDialog):
    """StartDialog is a Dialog window which forces the user to eiter choose an
       existent db or create a new one. this should prevent working without db,
       which is btw not possible at all and causes an ERROR""" 
    def __init__(self, parent=None): 
        QtGui.QWidget.__init__(self, parent)
        self.startDia=Ui_Dialog() 
        self.startDia.setupUi(self)
        self.connect(self.startDia.Start_newDB_botton,QtCore.SIGNAL("clicked()"), self.newDB)
        self.connect(self.startDia.Start_existingDB_button,QtCore.SIGNAL("clicked()"),self.existingDB)


    def newDB(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,self.tr("Save database as"),"", self.tr("Database (*.sqlite)"));

        if fileName:
            location.addpathname(os.path.split(uniDEcode(fileName))[0])
            self.fN=QtCore.QString(os.path.split(uniDEcode(fileName))[1]) 
            self.fN=self.fN.trimmed()
    
            if self.fN.endsWith(".sqlite",0):   #prüft ohne case sensitivity auf endung "sqlite"
                if self.fN.endsWith("sqlite",1):  #alles kleingeschrieben?
                    pass                             # ja: ok
                else:                              #nein: der schwanz wird abgeschnitten und durch 
                    self.fN.chop(6)                 # die kleingeschrieben variante ersetzt 
                    self.fN.append("sqlite")
            else:                               #keine endung auf sqlite vorhanden -> wird angefügt
                self.fN.append(".sqlite")

            location.addfilename(self.fN)
            statusbar_db_label=QtGui.QLabel()
            statusbar_db_label.setText(self.fN)
            myapp.ui.statusbar.addPermanentWidget(statusbar_db_label)
            location.addfs_dir(self.fN.split(".")[0])
            new_cur_ok=master_db.get_new_cur(os.path.join(uniDEcode(location.pathName),uniDEcode(location.fName)))
    
            os.mkdir(uniDEcode(os.path.join(uniDEcode(location.pathName), uniDEcode(location.fs_dir))))
            if new_cur_ok:
                self.closeDia()
            myapp.set_statusbar(self.tr("New database created: Ready"))

    def existingDB(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, uniDEcode(self.tr("Open database")), "", self.tr("Database (*.sqlite)"));

        if fileName:
            location.pathName=os.path.split(uniDEcode(fileName))[0] #[0:fileName.lastIndexOf("/")+1]
            
            fN=QtCore.QString(os.path.split(uniDEcode(fileName))[1]) 
            location.fName=fN
            #print(location.fName)
            location.fs_dir=fN.split(".")[0]
            #print(location.fName)
            statusbar_db_label=QtGui.QLabel()
            statusbar_db_label.setText(fN)
            myapp.ui.statusbar.addPermanentWidget(statusbar_db_label)
            cur_ok=master_db.get_cur(fileName)
            if cur_ok:
                self.closeDia()
            myapp.set_statusbar(self.tr("Database loaded: Ready"))
    
    def showDia(self):
        self.exec_()

    def closeDia(self):
        self.done(42)   # der trick beim schließen des dialogs ist es irgendeine(?) zahl zu übergeben, bestimmt den result wert


class ViewerDialog(QtGui.QDialog):
    """provides the interface to the integrated image viewer invoked by double
       clicking on images. It is heavily influenced by a code (unknown lincense) posted by Vincent Vande Vyvre <vins@swing.be>"""
       
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint)
        self.Vui=Ui_Viewer()
        self.Vui.setupUi(self)
        self.scene = QtGui.QGraphicsScene()
        self.scene.setBackgroundBrush(QtCore.Qt.black)
        self.view=QtGui.QGraphicsView(self.scene) 
        self.view.setLineWidth(0)
        self.view.setFrameShadow(QtGui.QFrame.Plain)
        self.Vui.horizontalLayout_2.addWidget(self.view)
        QtCore.QCoreApplication.processEvents()
        
        self.connect(self.Vui.pushButton, QtCore.SIGNAL("clicked()"), self.prev)
        self.connect(self.Vui.pushButton_2, QtCore.SIGNAL("clicked()"), self.next)
        self.connect(self.Vui.pushButton_3, QtCore.SIGNAL("clicked()"), self.close)
        
        self.Vui.widget.wheelEvent = self.wheel_event
        self.Vui.widget.resizeEvent=self.resize_event
        self.Vui.widget.keyPressEvent=self.key_event
        
    def set_view(self,Im_file_list):
        self.images=Im_file_list 
        self.zoom_step = 0.04
        self.w_vsize = self.view.size().width() 
        self.h_vsize = self.view.size().height() 
        """if self.w_vsize <= self.h_vsize:
            self.max_vsize = self.w_vsize
        else:
            self.max_vsize = self.h_vsize"""
        self.l_pix = ["", "", ""]
        
        self.i_pointer = 0
        self.p_pointer = 0
        self.load_current()
        self.p_pointer = 1
        self.load_next()
        self.p_pointer = 2
        self.load_prec()
        self.p_pointer = 0
        
    def wheel_event (self, event):
        numDegrees = event.delta() / 8.0
        numSteps = numDegrees / 15.0
        self.zoom(numSteps)
        event.accept()
        
    def key_event(self, event):
        key=event.key()   # since i can not figure out how to i commented it (the left or the right cursor do not trigger an event. solution: depends on focus policy in qtdesigner ... did not workout, every key except the right and left keys tirggered a keyevent... now switched to use key input to rotate images using lowercase l and r
        tags={}
        tags['Image Orientation']=fake_Tags()
        if key == QtCore.Qt.Key_L:
            tags['Image Orientation'].printable="Rotated 90 CCW"
            self.l_pix[self.p_pointer]=rotate_image(self.l_pix[self.p_pointer],tags)
            self.c_view=self.scale_image(self.l_pix[self.p_pointer]) # tags is a dict of objects
            self.view_current()
            event.accept()
        elif key == QtCore.Qt.Key_R:
            tags['Image Orientation'].printable="Rotated 90 CW"
            self.l_pix[self.p_pointer]=rotate_image(self.l_pix[self.p_pointer],tags)
            self.c_view=self.scale_image(self.l_pix[self.p_pointer])
            self.view_current()
            event.accept()
        else:
            event.ignore()
        
    def resize_event(self, event): 
        self.w_vsize = self.view.size().width() 
        self.h_vsize = self.view.size().height() 
        """if self.w_vsize <= self.h_vsize:
            self.max_vsize = self.w_vsize
        else:
            self.max_vsize = self.h_vsize"""
        #print(self.p_pointer)
        if self.p_pointer is 0:
            self.np_pointer=1
            self.pp_pointer=2
        elif self.p_pointer is 1:
            self.np_pointer=2
            self.pp_pointer=0
        else:
            self.np_pointer=0
            self.pp_pointer=1
        """self.c_view=self.l_pix[self.p_pointer].scaled(self.max_vsize, self.max_vsize, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.FastTransformation)"""
        self.c_view=self.scale_image(self.l_pix[self.p_pointer])
        self.view_current()
        
        """"self.n_view=self.l_pix[self.np_pointer].scaled(self.max_vsize, self.max_vsize, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.FastTransformation)"""
        self.n_view=self.scale_image(self.l_pix[self.np_pointer])
        """self.p_view=self.l_pix[self.pp_pointer].scaled(self.max_vsize, self.max_vsize, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.FastTransformation)"""
        self.p_view=self.scale_image(self.l_pix[self.pp_pointer])
        event.accept()
                
    def zoom(self, step):
        self.scene.clear()
        w = self.c_view.size().width()
        h = self.c_view.size().height()
        w, h = w * (1 + self.zoom_step*step), h * (1 + self.zoom_step*step)
        self.c_view = self.l_pix[self.p_pointer].scaled(w, h, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.FastTransformation)
        self.view_current()
        
    def next(self):
        self.i_pointer += 1
        if self.i_pointer == len(self.images):
            self.i_pointer = 0
        self.p_view = self.c_view
        self.c_view = self.n_view
        self.view_current()
        if self.p_pointer == 0:
            self.p_pointer = 2
            self.load_next()
            self.p_pointer = 1
        elif self.p_pointer == 1:
            self.p_pointer = 0
            self.load_next()
            self.p_pointer = 2
        else:
            self.p_pointer = 1
            self.load_next()
            self.p_pointer = 0

    def prev(self):
        self.i_pointer -= 1
        if self.i_pointer < 0:  # geändert von self.i_pointer<=0 
            self.i_pointer = len(self.images)-1
        self.n_view = self.c_view
        self.c_view = self.p_view
        self.view_current()
        if self.p_pointer == 0:
            self.p_pointer = 1
            self.load_prec()
            self.p_pointer = 2
        elif self.p_pointer == 1:
            self.p_pointer = 2
            self.load_prec()
            self.p_pointer = 0
        else:
            self.p_pointer = 0
            self.load_prec()
            self.p_pointer = 1

       
    def view_current(self):
        size_img = self.c_view.size()
        wth, hgt = QtCore.QSize.width(size_img), QtCore.QSize.height(size_img)
        self.scene.clear()
        self.scene.setSceneRect(0, 0, wth, hgt)
        self.scene.addPixmap(QtGui.QPixmap(self.c_view)) # QImage to QPixmap conversion
        QtCore.QCoreApplication.processEvents()

    def load_current(self):
        f=open(self.images[self.i_pointer], 'rb')  # according to EXIF.py
        tags = EXIF.process_file(f, details=False)
        f.close()
        self.l_pix[self.p_pointer]=rotate_image(QtGui.QImage(self.images[self.i_pointer]),tags) # QImage as working class
        
        #self.p_width=self.l_pix[self.p_pointer].size().width()
        #self.p_height=self.l_pix[self.p_pointer].size().height()
        self.c_view=self.scale_image(self.l_pix[self.p_pointer])
        """self.c_view = self.l_pix[self.p_pointer].scaled(self.max_vsize, self.max_vsize, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.FastTransformation)"""
        #change the previous line with QtCore.Qt.SmoothTransformation eventually
        self.view_current()
        
    def load_next(self):
        if self.i_pointer == len(self.images)-1:
            p = 0
        else:
            p = self.i_pointer + 1
        f=open(self.images[p], 'rb')  # according to EXIF.py
        tags = EXIF.process_file(f, details=False)
        f.close()
        self.l_pix[self.p_pointer] = rotate_image(QtGui.QImage(self.images[p]),tags)
        self.n_view=self.scale_image(self.l_pix[self.p_pointer])
        """self.n_view = self.l_pix[self.p_pointer].scaled(self.max_vsize, 
                                            self.max_vsize, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.FastTransformation)"""

    def load_prec(self):
        if self.i_pointer == 0:
            p = len(self.images)-1
        else:
            p = self.i_pointer - 1
        f=open(self.images[p], 'rb')  # according to EXIF.py
        tags = EXIF.process_file(f, details=False)
        f.close()
        self.l_pix[self.p_pointer]=rotate_image(QtGui.QImage(self.images[p]),tags)
        self.p_view=self.scale_image(self.l_pix[self.p_pointer])
        """self.p_view = self.l_pix[self.p_pointer].scaled(self.max_vsize, 
                                            self.max_vsize, 
                                            QtCore.Qt.KeepAspectRatio, 
                                            QtCore.Qt.FastTransformation)"""
    
    def scale_image(self, work_image):
        p_ratio=float(work_image.size().width())/float(work_image.size().height())
        v_ratio=float(self.w_vsize)/float(self.h_vsize)
        if v_ratio >= p_ratio:
            work_image=work_image.scaledToHeight(self.h_vsize-15)
        else: #elif v_ratio < p_ratio:
            work_image=work_image.scaledToWidth(self.w_vsize-15)
        
        return work_image
    
    def showViewer(self):
        self.show()
        self.raise_()

    def close(self):
        self.hide()
    
# This is an ugly object to be able to use the image rotate function (takes a dict of objects) without modifying much more code. and allow code reuse in other places
class fake_Tags(object):  
    def __init__(self):
        self.printable=""

class ThumbListWidget(QtGui.QListWidget): # class for the display of images (inspired by a post on the PyQt mailing list http://www.riverbankcomputing.com/mailman/listinfo/pyqt by Mads Ipsen-3 Mar 25, 2009; 09:10am)
    def __init__(self, parent=None, palette=None):
        super(ThumbListWidget, self).__init__(parent)
    
              # Setup
        self.setViewMode(QtGui.QListView.IconMode)
        self.setResizeMode(QtGui.QListView.Adjust)
        self.setLayoutMode(QtGui.QListView.SinglePass)
        self.setUniformItemSizes(0)
        self.setIconSize(QtCore.QSize(ICON_SIZE,ICON_SIZE))
        self.setHorizontalScrollBarPolicy(1)
        self.setAcceptDrops(1)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            l = []  # Sometimes i read the PEP 8 this time i found that using lowercase "L" as name is to be avoided. however i wont change the code and state that this and den following "l" are lowercase "L"
            for url in event.mimeData().urls():
                if url.toString()[-3:] in IMAGE_FORMATS:
                    l.append((url.toLocalFile()))
            if len(l):
                self.emit(QtCore.SIGNAL("dropped"), l)
            else:
                myapp.set_statusbar(self.tr("No file in your drop has been identified as image file: Ready"))
        else:
            event.ignore()

class database(object):
    """Database class: connects to the dbs and has methods for searching and updating
    """
    def get_new_cur(self,fileName):
        r=self.get_cur(fileName)
        self.new_table()
        return r

    def get_cur(self,fileName):
        #print(fileName)
        #print(type(fileName))
        self.con=sqlite3.connect(uniENcode(fileName))
        self.curs=self.con.cursor()
        #firstDia.closeDia()
        return 1
    
    def new_table(self):
        self.curs.execute("create table images(chksum,md5,year text,event,author,comment,relPath,fileName,sourceFileName,people_checksum,future1,future2,future3,future4,future5)") 
        self.curs.execute("create table Im2People(md5,pers)")

    def search_ImageDB(self, search_dic): # die übergabe erfolgt in einem dictionary / use a dictionary for providing the search parameters
        sql_str=QtCore.QString("SELECT * from images WHERE ")
        i=0
        for skey in search_dic.keys():
            i=i+1
            if skey is "md5": 
                sql_str.append("md5= '")
                sql_str.append(search_dic["md5"])
                sql_str.append("'")
            elif skey is "year":
                sql_str.append("year='")
                sql_str.append(search_dic["year"])
                sql_str.append("'")
            elif skey is "e_name":
                sql_str.append("event like '%")
                sql_str.append(search_dic["e_name"])
                sql_str.append("%'")
            elif skey is "e_type":
                sql_str.append("future1 like '%")
                sql_str.append(search_dic["e_type"])
                sql_str.append("%'")
            elif skey is "e_loc":
                sql_str.append("future2 like '%")
                sql_str.append(search_dic["e_loc"])
                sql_str.append("%'")
            elif skey is "author":
                sql_str.append("author like '%")
                sql_str.append(search_dic["author"])
                sql_str.append("%'")
            elif skey is "comment":
                sql_str.append("comment like '%")
                sql_str.append(search_dic["comment"])
                sql_str.append("%'")
            elif skey is "pers": #mit pers muss wohl eine liste der personen in das dic eingetragen werden / remark, that there is a list of names in the dictionary at key "pers"
                sql_str.append("md5 IN (SELECT md5 from Im2People WHERE pers='")
                for person in search_dic["pers"]:
                    sql_str.append(person)
                    sql_str.append("') AND md5 IN (SELECT md5 from Im2People WHERE pers='")   

                sql_str.chop(51)

            if i is not len(search_dic):  # TODO auch hier die elegante chop lösung von oben umsetzen/ use the "chop" solution as used above
                sql_str.append(" AND ")
        if not search_dic:
            sql_str="SELECT * from images WHERE year IS NULL AND event IS NULL AND author IS NULL AND future1 IS NULL AND future2 IS NULL"
        print(uniENcode(sql_str))
        self.curs.execute(uniENcode(sql_str))
        rows=self.curs.fetchall()
        rows=sorted(rows, key=lambda fn: fn[7])
        return rows
    
    def search_distinct(self,criterion):
        key=criterion.keys()
        sql_str=QtCore.QString("SELECT DISTINCT ")
        sql_str.append(key[0])
        sql_str.append(" FROM ")
        sql_str.append(criterion[key[0]])
        print(sql_str)
        self.curs.execute(uniENcode(sql_str))
        rows=self.curs.fetchall()
        print(rows)
        outli=[]
        for row in rows:    # search for a chksum md5 key pair returns pairs in tuples while the other requests so far only single value tubles 
            try:
                t=(row[0],row[1])  # this ok for chksum md5 (two values per tuble)
                outli.append(t)
            except IndexError:     # if there is only one value per tuble:
                outli.append(row[0])
        
        outli.sort()
        if outli:      # check for valid return list
            if outli[0] is not None:
                return outli
            elif outli[0] is None and len(outli)>1:
                outli.remove(None)
                #print(outli)
                return outli
            else:
                outli=[]
                return outli
        else:
            return outli
    
    
    def update_table(self,md5,up_dic):
        sql_str=QtCore.QString("UPDATE images SET chksum='")
        sql_str.append(up_dic["chksum"])
        sql_str.append("', ")
        i=0
        del up_dic["chksum"]
        for skey in up_dic.keys():
            i=i+1
            if skey is "year":
                sql_str.append("year='")
                sql_str.append(up_dic["year"])
                sql_str.append("'")
            elif skey is "e_name":
                sql_str.append("event = '")
                sql_str.append(up_dic["e_name"])
                sql_str.append("'")
            elif skey is "e_type":
                sql_str.append("future1 = '")
                sql_str.append(up_dic["e_type"])
                sql_str.append("'")
            elif skey is "e_loc":
                sql_str.append("future2 = '")
                sql_str.append(up_dic["e_loc"])
                sql_str.append("'")
            elif skey is "author":
                sql_str.append("author = '")
                sql_str.append(up_dic["author"])
                sql_str.append("'")
            elif skey is "comment":
                sql_str.append("comment = '")
                sql_str.append(up_dic["comment"])
                sql_str.append("'")
            elif skey is "people_checksum":
                sql_str.append("people_checksum = '")
                sql_str.append(up_dic["people_checksum"])
                sql_str.append("'")
            
            if i is not len(up_dic):
                sql_str.append(",  ")
                
        sql_str.append(" WHERE md5='")
        sql_str.append(md5)
        sql_str.append("'")
        print(uniENcode(sql_str))
        if not i is 0:
            self.curs.execute(uniENcode(sql_str))
            self.con.commit()


    def insert_Peop(self, md5, pili):
        self.curs.execute("SELECT pers from Im2People WHERE md5=?",(uniENcode(md5),))
        rows=self.curs.fetchall()
        outli=[]

        for row in rows:
            if row[0]:
                outli.append(row[0])

        if outli:      # check for valid return list
            if outli[0] is None:
                outli=[]

        people_ck=0
        pili=QtCore.QStringList(pili)
        outli=QtCore.QStringList(outli)
        
        for name in pili:
            if not outli.contains(name):
                outli.append(name)
                sql_str=QtCore.QString("INSERT INTO Im2People VALUES ('")
                sql_str.append(md5)
                sql_str.append("','")
                sql_str.append(name)
                sql_str.append("')")
                print(uniENcode(sql_str))
                self.curs.execute(uniENcode(sql_str))
                self.con.commit()
        
        outli.sort()
        for name in outli:
            people_ck=adler32(name,people_ck)&0xffffffff
        #if people_ck==0:
        #    return([])
        #else:
        #    return str(people_ck)  
        return people_ck

    def search_People(self,md5):
        self.curs.execute("SELECT pers from Im2People WHERE md5=?",(uniENcode(md5),))
        rows=self.curs.fetchall()
        outli=[]
        for row in rows:
            if row[0]:
                outli.append(row[0])

        if outli:      # check for valid return list
            if outli[0] is not None:
                return outli
            else:
                outli=[]
                return outli
        else:
            return outli

    def close_db(self):
        self.curs.close()
        self.con.close()
        #print("Sync db closed successfully")   #leftovers from testing phase


class paths_n_names(object):     # deklaration zum speichern von dateinamen und pfaden; vorallem für den ort der master_db/ structure for saving and providing the file and path names where the master_db lives
    def __init__(self,path="",fn="",fs=""):
        self.pathName=path
        self.fName=fn
        self.fs_dir=fs

    def addpathname(self,path):
        self.pathName=uniDEcode(path)

    def addfilename(self,fn):
        self.fName=uniDEcode(fn)

    def addfs_dir(self,fs):
        self.fs_dir=uniDEcode(fs)


class SingleIm(object):
    """Main class, here all data associated with an image is stored. methods 
       for providing the image tooltips and some db operations concerning 
       single images are provided
    """
    def __init__(self,m="",filename="",fs_fname=""): 
        self.md5check=m 
        self.file_name=filename #name der quell datei /name of the source file
        self.fs_path=location.fs_dir
        self.fs_filename=fs_fname
        self.pili=[] 
        self.e_loc="" 
        self.e_name=""
        self.e_type=""
        self.age=""
        self.auth=""

        self.comment=QtCore.QString("")
        self.cksum=0
        self.people_check=0

    def addEvent_name(self,e_name): #dirty use of three differnt names for the same data TODO: change to clearer code
        if e_name:
            self.e_name=e_name
    
    def addEvent_type(self,e_type):
        if e_type:
            self.e_type=e_type
            
    def addEvent_loc(self,e_loc):
        if e_loc:
            self.e_loc=e_loc

    def addyear(self,since):
        if since:
            since=QtCore.QString(since)
            if since.count(QtCore.QRegExp("[0-9]{1,1}")) is 4 and since.count() is 4:
                self.age=since
            elif since.count(QtCore.QRegExp("[0-9]{1,1}")) is 2 and since.count() is 2:
                if int(since)<65:
                    since.insert(0,"20")
                    self.age=since
                else:
                    since.insert(0,"19")
                    self.age=since

    def addauth(self,fotogr): # badly spelled photographer
        if fotogr:
            if fotogr.count(";") is 2:
                self.auth=fotogr

                fotogrli=fotogr.split(";")
                self.auth_nick=fotogrli[0]
                self.auth_nam=fotogrli[1]
                self.auth_famnam=fotogrli[2]
                return 1
            else:
                return 0
        else:
            return 1

    def addperson(self,pers):    
        if pers not in self.pili:
            self.pili.append(pers)

    def addcomment(self,com):
        com_li=QtCore.QString(com).split(";",QtCore.QString.SkipEmptyParts)
        for com in com_li:
	    com=com.trimmed()
            if not self.comment.contains(com,1):
                self.comment.append(com)
                self.comment.append("; ")
                
    def generateToolTip(self):
        tttext=QtCore.QString(self.md5check)
        tttext.append("<br>")
        tttext.append(self.file_name)
        tttext.append("<br>")
        if self.age:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Year: </i>","tooltip"))
            tttext.append(self.age)

        if self.e_loc and self.e_name and self.e_type: 
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Event: </i>","tooltip"))
            tttext.append(self.e_name)
            tttext.append(" ")
            tttext.append(QtCore.QCoreApplication.translate("tooltip"," in ","tooltip"))
            tttext.append(" ")
            tttext.append(self.e_loc)
            tttext.append(" (")
            tttext.append(self.e_type)
            tttext.append(")")
        elif self.e_name and self.e_loc:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Event: </i>","tooltip"))
            tttext.append(self.e_name)
            tttext.append(" ")
            tttext.append(QtCore.QCoreApplication.translate("tooltip"," in ","tooltip"))
            tttext.append(" ")
            tttext.append(self.e_loc)
        elif self.e_name and self.e_type:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Event: </i>","tooltip"))
            tttext.append(self.e_name)
            tttext.append(" (")
            tttext.append(self.e_type)
            tttext.append(")")
        elif self.e_type and self.e_loc:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Event: </i>","tooltip"))
            tttext.append(self.e_type)
            tttext.append(" ")
            tttext.append(QtCore.QCoreApplication.translate("tooltip"," in ","tooltip"))
            tttext.append(" ")
            tttext.append(self.e_loc)
        elif self.e_name:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Event: </i>","tooltip"))
            tttext.append(self.e_name)
        elif self.e_type:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Event: </i>","tooltip"))
            tttext.append(self.e_type)
        elif self.e_loc:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Location: </i>","tooltip"))
            tttext.append(self.e_loc)
    
        if self.auth:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Photographer: </i>","tooltip"))
            tttext.append(self.auth_nick)
            tttext.append(" ")
            tttext.append(self.auth_nam)
            tttext.append(" ")
            tttext.append(self.auth_famnam)
    
        if self.pili:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Whos who?: </i>","tooltip"))
            for name in self.pili:    
                nameList=name.split(";")
                nick=nameList[0]
                nam=nameList[1]
                famnam=nameList[2]

                tttext.append("<br>&nbsp;&nbsp;&nbsp;&nbsp;")
                if nick:
                    tttext.append(nick+" ")
                if nam:
                    tttext.append(nam+" ")
                tttext.append(famnam)
    
        if self.comment:
            tttext.append(QtCore.QCoreApplication.translate("tooltip","<br><i>Comment: </i>","tooltip"))
            tttext.append(self.comment)
        return tttext

    def db_insert(self): # dirty implemented db access TODO: implement in database clas
        self.cksum=adler32(uniENcode(self.md5check),self.cksum)&0xffffffff
    
        master_db.curs.execute("insert into images (chksum, md5, sourceFileName, fileName, relPath) values (?,?,?,?,?)",(uniDEcode(self.cksum), uniDEcode(self.md5check), uniDEcode(self.file_name),uniDEcode(self.fs_filename), uniDEcode(location.fs_dir),))
        master_db.con.commit()

    def update_DB(self):
        self.cksum=0
        up_dic={}

        if self.pili:
            self.people_check=master_db.insert_Peop(self.md5check,self.pili)
            self.people_check=uniDEcode(self.people_check)
            up_dic["people_checksum"]=self.people_check
            self.cksum=adler32(uniENcode(self.people_check),self.cksum)&0xffffffff

        self.cksum=adler32(uniENcode(self.md5check),self.cksum)&0xffffffff       

        if self.e_name:
            up_dic["e_name"]=self.e_name
            self.cksum=adler32(uniENcode(self.e_name),self.cksum)&0xffffffff
        if self.e_type:
            up_dic["e_type"]=self.e_type
            self.cksum=adler32(uniENcode(self.e_type),self.cksum)&0xffffffff
        if self.e_loc:
            up_dic["e_loc"]=self.e_loc
            self.cksum=adler32(uniENcode(self.e_loc),self.cksum)&0xffffffff
        if self.auth:
            up_dic["author"]=self.auth
            self.cksum=adler32(uniENcode(self.auth),self.cksum)&0xffffffff # TODO uniENcode vs uniDEcode !
        if self.age:
            up_dic["year"]=self.age
            self.cksum=adler32(uniENcode(self.age),self.cksum)&0xffffffff
        if self.comment:
            up_dic["comment"]=self.comment
            self.cksum=adler32(uniENcode(self.comment),self.cksum)&0xffffffff
        #if self.people_check:
            
        
        up_dic["chksum"]=uniDEcode(self.cksum)
        master_db.update_table(self.md5check,up_dic)
   

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf8"))
    cwd, dummy = os.path.split(os.path.abspath(__file__))
    #cwd=os.getcwd() # uncomment this for using py2exe to get cwd in the other cases the line above serves better
    translator=QtCore.QTranslator()
    if translator.load(os.path.join(cwd,"fotodb_tr_"+locale.getdefaultlocale()[0][0:2])):
        app.installTranslator(translator)
    myapp = StartGui()
    myapp.show()
    master_db=database()
    location=paths_n_names()  # der ort der datenbank und der name der datei /where the db lives
    firstDia=StartDialog()
    firstDia.showDia()
    dia_result=firstDia.result()
    if not dia_result:
        sys.exit(None)
    myapp.populate_cb()
    viewer=ViewerDialog()
    sys.exit(app.exec_())
    