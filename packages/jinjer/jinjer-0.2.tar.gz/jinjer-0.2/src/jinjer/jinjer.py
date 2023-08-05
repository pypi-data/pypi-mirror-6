#!/usr/bin/env python3
"""
templater

command-line wrapper for Jinja2

Usage:
   templater [options] TEMPLATE-FILE [(PARAMETER VALUE)] ...

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
            d = yaml.load(f.read())
            d.extend(parameters)
            parameters = d
    output = render(template_file, template_dir, parameters)
    if output_file:
        with open(output_file, 'w') as f:
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
