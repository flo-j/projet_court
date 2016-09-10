#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, request, flash, redirect, url_for, render_template
from flask import send_file
from werkzeug import secure_filename
import os
import sqlite3
import PIL
from PIL import Image
import re
from flask_nav.elements import Navbar, View
from flask_script import Manager
from flask_bootstrap import *
from flask_nav import *
app = Flask(__name__)
app.secret_key = 'd66HR8dç"f_-àgjYYic*dh'
DOSSIER_UPS = 'static/ups/'


#déclare le plug-in flask-script
manager = Manager( app)
#déclare le plug-in flask-bootStrap
bootstrap = Bootstrap(app)
#j'instancie le plug-in flask-Nav
nav = Nav()
#je déclare le plug-in dans l'application
nav.init_app(app)
#je déclare une barre de navigation contenant les routes
mynavbar = Navbar(
      'mysite',
      View('Upload', 'upload'),
      View('gallery', 'liste_upped'))
#je donne au plug-in ma barre de navigation
nav.register_element('top', mynavbar)


def extension_ok(nomfic):
    """ Renvoie True si le fichier possède une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('png', 'JPG', 'jpeg', 'gif', 'bmp')

def extension(nomfichier):
    return nomfichier.rsplit('.', 1)[1]

def createNewPicture(nomfic,kw):
    conn = sqlite3.connect('data.db')
    conn.execute("insert into img (CHEMIN, CREATION, MODIF,KEYWORDS) VALUES('static/ups/prov2',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,?)",(kw,))
    cursor = conn.execute("select id from IMG where creation == (select MAX(creation) from img)")
    for row in cursor:
        last_insert = "img"+str(row[0])+"."+extension(nomfic)
        conn.execute("update img set chemin=? where id==?",(DOSSIER_UPS+last_insert,row[0]))
    conn.commit()
    return last_insert

@app.route('/', methods=['GET', 'POST'])
def upload():
    print " upload"
    if request.method == 'POST':
       # if request.form['pw'] == 'up': # on vérifie que le mot de passe est bon
            f = request.files['fic']
            if f: # on vérifie qu'un fichier a bien été envoyé
                if extension_ok(f.filename): # on vérifie que son extension est valide
                    keywords = request.form['kw']
                    name = createNewPicture(f.filename,keywords)
                    f.save(DOSSIER_UPS + name)
                    flash(u'Image envoyée !', 'succes')
                    # a mettre dans une fonction, et nommer le forum
                    basewidth = 100
                    img = Image.open(DOSSIER_UPS+name)
                    wpercent = (basewidth/float(img.size[0]))
                    hsize = int((float(img.size[1])*float(wpercent)))
                    img2 = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
                    img2.save(DOSSIER_UPS+"resized_"+name)
                    return redirect(url_for('liste_upped'))
                else:
                    flash(u'Ce fichier ne porte pas une extension autorisée !', 'error')
            else:
                flash(u'Vous avez oublié le fichier !', 'error')
        #else:
        #    flash(u'Mot de passe incorrect', 'error')
    return render_template('up_up.html')


def is_resized(filename):
    return extension_ok(filename) and 'resized' in filename

def recup_info(chemin):
    conn = sqlite3.connect('data.db')
    cursor = conn.execute("select * from IMG where chemin == ?",(chemin,))



def recup_info(id):
    info={}
    info["id"] = id
    conn = sqlite3.connect('data.db')
    cursor = conn.execute("select * from img where id=?",(id,))
    for row in cursor:
        info["datecreation"]=row[2]
        info['datemodif']=row[3]
        info['kw']=row[4]
    return info


def recup_id(chemin):
     pat="[0-9]+"
     prog=re.compile(pat)
     id=prog.search(chemin).group()
     return id

@app.route('/view/')
def liste_upped():

    images = [img for img in os.listdir(DOSSIER_UPS) if extension_ok(img)] # la liste des images dans le dossier
    icones = [img for img in os.listdir(DOSSIER_UPS) if is_resized(img)]
    informations={}
    for ico in icones:
        informations[ico]={}
        id = recup_id(ico)
        informations[ico]=recup_info(id)

    return render_template('up_liste.html', images=images, icones=icones,info=informations)

@app.route('/view/<nom>')
def upped(nom):
    nom = secure_filename(nom)
    iden = recup_id(nom)
    info=recup_info(iden)
    img=nom
    return render_template('up_image.html',img=img,info=info)# sinon on redirige vers la liste des images, avec un message d'erreur

if __name__ == '__main__':
    app.run(debug=True)
