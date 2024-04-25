import logging
import memcache
from http.server import SimpleHTTPRequestHandler, HTTPServer
import streamlink
import urllib.parse
import threading
from concurrent import futures

  # Configuración del logging
logging.basicConfig(level=logging.DEBUG)

  # Conexión al servidor Memcached
mc = memcache.Client(['127.0.0.1:11211'], debug=0)

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
      parsed_path = urllib.parse.urlparse(self.path)
      query_params = urllib.parse.parse_qs(parsed_path.query)

      if 'url' in query_params:
        url = query_params['url'][0]
        self.send_live_stream_redirect(url)
      else:
        super().do_GET()

    def send_live_stream_redirect(self, url):
      live_stream_url = self.get_live_stream_url(url)

      if live_stream_url:
        self.send_response(301)
        self.send_header('Location', live_stream_url)
      else:
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.wfile.write(b'404 Not Found')
      self.end_headers()

    def get_live_stream_url(self, url):
      try:
        cached_url = mc.get(url)
        if cached_url:
          return cached_url

        # Usar hilos para mejorar el rendimiento
        with futures.ThreadPoolExecutor() as executor:
          future = executor.submit(get_live_stream_url_thread, url)
          stream_url = future.result()

        if stream_url:
          mc.set(url, stream_url)

        return stream_url
      except streamlink.exceptions.NoPluginError:
        logging.error(f"No se encontró ningún complemento para la URL: {url}")
      except streamlink.exceptions.StreamError:
        logging.error(f"Error al capturar la transmisión en vivo para la URL: {url}")
      return None

def get_live_stream_url_thread(url):
      try:
        streams = streamlink.streams(url)
        if streams:
          stream_url = streams['best'].url
          return stream_url
        else:
          logging.error(f"No se encontraron transmisiones en vivo para la URL: {url}")
      except streamlink.exceptions.NoPluginError:
        logging.error(f"No se encontró ningún complemento para la URL: {url}")
      except streamlink.exceptions.StreamError:
        logging.error(f"Error al capturar la transmisión en vivo para la URL: {url}")
      return None

def run_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, MyHTTPRequestHandler)
    print('Servidor en ejecución en el puerto 8080...')

    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()

    try:
      thread.join()
    except KeyboardInterrupt:
      pass
    finally:
      httpd.server_close()

if __name__ == '__main__':
    run_server()