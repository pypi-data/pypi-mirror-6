
import time
import csv
from collections import defaultdict


fmt_float = "{:.2f}".format
fmt_time = time.ctime


class Stats:
    def __init__(self):
        self.starttime = dict()
        self.endtime = dict()

    def report_job_start(self, job):
        self.starttime[job] = time.time()

    def report_job_end(self, job):
        self.endtime[job] = time.time()

    @property
    def rule_runtimes(self):
        runtimes = defaultdict(list)
        for job, t in self.starttime.items():
            runtimes[job.rule].append(self.endtime[job] - t)
        for rule, runtimes in runtimes.items():
            yield (
                rule,
                fmt_float(sum(runtimes) / len(runtimes)),
                fmt_float(min(runtimes)), fmt_float(max(runtimes)))

    @property
    def file_runtimes(self):
        for job, t in self.starttime.items():
            for f in job.expanded_output:
                start, stop = t, self.endtime[job]
                yield f, fmt_time(start), fmt_time(stop), fmt_float(stop - start)

    @property
    def overall_runtime(self):
        if self.starttime and self.endtime:
            return fmt_float(max(self.endtime.values()) - min(self.starttime.values()))
        else:
            return fmt_float(0)

    def to_csv(self, path):
        with open(path, "w") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow("overall-runtime".split())
            writer.writerow([self.overall_runtime])
            writer.writerow(
                "rule mean-runtime min-runtime max-runtime".split())
            for runtime in self.rule_runtimes:
                writer.writerow(runtime)
            writer.writerow(list())
            writer.writerow("file start-time stop-time duration".split())
            for runtime in self.file_runtimes:
                writer.writerow(runtime)
