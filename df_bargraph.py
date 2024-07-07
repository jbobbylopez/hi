import os
import psutil
import shutil
from termcolor import colored

# Constants for configurations
SIZE_MIN_WIDTH = 15
BAR_MIN_LENGTH = 10
LABEL_MAX_WIDTH = 35
USED_LABEL_WIDTH = 10  # Width to accommodate percentages like 100.0%
USED_VALUE_WIDTH = 7  # Width to accommodate percentages like 100.0%

def get_colored_bar(usage_percent, bar_length):
    """Generate a colored bar based on usage percentage."""
    num_hashes = int((usage_percent / 100) * bar_length)
    
    if usage_percent < 50:
        color = 'green'
    elif usage_percent < 80:
        color = 'yellow'
    else:
        color = 'red'

    bar = '=' * num_hashes
    bar = colored(bar, color)
    return bar + '-' * (bar_length - num_hashes)

def get_human_readable_size(size):
    """Convert bytes to a human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0

def format_size(used, total, free):
    """Format the size string for used, total, and free space."""
    used_str = get_human_readable_size(used)
    total_str = get_human_readable_size(total)
    free_str = get_human_readable_size(free)
    return used_str, total_str, free_str

def get_disk_usage():
    """Gather disk usage information."""
    partitions = psutil.disk_partitions()
    usage_list = []

    for partition in partitions:
        if ('loop' in partition.device or
            'cdrom' in partition.opts or 
            partition.fstype == '' or 
            partition.mountpoint.startswith('/var/snap') or
            partition.mountpoint == '/boot/efi'):
            continue
        
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            label = "root (/) " if partition.mountpoint == "/" else partition.mountpoint
            used, total, free = format_size(usage.used, usage.total, usage.free)
            usage_list.append((label, used, total, free, usage.percent))
        except PermissionError:
            # Skip mounts that are not accessible
            continue
    
    return usage_list

def display_bar_graph():
    """Display the disk usage as a bar graph."""
    usage_list = get_disk_usage()
    
    if not usage_list:
        print("No filesystem usage data available or all data filtered out.")
        return

    terminal_width = shutil.get_terminal_size().columns

    # Adjust label width dynamically but within a fixed max width.
    max_label_length = max(len(label) for label, _, _, _, _ in usage_list) if usage_list else 0
    label_width = min(max_label_length + 2, LABEL_MAX_WIDTH)
    size_width = SIZE_MIN_WIDTH  # Adjust size width to fit individual columns

    # Calculate the dynamic width for the bars, ensuring it fits within the terminal width
    bar_width = terminal_width - label_width - size_width * 3 - USED_VALUE_WIDTH - 20  # Space for brackets, spaces, and percentage
    bar_width = max(BAR_MIN_LENGTH, bar_width)  # Ensure at least the minimum width

    # Output header:
    print(f"{'Filesystem':<{label_width}} {'Used':<{size_width}} {'Total':<{size_width}} {'Free':<{size_width}} {'Bar':<{bar_width}} {'% Used':>{USED_LABEL_WIDTH}}")
    
    # Output rows:
    for label, used, total, free, usage in usage_list:
        bar = get_colored_bar(usage, bar_width)

        if len(label) > label_width:
            label = label[:label_width - 1] + '…'  # Truncate label if needed

        print(f"{label:<{label_width}} {used:<{size_width}} {total:<{size_width}} {free:<{size_width}} [{bar}]>{usage:>{USED_VALUE_WIDTH}.1f}%")

if __name__ == "__main__":
    display_bar_graph()
