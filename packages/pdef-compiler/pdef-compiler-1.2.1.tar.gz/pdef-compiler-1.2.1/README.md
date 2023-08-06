Pdef - Interface definition language for the web
================================================
Pdef (pi:def, stands for "protocol definition [language]") is a statically typed interface
definition language which supports JSON and a simple HTTP RPC. It allows to write
interfaces and data structures once and then to generate code and RPC clients/servers for
different languages. It is suitable for public APIs, internal service-oriented APIs,
configuration files, as a format for persistence, cache, message queues, logs, etc.
Features:

- Packages, modules, imports and namespaces.
- Circular module imports and type references (with some limitations).
- Simple type system built on a clear separation between data structures and interfaces.
- Message and interface inheritance.
- Chained method invocations.
- Default JSON format and HTTP RPC.
- Pluggable loosely-coupled formats and RPCs.
- Pluggable code generators.


Languages
---------
- [Java](https://github.com/pdef/pdef-java)
- [Python](https://github.com/pdef/pdef-python)
- [Objective-C](https://github.com/pdef/pdef-objc)


Links
-----
- **[Language guide](docs/language-guide.md)**
- [Style guide](docs/style-guide.md)
- [JSON format](docs/json-format.md)
- [HTTP RPC](docs/http-rpc.md)
- [Grammar in BNF](docs/grammar.bnf)
- [Generated and language specific code](docs/generated-lang-specific-code.md)
- [How to write a code generator](https://github.com/pdef/pdef-generator-template)
- [Google group](https://groups.google.com/d/forum/pdef) (pdef@googlegroups.com)


Requirements
------------
- The compiler requires Python 2.7 or Python 3.3.
- Bindings requirements are language specific.


Installation
------------
Pdef consists of a compiler, pluggable code generators, and language-specific bindings.

Install the compiler as a python package:
```bash
$ pip install pdef-compiler
```

Or [download](https://github.com/pdef/pdef/releases) the archive, unzip it and run:
```bash
$ python setup.py install
```

Install the code generators:
```bash
$ pip install pdef-java
$ pip install pdef-python
$ pip install pdef-objc
```

Run the check command with test package to check that the compiler works:
```bash
$ pdefc check https://raw.github.com/pdef/pdef/master/example/world.yaml
```


Getting Started
---------------
Create a package file `myproject.yaml`
```yaml
package:
    name: myproject
    modules:
        - posts
        - photos
```

Create the module files:

`posts.pdef`
```pdef
namespace myproject;
import myproject.photos;

interface Posts {
    get(id int64) Post;

    @post
    create(title string, text string) Post;
}

message Post {
    id      int64;
    title   string;
    text    string;
    photos  list<Photo>;
}
```

`photos.pdef`
```pdef
namespace myproject;

message Photo {
    id  int64;
    url string;
}
```

Generate the source code:
```bash
$ pdefc generate-java myproject.yaml --out generated/
$ pdefc generate-objc myproject.yaml --out generated/
$ pdefc generate-python myproject.yaml --out generated/
```

Example
-------
Example package [sources](https://github.com/pdef/pdef/tree/master/example/).

Interfaces:
```pdef
namespace world;
from world import continents, space;    // Import two modules from a package.

/**
 * The world interface.
 * A god-like person can use it to rule the world.
 */
interface World {
    /** Returns the humans interface. */
    humans() Humans;                    // Returns another interface.

    /** Returns the continents interface. */
    continents() Continents; // Returns an interface from another module.

    /** Switches the light. */
    switchDayNight() void;

    /** Returns the last world events, the events are polymorphic. */
    events(limit int32, offset int64) list<Event>;
}

interface Humans {
    /** Finds a human by id. */
    find(id int64) Human;

    /** Lists all people. */
    all(limit int32, offset int32) list<Human>;

    /** Creates a human. */
    @post  // A post method (a mutator).
    create(human Human) Human;
}
```

Enums:
```pdef
enum Sex {
    MALE, FEMALE, UNCLEAR;
}

// An discriminator.
enum EventType {
    HUMAN_EVENT,
    HUMAN_CREATED,
    HUMAN_DIED;
}
```

Messages:
```pdef
message Thing {                     // A simple message definition.
    id          int64;              // an id field of the int64 type.
    location    Location;
}

/** Human is a primate of the family Hominidae, and the only extant species of the genus Homo. */
message Human : Thing {             // A message with a base message and a docstring.
    name        string;
    birthday    datetime;
    sex         Sex;
    continent   Continent;
}
```

Polymorphic inheritance:
```pdef
// A polymorphic message with EventType as its discriminator.
message Event {
    type    EventType @discriminator;
    id      int32;
    time    datetime;
}

// A polymorphic subtype.
message HumanEvent : Event(EventType.HUMAN_EVENT) {
    human   Human;
}

// Multi-level polymorphic messages.
message HumanCreated : HumanEvent(EventType.HUMAN_CREATED) {}
message HumanDied : HumanEvent(EventType.HUMAN_DIED) {}
```

### Curl
Pdef uses an [HTTP RPC](docs/http-rpc.md) with a [JSON format](docs/json-format.md)
which are easy to use without specially generated clients. These are examples,
there is no real server.

Create a new human:
```bash
$ curl -d human="{\"id\": 1, \"name\":\"John\"}" http://example.com/world/humans/create
{
    "data": {
        "id": 1,
        "name": "John"
    }
}
```

Switch the light:
```bash
$ curl -X POST http://example.com/world/switchTheLight
{
    "data": null
}
```

List people:
```bash
$ curl "http://example.com/world/humans/all?limit=2&offset=10"
{
    "data": [
        {"id": 11, "name": "John"},
        {"id": 12, "name": "Jane"}
    ]
}
```


License and Copyright
---------------------
Copyright: 2013 Ivan Korobkov <ivan.korobkov@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
