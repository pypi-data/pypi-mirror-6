import asyncore
from threading import Thread
from multiprocessing import Process

from tornado.web import StaticFileHandler
from tornado import template, ioloop, web

from .smtp import start_smtp_server, ProxyDebugServer
from .handlers import *
from .settings import *
from .utils.http import split_host_port
from .utils.termcolors import colorize
from . import __version__

application = web.Application(
    [
        (r"/", IndexHandler),
        (r"/mail/", MailListHandler),
        (r"/mail/([0-9^/]+)/", MailDetailHandler),
        (r"/mail/all/read/", ReadAllMailHandler),
        (r"/mail/all/delete/", DeleteAllMailHandler),
        (r'/medias/(.*)', StaticFileHandler, {'path': MEDIAS_DIR}),
    ] + EchoSockjsRouter('/inbox'),
    debug=DEBUG,
    compiled_template_cache=CACHE_TEMPLATES,
    template_loader=template.Loader(TEMPLATES_DIR)
)


def runserver(args):
    http_host, http_port = split_host_port(args.http_bind)
    smtp_host, smtp_port = split_host_port(args.smtp_bind)
    
    print colorize(" * PyLocalSMTP V%s" % __version__, fg="green")
    print colorize(" * Web server listening at http://%s/" % args.http_bind, fg="green")
    print colorize(" * SMTP server listening at %s" % args.smtp_bind, fg="green")
    print "(To stop PyLocalSMTP, press Ctrl+C)"

    thread = Thread(target=start_smtp_server, args=(smtp_host, smtp_port), kwargs={'queue': MAIN_QUEUE})
    thread.daemon = True
    thread.start()

    try:
        p = Process(target=asyncore.loop)
        p.start()
        application.listen(int(http_port), address=http_host)
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
