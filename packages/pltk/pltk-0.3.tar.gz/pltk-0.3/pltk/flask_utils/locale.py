"""Locale support."""
from flask import request


def setup_locale(babel, app):
    """Setup locale."""
    # don't select a different locale when running tests
    if app.config['TESTING']:
        return

    @babel.localeselector
    def get_locale():
        """Guess the language from the user accept header."""
        return request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'])
