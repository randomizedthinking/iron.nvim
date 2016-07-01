# encoding:utf-8
"""Leiningen repl definition for iron.nvim. """
import os
from functools import partial


# Get Data
def get_current_parens(iron):
    iron.call_cmd("""silent normal! mx%"sy%`x""")
    return iron.register('s')


def get_current_ns(iron):
    iron.call_cmd("""silent normal! mxggf w"sy$`x""")
    return iron.register('s')


def lein_require(iron, send_fn):
    data = "(require '{})".format(get_current_parens(iron))
    return send_fn((data, "clojure"))


def lein_import(iron, send_fn):
    data = "(import '{})".format(get_current_parens(iron))
    return send_fn((data, "clojure"))


# Transform data
def lein_require_file(iron, send_fn):
    data = "(require '[{}] :reload)".format(get_current_ns(iron))
    return send_fn((data, "clojure"))


def lein_require_with_ns(iron, send_fn):
    ns = iron.prompt("with alias")
    data = "(require '[{} :as {}])".format(
        get_current_ns(iron), ns
    )
    return send_fn((data, "clojure"))


def lein_send(iron, send_fn):
    iron.call_cmd("""
exec "normal! mx"
exec "?^("
exec 'silent normal! "sya(`x'
nohl""".replace("\n", " | "))
    return send_fn((iron.register('s'), "clojure"))


def lein_load_facts(iron, send_fn):
    data = "(load-facts '{}-test)".format(get_current_ns(iron))
    return send_fn((data, "clojure"))


def lein_prompt_require(iron, send_fn):
    require = iron.prompt("require file")
    data = "(require '[{}])".format(require)
    return send_fn((data, "clojure"))


def lein_prompt_require_as(iron, send_fn):
    require = iron.prompt("require file")
    alias = iron.prompt("as")
    data = "(require '[{} :as {}])".format(require, alias)
    return send_fn((data, "clojure"))


# send data
def nrepl_eval(iron, data):
    "requires nrepl-python-client"
    try:
        import nrepl
    except:
        iron.call_cmd("echomsg 'Unable to eval - missing nREPL client lib'")
        return

    vim_pwd = iron.call("getcwd")
    with open(os.path.join(vim_pwd, ".nrepl-port")) as port:
        c = nrepl.connect("nrepl://localhost:{}".format(port.read()))


    c.write({"op": "eval", "code": data})
    r = c.read()
    value = c.read()["value"] if "value" not in r else r["value"]

    c.read()
    c.close()
    return value


def lein_prompt_eval(iron):
    cmd = iron.prompt("cmd")
    ret = nrepl_eval(iron, cmd)
    iron.call_cmd("echomsg '{}'".format(ret))

repl = {
    'command': 'lein repl',
    'language': 'clojure',
    'detect': lambda *args, **kwargs: True,
    'mappings': [
        ('<leader>so', 'require',
         lambda iron: lein_require(iron, iron.send_to_repl)),

        ('<leader>si', 'import',
         lambda iron: lein_import(iron, iron.send_to_repl)),

        ('<leader>sr', 'require_file',
         lambda iron: lein_require_file(iron, iron.send_to_repl)),

        ('<leader>sR', 'require_with_ns',
         lambda iron: lein_require_with_ns(iron, iron.send_to_repl)),

        ('<leader>s.', 'prompt_require',
         lambda iron: lein_prompt_require(iron, iron.send_to_repl)),

        ('<leader>s/', 'prompt_require_as',
         lambda iron: lein_prompt_require_as(iron, iron.send_to_repl)),

        ('<leader>ss', 'send',
         lambda iron: lein_send(iron, iron.send_to_repl)),

        ('<leader>sm', 'midje',
         lambda iron: lein_load_facts(iron, iron.send_to_repl)),

        ('<leader>eo', 'eval-require',
         lambda iron: lein_require(iron, partial(nrepl_eval, iron))),

        ('<leader>ei', 'eval-import',
         lambda iron: lein_import(iron, partial(nrepl_eval, iron))),

        ('<leader>er', 'eval-require_file',
         lambda iron: lein_require_file(iron, partial(nrepl_eval, iron))),

        ('<leader>eR', 'eval-require_with_ns',
         lambda iron: lein_require_with_ns(iron, partial(nrepl_eval, iron))),

        ('<leader>e.', 'eval-prompt_require',
         lambda iron: lein_prompt_require(iron, partial(nrepl_eval, iron))),

        ('<leader>e/', 'eval-prompt_require_as',
         lambda iron: lein_prompt_require_as(iron, partial(nrepl_eval, iron))),

        ('<leader>es', 'eval-send',
         lambda iron: lein_send(iron, partial(nrepl_eval, iron))),

        ('<leader>em', 'eval-midje',
         lambda iron: lein_load_facts(iron, partial(nrepl_eval, iron))),

        ('<leader>ep', 'prompt_eval', lein_prompt_eval),
    ]
}
