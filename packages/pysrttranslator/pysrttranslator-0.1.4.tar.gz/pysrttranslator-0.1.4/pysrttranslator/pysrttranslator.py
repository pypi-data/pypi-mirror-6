#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,json,urllib
from pysrt import SubRipFile, SubRipItem
from apiclient.discovery import build
import logging
import configglue
from configglue import glue, schema, app, parser
from optparse import OptionParser
_logger = logging.getLogger('- Translater -')


def translate(text, input_language, output_language, api_key):
    '''
    Build a service object for interacting with the API. Visit the Google APIs Console
    <http://code.google.com/apis/console> to get an API key for your own application.
    
    returns Translated text
    '''
    service = build('translate', 'v2',
            developerKey=api_key)
    dec = text.replace('\n',' ') 
    translated = service.translations().list(
            source = input_language,
            target = output_language,
            q = dec
    ).execute()
    done = translated.get('translations')[0].get('translatedText')
    msg = "[Origin]: %s [Destiny]: %s " % (dec, done)
    _logger.info(msg)
    return done 

def translate_srt_file(input_file, output_file, input_language, output_language, api_key):
    """translate a srt file from a language to another

    :input_file: srt file with subtitles
    :output_file:
    :input_language:
    :output_language:
    :api_key: Google API key generally from config file.
    """

    _logger.info('[FileName]: %s' % input_file)
    subs = SubRipFile.open(input_file)
    for sentence in subs:
        dec = sentence.text.encode('iso-8859-1', 'ignore')
        sentence.text = '%s \n' % translate(dec, input_language, output_language, api_key)
    subs.save(output_file, 'utf-8')

def get_options():
    pa = OptionParser(usage='%prog input.srt [optional| output.srt] [options]')
    a = app.App(MyAppConfig, parser=pa, name='pysrttranslator')
    result = {}
    scp = parser.SchemaConfigParser(MyAppConfig())
    scp.read(a.config.get_config_files(a))
    # read the configuration files
    # support command-line integration
    op, opts, args = glue.schemaconfigglue(scp)
    # validate the config (after taking into account any command-line
    # provided options
    is_valid, reasons = scp.is_valid(report=True)
    if not is_valid:
        op.error(reasons[0])
    values = scp.values('__main__')
    for opt in ('input_lang', 'output_lang', 'log_file', 'google_api_key'):
        option = scp.schema.section('__main__').option(opt)
        value = values.get(opt)
        result[opt] = value
    if args: 
        result['input_file'] = args[0]
        result['output_file'] = len(args)>=2 and args[1] or 'output.srt'
    else:
        raise ValueError('You must provide at least the input srt file, see program --help for options')
    if not result.get('google_api_key'):
        raise ValueError('You must as first step configure your API key in the config file, see program --help for options')
    return result

class MyAppConfig(schema.Schema):
    '''
    This class is to instanciate the configglue options to manage the configuration file and
    optparsers toghether. You will be able to load the configuration option from the command line
    and some of this 3 paths.::

        /etc/xdg/pysrttranslator/pysrttranslator.cfg
        /home/<user>/.config/pysrttranslator/pysrttranslator.cfg
        ./local.cfg

    See pysrttranslator --help to read the options available, you can create this files as any
    normal text file with the ini syntax.

    You can see below some options.
    '''
    
    input_lang = schema.StringOption(short_name='i', default='en',
               help='ISO Code for input file  lang i.e: "en" for english')
    'ISO Code for input file  lang i.e: "en" for english'
    output_lang = schema.StringOption(short_name='o', default='es',
               help='ISO Code for output file lang i.e: "es" for spanish')
    'ISO Code for output file lang i.e: "es" for spanish'
    log_file = schema.StringOption(short_name='l', default='pysrttranslator.log',
               help='Set the log file by default in the folder you are running'
                    'the script you will have a translate.log')
    '''Set the log file by default in the folder you are running the script you will have a
    pysrttranslate.log in the path you are running the script'''
    google_api_key = schema.StringOption(short_name='A', default=False, fatal=True,
               help='Set your google api key, read the doc for more information')
    '''Set your google api key, read the google doc for more information'''
#TODO: This options will be necesary to autocreate the config file on installation process.
#pa.add_option('-s', '--save-config', help="Generate and save arguments in config file.")
#pa.add_option('-f', '--input-file', help="Input file to translate ie.: examplesubtitle.srt.")
#pa.add_option('-g', '--output-file', help="Output file to translate ie.: examplesubtitle-tr.srt.")

if __name__ == '__main__':
    o = get_options()
    logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s %(message)s',
        filename=o['log_file'], level=logging.DEBUG)
    _logger.warning('Using this api Key %s' % o['google_api_key'])
    translate_srt_file(o['input_file'],
                       o['output_file'],
                       o['input_lang'],
                       o['output_lang'],
                       o['google_api_key'])

