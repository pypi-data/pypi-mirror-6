import werkzeug._internal


def _color_log(type, message, *args, **kwargs):
    if not message.startswith(' * '):
        return global_log(type, message, *args, **kwargs)
    
    time = term.cyan(str(datetime.now().time())) + ' |'

    results = findall(' * Running on (.*)', message)
    if results:
        match = term.magenta(results[0])
        message = message.replace(results[0], match)

    results = findall(' * Detected change in (.*), reloading', message)
    if results:
        match = term.magenta(results[0])
        message = ' * Detected change in ' + match + term.cyan(', reloading')
 
    global_log(type, time + term.cyan(message), *args, **kwargs)


global_log = werkzeug._internal._log
werkzeug._internal._log = _color_log
_log = _color_log


from werkzeug.serving import run_simple, WSGIRequestHandler
from blessings import Terminal
from datetime import datetime
from colorama import init
from re import findall


init()
term = Terminal()


class ColoredLogsRequestHandler(WSGIRequestHandler):
    
    def get_colored_http_code(self, code):
        code_output = term.bold_yellow(str(code)) 
        if code >= 400:
            code_output = term.bold_red(str(code))
        elif code >= 300:
            code_output = term.bold_blue(str(code))
        elif code >= 200:
            code_output = term.bold_green(str(code))

        return code_output

    def log_request(self, code=None, size=None):
        code_output = self.get_colored_http_code(code) if code else term.bold_white('???')
        message = '%s - %s' % (code_output, term.yellow(self.requestline))

        if size:
            message += size

        time = term.cyan(self.log_date_time_string())
        address = term.green(self.address_string())

        _log('info', '%s | %s → %s\n' % (time, address, message))

    def log_error(self, *args):
        _log('error', *args)

    def log_date_time_string(self, *args):
        return str(datetime.now().time()) 

    def log_message(self, format, *args):
        _log('info', format, *args)

def run(hostname, port, application, use_reloader=False,
        use_evalex=True,
        extra_files=None, reloader_interval=1, threaded=False,
        processes=1, static_files=None,
        passthrough_errors=False, ssl_context=None):

    run_simple(hostname, port, application,
               request_handler=ColoredLogsRequestHandler, 
               passthrough_errors=passthrough_errors, 
               reloader_interval=reloader_interval, 
               static_files=static_files,
               use_reloader=use_reloader,
               extra_files=extra_files, 
               ssl_context=ssl_context,
               use_evalex=use_evalex,
               processes=processes, 
               threaded=threaded,
               use_debugger=True)
