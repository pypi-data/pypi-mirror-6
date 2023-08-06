# -*- coding: utf-8 -*-
import argparse
import polib
import re
import time
import urllib2

from translate import Translator


DEFAULT = re.compile(r'Default:\s(.*)')
VAR_REGEX = re.compile(r'(\$\{[^\}]*\})')
SOURCE_LANGUAGE = 'en'
BREATHE = 0.25
ERROR = 31
SUCCESS = 32
INFO = 33


def log(bash_color, type, text):
    print u'[\033[{0}m {1} \033[0m] {2}'.format(bash_color, type, text)


def autotranslate(path, source_language, target_language,
                  ignore_already_translated=True):
    """Given a po file which is opened using polib and processed through
       Google Translator for all untranslated items by default
    """

    try:
        catalog = polib.pofile(path)
    except UnicodeDecodeError:
        raise Exception(("Encoding problem while parsing {0}, are you "
                         "sure that's a PO file?").format(path))

    translator = Translator(to_lang=target_language, from_lang=source_language)
    try:
        for idx, entry in enumerate(catalog):

            if ignore_already_translated and entry.translated():
                continue

            default_text = DEFAULT.match(entry.comment)
            if default_text:
                to_translate = default_text.group(1)
            else:
                to_translate = entry.msgid

            # Do we have to handle variables?
            variables = VAR_REGEX.search(to_translate)
            try:
                translated = translator.translate(to_translate.encode('utf-8'))
            except urllib2.HTTPError as e:
                log(ERROR, 'Error', u'{0:s} raised {1}: {2:s}'.format(
                    entry, e.__class__, e))
                continue

            if variables is not None:
                log(INFO, 'Found variable(s)', ', '.join(variables.groups()))

            log(SUCCESS, 'Success', u'{0} -> {1}'.format(
                to_translate, translated))

            # Save entry
            catalog[idx].msgstr = translated
            time.sleep(BREATHE)

    except KeyboardInterrupt:
        log(ERROR, 'Quit', '')

    catalog.save()


def AutoTranslator():
    parser = argparse.ArgumentParser(description='Translate Po files.')
    parser.add_argument('-i',
                        dest='input', action='append', nargs=2,
                        required=True, metavar=('<locale>', '<po file>'),
                        help='Locale and filename of po-file to process')
    parser.add_argument('-s',
                        dest='source_lang', type=str,
                        default=SOURCE_LANGUAGE, metavar='LANGUAGE',
                        help='Source language to translate from.')
    parser.add_argument('-u',
                        dest='update', action='store_true',
                        help='Force updating translations by '
                             'retranslating all msgids.')
    options = parser.parse_args()

    for target_lang, pofile in options.input:
        autotranslate(
            pofile, options.source_lang, target_lang, not options.update)
