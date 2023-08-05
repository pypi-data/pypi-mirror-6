   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Description: betamax
        =======
        
        Betamax is a VCR_ imitation for requests. This will make mocking out requests
        much easier. It is tested on `Travis CI`_.
        
        Put in a more humorous way: "Betamax records your HTTP interactions so the NSA
        does not have to."
        
        Example Use
        -----------
        
        ::
        
            from betamax import Betamax
            from requests import Session
            from unittest import TestCase
        
            with Betamax.configure() as config:
                config.cassette_library_dir = 'tests/fixtures/cassettes'
        
        
            class TestGitHubAPI(TestCase):
                def setUp(self):
                    self.session = Session()
                    self.headers.update(...)
        
                # Set the cassette in a line other than the context declaration
                def test_user(self):
                    with Betamax(self.session) as vcr:
                        vcr.use_cassette('user')
                        resp = self.session.get('https://api.github.com/user',
                                                auth=('user', 'pass'))
                        assert resp.json()['login'] is not None
        
                # Set the cassette in line with the context declaration
                def test_repo(self):
                    with Betamax(self.session).use_cassette('repo'):
                        resp = self.session.get(
                            'https://api.github.com/repos/sigmavirus24/github3.py'
                            )
                        assert resp.json()['owner'] != {}
        
        What does it even do?
        ---------------------
        
        If you are unfamiliar with VCR_, you might need a better explanation of what
        Betamax does.
        
        Betamax intercepts every request you make and attempts to find a matching
        request that has already been intercepted and recorded. Two things can then
        happen:
        
        1. If there is a matching request, it will return the response that is
           associated with it.
        2. If there is **not** a matching request and it is allowed to record new
           responses, it will make the request, record the response and return the
           response.
        
        Recorded requests and corresponding responses - also known as interactions -
        are stored in files called cassettes. (An example cassette can be seen in
        the `examples section of the documentation`_.) The directory you store your
        cassettes in is called your library, or your `cassette library`_.
        
        VCR Cassette Compatiblity
        -------------------------
        
        Betamax can use any VCR-recorded cassette as of this point in time. The only
        caveat is that python-requests returns a URL on each response. VCR does not
        store that in a cassette now but we will. Any VCR-recorded cassette used to
        playback a response will unfortunately not have a URL attribute on responses
        that are returned. This is a minor annoyance but not something that can be
        fixed.
        
        Contributing
        ------------
        
        You can check out the project board on waffle.io_ to see what the status of
        each issue is.
        
        .. _VCR: https://github.com/vcr/vcr
        .. _Travis CI: https://travis-ci.org/sigmavirus24/betamax
        .. _waffle.io: https://waffle.io/sigmavirus24/betamax
        .. _examples section of the documentation:
            http://betamax.readthedocs.org/en/latest/api.html#examples
        .. _cassette library:
            http://betamax.readthedocs.org/en/latest/cassettes.html
        
        
        History
        =======
        
        0.1.6 - 2013-xx-xx
        ------------------
        
        - Fix how global settings and per-invocation options are persisted and 
          honored. (#10)
        
        - Support ``match_requests_on`` as a parameter sent to
          ``Betamax#use_cassette``. (No issue)
        
        0.1.5 - 2013-09-27
        ------------------
        
        - Make sure what we pass to ``base64.b64decode`` is a bytes object
        
        0.1.4 - 2013-09-27
        ------------------
        
        - Do not try to sanitize something that may not exist.
         
        0.1.3 - 2013-09-27
        ------------------
        
        - Fix issue when response has a Content-Encoding of gzip and we need to 
          preserve the original bytes of the message.
        
        0.1.2 - 2013-09-21
        ------------------
        
        - Fix issues with how requests parses cookies out of responses
        
        - Fix unicode issues with ``Response#text`` (trying to use ``Response#json``
          raises exception because it cannot use string decoding on a unicode string)
        
        0.1.1 - 2013-09-19
        ------------------
        
        - Fix issue where there is a unicode character not in ``range(128)``
        
        0.1.0 - 2013-09-17
        ------------------
        
        - Initial Release
        
        - Support for VCR generated cassettes (JSON only)
        
        - Support for ``re_record_interval``
        
        - Support for the ``once``, ``all``, ``new_episodes``, ``all`` cassette modes
        
        - Support for filtering sensitive data
        
        - Support for the following methods of request matching:
        
          - Method
        
          - URI
        
          - Host
        
          - Path
        
          - Query String
        
          - Body
        
          - Headers
        
Platform: UNKNOWN
Classifier: Development Status :: 4 - Beta
Classifier: License :: OSI Approved
Classifier: Intended Audience :: Developers
Classifier: Programming Language :: Python
Classifier: Programming Language :: Python :: 2
Classifier: Programming Language :: Python :: 2.6
Classifier: Programming Language :: Python :: 2.7
Classifier: Programming Language :: Python :: 3
Classifier: Programming Language :: Python :: 3.2
Classifier: Programming Language :: Python :: 3.3
Classifier: Programming Language :: Python :: Implementation :: CPython
