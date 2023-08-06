from hashlib import md5
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str
from django.utils.importlib import import_module
from static_precompiler.exceptions import UnsupportedFile
from static_precompiler.settings import MTIME_DELAY, POSIX_COMPATIBLE, STATIC_URL, COMPILERS
import os
import re
import socket
import subprocess
import urlparse


def normalize_path(posix_path):
    """ Convert posix style path to OS-dependent path.
    """
    if POSIX_COMPATIBLE:
        return posix_path
    return os.path.join(*posix_path.split("/"))


def fix_line_breaks(text):
    """ Convert Win line breaks to Unix
    """
    return text.replace("\r\n", "\n")


def get_hexdigest(plaintext, length=None):
    digest = md5(smart_str(plaintext)).hexdigest()
    if length:
        return digest[:length]
    return digest


def get_cache_key(key):
    return "django_coffescript.{0}.{1}".format(socket.gethostname(), key)


def get_mtime_cachekey(filename):
    return get_cache_key("mtime.{0}".format(get_hexdigest(filename)))


def get_mtime(filename):
    if MTIME_DELAY:
        key = get_mtime_cachekey(filename)
        mtime = cache.get(key)
        if mtime is None:
            mtime = os.path.getmtime(filename)
            cache.set(key, mtime, MTIME_DELAY)
        return mtime
    return os.path.getmtime(filename)


#noinspection PyShadowingBuiltins
def run_command(args, input=None, cwd=None):

    popen_kwargs = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if cwd is not None:
        popen_kwargs["cwd"] = cwd

    if input is not None:
        popen_kwargs["stdin"] = subprocess.PIPE

    if os.name == "nt":
        popen_kwargs["shell"] = True

    p = subprocess.Popen(args, **popen_kwargs)

    return p.communicate(input)


class URLConverter(object):

    URL_PATTERN = re.compile(r"url\(([^\)]+)\)")

    @staticmethod
    def convert_url(url, source_dir):
        assert source_dir[-1] == "/"
        url = url.strip(' \'"')
        if url.startswith(('http://', 'https://', '/', 'data:')):
            return url
        return urlparse.urljoin(STATIC_URL, urlparse.urljoin(source_dir, url))

    def convert(self, content, path):
        source_dir = os.path.dirname(path)
        if not source_dir.endswith("/"):
            source_dir += "/"
        return self.URL_PATTERN.sub(
            lambda matchobj: "url('{0}')".format(
                self.convert_url(matchobj.group(1), source_dir)
            ),
            content
        )


url_converter = URLConverter()


def convert_urls(content, path):
    return url_converter.convert(content, path)


compilers = None


def get_compilers():
    global compilers

    if compilers is None:
        compilers = []
        for compiler_path in COMPILERS:
            try:
                compiler_module, compiler_classname = compiler_path.rsplit('.', 1)
            except ValueError:
                raise ImproperlyConfigured('{0} isn\'t a compiler module'.format(compiler_path))
            try:
                mod = import_module(compiler_module)
            except ImportError as e:
                raise ImproperlyConfigured('Error importing compiler {0}: "{1}"'.format(compiler_module, e))
            try:
                compiler_class = getattr(mod, compiler_classname)
            except AttributeError:
                raise ImproperlyConfigured('Compiler module "{0}" does not define a "{1}" class'.format(compiler_module, compiler_classname))

            compilers.append(compiler_class())

    return compilers


def compile_static(path):

    for compiler in get_compilers():
        if compiler.is_supported(path):
            return compiler.compile(path)

    raise UnsupportedFile("The source file '{0}' is not supported by any of available compilers.".format(path))


def compile_static_lazy(path):

    for compiler in get_compilers():
        if compiler.is_supported(path):
            return compiler.compile_lazy(path)

    raise UnsupportedFile("The source file '{0}' is not supported by any of available compilers.".format(path))
