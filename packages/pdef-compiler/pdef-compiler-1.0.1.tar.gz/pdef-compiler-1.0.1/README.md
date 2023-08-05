Pdef - Header files for the web
===============================
Pdef (pi:def, stands for "protocol definition [language]") is a statically typed interface
definition language which supports JSON and a simple HTTP RPC. It allows to write
interfaces and data structures once and then to generate code and RPC clients/servers for
different languages. It is suitable for public APIs, internal service-oriented APIs,
configuration files, as a format for persistence, cache, message queues, logs, etc.

Links
-----
- **[Language guide](docs/language-guide.md)**
- [Style guide](docs/style-guide.md)
- [JSON format](docs/json-format.md)
- [HTTP RPC](docs/http-rpc.md)
- [Grammar in BNF](docs/grammar.bnf)
- [Generated and language specific code](docs/generated-lang-specific-code.md)
- [How to write a code generator](https://github.com/pdef/pdef-generator-template)

Contents
--------
- [Features](#features)
- [Languages](#languages)
- [Requirements](#requirements)
- [Installation](#installation)
- [Examples](#examples)
    - [Pdef example](#pdef-example)
    - [Curl example](#curl-example)
    - [Java example](#java-example)
    - [Python example](#python-example)
    - [Objective-C example](#objective-c-example)
- [License and copyright](#license-and-copyright)

Features
--------
- Clear separation between data structures and interfaces.
- Interfaces, not services, to allows Object-Oriented APIs.
- Simple type system.
- Message inheritance.
- Packages and modules with imports.
- Circular module imports (with some limitations).
- Circular references in message and interface definitions
  (with some limitations to support interpreted languages).
- Pluggable loosely-coupled formats and RPCs, with JSON and a simple HTTP RPC as the defaults.
- Pluggable code generators.

Languages
---------
- [Java](https://github.com/pdef/pdef-java)
- [Python](https://github.com/pdef/pdef-python)
- [Objective-C](https://github.com/pdef/pdef-objc)

Requirements
------------
- Python 2.7 or Python 3.3.

Installation
------------
Pdef consists of a compiler, pluggable code generators, and language-specific bindings.

Install the compiler as a python package:
```bash
pip install pdef-compiler
# or
easy_install pdef-compiler
```

Or [download](https://github.com/pdef/pdef/releases) the archive, unzip it and run:
```bash
python setup.py install
```

Install the code generators:
```bash
pip install pdef-java
pip install pdef-python
pip install pdef-objc
```

Check the test package (no source code is generated):
```bash
pdefc check https://raw.github.com/pdef/pdef/master/example/world.yaml
```

List the installed generators:
```bash
pdefc generate -h
```

Generate some code:
```bash
pdefc generate https://raw.github.com/pdef/pdef/master/example/world.yaml \
    --generator java
    --module world:com.company.world
    --out generated
```

Examples
--------

### Pdef example
Sources:

- [world.yaml](https://github.com/pdef/pdef/tree/master/example/example.yaml) (package)
- [world.pdef](https://github.com/pdef/pdef/tree/master/example/world.pdef)
- [continents.pdef](https://github.com/pdef/pdef/tree/master/example/continents.yaml)
- [space.pdef](https://github.com/pdef/pdef/tree/master/example/space.yaml)


Interfaces:
```pdef
from world import continents, space;    // Import two modules from a package.

/**
 * The world interface.
 * A god-like person can use it to rule the world.
 */
interface World {
    /** Returns the humans interface. */
    humans() Humans;                    // Returns another interface.

    /** Returns the continents interface. */
    continents() continents.Continents; // Returns an interface from another module.

    /** Switches the light. */
    switchDayNight() void;

    /** Returns the last world events, the events are polymorphic. */
    events(limit int32 @query, offset int64 @query) list<Event>;
}

interface Humans {
    /** Finds a human by id. */
    find(id int64) Human;

    /** Lists all people. */
    all(  // A method with query arguments.
        limit int32 @query,
        offset int32 @query) list<Human>;

    /** Creates a human. */
    @post  // A post method (a mutator).
    create(human Human @post) Human;
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
    location    space.Location;
}

/** Human is a primate of the family Hominidae, and the only extant species of the genus Homo. */
message Human : Thing {             // A message with a base message and a docstring.
    name        string;
    birthday    datetime;
    sex         Sex;
    continent   continents.Continent;
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

### Curl example
Pdef uses an [HTTP RPC](docs/http-rpc.md) with a [JSON format](docs/json-format.md)
which are easy to use without specially generated clients. These are examples,
there is no real server

Create a new human:
```
$ curl -F human="{\"id\": 1, \"name\":\"John\"}" http://example.com/world/humans/create
{
    "data": {
        "id": 1,
        "name": "John"
    }
}
```

Switch the light:
```
$ curl -X POST http://example.com/world/switchTheLight
{
    "data": null
}
```

List people:
```
$ curl "http://example.com/world/humans/all?limit=2&offset=10"
{
    "data": [
        {"id": 11, "name": "John"},
        {"id": 12, "name": "Jane"}
    ]
}
```


### Java example
Generate the code:
```bash
pdefc generate https://raw.github.com/pdef/pdef/master/example/world.yaml \
    --generator java
    --module pdef_test:io.pdef
    --out target/generated-sources
```

JSON:
```java
// Read a human from a JSON string or stream.
Human human = Human.fromJson(jsonString);
human.setContinent(ContinentName.NORTH_AMERICA);

// Serialize a human to a JSON string.
String json = human.toJson();
```

Client:
```java
// Create an HTTP RPC client.
RpcClient<World> client = new RpcClient<World>(World.DESCRIPTOR, "http://example.com/world/");
World world = client.proxy();

// Create a man.
Human man = world.humans().create(new Human()
        .setId(1)
        .setName("John")
        .setSex(Sex.MALE)
        .setContinent(ContinentName.ASIA));

// Switch day/night.
world.switchDayNight();
```

Server:
```java
World world = getMyWorldImplementation();
RpcHandler<World> handler = new RpcHandler<World>(World.DESCRIPTOR, world);
RpcServlet<World> servlet = new RpcServlet<World>(handler);

// Pass it to your servlet container,
// or wrap in another servlet as a delegate.
```

### Python example
Generate the code:
```bash
pdefc generate https://raw.github.com/pdef/pdef/master/example/world.yaml \
    --generator python
    --out generated
```

JSON:
```python
# Read a human from a JSON string.
human = Human.from_json(s)
human.continent = ContinentName.AFRICA

# Serialize a human to a JSON string.
json = human.to_json()
```

Client:
```python
# Create an HTTP RPC client.
client = pdef.rpc_client(World, url='http://example.com/world/')
world_client = client.proxy()

# Create a man.
man = world_client.humans().create(
    Human(1, name='John', sex=Sex.MALE, continent=ContinentName.ASIA))

# Switch day/night.
world_client.switchDayNight()
```

Server:
```python
world_service = get_my_world_implementation()
handler = pdef.rpc_handler(World, world_service)
wsgi_app = pdef.wsgi_app(handler)
# Pass it to a WSGI-server.
```

### Objective-C Example
Generate the code:
```bash
pdefc -v generate https://raw.github.com/pdef/pdef/master/example/world.yaml \
    --generator objc \
    --out GeneratedClasses
```

JSON:
```objectivec
// Create a new human.
Human *human = [[Human alloc]init];
human.id = 1;
human.name = @"John";
human.sex = Sex_MALE;
human.continent = ContinentName_EUROPE;

// Serialize a human to JSON data.
NSError *error = nil;
NSData *humanData = [human toJsonError:&error];

// Parse a human from JSON data (supports polymorphic messages).
Human *human2 = [Human messageWithJson:humanData error:&error];
```

Client:
```objectivec
// Create an HTTP RPC client;
PDRpcClient *client = [[PDRpcClient alloc] initWithDescriptor:WorldDescriptor()
                                                      baseUrl:@"http://example.com/world"];
WorldClient *world = [[WorldClient alloc] initWithHandler:client];

// Switch the light.
[world switchDayNightCallback:^(id result, NSError *error) {
    NSLog(@"Switched the light");
}];

// List the first ten people.
[[world humans] allLimit:10 offset:0 callback:^(id result, NSError *error) {
    if (error) {
        NSLog(@"%@", error.localizedDescription);
    } else {
        NSArray *humans = result;
        for (Human *h in humans) {
            NSLog(@"%@", h.name);
        }
    }
}];
```

Objective-C does not have a server implementation.

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
