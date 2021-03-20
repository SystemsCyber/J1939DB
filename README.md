# J1939DB
A server system to provide JSON formatted data to decode J1939 messages. This is a framework only and requires a licensed copy of the J1939 standard, which is not included.

## Needs Analysis
In many applications that use CAN data from SAE J1939 networks, it is nice to be able to interpret the data according to the standard. To do this, we can use a legitimate copy of the [SAE Digital Annex](https://www.sae.org/standards/content/j1939da_202001/) from the SAE website. However, this version for MS Excel is not useful in lightweight applications or for automatically looking up meaning from CAN messages. Therefore, we need to be able to utilize the Digital Annex in a more useful way.

The work done at the National Motor Freight Traffic Association (NMFTA) produced a framework called [pretty_j1939](https://github.com/nmfta-repo/pretty_j1939) that provides the tooling available to convert the SAE J1939 Digital Annex into a nested JSON format. Using the JSON version, a tool was produced that converted the Linux can-utils candump logs into a human readable form with meaning for the J1939 messages. This is a nice utility for static log files. 

The drawback of this approach is that it is heavy in that the entire database is needed for the tool. Furthermore, it's challenging to use the J1939 JSON file for other projects as it may need to be updated, reduced, or patched depending on the situation. For embedded applications, the full J1939 database may not be desired. 

Also, research programs and companies often maintain a suite of tools that depend on the J1939 database. Therefore, it's helpful to just maintain a single source for this and be able to apply it to any of the tools. 

The need for this project is to provide a web service that can produce J1939 decoding data in a JSON format for use in applications that interpret SAE J1939. 

## System Requirements

These requirements are specific to the Systems Cyber research group at Colorado State University. However, they may be easily adapted for your purpose. A proper set of requirements will address system function and performance only; however, we have to also include requirements for existing resources. As part of the requirements, we'll also try to include a method for testing or verifying the requirement.

1. The system should be compatible the JSON file produced by the pretty_j1939 utility from NMFTA. This will be the primary data source for the service.

Verification: Run the script at https://github.com/nmfta-repo/pretty_j1939/blob/master/create_j1939db-json.py to produce a JSON file. Use the new file as a source in this service and demonstrate the tests pass.

2. The service must be hosted on a machine protected behind a firewall as the data it produces is from a licensed source.

Verification: Demonstrate access to the tool when connected to the campus network. Demonstrate there is no access to the tool when off campus. 

3. The connection must be secured with TLS1.2 or greater. 

Verification: Attempt to connect to the service with TLS less than 1.2 and verify the operation fails. Monitor the network traffic with Wireshark to see the protocol exchange. Demonstrate a working version is using TLS1.2 or better using Wireshark.

4. All responses must be in a standard JSON format as specified by [ECMA-404](https://www.ecma-international.org/publications-and-standards/standards/ecma-404/) and implemented using the Python json library.

Verification: Use a JSON linter on outputs to verify the output. Also, be able to ingest the output with a JSON aware tool, like the json.load method in Python. 

5. The tool should accept a request in the form of an HTTP GET request with the query string having the following options, each corresponding to a part of the SAE J1939 standard. 
   1. `PGN`
   2. `SPN`
   3. `SA`
   4. `NAME`
   5. `FMI`
   6. `SLOT`

   For example, the request URL may look as follows: 
```https://cybertruck1.engr.colostate.edu/j1939.html?PGN=65235```

which produces a JSON response including the pertinent information for PGN 65265 (and only PGN 65265).

```
{
  "J1939PGNdb": {
    "65265": {
      "Label": "CCVS1",
      "Name": "Cruise Control/Vehicle Speed 1",
      "PGNLength": "8",
      "Rate": "100 ms",
      "SPNs": [
        69,
        70,
        1633,
        3807,
        84,
        595,
        596,
        597,
        598,
        599,
        600,
        601,
        602,
        86,
        976,
        527,
        968,
        967,
        966,
        1237
      ],
      "SPNStartBits": [
        [0],
        [2],
        [4],
        [6],
        [8,16],
        [24],
        [26],
        [28],
        [30],
        [32],
        [34],
        [36],
        [38],
        [40],
        [48],
        [53],
        [56],
        [58],
        [60],
        [62]
      ]
    }
  }
}
```

Similarly, the 

```https://cybertruck1.engr.colostate.edu/j1939.html?SA=11```


which should produce a result of
```
{ "J1939SATabledb": {
    "11": "Brakes - System Controller"
  }
}
```

6. The tool should process a POST request that includes the J1939 frame with the CAN ID represented as a base 10 integer and the data portion of the message represented as base64 encoded bytes. The result should be a JSON of the interpreted CAN message like the pretty_j1939 tool. 

7. The tool must be extensible to add proprietary definitions in a similar format to pretty_j1939.

8. The code for the service will be release into the open under and MIT license. It should be maintained on Github.

9. The server and service should be optimized to run on the server hardware.

10. Each function in the source code should have a unit test associated with it.

11. Continuous integration and continuous deployment mechanisms should be built. 

12. An API must be made available for the use of the service.

13. The service must be only for available authenticated users. 

## Preliminary Design
The service will run as a Python3 Tornado application. The service should run on port 8080 and will be reverse proxied through nginx running on cybertruck1.engr.colostate.edu. The nginx instance is set to serve the tornado application. The following is a basic server that is proxied. 

```
import tornado.httpserver
import tornado.ioloop
import tornado.web

class MainApp(tornado.web.RequestHandler):
    def get(self):
        self.write('{"message":"hello. This is the main app."}')

application = tornado.web.Application([
    (r'/', MainApp),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
```

The application will need to be built, which is the purpose of this project.

## Detailed Design

Create a functional flow diagram for the project and propose solutions for the different functions

## Unit Testing

When using Tornado, the unit testing service of pytest can make short work of unit testing. 

Be sure to include known good cases as well as known bad cases. The faker library can produce a randomized test each time it is run. 

## Integration Tests

Test the Tornado application as it is proxied by nginx. Develop a unified test script that tests different cases and builds a local database from the GET requests. 

## System Testing
Verify each requirement is met with an automated test of some sort. Be sure to document the results, or produce result documentation automatically. 
