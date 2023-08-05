import json
import os
import pydoc
import sys

DEFAULT_WELCOME = '''
Welcome to interactive help.
Ask for topic for help on it,
write %(list)r to see list of available topics,
or write %(exit)r to exit.'''.strip()

builtin_input = input if sys.version_info[0]>2 else raw_input

def evaluator(left="<%[", right="]%>"):
    '''
    Returns function which can be used as processor.
    Returned function will evaluate eveyrthing what is surrounded with
    left and right strings as python expression and return str() representation
    of it.
    Evaluation is recursive, so following code will go without exceptions:
        foo = evaluator()
        txt="a <%[ 1+ 3 ]%> c <%[ <%[ 'x'.upper() ]%> d <%[ <%[ int('2') ]%> * 3 ]%> "
        assert foo(txt) == "a 4 c <%[ X d 6 "
    as you can see, last "6" comes from "<%[ <%[ int('2') ]%> * 3 ]%>".
    '''
    def out(text):
        replacing = True
        while replacing:
            partitioned = []
            for part in text.split(left):
                for block in part.split(right):
                    partitioned.append(block)
                    partitioned.append(right)
                partitioned.pop(-1)
                partitioned.append(left)
            partitioned.pop(-1)
            # at this moment partitioned should be list of lefts, rights and blocks of texts between, in order


            if len(partitioned)<3:
                return text


            replacing = False
            for idx in range(1, len(partitioned)-1):
                if partitioned[idx-1] == left and partitioned[idx +1] == right:
                    replacing = True
                    partitioned[idx-1:idx+2] = [None, eval(partitioned[idx]), None]
            while None in partitioned:
                partitioned.remove(None)
            text = "".join(map(str, partitioned))
        return text
    return out

if __name__=="__main__":
    foo = evaluator()
    txt="a <%[ 1+ 3 ]%> c <%[ <%[ 'x'.upper() ]%> d <%[ <%[ int('2') ]%> * 3 ]%> "
    print(txt)
    print(foo(txt))


class PyMan(object):
    '''
    Class to be used for help system.
    At instantiation you need to pass (at least) file with description of 
    existing topics.
    Man page DB format is described in constructor docstring.
    
    Example use case:
    Lets assume we have application (lets call it APP) that has two modes: "get"
    and "post". Also, we want to include help. Here we can see basic usage for 
    this mode:
    APP help - should go to interactive session, in which we can input 
        (case-insensitive) topic: get or post, ask for list of topics, or ask
        app to exit
    APP help get - should show user help for "get" mode
    APP help post - should show user help for "post" mode
    
    We create following files:
    get_man.txt - containing help for "get" mode
    post_man.txt - containing help for "post" mode
    mandb.json - with following content:
    (content begin)
    [
        {
        "topics": ["get"],
        "file": "get_man.txt"
        },
        {
        "topics": ["post"],
        "file": "post_man.txt"
        }
    ]
    (content end)
    
    We create following PyMan instance (assuming db.json is in the same directory
    as module containing instance):
    with open(os.path.realpath(
                    os.path.join(
                        os.path.split(__file__)[0],
                        "mandb.json"
                    )
                )) as f:
        man = PyMan(f, case_sensitive = False)
    Also, we bind call to 'APP help' (with no topic) to:
        man.start_interactive_session()
    and call to 'APP help <topic>' to (assuming value of <topic> will be in
    variable topic):
        man.view(topic)
    '''
    def __init__(self, db_stream, cached = True, case_sensitive=True,
                        base="", header = '', footer = "\n\n\nViewed with PyMan",
                        processor = lambda x: x):
        '''
        full_db_path -  file-like object from which man-db will be loaded*
        cached -        if True, each man page will be loaded only once; 
            else each call to topic will result in opening man page file
        case_sensitive - if False, call topic x will have the same result as
            call to x.lower(), else the same word with other casing will have
            different results (possibly wont be found)
        base -          if provided, each file will be searched relatively
            to this path**
        header -        string to be added at the beginning of each man page
            (you probably want to end it with new line, or even many)
        footer -        string to be attached at the end of each man page
            (you probably want to start it with new line or even many)
        processor -     function taking one argument - man page; it should
            return string, that will be formatted (header and footer will
            be added); default is lambda x: x, you can use use your own to 
            introduce some kind of marker language

        *     db_stream.read() should return JSON list of objects with fields "topics"
            and "file"; "topics" should be JSON list of strings representing
            topics; "file" should be path to file containing man page for given
            topics
        **   it works by getting real path for joined base and searched relative
            path
        '''
        self._base = base
        self._header = header
        self._footer = footer
        self._processor = processor
        self._case_sensitive = case_sensitive
        self._cached = cached
        self._db = {}
        self._cache = {}
        loaded = json.load(db_stream)
        for entry in loaded:
            for topic in entry['topics']:
                if not case_sensitive:
                    topic = topic.lower()
                self._db[topic] = entry['file']

    def view(self, topic):
        '''
        View man page for given topic (considering case_sensitive parameter).
        It will use best possible pager - using the same technique as builtin
        help() function.
        '''
        if not self._case_sensitive:
            topic = topic.lower()
        if self._cached and topic in self._cache:
            txt = self._cache[topic]
        else:
            path = os.path.realpath(os.path.join(self._base, self._db[topic]))
            with open(path) as f:
                txt = f.read()
            txt = self._processor(txt)
            txt = self._header + txt + self._footer
        pydoc.pager(txt)

    def topics(self):
        '''
        Returns list of registered topics (according to given man page base).
        '''
        return self._db.keys()

    def start_interactive_session(self, welcome=DEFAULT_WELCOME, prompt="help> ",
                                list_keyword="list", exit_keyword="exit", 
                                input_method=builtin_input):
        '''
        Start interactive help session. User will be asked to input desired topic
        or one of list or exit command (which will result in listing registered
        topics, or exiting interactive session).

        welcome - string to be printed at the very beginning of session, formatted
            with dict {"list": <list_keyword>, "exit": <exit_keyword>} (for values
            see: below)
        prompt - string to be passed to input_method (see: below)
        list_keyword - string, which when inputted by user will result in listing
            registered topics
        exit_keyword - string, which when inputted by user will result in exiting
            interactive session
        input_method - function taking one argument - prompt string and returning
            topic to be viewed; default is builtin function (raw_)input*; it should have
            similiar interface

        * depends on python version
        '''
        if list_keyword in self.topics():
            print("Keyword for listing (%r) topics shadows some topic!" % list_keyword, file=sys.stderr)
        if exit_keyword in self.topics():
            print("Keyword for exiting (%r) topics shadows some topic!" % exit_keyword, file=sys.stderr)
        print(welcome % {"list": list_keyword, "exit": exit_keyword})
        asked = input_method(prompt)
        while not asked == exit_keyword:
            if asked == list_keyword:
                pydoc.pager('''Registered topics:
'''+
                            ( "\n".join(sorted(list(set(
                                map(
                                    lambda x: "- "+x,
                                    self.topics()
                                )
                            )))
                            )
                            )
                )
            elif asked in self.topics():
                self.view(asked)
            else:
                print("Topic %r not found!" % asked)
            asked = input_method(prompt)

