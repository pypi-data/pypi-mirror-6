*Edited using notepag.es*

# Welcome to Longtang

## What's Longtang?

Longtang is a command-line software based on [actors model](https://en.wikipedia.org/wiki/Actor_model) capable of processing any sloppy mp3 collection that you have into a well-organized, easy-to-locate tagged media library.

## Why should I use it?

Because it will save you a __*HUGE*__ amount of time by:

* Tagging all your _mp3_ files with their right ID3Tag information.
* Downloading album cover art __(New feature!!)__
* Decompressing and tagging any __*zip*__, __*rar*__ or __*7z*__ file that you have with music on it transparently 
* Creating a hierarchical media tree organized by artists and albums.
* Naming all files in a simple and yet clear syntax.
* Detecting tag issues that prevent files from being accurately classified.
* Avoiding any stranded or unknown music files inside any portable music player (which usually happens in Creative Zen players, just to name an example) which take up storage space and are not easily detected.

## Installation guide:

Before proceeding with the installation, please check if your system already has the following packages installed:


* Python 2.7.x and headers (python-dev)
* Chromaprint tools (libchromaprint-tools)
* Libevent headers (libevent-dev)
* Libxml (libxml2-dev and libxslt-dev)
* unrar and 7z commands available within your system _PATH_ 


After that, you can proceed to install in either two manners: from the source code or from [Pypi](https://pypi.python.org/pypi) by using _[pip](http://www.pip-installer.org/en/latest/)_ utility.

### 1. Using the source code

1. Checkout the source code:

```
  git clone https://bitbucket.org/gszeliga/longtang.git
```

2. Execute the setup utility as follows:

```
  python setup.py install
```

### 2. Using _pip_

```
pip install longtang
```

## Command guide:

The main binary is called _longtang_ (as you can imagine) and it accepts the following parameters:

* __--source__: Source path where all the to-be-processed files are located.
* __--target__: Target path where the hierarchical structure will be created.
* __--verbosity__: Level of debug information to be printed. Accepted values are: _DEBUG_, _INFO_, _WARN_ or _ERROR_. Default value is _NONE_
* __--override-tags__: _(Optional)_ Whether you want _Longtang_ to override any id3tag information on the source music files. _Bear in mind that if the amount of files is high it will turn the process to be real slow_.
* __--offline__: _(Optional)_ Since any missing id3tag information will be retrieved using [Acoustid](http://acoustid.org/chromaprint) service, maybe you might be interesed in not performing this action and just handle your media collection with the already existing id3 information and point out any failure during the process.
* __--disable-cover-art__: _(Optional)_ Disables resolution of all cover art from all matched artists and albums.
* __--help__: Prints out help information


## What's coming next?


Well, i currently have a lot of ideas but, in a short term, i'm thinking in:

* Supporting more music formats: ogg, mpc, flac and so on.
* Porting source code into Python 3.
* Replacing _gevent_ with _multiprocessing_ library so that we gain execution _**parallelism**_ (take a look at branch __features/multiprocessing__ for further details).

## Bugs and Feedback

You can contact me at _gszeliga@gmail.com_ or follow me on twitter: [@gszeliga](https://twitter.com/gszeliga)
