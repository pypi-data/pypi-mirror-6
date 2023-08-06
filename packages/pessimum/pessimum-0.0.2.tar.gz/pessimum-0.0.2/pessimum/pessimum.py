from .utils.shims import PluginShim
from .durations_report import DurationsReport
from .print_durations import PrintDurations


class Pessimum(PluginShim):
    def __init__(self, durations_report=DurationsReport):
        self.stream = None
        self.print_durations = None
        self.durations_report = durations_report()
        super(Pessimum, self).__init__()

    def before_test(self, test):
        self.durations_report.start(test)

    def after_test(self, test):
        self.durations_report.end(test)

    def set_output_stream(self, stream):
        self.print_durations = PrintDurations(
            stream, self.durations_report
        )

    def finalize(self, result):
        self.print_durations.print_header()
        self.print_durations.print_body(10)
        self.print_durations.write_line()

    def options(self, parser, env):
        parser.add_option(
            "--slow-report",
            action="store_true",
            default=False,
            dest="slow_report",
            help="show the top 10 worst performing tests"
        )

    def configure(self, options, env):
        if options.slow_report:
            self.enabled = True

    @property
    def times(self):
        return list(self.durations_report)