#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
 
# notez qu'on import la lib
# donc assurez-vous que l'importe n'a pas d'effet de bord
import ssouben_lib
 
# Ceci n'est qu'un appel de fonction. Mais il est tres long
# et il comporte beaucoup de parametres
setup(
 
    # le nom de votre bibliotheque, tel qu'il apparaitre sur pypi
    name='ssouben_lib',
 
    # la version du code
    version=ssouben_lib.__version__,
 
    # Liste les packages a inserer dans la distribution
    # plutot que de le faire a la main, on utilise la foncton
    # find_packages() de setuptools qui va cherche tous les packages
    # python recursivement dans le dossier courant.
    # C'est pour cette raison que l'on a tout mis dans un seul dossier:
    # on peut ainsi utiliser cette fonction facilement
    packages=find_packages(),
 
    # votre pti nom
    author="Sam",
 
    # Votre email, sachant qu'il sera publique visible, avec tous les risques
    # que ca implique.
    author_email="sam@gmail.com",
 
    # Une description courte
    description="Proclame la bonne parole de sieurs Sam et Max",
 
    # Une description longue, sera affichee pour presenter la lib
    # Generalement on dump le README ici
    long_description=open('README.md').read(),
 
    # Vous pouvez rajouter une liste de dependances pour votre lib
    # et meme preciser une version. A l'installation, Python essayera de
    # les telecharger et les installer.
    #
    # Ex: ["gunicorn", "docutils >= 0.3", "lxml==0.5a7"]
    #
    # Dans notre cas on en a pas besoin, donc je le commente, mais je le
    # laisse pour que vous sachiez que ca existe car c'est tres utile.
    # install_requires= ,
 
    # Active la prise en compte du fichier MANIFEST.in
    include_package_data=True,
 
    # Une url qui pointe vers la page officielle de votre lib
    #url='http://github.com/sametmax/sm_lib',
 
    # Il est d'usage de mettre quelques metadata a propos de sa lib
    # Pour que les robots puissent facilement la classer.
    # La liste des marqueurs autorisees est longue, alors je vous
    # l'ai mise sur 0bin: http://is.gd/AajTjj
    #
    # Il n'y a pas vraiment de regle pour le contenu. Chacun fait un peu
    # comme il le sent. Il y en a qui ne mettent rien.
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications",
    ],
 
 
    # C'est un systeme de plugin, mais on s'en sert presque exclusivement
    # Pour creer des commandes, comme "django-admin".
    # Par exemple, si on veut creer la fabuleuse commande "proclame-sm", on
    # va faire pointer ce nom vers la fonction proclamer(). La commande sera
    # cree automatiquement. 
    # La syntaxe est "nom-de-commande-a-creer = package.module:fonction".
    entry_points = {
        'console_scripts': [
            'proclame-sm = ssouben_lib.core:proclamer',
        ],
    },
 
    # A fournir uniquement si votre licence n'est pas listee dans "classifiers"
    # ce qui est notre cas
    license="WTFPL",
 
    # Il y a encore une chiee de parametres possibles, mais avec ca vous
    # couvrez 90% des besoins
 
)