class Util:

    @staticmethod
    def time_diff_as_hhmmss(self, time_difference):
        total_seconds = time_difference.total_seconds()
        hours = int(total_seconds // 3600)
        remaining_seconds = total_seconds % 3600
        minutes = int(remaining_seconds // 60)
        seconds = round(remaining_seconds % 60)
        return f'{hours} hours, {minutes} minutes and {seconds} seconds'