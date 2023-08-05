# threebean_tahrir_theme

Custom threebean.org theme for Tahrir. To be used for my personal badges.

## Usage

In your Tahrir virtualenv, install this theme from PyPI:

    pip install threebean_tahrir_theme

In the config file you use to start your server, make sure the following
option is set:

    tahrir.theme_name = threebean_tahrir_theme

So if you start your server with `pserve myconfig.ini --reload` or something
of that nature, you want to make the change in `myconfig.ini`. Tahrir by
default comes with a `production.ini` and a `development.ini`. You can make
use of one of these, or create your own based on one.

If those two things are all set, you should be good!

## License

This project is licensed under GPLv3+. The full text of this license should be
included with this project in the `LICENSE` file.

## Contributors

-   Ralph Bean (threebean)

Forked from the fossrit_tahrir_theme originally written by:

-   David Gay (oddshocks)
