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
DOSSIER_UPS = 'ups/'


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
      View('gallery', 'liste_upped'),
      View('mentions legales','mentions_legales'),
      View('recherche','research')
      )
#je donne au plug-in ma barre de navigation
nav.register_element('top', mynavbar)


def extension_ok(nomfic):
    """ Renvoie True si le fichier possède une extension d'image valide. """
    return '.' in nomfic and nomfic.rsplit('.', 1)[1] in ('png', 'JPG', 'jpeg', 'gif', 'bmp')

def extension(nomfichier):
    return nomfichier.rsplit('.', 1)[1]

def createNewPicture(nomfic,kw):
    conn = sqlite3.connect('data2.db')
    kws=kw.replace(" ",";")
    conn.execute("insert into img (CHEMIN,CHEMIN_MINI, CREATION, MODIF,KEYWORDS) VALUES('static/ups/prov2','static/ups/prov',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,?)",(kws,))
    cursor = conn.execute("select id from IMG where creation == (select MAX(creation) from img)")
    for row in cursor:
        last_insert = "img"+str(row[0])+"."+extension(nomfic)
        conn.execute("update img set chemin=? where id==?",(DOSSIER_UPS+last_insert,row[0]))
    conn.commit()
    return last_insert

def update_chemin_mini(id, value):
    conn = sqlite3.connect('data2.db')
    conn.execute('update img set CHEMIN_MINI=? where id==?',(value,id))
    conn.commit()
    return 0

def get_chemin_mini(id):
    conn = sqlite3.connect('data2.db')
    cursor = conn.execute("select chemin_mini from img where id==?",(id,))
    for row in cursor:
        res=row[0]
    return res

def get_chemin(id):
    conn = sqlite3.connect('data2.db')
    cursor = conn.execute("select chemin from img where id==?",(id,))
    for row in cursor:
        res=row[0]
    return res


@app.route('/',methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
       # if request.form['pw'] == 'up': # on vérifie que le mot de passe est bon
            f = request.files['fic']
            if f: # on vérifie qu'un fichier a bien été envoyé
                if extension_ok(f.filename): # on vérifie que son extension est valide
                    keywords = request.form['kw']
                    name = createNewPicture(f.filename,keywords)
                    f.save('static/'+DOSSIER_UPS + name)
                    f=resize('static/'+DOSSIER_UPS+name,400)
                    f.save('static/'+DOSSIER_UPS+name)
                    flash(u'Image envoyée !', 'succes')
                    # a mettre dans une fonction, et nommer le forum
                    img2 = resize('static/'+DOSSIER_UPS+name, 100)
                    name_mini = DOSSIER_UPS+"mini_"+name
                    img2.save('static/'+name_mini)
                    update_chemin_mini(recup_id(name_mini),name_mini)
                    return redirect(url_for('liste_upped'))
                else:
                    flash(u'Ce fichier ne porte pas une extension autorisée !', 'error')
            else:
                flash(u'Vous avez oublié le fichier !', 'error')
        #else:
        #    flash(u'Mot de passe incorrect', 'error')
    return render_template('up_up.html')

@app.route('/research/',methods=['GET','POST'])
def research():
    if request.method == "POST":
        keyword = request.form['kws']
        return redirect(url_for('research_res',keyword))
    return render_template('up_research.html')

@app.route('/research_res/',methods=['GET','POST'])
def research_res(keyword):
    conn = sqlite3.connect('data2.db')
    #images = [img for img in os.listdir('static/'+DOSSIER_UPS) if extension_ok(img)] # la liste des images dans le dossier
    #icones = [img for img in os.listdir('static/'+DOSSIER_UPS) if is_mini(img)]
    res = conn.execute("select chemin from img where keywords like %?%",(keyword,))
    vignette = []
    for row in res:
        result = row[0].split("/")[1]
        vignette.append(result)
    informations={}
    for ico in vignette:
        informations[ico]={}
        id = recup_id(ico)
        informations[ico]=recup_info(id)
        informations[ico]['chemin']=get_chemin_mini(id)
    return render_template('up_research_res.html', icones=vignette,info=informations,word=keyword)



def resize(filename, basewidth):
    basewidth = basewidth
    img = Image.open(filename)
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img2 = img.resize((basewidth,hsize), PIL.Image.ANTIALIAS)
    return img2

def is_mini(filename):
    return extension_ok(filename) and 'mini' in filename


def recup_info(id):
    info={}
    info["id"] = id
    conn = sqlite3.connect('data2.db')
    cursor = conn.execute("select * from img where id=?",(id,))
    for row in cursor:
        info["datecreation"]=row[3]
        info['datemodif']=row[4]
        info['kw']=row[5]
    return info


def recup_id(chemin):
     pat="[0-9]+"
     prog=re.compile(pat)
     id=prog.search(chemin).group()
     return id

@app.route('/view/')
def liste_upped():
    conn = sqlite3.connect('data2.db')
    #images = [img for img in os.listdir('static/'+DOSSIER_UPS) if extension_ok(img)] # la liste des images dans le dossier
    #icones = [img for img in os.listdir('static/'+DOSSIER_UPS) if is_mini(img)]
    res = conn.execute("select chemin from img")
    vignette = []
    for row in res:
        result = row[0].split("/")[1]
        vignette.append(result)
    informations={}
    for ico in vignette:
        informations[ico]={}
        id = recup_id(ico)
        informations[ico]=recup_info(id)
        informations[ico]['chemin']=get_chemin_mini(id)

    return render_template('up_liste.html', icones=vignette,info=informations)
@app.route('/mentions_legales')
def mentions_legales():
    return render_template('up_legales.html')

@app.route('/view/<nom>', methods=['GET','POST'])
def upped(nom):
    nom = secure_filename(nom)
    iden = recup_id(nom)
    info=recup_info(iden)
    img=get_chemin(iden)
    if request.method=="POST":
        conn=sqlite3.connect('data2.db')
        conn.execute("delete from img where id ==?",(iden,))
        conn.commit()
        return redirect(url_for('liste_upped'))


    return render_template('up_image.html',img=img,info=info)# sinon onconn=sqlite3.connect redirige vers la liste des images, avec un message d'erreur

if __name__ == '__main__':
    app.run(debug=True)
