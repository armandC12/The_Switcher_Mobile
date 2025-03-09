# The_Switcher_Mobile_Frontend
Adaptacion del juego de mesa "The Swticher" para dispositivo moviles
## Como levantar el proyecto
* Verificar si tenemos instalado en el sistema Node.js en la ultima version.
Para eso ir a la seccion: 
[Instalar o Verificar Node.js usando nvm (Node Version Manager)](#instalar-o-verificar-nodejs-usando-nvm-node-version-manager)


* Hecho lo anterior hacemos lo siguiente:
* Clonar el repositorio del proyecto 

        $ git clone https://github.com/IngSoft1-Capybaras/switcher-frontend.git

* Nos Posicionamos en el directorio y ejecutar los dos comandos siguientes
        
        $ cd switcher
        $ npm install
        $ npm run dev       # Para ejecutar en computadoras

* Para levantar el proyecto en dispositivo moviles ejecutamos este comando:

        $ npm run dev -- --host 0.0.0.0

* Por ultimo copiamos la URL que nos sale en la consola y lo pegamos en un navagedor.

## Instalar o Verificar Node.js usando nvm (Node Version Manager)
### Primero verifcamos si esta instalado Node.js. 
Ejecutar el siguiente comando en la consola:
    
    $ node -v

Esto debe mostrar la version de node.js en el sistema, por ejemplo:
    
    $ v20.7.0

En caso de no tenerlo instalado, el sistema devolverá un mensaje de error:

    $ "command not found" 
En Linux/macOS

### Para instalar nvm hay que seguir los siguientes pasos:

1) Ejecutar el siguiente comando en la terminal

    >$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

2) Luego, recargar el entorno de la terminal para que los comandos de nvm estén disponible.
    >$ source ~/.bashrc

### Para instalar Node.js con NVM

Instalar la ultima version de node.js (o una version especifica) usando nvm:
* Para instalar la ultima version LTS

        $ nvm install --lts

* O para una version especifica, como la version 20.x:
        
        $ nvm install 20.17

### Verificamos la instalacion
Para verificar si se instalaron correctamente Node.js y npm en el sistema, ejecutar:

    $ node -v
    $ npm -v
