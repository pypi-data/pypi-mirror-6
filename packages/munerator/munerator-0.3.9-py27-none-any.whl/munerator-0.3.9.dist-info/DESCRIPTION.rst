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
Description: ===============================
        munerator
        ===============================
        
        .. image:: https://badge.fury.io/py/munerator.png
            :target: http://badge.fury.io/py/munerator
        
        .. image:: https://travis-ci.org/aequitas/munerator.png?branch=master
                :target: https://travis-ci.org/aequitas/munerator
        
        .. image:: https://pypip.in/d/munerator/badge.png
                :target: https://crate.io/packages/munerator?version=latest
        
        
        Munerator: Organizer of gladiatorial fights. (http://www.unrv.com/culture/gladiator.php)
        
        Installing/Running
        ------------------
        
            pip install -e .
        
            munerator -h
        
        To run the minimal stack:
        
            munerator trans &
            munerator context &
            
            munerator wrap "cat tests/game_output.txt"
        
        Add -v for verbose output.
        
        
        Modules
        -------
        
        - wrap: wrap game/command, capture output, send to translator
        - trans: translator, match incoming lines to regex, create event, send to context
        - context: add context to events, eg mapname, players, and broadcast events to subscribers
        
        - ledbar: subscribe to game events, show status on ledbar
        - old: subscribe to game events, proxy events to old api http://quake.ijohan.nl
        
        
        Features
        --------
        
        * TODO
        
        Requirements
        ------------
        
        - Python >= 2.6 or >= 3.3
        - ZMQ
        - OpenArena
        
        License
        -------
        
        MIT licensed. See the bundled `LICENSE <https://github.com/aequitas/munerator/blob/master/LICENSE>`_ file for more details.
        
Platform: UNKNOWN
Classifier: Development Status :: 2 - Pre-Alpha
Classifier: Intended Audience :: Developers
Classifier: License :: OSI Approved :: MIT License
Classifier: Natural Language :: English
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: Implementation :: CPython
Classifier: Programming Language :: Python :: Implementation :: PyPy
