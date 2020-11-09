# Flock AI

### About
This repository contains
- Flock AI: A machine learning python library which is designed as a plugin for webots.
- Webots simulations: Sample simulations that demonstrate the usage of Flock AI


### Webots
- Nightly Version: [r2020b-rev2](https://github.com/cyberbotics/webots/releases)
- Release: [R2020b-rev1](https://github.com/cyberbotics/webots/releases/tag/R2020b-rev1)
- Installation steps per OS can be found [here](https://cyberbotics.com/doc/guide/installation-procedure).

### Development

##### Prerequisites
1. Set up the [webots required enviroment variables](https://cyberbotics.com/doc/guide/running-extern-robot-controllers?tab-language=python&tab-os=linux#environment-variables)
2. Create a `.pypirc` file which will contain the pypi credentials:
  ``` 
    [distutils]
    index-servers= pypi
    
    [pypi]
    repository = https://upload.pypi.org/legacy/
    username = the_username
    password = the_password
  ```

##### Development Pipeline
1. `make config`
    Copies the `.pypirc` to your user home folder and allows automated uploads using twine.
2. `make requirements`
    Installs project requirements.
3. `make package`
    Generates the new package under the `dist/` directory.
4. `make upload`
    Uploads the package in the specified pypi repository. **Note**: The version number should be upgraded in `setup.py` in order to push to the repository (ie. 0.0.1 -> 0.0.2) 
5. `make install`
    Install Flock AI in Webots home folder to be used as a library.
6. `make clean` (*Optional*)
    Cleans the build directory. This step should be done before rebuilding the package.

 
