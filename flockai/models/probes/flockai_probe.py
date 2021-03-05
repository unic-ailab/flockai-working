from time import time
from typing import List
import psutil
from flockai.PyCatascopia.Metrics import SimpleMetric, TimerMetric, DiffMetric, CounterMetric, Metric
from flockai.PyCatascopia.Probe import Probe


class FlockAIProbe(Probe):
    __PROC_TIMESTEP__ = 0.2

    def __init__(self, metrics: List[Metric], name, periodicity, pid=None):
        super().__init__(name, periodicity)
        self.probe_metrics = {}
        for metric in metrics:
            print(type(metric).__name__, '   ', metric)
            self.probe_metrics[type(metric).__name__] = metric
            self.add_metric(metric)

        self.proc = psutil.Process(pid)
        self.col_start = time()

    def get_desc(self):
        name = self.get_name()
        periodicity = self.get_periodicity()
        return f'{name} probe running every {str(periodicity)} seconds'

    def collect(self):
        for name, metric in self.probe_metrics.items():
            ct = self.proc.cpu_times()

            if name == ProcessCpuUtilizationMetric.__name__:
                metric.set_val(self.proc.cpu_percent(interval=FlockAIProbe.__PROC_TIMESTEP__))
            if name == ProcessCpuTimeMetric.__name__:
                metric.set_val(sum(ct[:4]))
            if name == ProcessIOTimeMetric.__name__:
                metric.set_val(ct[3])
            if name == ProcessAliveTimeMetric.__name__:
                metric.set_val(time() - self.proc.create_time())
            if name == ProcessMemoryMetric.__name__:
                metric.set_val(self.proc.memory_percent())
            if name == ProbeAliveTimeMetric.__name__:
                metric.set_val(time() - self.col_start)
            if name == SimpleMetric.__name__:
                pass
            if name == DiffMetric.__name__:
                pass
            if name == TimerMetric.__name__:
                pass
            if name == CounterMetric.__name__:
                pass
            # Expand this list on demand

    def get_metric(self, name):
        return self.probe_metrics[name]

class ProcessCpuUtilizationMetric(SimpleMetric):
    def __init__(self, name, units, desc, minVal = float('-inf'), maxVal = float('inf'), higherIsBetter=True):
        super().__init__(name, units, desc, minVal=minVal, maxVal=maxVal, higherIsBetter=higherIsBetter)


class ProcessAliveTimeMetric(SimpleMetric):
    def __init__(self, name, units, desc, minVal = float('-inf'), maxVal = float('inf'), higherIsBetter=True):
        super().__init__(name, units, desc, minVal=minVal, maxVal=maxVal, higherIsBetter=higherIsBetter)


class ProcessIOTimeMetric(SimpleMetric):
    def __init__(self, name, units, desc, minVal = float('-inf'), maxVal = float('inf'), higherIsBetter=True):
        super().__init__(name, units, desc, minVal=minVal, maxVal=maxVal, higherIsBetter=higherIsBetter)


class ProcessMemoryMetric(SimpleMetric):
    def __init__(self, name, units, desc, minVal = float('-inf'), maxVal = float('inf'), higherIsBetter=True):
        super().__init__(name, units, desc, minVal=minVal, maxVal=maxVal, higherIsBetter=higherIsBetter)


class ProcessCpuTimeMetric(SimpleMetric):
    def __init__(self, name, units, desc, minVal = float('-inf'), maxVal = float('inf'), higherIsBetter=True):
        super().__init__(name, units, desc, minVal=minVal, maxVal=maxVal, higherIsBetter=higherIsBetter)

class ProbeAliveTimeMetric(SimpleMetric):
    def __init__(self, name, units, desc, minVal = float('-inf'), maxVal = float('inf'), higherIsBetter=True):
        super().__init__(name, units, desc, minVal=minVal, maxVal=maxVal, higherIsBetter=higherIsBetter)