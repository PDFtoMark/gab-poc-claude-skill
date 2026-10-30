import http.server, json, socketserver

LOG = '/tmp/mock-requests.log'

SSE = (
    'event: message_start\n'
    'data: {"type":"message_start","message":{"id":"msg_poc","type":"message","role":"assistant","model":"claude-opus-5-5","content":[],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":10,"output_tokens":1}}}\n\n'
    'event: content_block_start\n'
    'data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}\n\n'
    'event: content_block_delta\n'
    'data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"ok"}}\n\n'
    'event: content_block_stop\n'
    'data: {"type":"content_block_stop","index":0}\n\n'
    'event: message_delta\n'
    'data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":1}}\n\n'
    'event: message_stop\n'
    'data: {"type":"message_stop"}\n\n'
)


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def _log(self, line, body=b''):
        with open(LOG, 'ab') as f:
            f.write(line + b'\n' + body + b'\n')

    def do_POST(self):
        n = int(self.headers.get('content-length') or 0)
        body = self.rfile.read(n)
        self._log(b'=== POST ' + self.path.encode(), body)
        if 'count_tokens' in self.path:
            out = json.dumps({"input_tokens": 10}).encode()
            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.send_header('content-length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)
            return
        out = SSE.encode()
        self.send_response(200)
        self.send_header('content-type', 'text/event-stream')
        self.send_header('content-length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def do_GET(self):
        self._log(b'=== GET ' + self.path.encode())
        out = b'{}'
        self.send_response(200)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('127.0.0.1', 8787), H) as s:
    s.serve_forever()
