---
Title: Kwargs Considered Harmful
Date: 2025-02-18 23:51
Modified: 2025-02-19 01:57
Category: Python
Tags: python, code-style, kwargs, typing
Authors: Zach Paden
Summary: kwargs are bad, but we can make them better.
---

# WIP: This post is still being written,
At work, we'd been having an issue for awhile. A certain service would test succesfully locally, deploy well but then after a few hours would start breaking at a notably high frequency. What was going on? A review of the code led us to believe there were no problems with it, and the tests passed. The assumption we all walked away with was "that protocol must be super flaky, it's legacy anyways".

A few months later, we came to another fork in the road. Either use that flaky python legacy code, or, use a managed provider that the team all thought was even worse. Could we fix the flaky code and figure out what was going on?

I cracked open my editor and started digging down into the problem. After digging up and down and trying to understand the entire library better we figured something out...

The code, essentially, looked like this:

```py
# High Level Module
from .connections import connection
from .low_level import read_file
def read_something(src:str, server:str, username:str, password:str, **kwargs) -> str:
    raw = read_file(src, server, username, passowrd, **kwargs)
    ...
```

```py
# low_level.py
def read_file(src: str, server:str, username:str, password:str, connection=None, **kwargs):
    ...

```

```py
# connections.py
import atexit

cache = {}

def register_connection(username)
class Connection:
    def __init__(self, username:str, password:str, hostname:str):
        ...

    def open_connection(self):
        if self.hostname in cache.keys():


    def close(self):
        # properly close the connection
        ...

def _close_cache():
    for server, conn in cache.items()
        conn.close()

atexit.register(_close_cache)
```

While the actual code had a lot more going on, being hundreds of lines across more than just the three simple layers here, this still shows the general pattern and the issue I had found.

In the server process, connections were being open implicitly, cached in memory and never closed -- since the cache that no one knew existed was only ever cleared when the python process was shut down, which in our case only happened when we did a deployment.

People using the high level abstraction do not, and should not _need_ to think about the internal mechanisms much.

## Why Kwargs?

Really the problem here is that we had undocumented side effects of code that were hidden under layers of indirection, not with kwargs itself, however, kwargs allowed this to be easily hidden, had the high level api looked more like:

```py
def read_something(src:str, server:str, username:str, password:str, alternative_connection_cache=None) -> str:
    raise NotImplementedError("Finish writing the blog")
```

Someone else likely would have found this issue much earlier. Note also here that we are explicitly naming the keyword argument here "alternative_connection_cache" instead of just "connection_cache", which is something that I often see in python. This is since by default, if nothing is supplied (eg: it is left as `None`) the default cache in the module will be used as default. This slight name tweak makes it a lot more obvious what will be done under the hood.

## How can we do better?

Right, **kwargs is still a useful way to collect and create a sort of 'passthrough' to various lower level abstractions. How can we re-do this without adding optional keyword arguments to every single method that may need them?

Luckily people up in python have already thought of how to do this with [PEP 589](https://peps.python.org/pep-0589/), this allows us to write something like the following instead:

```py
from typing import TypedDict, Unpack

class ReadProps(TypedDict, total=False):
    username:str
    password:str
    server: str
    alternative_connection_cache:dict

def read_something()
```

## Lessons Learned

- Clean code isn't just how clean the code looks, it's how neatly your abstractions work for the users.
- Explicit better than implicit
- Side effects need to be explicit.

