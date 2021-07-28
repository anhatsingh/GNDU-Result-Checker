# GNDU-Result-Checker

![Debug Status](https://github.com/anhatsingh/GNDU-Result-Checker/actions/workflows/python-package2.yml/badge.svg?branch=main)
![Build Status](https://github.com/anhatsingh/GNDU-Result-Checker/actions/workflows/python-package.yml/badge.svg?branch=main)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Downloads](https://img.shields.io/badge/download-all%20releases-brightgreen.svg)](https://github.com/anhatsingh/GNDU-Result-Checker/releases/)

## About

This Application uses the `requests`, `BeautifulSoup`, `Whastapp Python API` with MultiThreading Support to check if any new result is declared on GNDU website, and reports back to us through Whatsapp.

## Changelog
Version 1.x
1. Implements `Selenium` library to check if the result is declared on GNDU website.
2. Reports the status constantly through Whatsapp.

The lead developer is Anhat Singh

## Building / Installing Python-Auto-Attendance

### Pre-Requisites
1. Install the Python dependencies by running the following pip commands
    ```
    pip install -r requirements.txt --no-index --find-links file:///tmp/packages
    ```
2. Open your whatsapp, create a group named `Automation`. Note that it is case sensitive.
3. Use the included `chromedriver.exe` or download the latest one from [ChromeDriver - WebDriver for Chrome](https://chromedriver.chromium.org/) and keep it in the root directory.

## Running GNDU-Result-Checker

1. Run the following command:
    ```
    py app.py
    ```
2. Login to Whatsapp Web using your phone.
3. Enjoy!

## License

    The code in this repository is licensed under the GNU General Public Licence, Version 3.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       https://www.gnu.org/licenses/gpl-3.0.en.html

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

**NOTE**: This software depends on other packages that may be licensed under different open source licenses.
