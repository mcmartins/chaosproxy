# ChaosProxy

ChaosProxy is a proxy server that creates an unstable environment where connections 
are delayed or dropped making requests not reach a remote host and responses not arriving.

This tool runs locally on a specific port and forwards all requests to a specific remote server.

## Use Cases

This tool is useful for testing Web APIs, where one needs to test reconciliation on rainy day scenarios.

ChaosProxy will sit between both ends of a distributed system. E.g.: A system **A** sends requests to system **B**. 
So system **A** should be configured with the ChaosProxy server address (e.g. http://localhost:9090) 
and the ChaosServer should be configured with system **B** server address (e.g. http://localhost:9091).

Each request passing through the proxy will include information headers on the operations performed.
The main header is *chaosproxy-requestid* and will allow tracking the request across all systems.

Sample configuration for the mentioned example:

```none
{
  "local": {
    "port": 9090
  },
  "remote": {
    "host": "http://localhost:9091"
  },
  "connection": {
    "stableInterval": 60,
    "unstableInterval": 15,
    "ignoreIfEndpointContains": ["login"]
    "request": {
      "dropRandomly": true,
      "delay": {
        "logNormal": {
          "mean": 200,
          "sigma": 20
        }
      }
    },
    "response": {
      "dropRandomly": true,
      "delay": {
        "logNormal": {
          "mean": 200,
          "sigma": 20
        }
      }
    }
  }
}
```

So, a request sent to *http://localhost:9090/rest/service/resource* will be forward to *http://localhost:9091/rest/service/resource*:

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

## How to use

### System commands

Add the following command line helper functions:

```bash
[mcmartins@local ~]$ echo "function conf_chaosproxy() { (wget -nc -O ~/.conf_chaosproxy.json https://raw.githubusercontent.com/mcmartins/chaosproxy/master/sample-conf.json &> /dev/null || true) && vi ~/.conf_chaosproxy.json ;}" >> ~/.bashrc && source ~/.bashrc
[mcmartins@local ~]$ echo "function start_chaosproxy() { (wget -nc -O ~/.start_chaosproxy.sh https://raw.githubusercontent.com/mcmartins/chaosproxy/master/bin/chaosproxy.sh &> /dev/null && chmod +x ~/.start_chaosproxy.sh || true) && ~/.start_chaosproxy.sh ;}" >> ~/.bashrc && source ~/.bashrc
[mcmartins@local ~]$ echo "function stop_chaosproxy() { (wget -nc -O ~/.stop_chaosproxy.sh https://raw.githubusercontent.com/mcmartins/chaosproxy/master/bin/kill_chaosproxy.sh &> /dev/null && chmod +x ~/.stop_chaosproxy.sh || true) && ~/.stop_chaosproxy.sh ;}" >> ~/.bashrc && source ~/.bashrc
```

This will create the basic commands to interact with ProxyChaos on your local machine. 

To create and default configuration and change it:

```bash
[mcmartins@local ~]$ conf_chaosproxy
```

To start the server:

```bash
[mcmartins@local ~]$ start_chaosproxy
```

To stop the server:

```bash
[mcmartins@local ~]$ stop_chaosproxy
```

### Configure the server

The following is a configuration file with all options available:

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

A JSON configuration is needed for ChaosProxy to work. The configuration is split in 3 groups:

1 Local: refers to the local environment for the ChaosProxy and the only available option is:

- port: the local port where the server will be listening on

2 Remote: refers to the remote server for which ChaosProxy will forward all requests:

- host: the full address (including port if not a default for http 80 or https 443). Chaos proxy will use this address to forward the original request.

3 Connection: refers to the instability that will be created on connections.

- stableInterval:  an interval time where ChaosProxy **won't** interfere with the connections (in milliseconds)
- unstableInterval: an interval time where ChaosProxy **will** interfere with the connections (in milliseconds)
- ignoreIfEndpointContains: a list of strings for which ChaosProxy **will never** interfere, if they are present in the endpoint
- ignoreIfBodyContains: a list of strings for which ChaosProxy **will never** interfere, if they are present in the body

3.1 Request: refers to the instability to create on requests

- dropRandomly: setting this to true, will drop requests on a random number divisible by 3 in a range of 1 to 5000, and **no response from server will be returned**
- delay.random: delay requests based on a random number within the range a, b (inclusive) (in milliseconds)
- delay.logNormal: delay requests based on an approximation on the 50th percentile (in milliseconds)
- delay.fixed: delay requests based on this fixed value (in milliseconds)

3.2 Response: refers to the instability to create on response

- dropRandomly: setting this to true, will drop responses on a random number divisible by 3 in a range of 1 to 5000, and **a 500 http error code with all response headers will be returned**
- delay.random: delay requests based on a random number within the range a, b (inclusive) (in milliseconds)
- delay.logNormal: delay requests based on an approximation on the 50th percentile (in milliseconds)
- delay.fixed: delay requests based on this fixed value (in milliseconds)

# LICENSE

MIT License
