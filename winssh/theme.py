"""

(c) 2023 by Bas ten Berge. All rights reserved

This program is distributed in the hope that it will be useful, but is provided AS IS with ABSOLUTELY NO WARRANTY;
The entire risk as to the quality and performance of the program is with you. Should the program prove defective,
you assume the cost of all necessary servicing, repair or correction. In no event will any of the developers, or
any other party, be liable to anyone for damages arising out of the use or inability to use the program.
You may copy and distribute copies of the Program, provided that you keep intact all the notices that refer to the
absence of any warranty.

"""
theme_settings = {
    'dark': {
        'button': {
            'bg': '#42414d',
            'fg': '#ffffff',
        },
        'controls': {
            'bg': '#2b2a33',
        },
        'form': {
            'bg': '#2b2a33',
        },
        'label': {
            'bg': '#2b2a33',
            'fg': '#ffffff',
        },
    },
    'light': {
        'button': {
            'bg': '#42414d',
            'fg': '#ffffff',
        },
        'controls': {
            'bg': '#ffffff',
        },
        'form': {
            'bg': '#ffffff',
        },
        'label': {
            'bg': '#ffffff',
        },
    },
}


class OnThemeChangedMixin:
    """
    Adds a method that watches the theme to change the view accordingly

    """
    def on_theme_changed(self, new_mode, **kwargs):
        """
        Fired when the theme has changed

        new_mode contains 'Dark' when dark mode is selected and 'Light' otherwise.

        """


__all__ = [
    'OnThemeChangedMixin',
    'theme_settings',
]