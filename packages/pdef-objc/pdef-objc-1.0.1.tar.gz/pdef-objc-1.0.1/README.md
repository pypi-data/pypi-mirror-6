Pdef Objective-C
================
Objective-C code generator for [Pdef compiler](https://github.com/pdef/pdef)
and Objective-C implementation of descriptors, JSON format and HTTP RPC.

Requirements
------------
- Objective-C: iOS 6.0, Mac OSX 10.8, AFNetworking 2.0.
- Code generator: [Pdef compiler 1.0+](https://github.com/pdef/pdef),
  Python 2.6 or Python 3.3+.

Installation
------------
- Code generator:
    Install the code generator as a python package:
    ```bash
    $ [sudo] pip install pdef-objc
    # or
    $ [sudo] easy_install pdef-objc
    ```

    Or [download](https://github.com/pdef/pdef-objc/releases) the release,
    unzip it and in the `generator` directory run:
    ```bash
    $ [sudo] python setup.py install
    ```

    The Objective-C generator will appear in the installed generators:
    ```bash
    $ pdefc generate -h
    usage: pdefc generate [...]
    available generators:
      - objc: Objective-C generator, ignores module names, supports prefixes.
    ```

- Objective-C package via CocoaPods:
    ```ruby
    pod "Pdef", "~> 1.0"
    ```

Code generation
---------------
Pass a pdef package path or a url to the compiler:
```bash
$ pdefc generate https://github.com/pdef/pdef/blob/master/example/world.yaml \
    --generator objc
    --out Generated
```

The generator supports prefixes specified by for modules and submodules:
```bash
$ pdefc generate https://github.com/pdef/pdef/blob/master/example/world.yaml \
    --generator objc
    --prefix world.space:SP
    --prefix world:WL
    --out target/generated-sources
```

Messages
--------
Generated messages implement the `isEqual`, `hash` methods, the `NSCopying` and `NSCoding`
protocols and support merging. The `copyWithZone` method returns a message deep copy.
The messages are not thread-safe. The examples are based on
the [pdef example package](https://github.com/pdef/pdef/tree/master/example).

```objectivec
Human *human = [[Human alloc]init];
human.id = 1;
human.name = @"John";
human.sex = Sex_MALE;
human.continent = ContinentName_EUROPE;

Human *copy = [human copy];
assert([human isEqual:copy]);
```

Messages support merging which deep copies fields from a source message to a destination one:
```
Human *human = [[Human alloc]init];
    human.id = 1;
    human.name = @"John";
    human.sex = Sex_MALE;
    human.continent = ContinentName_EUROPE;

Human *another [[Human alloc]init];
[another merge:human];

assert([another isEqual:human]);
```

Messages use unboxed types for primitives and bool flags to indicate when a field is set or empty.
```objectivec
// Primitive fields return default values, has{FieldName} returns NO.
Human *human = [[Human alloc]init];
assert(human.id == 0);
assert([human hasId] == NO);

// When a field is set has{FieldName} returns YES.
human.id = 123;
assert([human hasId] == YES);

// Execute a special clear method to clear a field.
[human clearId];
```

JSON Format
-----------
JSON serialization is based on `NSJSONSerialization` with the additional support
to serialize/deserialize primitives as root JSON objects (not only objects and arrays).
```objectivec
// To a JSON-compatible dictionary.
NSDictionary *dict = [human toDictionary];

// To JSON data.
NSError *error = nil;
NSData *data = [human toJsonError:&error];
```

Parsing:
```objectivec
// From a JSON-compatible dictionary, supports polymorphic messages.
NSDictionary *dict = getJsonDictionary();
Human *human = [Human messageWithDictionary:dict];

// From JSON data, supports polymorphic messages.
Human *human1 = [Human messageWithData:data error:&error];
```

User `PDJsonFormat` to read/write other pdef data types:
```objectivec
// Serialize a list of ints.
PDDataTypeDescriptor *listd = [PDDescriptors listWithElement:[PDDescriptors int32]];
NSArray *array = @[@1, @2, @3];
NSError *error = nil;
NSString *json = [PDJsonFormat writeString:array descriptor:listd error:&error];

// Parse a list of ints.
NSArray *parsed = [PDJsonFormat readString:array descriptor:listd error:&error];
```

HTTP RPC Client
---------------
RPC client is based on [AFNetworking](https://github.com/AFNetworking/AFNetworking),
the implementation is thread-safe.

```
// Create an RPC client as an invocation handler.
PDRpcClient *handler = [[PDRpcClient alloc]
    initWithDescriptor:WorldDescriptor()
               baseUrl:@"http://example.com/world"];

// Create a generated protocol client and pass the handler to it.
World *world = [[WorldClient alloc] initWithHandler:client];

// Execute a void remote method.
[world switchDayNightCallback:^(id result, NSError *error) {
    NSLog(@"Switched the light");
}];

// Execute a remote method with result.
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

Initialize the `PDRpcClient` with a custom `NSURLSession` or `AFURLSessionManager`
when you need custom headers, or subclass it.

Remote application errors are passed as `NSErrors` with the `PDefErrorDomain` domain
and the `PDRpcException` code, the exception message is put in the user dict
under the `PDRpcExceptionKey` key.
```
// Get a remote exception.
[[world humans] allLimit:10 offset:0 callback:^(id result, NSError *error) {
    if ([error.domain isEqualToString:PDefErrorDomain] && error.code == PDRpcException) {
        PDMessage *exception = [error.userInfo objectForKey:PDRpcExceptionKey];
    }
}];

// Or a simplified version.
[[world humans] allLimit:10 offset:0 callback:^(id result, NSError *error) {
    if (PDIsRpcError(error)) {
        PDMessage *exception = PDGetRpcException(error);
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
