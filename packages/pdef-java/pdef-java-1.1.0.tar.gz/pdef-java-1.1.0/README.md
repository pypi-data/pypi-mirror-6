Pdef Java
=========
Java code generator for [Pdef compiler](https://github.com/pdef/pdef)
and Java implementation of descriptors, JSON format and HTTP RPC.

Requirements
------------
- Java 6+.
- Code generator: [Pdef compiler 1.1+](https://github.com/pdef/pdef), Python 2.6 or Python 3.3+.

Installation
------------
- Code generator:
    ```bash
    $ pip install pdef-java
    ```

    Or [download](https://github.com/pdef/pdef-java/releases) the release,
    unzip it and in the `generator` directory run:
    ```bash
    $ python setup.py install
    ```

- Java package (maven):
    ```xml
    <dependency>
        <groupId>io.pdef</groupId>
        <artifactId>pdef</artifactId>
        <version>1.0.0</version>
    </dependency>

    <dependency>
        <groupId>io.pdef</groupId>
        <artifactId>pdef-servlet</artifactId>
        <version>1.0.0</version>
    </dependency>
    ```

Code generation
---------------
Pass a pdef package path or a url to the compiler:
```bash
$ pdefc generate-java https://raw.github.com/pdef/pdef/1.1/example/world.yaml \
    --out target/generated-sources
```

The generator uses absolute module names (`package.module`) as java package names.
Use the `--module` argument to manually map pdef modules to java packages.
Also it is possible to add namespace class prefixes via the `--prefix` argument.
```bash
$ pdefc generate-java https://raw.github.com/pdef/pdef/1.1/example/world.yaml \
    --prefix world:W \
    --module world:com.mycompany.world \
    --module world.space:com.mycompany.common \
    --out target/generated-sources
```

Messages
--------
Generated messages implement `equals`, `hashCode`, copy constructors, a `copy` method
which returns a deep copy of a message, and merging methods. The messages are not thread-safe.
The examples are based on the [pdef example package](https://github.com/pdef/pdef/tree/1.1/example).

Messages have a fluent interface.
```java
Human human = new Human()
    .setId(1)
    .setName("John")
    .setSex(Sex.MALE)
    .setContinent(ContinentName.ASIA)

Human copy0 = human.copy();
Human copy1 = new Human(human);

assert human.equals(copy0);
assert human.equals(copy1);
```

Messages support merging which deep copies set fields from a source message to destination one:
```
Human human = new Human()
    .setId(1)
    .setName("John")
    .setSex(Sex.MALE)
    .setContinent(ContinentName.ASIA)

Human another = new Human();
another.merge(human);

assert another.getName().equals(human.getName());
```

Messages try to be null-safe and return default values for null fields.
If a null field is a collection or a message then it is initialized to an empty
object on the first access.
```java
// All getters return the default values when the fields are not present or null.
Human human = new Human();
assert human.getId() == 0;
assert human.getName().equals("");

// Special methods allow to check if the field is present.
assert human.hasId() == false;
assert human.hasName() == false;

// Collection and message getters initialize null fields to empty objects.
Continent continent = new Continent();
assert continent.hasHumans() == false;

// The collection is initialized to an empty one.
continent.getHumans().add(human);
assert continent.getHumans().equals(Arrays.asList(human));
assert continent.hasHumans();

// Clear fields.
continent.clearName().clearHumans();
```

JSON Format
-----------
JSON serialization is based on the [Jackson parser](https://github.com/FasterXML/jackson-core)
(not the data binding package):
```java
// To a JSON-compatible map.
Map<String, Object> map = human.toMap();

// To JSON string.
String json = human.toJson();

// To pretty-printed JSON string.
json = human.toJson(true);

// Write to an output stream.
OutputStream stream = getOutput();
human.toJson(stream, true);  // indent=true/false.

// Write to a print writer.
PrintWriter writer = getWriter();
human.toJson(writer, true);
```

Parsing:
```java
// From a JSON compatible map (only JSON primitives and collections).
Map<String, Object> map = new HashMap<>;
map.put("name", "John");
map.put("birthday", "2012-01-01T01:12:33Z");
map.put("sex", "male");

Human human0 = Human.fromMap(map);
assert human0.getName().equals("John");

// From a JSON-string:
String json = getJson();
Human human1 = Human.fromJson(json);

// Merging for parsing input streams and readers.
```

Use `JsonFormat` to read/write other pdef data types:
```java
// Convert an int to a JSON string.
String json = JsonFormat.write(Descriptors.int32, 123);

// Write a list of integers to an output stream.
OutputStream output = getOutput();
ListDescriptor<Integer> listDescriptor = Descriptors.list(Descriptors.int32);
JsonFormat.write(output, listDescriptor, Arrays.asList(1, 2, 3));

// Read a message from an input stream.
InputStream input = getInput();
Human human = JsonFormat.read(Human.DESCRIPTOR, input);
```

HTTP RPC Client
---------------
Client and server implementations are thread-safe.

Create an HTTP RPC client based on the `HttpUrlConnection`.
```java
RpcClient<World> client = new RpcClient<World>(World.DESCRIPTOR, "http://example.com/world/");
World world = client.proxy();

// Execute a remote method.
List<Human> humans = world.humans().all(10, 0); // limit=10, offset=0.

// Execute a void remote method.
world.switchDayNight();
```

Null primitive results are automatically converted into default values.
```java
// It is null-safe to write:
int result = calculator.sum(1, 2);
```

Create an RPC client with a custom `RpcSession`:
```
RpcSession session = createCustomSession();
RpcClient<World> client = new RpcClient<World>(World.DESCRIPTOR, session);
World world = client.proxy();
```

Full client example:
```
RpcSession session = new HttpUrlConnectionRpcSession("http://example.com/world/");
RpcClient<World> client = new RpcClient<World>(World.DESCRIPTOR, session);
Invoker invoker = client;
World world = InvocationProxy.create(World.DESCRIPTOR, invoker);
```
To add custom headers or other HTTP logic subclass `HttpUrlConnectionRpcSession`,
or implement a custom `RpcSession`.


HTTP RPC Server
---------------
Create an HTTP RPC handler:
```java
World world = getWorldImplementation();
RpcHandler<World> handler = new RpcHandler<World>(World.DESCRIPTOR, world);
RpcServlet<World> servlet = new RpcServlet<World>(handler);
// Pass the servlet to your servlet container,
// or wrap in another servlet as a delegate.
```

Use a custom provider when you need to get a fresh service instance for each request:
```java
Provider<World> provider = getWorldProvider();
RpcHandler<World> handler = new RpcHandler<World>(World.DESCRIPTOR, provider);
```

Primitive null arguments are automatically converted into the default values.
```
class MyHumans implements Humans {
    public List<world.Human> all(int limit, int offset) {
        // Null limit and offset are set to 0.
        return null;
    }
}
```

Wrap an `RpcServlet` in another servlet as a delegate to add custom headers and custom HTTP
logic (authentication, rate-limiting, etc).

`RpcHandler` takes a simple bean-like `RpcRequest` and returns an `RpcResult` which
allows to use it with custom HTTP transports such as Netty.


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
