class PaperPickListRackSubOrder(object):
    def __init__(self, order_id, source_bins, recieve_bin):
        self.order_id = order_id

        # Get tuples of the source bins' tags and the number of items in that bin
        # Use [:1] to get just the numbers "13" instead of "A13"
        source_bin_tags_and_counts = [(source_bin.tag[:1], source_bin.count) for source_bin in source_bins]
        # Sort these bins by the tag
        self.source_bin_tags_and_counts = sorted(source_bin_tags_and_counts, key=lambda tag_and_count: tag_and_count[0])

        self.recieve_bin = recieve_bin


class PaperPickListRackSu(object):
    def __init__(self, rack_name, paper_pick_list_rack_orders):
        self.rack_name = rack_name
        self.paper_pick_list_rack_orders = paper_pick_list_rack_orders


class PaperPickTask(object):
    def __init__(self, task_id, paper_pick_list_racks):
        self.task_id = task_id
        self.paper_pick_list_racks = paper_pick_list_racks
