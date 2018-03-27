class SourceBin(object):
    def __init__(self, tag, count):
        self.tag = tag
        self.count = count


class ReceiveBin(object):
    def __init__(self, tag, expected_count):
        self.tag = tag
        self.expected_count = expected_count


class RackOrders(object):
    def __init__(self, task_id, order_id, rack, source_bins, receive_bin):
        self.task_id = task_id
        self.order_id = order_id
        self.rack = rack
        self.source_bins = source_bins
        self.receive_bin = receive_bin  # type: ReceiveBin

    @property
    def source_bins_in_dict(self):
        return {bin.tag: bin.count for bin in self.source_bins}

    @property
    def receive_bin_in_dict(self):
        return {self.receive_bin.tag: self.receive_bin.expected_count}

    @property
    def for_init_displays(self):
        display_dict = self.source_bins_in_dict
        display_dict.update(self.receive_bin_in_dict)
        return display_dict

    def __str__(self):
        return "Task (Order ID=%d, Task ID=%d): %d bins -> %s" % (self.task_id, self.order_id, len(self.source_bins), self.receive_bin.tag)
