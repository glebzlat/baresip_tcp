# Demo of the usage of BareSIP TCP interface

The goal of this project is to explore the actual responses and events BareSIP
sends over TCP. It exhibits the usage of `ctrl_tcp` module, and uses PyQt6 for
socket communication and GUI rendering.

## Configuration

This example requires BareSIP to be properly configured in order to work.
Enable the TCP control module in `~/.baresip/config`:

```
module_app		ctrl_tcp.so
```

## Usage

To use this program, first start a BareSIP instance, then (assuming you have
all dependencies already installed) run the module:

```sh
python -m baresip_tcp
```

The program allows to connect to running BareSIP instance, add and delete User 
Agents, make, receive, terminate, mute, resume, and switch calls. It logs
current operations in the history window and is able to make history snapshots.

For example, the following excerpt shows connection to an instance,
agent creation, incoming call, hangup, and user agent deletion:

```
{
  "kind": "status",
  "time": "2026-03-27T12:50:52",
  "payload": {
    "connected": true,
    "host": "127.0.0.1",
    "port": "4444"
  }
}

{
  "kind": "user",
  "time": "2026-03-27T12:51:02",
  "payload": {
    "command": "uanew",
    "params": "<sip:490@10.10.2.4>;auth_pass=\"490490\"",
    "token": "b5dcc1de-0771-44fe-aee6-42e291fc3e70"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:02",
  "payload": {
    "event": true,
    "class": "ua",
    "type": "CREATE",
    "accountaor": "sip:490@10.10.2.4",
    "param": "sip:490@10.10.2.4"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:02",
  "payload": {
    "event": true,
    "class": "ua",
    "type": "REGISTERING",
    "accountaor": "sip:490@10.10.2.4"
  }
}

{
  "kind": "response",
  "time": "2026-03-27T12:51:02",
  "payload": {
    "response": true,
    "ok": true,
    "data": "Creating UA for <sip:490@10.10.2.4>;auth_pass=\"490490\" ...\n\n--- User Agents (1) ---\n0 - sip:490@10.10.2.4                             \u001b[33mzzz\u001b[;m \n\n",
    "token": "b5dcc1de-0771-44fe-aee6-42e291fc3e70"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:02",
  "payload": {
    "event": true,
    "class": "ua",
    "type": "REGISTER_OK",
    "accountaor": "sip:490@10.10.2.4",
    "param": "200 OK"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:07",
  "payload": {
    "event": true,
    "class": "call",
    "type": "CALL_REMOTE_SDP",
    "accountaor": "sip:490@10.10.2.4",
    "direction": "incoming",
    "peeruri": "sip:477@lim1.mxone;user=phone",
    "contacturi": "sip:477@10.10.2.4:5060;transport=UDP",
    "localuri": "sip:490@lim1.mxone;user=phone",
    "remoteaudiodir": "sendrecv",
    "remotevideodir": "inactive",
    "audiodir": "sendrecv",
    "videodir": "inactive",
    "localaudiodir": "sendrecv",
    "localvideodir": "inactive",
    "param": "offer"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:07",
  "payload": {
    "event": true,
    "class": "call",
    "type": "CALL_INCOMING",
    "accountaor": "sip:490@10.10.2.4",
    "direction": "incoming",
    "peeruri": "sip:477@lim1.mxone;user=phone",
    "contacturi": "sip:477@10.10.2.4:5060;transport=UDP",
    "localuri": "sip:490@lim1.mxone;user=phone",
    "id": "zIM9oy44nyEjywAhwGulGg..",
    "remoteaudiodir": "sendrecv",
    "remotevideodir": "inactive",
    "audiodir": "sendrecv",
    "videodir": "inactive",
    "localaudiodir": "sendrecv",
    "localvideodir": "inactive",
    "param": "sip:477@lim1.mxone;user=phone"
  }
}

{
  "kind": "user",
  "time": "2026-03-27T12:51:13",
  "payload": {
    "command": "accept",
    "token": "6669a8ae-155b-4533-8873-62ee2c108072"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:13",
  "payload": {
    "event": true,
    "class": "call",
    "type": "CALL_LOCAL_SDP",
    "accountaor": "sip:490@10.10.2.4",
    "direction": "incoming",
    "peeruri": "sip:477@lim1.mxone;user=phone",
    "contacturi": "sip:477@10.10.2.4:5060;transport=UDP",
    "localuri": "sip:490@lim1.mxone;user=phone",
    "id": "zIM9oy44nyEjywAhwGulGg..",
    "remoteaudiodir": "sendrecv",
    "remotevideodir": "inactive",
    "audiodir": "sendrecv",
    "videodir": "inactive",
    "localaudiodir": "sendrecv",
    "localvideodir": "inactive",
    "param": "answer"
  }
}

{
  "kind": "response",
  "time": "2026-03-27T12:51:13",
  "payload": {
    "response": true,
    "ok": true,
    "data": "",
    "token": "6669a8ae-155b-4533-8873-62ee2c108072"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:13",
  "payload": {
    "event": true,
    "class": "call",
    "type": "CALL_ESTABLISHED",
    "accountaor": "sip:490@10.10.2.4",
    "direction": "incoming",
    "peeruri": "sip:477@lim1.mxone;user=phone",
    "contacturi": "sip:477@10.10.2.4:5060;transport=UDP",
    "localuri": "sip:490@lim1.mxone;user=phone",
    "id": "zIM9oy44nyEjywAhwGulGg..",
    "remoteaudiodir": "sendrecv",
    "remotevideodir": "inactive",
    "audiodir": "sendrecv",
    "videodir": "inactive",
    "localaudiodir": "sendrecv",
    "localvideodir": "inactive",
    "param": "sip:477@lim1.mxone;user=phone"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:13",
  "payload": {
    "event": true,
    "class": "call",
    "type": "CALL_RTPESTAB",
    "accountaor": "sip:490@10.10.2.4",
    "direction": "incoming",
    "peeruri": "sip:477@lim1.mxone;user=phone",
    "contacturi": "sip:477@10.10.2.4:5060;transport=UDP",
    "localuri": "sip:490@lim1.mxone;user=phone",
    "id": "zIM9oy44nyEjywAhwGulGg..",
    "remoteaudiodir": "sendrecv",
    "remotevideodir": "inactive",
    "audiodir": "sendrecv",
    "videodir": "inactive",
    "localaudiodir": "sendrecv",
    "localvideodir": "inactive",
    "param": "audio"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:15",
  "payload": {
    "event": true,
    "class": "call",
    "type": "CALL_RTCP",
    "accountaor": "sip:490@10.10.2.4",
    "direction": "incoming",
    "peeruri": "sip:477@lim1.mxone;user=phone",
    "contacturi": "sip:477@10.10.2.4:5060;transport=UDP",
    "localuri": "sip:490@lim1.mxone;user=phone",
    "id": "zIM9oy44nyEjywAhwGulGg..",
    "remoteaudiodir": "sendrecv",
    "remotevideodir": "inactive",
    "audiodir": "sendrecv",
    "videodir": "inactive",
    "localaudiodir": "sendrecv",
    "localvideodir": "inactive",
    "param": "audio",
    "rtcp_stats": {
      "tx": {
        "sent": 77,
        "lost": 0,
        "jit": 3125
      },
      "rx": {
        "sent": 68,
        "lost": 0,
        "jit": 8250
      },
      "rtt": 0
    }
  }
}

{
  "kind": "user",
  "time": "2026-03-27T12:51:30",
  "payload": {
    "command": "hangup",
    "token": "6d14fa58-396a-430e-9898-b503b1a12936"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:30",
  "payload": {
    "event": true,
    "class": "call",
    "type": "CALL_CLOSED",
    "accountaor": "sip:490@10.10.2.4",
    "direction": "incoming",
    "peeruri": "sip:477@lim1.mxone;user=phone",
    "contacturi": "sip:477@10.10.2.4:5060;transport=UDP",
    "localuri": "sip:490@lim1.mxone;user=phone",
    "id": "zIM9oy44nyEjywAhwGulGg..",
    "remoteaudiodir": "sendrecv",
    "remotevideodir": "inactive",
    "audiodir": "sendrecv",
    "videodir": "inactive",
    "localaudiodir": "sendrecv",
    "localvideodir": "inactive",
    "param": "Rejected by user"
  }
}

{
  "kind": "response",
  "time": "2026-03-27T12:51:30",
  "payload": {
    "response": true,
    "ok": true,
    "data": "",
    "token": "6d14fa58-396a-430e-9898-b503b1a12936"
  }
}

{
  "kind": "user",
  "time": "2026-03-27T12:51:42",
  "payload": {
    "command": "uadelall",
    "token": "27caa330-af71-4ea0-b925-04def8614c88"
  }
}

{
  "kind": "event",
  "time": "2026-03-27T12:51:42",
  "payload": {
    "event": true,
    "class": "ua",
    "type": "UNREGISTERING",
    "accountaor": "sip:490@10.10.2.4"
  }
}

{
  "kind": "response",
  "time": "2026-03-27T12:51:42",
  "payload": {
    "response": true,
    "ok": true,
    "data": "\n--- User Agents (0) ---\n\n",
    "token": "27caa330-af71-4ea0-b925-04def8614c88"
  }
}
```
