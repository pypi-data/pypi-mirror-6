"""
GoldSaxTamilTranslate Version 0.1.
	To enable easy translation for python applications to use this package on from English to Tamil, including a transliteration.

Copyright (c) <2014> Author Vance King Saxbe. A, and contributors Power Dominion Enterprise, Precieux Consulting and other contributors.

To install the package, you should be using Python 3.3 and above.(It also works with 2.7).

pip install GoldSaxTamilTranslate 



This will install the package for you.

from the python IDE,

from GoldSaxTamilTranslate import *

print(GoldSaxTamilTranslate.Translate("sincere"))



Please refer to documentation for further use of this package.

For further support email Vance King Saxbe. A to vsaxbe@yahoo.com.

This Package is released under Contributor Agreement between Python Software Foundation (“PSF”) and Vance King Saxbe. A. and MIT License.

The MIT License (MIT)

Copyright (c) 2014 Author Vance King Saxbe. A, and contributors GoldSax Group, GoldSax Foundation, GoldSax Technologies, Power Dominion Enterprise, Precieux Consulting and other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import urllib3
import string
class GoldSaxTamilTranslate:
    def Translate(sentence):
        words = sentence.split(' ')
        translatedsentence = ""
        transliteratedsentence = ""
        for word in words:
            url = "http://www.shabdkosh.com/ta/translate?e="+word+"&l=ml"
            http = urllib3.PoolManager()        
            g_connector = http.request('GET', url)
            g_connector.release_conn()
            datadecoder = g_connector.data.decode("utf-8")
            try:
                first_splitter = datadecoder.split('</a><span class="latin" style="display:none;"><br>')
                second_splitter = first_splitter[0].split('>')
                third_splitter = first_splitter[1].split('</span>')
                translatedsentence = translatedsentence+" "+second_splitter[-1]
                transliteratedsentence = transliteratedsentence+" "+third_splitter[0]
            except IndexError:
                print("Word Translation not found for ", word," ...Please try another word")
        return(translatedsentence, transliteratedsentence)
        
