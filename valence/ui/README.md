Rack Scale Design (RSD) Web UI
==============================

The `ui` folder contains HTML, JavaScript and CSS code for a Web UI that can be used to explore Rack Scale Design (RSD) artifacts and compose/disassemble nodes.

##Pre-reqs
1. Install Node and NPM using the OS-specific installer on <https://nodejs.org/en/download/>
2. Update npm to the latest verions
   ```
   sudo npm install npm -g
   ```
3. Follow the instructions in the docs directory for setting up the apache ui-proxy.

##Install
1. `cd` to the `ui` directory and run:
   ```
   npm install
   ```
   * This will install all packages listed in `package.json` file.
   * If you are adding a new package dependency, make sure to save it to the `package.json` file. You can install the package and update `package.json` in a single command: `npm install --save new-package@6.2.5`
   * This installs the webpack dev server which can be used for serving the Web UI during development.

##Run
1. Build
   ```
   npm run build
   ```
2. Start webpack-dev-server in watch mode on the `src` dir:
   ```
   npm run devserver
   ```
   * The `devserver` command is defined in `package.json`. It launches the `webpack-dev-server` program in `hot` mode and watches the `src` directory. If you make any changes to any file in the `src` dir, `webpack-dev-server` compiles everything to a temp location and reloads the display page (`index.html`).
 
3. Open browser and goto <http://localhost:8080/> to view the UI

##Develop
1. The `src\index.html` is the root HTML page for the Web UI. It has a `div` element called `app` which is where the dynamic UI contents get inserted. The file `src/js/main.js` does this insertion using:
   ```
   ReactDOM.render(<Layout/>, document.getElementById('app'));
   ```
   The root of the app content is provided by the React component `src/js/components/Layout.js`. It wraps others components Pods.js, Racks.js, etc which encapsulate the state and rendering details of Pods, Rack, etc respectively.
2. The file `webpack.config.js` contains loaders that transpile React components to plain JavaScript that any browser can understand. The command `webpack` (`package.json` contains `dev-build` and `build` commands which can be used instead via `npm run <command>`) kicks off this transpilation process.
3. Modify appropriate files and use the devserver detailed above to test your changes.

