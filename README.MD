![Python](http://python.org/static/img/python-logo.png)
# Vinli Challenge #

## Setup ##
#### Install necessary applications ####
These instructions are for Mac OS. If you have [Python 3.6 or higher](http://www.python.org) or [Homebrew](https://brew.sh) already installed you can skip those steps.
```sh
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew install python3
```

Now, install the Python packages required. From the project directory, run:
```sh
pip3 install -r requirements.txt
```

You can also install [nose2](https://github.com/nose-devs/nose2) to use as a test runner.

#### Configuration ####

Due to time constraints, there is no configuration. Normally the URL and other options would be configurable via file and command line.

## Running Tests ##
From the project root, you can run the tests with:
```sh
nose2
```

You can also run using:
```sh
python3 testAll.py
``` 