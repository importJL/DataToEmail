# Guidance Notes

## Introduction
The repository consists of a Python module (i.e. DataToEmail) and 2 main Python script files as examples for program execution.
Among these scripts, several folders are provided containing example outputs and config files required for API access and Outlook SMTP settings.

## Folder Organization
The repository is organized in below schematic:
```
.
├── DataToEmail
│   ├── __init__.py
│   ├── alphachart.py
│   ├── email_components.py
│   └── news.py
├── config
│   ├── config.json
│   └── keys.json
├── examples
│   ├── EmailResult1.png
│   └── EmailResult2.png
├── templates
│   ├── text_body.html
│   └── text_body.txt
├── main_news.py
├── main_email.py
├── Pipfile
└── README.md
```

## Requisites
#### API keys
For data extraction, the following APIs are used which require sign-up for API key access. Each API source has a free-tier pricing option so development and personal use.

Links for API sources are:
1. NewsDataIO - https://newsdata.io/
2. News API - https://newsapi.org/
3. Alpha Vantage - https://www.alphavantage.co/

#### Outlook e-mail settings
To utilize automated e-mail preparation, personal e-mail credentials are needed to allow authentication and email transfer.
If you do not have an Outlook e-mail account, you may register one at https://outlook.live.com/owa/.

#### Python
All scripts are developed using Python programming language. To execute these scripts, download the software at https://www.python.org/downloads/.
Installing the required libraries for this repository depend on the Python version you have or will get. It is required to use Python 3.9 if installing libraries by Pipenv (see below Instructions) or Other Python 3.xx versions if using Pip.

Further, to aid in your own development and enhancements to these scripts, you can download IDEs such as VS Code and PyCharm which can be found in the links below:

- Visual Studio (VS) Code - https://code.visualstudio.com/
- PyCharm - https://www.jetbrains.com/pycharm/

## Instructions
1. Clone/fork this repository to your personal environment.
2. Install Pipenv via:

    `pip install --user pipenv` (for Windows)

    `sudo apt install pipenv` (for Linux)

   Alternatively, you may use "virtualenv" to set up a separate environment for running this repository.
   Install virtualenv using `pip install virtualenv` and activate your environment by directing to that your environment folder and entering `.\Scripts\activate` (for Windows) or `source ./bin/activate` (for Linux).

4. Install Python dependencies using `pipenv install` or `pipenv install --ignore-pipfile` or `pip install -r requirements.txt` (if using virtualenv)

5. Under config directory:
   - Input your Outlook account credentials in config.json file with the following parameters:

```
   {
     "profile": {
       "outlook": {
         "sender": "<insert your e-mail address>",
         "password": "<insert your e-mail password>",
         "recipients": "<insert recipient e-mail address>",
         "cc": "<insert recipient e-mail address>",             # (this is optional)
         "bcc": "<insert recipient e-mail address>"             # (this is optional)
       }
     }
   }
```

  - Input your API keys after registration from the above API sources in keys.json file

```
   {
     "newsapi": {
       "key": "<insert api key>"
     },
     "newsdataio": {
       "key": "<insert api key>"
     },
     "alphavantage": {
       "key": "<insert api key>"
     }
   }
```

5. After all dependencies are installed and config files are set, run either main_news.py or main_price.py via
   
   (i) accessing your virtual environment: `pipenv shell` (if using Pipenv) or `.\Scripts\activate` (Windows) or `source ./bin/activate` (Linux) if using virtualenv
   
   (ii) running Python script: `pipenv run {python script}` (for Pipenv) or `python {python script}` (for virtualenv).
