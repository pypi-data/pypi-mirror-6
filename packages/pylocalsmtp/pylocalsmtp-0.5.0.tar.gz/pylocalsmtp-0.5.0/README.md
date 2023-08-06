PyLocalSmtp
===========

Cette application est en cours de développement. 

Elle permet de recevoir les emails envoyés lors de dévelopement local sur une interface web. L'avantage est de pouvoir lire plus facilement les messages envoyés que dans le terminal. 

Initialement inspiré de `python -m smtpd -n -c DebuggingServer localhost:1025` cette application utilise Tornado, smtpd.SMTPServer, sockjs et SQLite. 


[![Build Status](https://drone.io/bitbucket.org/m_clement/pylocalsmtp/status.png)](https://drone.io/bitbucket.org/m_clement/pylocalsmtp/latest)



Install
-------

    pip install pylocalsmtp
    

Run
---

Lancer la commande suivante : 

    pylocalsmtpd


* Le serveur SMTP sera lancé en localhost sur le port 1025
* Tornado sera lancé sur l'adresse : http://127.0.0.1:8888/

Plus d'options à venir.


Requirements
------------

Ces prérequis sont installés automatiquement

* peewee==2.1.1
* https://github.com/mrjoes/sockjs-tornado
* tornado==3.0.1


LICENCE
-------


    The MIT License (MIT)

    Copyright (c) 2013 Martyn CLEMENT

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
    the Software, and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


CONTRIBUTION
------------

Si cette idée vous plait ou vous déplait, vous pouvez contribuer ou m'envoyer des bières.
