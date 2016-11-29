# ChaosProxy

ChaosProxy is a proxy server that creates an unstable environment where connections 
are delayed or dropped making requests not reach a remote host and responses not arriving.

This tool runs locally on a specific port and redirects all requests to a specific remote server.

## Use Cases

This tool is useful for testing Web APIs, where one needs to test reconciliation on rainy day scenarios.

ChaosProxy will sit between both ends of a distributed system. The requester system should be configured with the
ChaosProxy server address (e.g. localhost:9090) and the ChaosServer should be configured with the
requested server address (e.g. localhost:9091).

Each request passing through the proxy will include headers with information on the operations performed.
The main header is *chaosproxy-requestid* and will allow tracking the request in all systems.

So, e.g., a request to *http://localhost:9090/rest/service/resource* will be forward to *http://localhost:9091/rest/service/resource*:

```none
2016-10-28 10:59:37,174 - [INFO] - 53fe99e8d9522L - [POST] Request received
2016-10-28 10:59:37,176 - [INFO] - 53fe99e8d9522L - Forwarding request to [http://localhost:9091/rest/service/resource]
2016-10-28 10:59:37,184 - [DEBUG] - 53fe99e8d9522L - Request headers:
{
  "origin": "chrome-extension://fhbjgbiflinjbdggehcddcbncdddomop", 
  "content-length": "419", 
  "accept-language": "pt-PT,pt;q=0.8,it-IT;q=0.6,it;q=0.4,en-US;q=0.2,en;q=0.2", 
  "chaosproxy-requestid": "53fe99e8d9522L", 
  "chaosproxy-host": "PC-25.local", 
  "connection": "keep-alive", 
  "accept": "*/*", 
  "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36", 
  "cache-control": "no-cache", 
  "content-type": "application/json; charset=UTF-8"
}
2016-10-28 10:59:37,180 - [DEBUG] - 53fe99e8d9522L - Request body:
{
  "id": "123", 
  "name": "Name"
}
2016-10-28 11:03:02,038 - [INFO] - 53fe99e8d9522L - Response Delayed for [0.5 s]
2016-10-28 11:03:02,190 - [DEBUG] - 53fe99e8d9522L - Response headers:
{
  "chaosproxy-drop-request": "False", 
  "chaosproxy-drop-response": "False", 
  "x-powered-by": "PHP/7.0.10", 
  "transfer-encoding": "chunked", 
  "chaosproxy-requestid": "53fe99e8d9522L", 
  "chaosproxy-host": "PC-25.local", 
  "chaosproxy-delay-request": "False", 
  "server": "ChaosServer/0.0.1 Python/2.7.11", 
  "connection": "close", 
  "date": "Fri, 28 Oct 2016 10:03:02 GMT", 
  "content-type": "text/html; charset=UTF-8", 
  "chaosproxy-delay-response": "0.5 s"
}
2016-10-28 11:03:02,196 - [INFO] - 53fe99e8d9522L - [POST] Request processed
```

## Usage

### Installation

```bash
[mcmartins@local ~]$ git clone http://github.com/mcmartins/chaosproxy
[mcmartins@local ~]$ cd chaosproxy
[mcmartins@local ~]$ python setup.py clean build install
```

### Configure the server

The following is a sample configuration file:

```json
{
  "local": {
    "port": 8080
  },
  "remote": {
    "host": "http://some-remote-service.com:8080"
  },
  "connection": {
    "stableInterval": 60,
    "unstableInterval": 15,
    "ignoreIfEndpointContains": ["endpoint"],
    "ignoreIfBodyContains": ["initsession"],
    "request": {
      "dropRandomly": true,
      "delay": {
        "random": {
          "min": 100,
          "max": 500
        },
        "logNormal": {
          "mean": 200,
          "sigma": 20
        },
        "fixed": 1000
      }
    },
    "response": {
      "dropRandomly": true,
      "delay": {
        "random": {
          "min": 100,
          "max": 500
        },
        "logNormal": {
          "mean": 200,
          "sigma": 20
        },
        "fixed": 1000
      }
    }
  }
}
```

A simple json configuration is needed for ChaosProxy to work. The configuration is split in 3:

1 Local: refers to the local environment for the ChaosProxy and the only available option is:

- port: the port where the server will be listening on

2 Remote: refers to the remote server for which ChaosProxy will forward all requests:

- host: the full address (including port if not the default for http 80 or https 443). Chaos proxy will use this address to forward the original request.

3 Connection: refers to the instability that will be created on connections.

- stableInterval:  refers to the interval time where connections **won't** be affected (in seconds)
- unstableInterval: refers to the interval time where connections **will** be affected (in seconds)
- ignoreIfEndpointContains: a list of strings for which connections instability **will never** apply if they are present in the endpoint
- ignoreIfBodyContains: a list of strings for which connections instability **will never** apply if they are present in the body

3.1 Request: refers to the instability to create on requests

- dropRandomly: setting this to true, will drop requests on a random number divisible by 3 in a range of 1 to 5000, and **you'll get no response from server**
- delay.random: delays requests based on a random number within the range a, b (inclusive)
- delay.logNormal: delays requests based on an approximation on the 50th percentile
- delay.fixed: delays requests based on this fixed value (in milliseconds)

3.2 Response: refers to the instability to create on response

- dropRandomly: setting this to true, will drop responses on a random number divisible by 3 in a range of 1 to 5000, and **you'll get a 500 http error code with all response headers**
- delay.random: delays requests based on a random number within the range a, b (inclusive)
- delay.logNormal: delays requests based on an approximation on the 50th percentile
- delay.fixed: delays requests based on this fixed value (in milliseconds)

### Running the server

The bin folder contains a script to start the server and one to stop it. 

The script *chaosproxy.sh* downloads the latest version and starts the server.

```bash
# will download, install and run always the latest code available
[mcmartins@local ~]$ ./chaosproxy.sh path/to/input.json
# or if you don't want to download the latest version include false in the end
[mcmartins@local ~]$ ./chaosproxy.sh path/to/input.json false
# to kill the server
[mcmartins@local ~]$ ./kill_chaosproxy.sh
```

Or, if you prefer to do it manually:

```bash
# importing a file as configuration
[mcmartins@local ~]$ python -m chaosproxy -v -i path/to/input.json -p /var/logs
# or importing a string as configuration
[mcmartins@local ~]$ python -m chaosproxy -v -i '{"json": 0}' -p /var/logs
```

# LICENSE

MIT License
