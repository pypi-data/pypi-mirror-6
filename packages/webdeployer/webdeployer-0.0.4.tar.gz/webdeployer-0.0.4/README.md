DEPLOYER
========

### This webdeployer allows you to deploy fast and easy to your webserver.
Automate deployments of your webapps using :

-   GUNICORN
-   NGINX
-   SUPERVISORD

You need to use a directory format like : ```/projects/client/client_name/project/source```

requirements :
- Python 2.7
- Fabric
- Jinja2


On your server you need to have already installed and running:
-   nginx
-   gunicorn(not realy only you need to have the package installed)
-   supervisord


This is being set free from Private so it may take time to free out all the mess from my private repo


TO INSTALL
==========

```
pip install webdeployer
```


If you are deploying for the first time :
go in your project directory and type : webdeployer init

edit the webdeployer-config.py

then type webdeployer deploy

MILESTONE/ROADMAP

- I want to make it more customizable