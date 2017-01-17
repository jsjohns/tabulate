#!/usr/bin/env python3

import json
import io
import sys
import os.path
import magic
import csv
import json
from shlex import quote
from shutil import copyfile
from subprocess import check_call, PIPE, DEVNULL, check_output
from flask import Flask, render_template, request


INTERNAL_PDF_DIR = os.path.dirname(os.path.realpath(__file__)) + "/static/processed"


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = os.path.join("/tmp", file.filename)
    file.save(filename)

    return json.dumps(tabulate(filename))

def tabulate(filename):
    if magic.from_file(filename, mime=True) == "application/pdf":
        return tabulate_pdf(filename)
    else:
        return tabulate_image(filename)


def tabulate_pdf(filename):
    basename = os.path.basename(filename)
    filename = os.path.join(INTERNAL_PDF_DIR, basename)
    copyfile(filename, os.path.join(INTERNAL_PDF_DIR, basename))

    return {
        "searchable_pdf_url": searchable_pdf_url(basename),
        "table_data": table_data(filename, original_is_pdf=True)
    }


def tabulate_image(image_filename):
    oriented_image_filename = "/tmp/oriented-" + os.path.basename(image_filename)
    make_oriented_image(image_filename, oriented_image_filename)
    pdf_filename = os.path.join(INTERNAL_PDF_DIR, os.path.basename(image_filename) + ".pdf")
    make_searchable_pdf(oriented_image_filename, pdf_filename)

    return {
        "searchable_pdf_url": searchable_pdf_url(pdf_filename),
        "table_data": table_data(pdf_filename)
    }


def searchable_pdf_url(pdf_filename):
    return os.path.join("/static/processed", os.path.basename(pdf_filename))


def make_oriented_image(source_image_filename, destination_image_filename):
    # Rotates the image to be in the correct orientation (via ImageMagick).

    source_image_filename = quote(source_image_filename)
    destination_image_filename = quote(destination_image_filename)
    check_call("convert -auto-orient %s %s" % (source_image_filename, destination_image_filename), shell=True)


def make_searchable_pdf(source_image_filename, destination_pdf_filename):
    # Creates a searchable PDF representing the given image (via Tesseract).

    source_image_filename = quote(source_image_filename)
    destination_pdf_filename = quote(destination_pdf_filename)
    check_call("tesseract %s stdout -psm 6 pdf > %s" % (source_image_filename, destination_pdf_filename), shell=True)


def table_data(pdf_filename, original_is_pdf=False):
    # Returns a list of table rows representing the given PDF (via Tabula).

    tabula_jar = "java -jar /bin/tabula-0.9.1-jar-with-dependencies.jar"
    if original_is_pdf:
        args = "--guess " + quote(pdf_filename)
    else:
        args = "-a 1,1,999999,999999 " + quote(pdf_filename)
    stdout = check_output(tabula_jar + " " + args, stderr=DEVNULL, shell=True)

    return list(csv.reader(io.StringIO(stdout.decode('ascii', errors='ignore'))))


if __name__ == '__main__':
      app.run(host='0.0.0.0', port=80, debug=True)
