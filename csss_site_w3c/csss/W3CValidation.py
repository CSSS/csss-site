import codecs
import gzip
import os
import re
import sys
from io import BytesIO

import requests
from django.conf import settings
from django.test import SimpleTestCase


class W3CValidation(SimpleTestCase):

    def validate_page(self, path="/"):
        original_url = settings.W3C_TESTS_URL + path
        print(f"testing path [{original_url}]")
        response = requests.request("GET", original_url, headers={}, data={})

        path = "/index" if path == "/" else path
        lastForwardSlash = path.rfind("/")
        html_file = f'{settings.W3C_TEST_RESULT_DIRECTORY}{path}.html'
        if not os.path.exists(f'{settings.W3C_TEST_RESULT_DIRECTORY}{path[:lastForwardSlash]}'):
            os.makedirs(f'{settings.W3C_TEST_RESULT_DIRECTORY}{path[:lastForwardSlash]}', 0o755, exist_ok=True)

        with open(html_file, 'wb') as f:
            f.write(response.content)
        with BytesIO() as buf:
            with gzip.GzipFile(fileobj=buf, mode='wb') as gzipper:
                gzipper.write(response.content)
            gzippeddata = buf.getvalue()

        req = requests.post(
            "https://html5.validator.nu/",
            params={
                'out': 'gnu',
            },
            headers={
                'Content-Type': response.headers['Content-Type'],
                'Accept-Encoding': 'gzip',
                'Content-Encoding': 'gzip',
                'Content-Length': str(len(gzippeddata)),
            },
            data=gzippeddata
        )

        output = req.text
        validation_issues = output and not re.search(r'The document (is valid|validates)', output)
        if validation_issues:
            sys.stderr.write("\n\n")
            sys.stderr.write(f"{settings.W3C_TESTS_URL + path}")
            sys.stderr.write(f"\n{output}")
            sys.stderr.write("To debug, see:")
            sys.stderr.write(f"\t{html_file}")
            txt_file = re.sub(r'\.x?html$', '.txt', html_file)
            assert txt_file != html_file
            sys.stderr.write(f"\t{txt_file}")
            with codecs.open(txt_file, 'w', 'utf-8') as f:
                f.write('Arguments to GET:\n')
                f.write('\n')
                f.write(output)
        self.assertTrue(not validation_issues, f"Validation issue for {original_url}")
