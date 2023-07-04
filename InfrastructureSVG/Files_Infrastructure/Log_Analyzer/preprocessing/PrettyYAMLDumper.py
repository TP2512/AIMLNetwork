import yaml


class PrettyYAMLDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(PrettyYAMLDumper, self).increase_indent(flow, False)
