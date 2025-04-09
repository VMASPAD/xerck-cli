#!/usr/bin/env node

const { utils, globals } = require('../content');
const {exec} = require('child_process');
const fs = require('fs');
const args = process.argv.slice(2);
const command = args[0];
const path = process.cwd() + "\\";
const version = '1.0.0';

switch (command) {
  case 'init':
    // Verificar si existe un package.json en el directorio actual
    fs.access(path + 'package.json', fs.constants.F_OK, (err) => {
      if (err) {
        console.error('Error: No se encontró un archivo package.json. Asegúrate de estar en un proyecto de Node.js válido.');
        return;
      }
      
      // Continuar con la inicialización solo si package.json existe
      fs.mkdir(path + 'components', (err) => {
        if (err) {
            console.error('Components folder already created or containing folder');
          return;
        }
        exec("npm i clsx tailwind-merge")
        console.log('Xerck Started!');
        fs.mkdir(path + 'app', { recursive: true }, (err) => {
            if (err) {
                console.error('Error creating app directory:', err);
                return;
            }
            const globalsPath = path + 'app/globals.css';
            fs.access(globalsPath, fs.constants.F_OK, (err) => {
                if (err) {
                    fs.writeFile(globalsPath, globals, (err) => {
                        if (err) {
                            console.error('Error writing globals.css:', err);
                            return;
                        }
                        console.log('globals.css writed successfully');
                    });
                } else {
                    fs.readFile(globalsPath, 'utf8', (err, data) => {
                        if (err) {
                            console.error('Error reading globals.css:', err);
                            return;
                        }
                        const newContent = globals + data;
                        fs.writeFile(globalsPath, newContent, (err) => {
                            if (err) {
                                console.error('Error updating globals.css:', err);
                                return;
                            }
                            console.log('globals.css updated successfully');
                        });
                    });
                }
            });
        });
      });
      fs.mkdir(path + 'lib', (err) => {
          if (err) {
            console.error('utils.ts file already created or containing folder');
            return 0;
          }
          fs.writeFile(path + 'lib/utils.ts', utils, (err) => {
              if (err) {
                  console.error('Not initiliced:');
                  return;
                  }
              }
          )
      });
    });
    break;
  case 'version':
    console.log(`Xerck CLI v${version}`);
    break;
  case 'test':
    console.log(path)
    break;
  case 'add':
    fetch(`https://portfoliotavm.com/xerck-components/${args[1]}.json`)
      .then(response => response.json()) 
      .then(data => {
        fs.writeFile(path + `components/${data.name}.tsx`, data.component, (err) => {
            if (err) {
                console.error('Error to create archive:', err);
                return;
                }
            }
        )
    
        console.log(`Component ${data.name} created successfully`)
    }
    )
      .catch(error => {
        console.error('Error al obtener la última versión:', error);
      });
    break;
  default:
    if (!command) {
      console.log(`Xerck CLI v${version}`);
      console.log(`
        xerck-cli <option>

        init        Create the project structure
        add <name>  Add component to your project
        
        `);
      
    } else {
      console.log(`Xerck CLI v${version}`);
      console.log(`
        xerck-cli <option>

        init        Create the project structure
        add <name>  Add component to your project
        
        `);
    }
    break;
}
