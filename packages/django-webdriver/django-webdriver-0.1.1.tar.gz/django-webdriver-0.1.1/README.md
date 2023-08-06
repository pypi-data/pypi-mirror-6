# django-webdriver

Django app to run selenium tests with webdriver

## Features

Extends the feature of [django-nose](https://github.com/django-nose/django-nose) to manage the selenium tests.

## Installation

You can get django-webdriver from PyPi:
```bash
pip install django-webdriver
```
  
To use it you should add it to your `INSTALLED_APPS` in `settings.py`.  
Django-webdriver uses django-nose to run the tests, so you should also configure django-nose in your project:

```python
INSTALLED_APPS = (
    ...  
    'django_webdriver',
    'django_nose',
    ...
)
  
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
```
  
## Usage

With django-webdriver you may run just unit tests or just selenium tests or the both.

### Launch tests

* `--selenium-only`: only run selenium tests
* `--with-selenium`: run all tests (unit and selenium)
* ` `: will only run unit test.

### Configure

#### Local

Add `--webdriver=` to specify webdriver you want to use locally.

It can be one of these for example (be careful to case):
* Firefox
* PhantomJS
* Chrome
* ...
* [More here](http://selenium-python.readthedocs.org/en/latest/api.html#webdriver-api)

##### Example

```bash
./manage.py test --with-selenium --webdriver=PhantomJS
```

#### Remote

* Add `--remote_selenium_provider=` to specify which remote grid you want to use.
* Add configuration for each grid in your `settings.py`:
```python
DJANGO_WEBDRIVER_SETTINGS = {
    'remote_providers': {
        'grid': {
            'url': 'http://192.168.0.18:4444/wd/hub',
            # will use 'default' capabilities
        },
        'sauce-lab': {
            'url': 'http://my_url',
            'capabilities': 'ie',
        },
    },
    'remote_capabilities': {
        'default': [
            {
                'browser': 'firefox',
                'platform': 'WINDOWS'
            },
        ],
        'ie': [
            {
                'browser: 'internet explorer',
                'version': 6,
            }
        ]
    }
}
```
