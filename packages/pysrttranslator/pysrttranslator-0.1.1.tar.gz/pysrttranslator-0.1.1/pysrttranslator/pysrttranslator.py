#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,json,urllib
from pysrt import SubRipFile, SubRipItem
from apiclient.discovery import build
import logging
import argparse
_logger = logging.getLogger('- Translater -')

service = build('translate', 'v2',
        developerKey='AIzaSyBg4DhmbLLSfBq5pZpNECuJZYm0nKKp8WI')

def translate(text, input_language, output_language):
    '''
    Build a service object for interacting with the API. Visit the Google APIs Console
    <http://code.google.com/apis/console> to get an API key for your own application.
    
    returns Translated text
    '''
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

def translate_srt_file(input_file, output_file, input_language, output_language):
    """translate a srt file from a language to another

    :input_file: srt file with subtitles
    :output_file:
    :input_language:
    :output_language:
    """

    _logger.info('[FileName]: %s' % input_file)
    subs = SubRipFile.open(input_file)
    for sentence in subs:
        dec = sentence.text.encode('iso-8859-1', 'ignore')
        sentence.text = '%s \n' % translate(dec, input_language, output_language)
    subs.save(output_file, 'utf-8')


def return_parser():
    parser = argparse.ArgumentParser(prog='SRT python translator with google')
    parser.add_argument('-i', help='Input File srt format example: MyFile.srt')
    parser.add_argument('-o', help='Output File srt format example: MyFileOut.srt')
    parser.add_argument('-il', default='en', help='Code ISO for input lang i.e: "en" for english')
    parser.add_argument('-ol', default='es', help='Code ISO for output lang i.e: "es" for spanish')
    parser.add_argument('--config', default=None, help='Config File i.e; Config File i.e; /home/username/ConfigFile.cfg')
    parser.add_argument('--log_file', default='translate.log', help='Set the log file by default in the folder you are running'
            'the script you will have a translate.log')
    parser.add_argument('--google-key', help='Google Developer Key')
    return parser


if __name__ == '__main__':

    #TODO: Here we should write the algorithm to read the config file too
    args = return_parser().parse_args() 
    logging.basicConfig(format='%(levelname)s:%(name)s:%(asctime)s %(message)s',
        filename=args.log_file, level=logging.DEBUG)
