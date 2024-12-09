# Generate executables instructions

### In order to build from a macOS system, follow these steps:

> 1. install wine-crossover:
> > **`brew install --no-quarantine gcenx/wine/wine-crossover`**
> 2. from a shell type the following to open a windows shell:
> > **`wine cmd`**
> 3. set windows version to windows 10 in wine configuration:
> > **`winecfg`**
> 4. download python for windows (python-3.10.11-amd64.exe).
> 5. go to the download path and run the .exe to install python (while installing go to Advanced Options and flag "Add
     Python to environment variables"):
> > **`python-3.10.11-amd64.exe`**
> 6. create a windows virtual environment in project root:
> > **`python -m venv .winenv`**
> 7. activate the env:
> > **`./.winenv/Scripts/Activate`**
> 8. install requirements:
> > **`pip install -r requirements.txt`**
> 9. move to deploy dir and execute this command:
> > **`python exec_deploy.py`**
> 10. in your local system (assuming macOS platform) activate the macOS env:
> > **`source .venv/bin/activate`**
> 11. move to deploy dir and execute this command:
> > **`python3 exec_deploy.py`**

### The executables will be located in deploy/output/(windows / macOS)/dist/.
