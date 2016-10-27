# ChaosProxy

ChaosProxy is a proxy server that creates an unreliable environment where connections 
are delayed or dropped making requests not reach the remove host and responses not arriving.

This server runs locally on a specific port and redirects all requests to a specific remote server.

## Use Cases

This tool is useful for testing Web APIs, where one needs to test reconciliation and rainy day scenarios.

### Testing SOAP / REST services

...

## Usage

### Installation

```bash
[mmartins@local ~]$ git clone http://github.com/mcmartins/chaosproxy && cd chaosproxy
[mmartins@local ~]$ python setup.py clean build install
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

### Running the server

```bash
[mmartins@local ~]$ python -m chaosproxy -v -i path/to/input.json -p /var/logs
# or
[mmartins@local ~]$ python -m chaosproxy -v -i '{"json": 0}' -p /var/logs
```

# LICENSE

MIT License