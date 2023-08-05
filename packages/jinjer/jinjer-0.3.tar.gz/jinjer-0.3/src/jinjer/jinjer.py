#!/usr/bin/env python3
"""
jinjer

command-line wrapper for Jinja2

Usage:
   jinjer [options] TEMPLATE-FILE [(PARAMETER VALUE)] ...

Options:
   -o OUTPUT-FILE       Output file, writes to stdout if not specified
   -p PARAMETERS-FILE   Yaml file containing parameters to be used in templating
   -t TEMPLATES-DIR     Directory containing jinja2 templates
"""
import sys
from docopt import docopt
import jinja2


def main():
    args = docopt(__doc__)
    template_file = args['TEMPLATE-FILE']
    template_dir = args['-t']
    parameters = dict(zip(args['PARAMETER'], args['VALUE']))
    output_file = args['-o']
    if args['-p']:
        import yaml

        with open(args['-p']) as f:
            docs = list(yaml.load_all(f))
    else:
        docs = [{}]
    i = 0
    of = output_file
    for d in docs:
        i += 1
        d.update(parameters)
        output = render(template_file, template_dir, d)
        if output_file:
            of = output_file.format(**d)
            if of == output_file:
                of = output_file + str(i)
        if of:
            with open(of, 'w') as f:
                f.write(output)
        else:
            print(output)
    return True


def render(template_file, template_dir, parameters):
    if template_dir is None:
        template_dir = '.'
    loader = jinja2.FileSystemLoader(template_dir)
    env = jinja2.Environment(loader=loader)
    template = env.get_template(template_file)
    return template.render(**parameters)


if __name__ == "__main__":
    sys.exit(not main())
