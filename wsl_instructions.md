## Installing WSL
To install WSL, you will need administrative access.

Start by launching a new Command Prompt with administraive access. This can be done by using the "Run as Adminstrator" option when right-clicking the Command Prompt icon.

Type
```
wsl –install -d ubuntu-22.04
```
This will install Ubuntu 22.04 as an available linux distribution. You will be prompted for a username and password. After the process completes, you should be inside a bash shell.

This is the only step that requires administraive access. You can open other Command Prompts normally and enter the linux environment with
```
wsl -d ubuntu-22.04
```

## Installing dependencies
Additional linux dependencies are required for running Phenix and Coot. The `sudo` command is used since installing dependencies requires administrative rights in linux. The password will be the password you created when installing WSL. To install these dependencies type
```
sudo apt-get update
sudo apt-get install \
  build-essential \
  freeglut3-dev \
  libglu1-mesa-dev \
  libgtk2.0-0 \
  libxxf86vm1 \
  mesa-common-dev
  mesa-utils \
  openssl \
  x11-apps
```
For Coot, there is a build for Ubuntu 20.04 and for that build to work on Ubuntu 22.04, an older version of `libssl` needs to be installed. To do this, type
```
echo "deb http://security.ubuntu.com/ubuntu focal-security main" | sudo tee /etc/apt/sources.list.d/focal-security.list

sudo apt-get update
sudo apt-get install libssl1.1

sudo rm /etc/apt/sources.list.d/focal-security.list
sudo apt-get update
```

## Installing locales
On Ubuntu, both `en_US` and `en_GB` are required. To install these locales, type
```
sudo locale-gen en_US.utf8 en_GB.utf8
```

## Installing an X11 server
If you on Windows 11, this step should not be needed. However, if you are on Windows 10, you will need to install an X11 server for Coot to work. These steps are for Windows, not Ubuntu. You can use the one from

https://sourceforge.net/projects/vcxsrv/

After installing the software, follow the directions here to set up the X11 server.

https://gist.github.com/Mluckydwyer/8df7782b1a6a040e5d01305222149f3c#2-window-server

## Installing Phenix
Download the **linux** installer from the Phenix website. You can download the installer from a Windows browser. The Ubuntu installation will have access to `C:\` in `/mnt/c`. You can go to your Windows download page by typing
```
cd /mnt/c/Users/<Windows username>/Downloads
```
The installer should be in that directory if you use your default folder for downloads.

The installer must be extracted on the linux filesystem. You can go to your linux home directory by typing
```
cd
```
This should go to `/home/<linux username>`. You can check with the
```
pwd
```
command.

To extract the linux installer, type
```
cd
tar -xf /mnt/c/Users/<Windows username>/Downloads/<Phenix installer file>
```
This will create a new directory in your linux home directory that will look like `phenix-installer-<version>-<platform>`. You can then run the installer by typing
```
cd phenix-installer-<version>-<platform>
./install --prefix ${HOME}
```
This will install Phenix into your linux home directory. The installation must be in the linux filesystem.

## Installing Coot
Download the Ubuntu 20.04 build of Coot 0.9.8 with this link

https://www2.mrc-lmb.cam.ac.uk/personal/pemsley/coot/binaries/release/coot-0.9.8-binary-Linux-x86_64-ubuntu-20.04.4-python-gtk2.tar.gz

Like with the Phenix installer, extract it with
```
cd
tar -xf /mnt/c/Users/<Windows username>/Downloads/coot-0.9.8-binary-Linux-x86_64-ubuntu-20.04.4-python-gtk2.tar.gz
```

## Final setup steps
For the model viewer in Phenix to work, one of the files needed to be changed. You can do this by typing
```
ln -s -f /usr/lib/x86_64-linux-gnu/libstdc++.so.6 <Phenix directory>/conda_base/lib/libstdc++.so.6
```
To set up your linux environment to run Phenix, type
```
export LIBGL_ALWAYS_INDIRECT=0
source <Phenix directory>/phenix_env.sh
```
To simplify this, you can add these lines to your `.bashrc` file. Then, whenever a new linux shell is started, the Phenix environment will already be set up.

## Starting Phenix and linking Coot
To start the Phenix GUI, type
```
phenix
```
Once you are in the main GUI, you can point Phenix to the location of Coot by opening the "Preferences", then go to "Graphics". You should see a field for "Coot path". In that field, type
```
/home/<linux username>/coot-Linux-x86_64-ubuntu-20.04.4-gtk2-python/bin/coot
```
