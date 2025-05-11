# built-in
import argparse

# third-party
import pandas as pd

# local
from job_hunt_sankey.job_hunt_sankey import JobHuntSankey

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--filepath', default='notebooks/data.xlsx', help='Path to data Excel file.')
    args = parser.parse_args()

    data = pd.read_excel(args.filepath)

    sankey = JobHuntSankey(data)
    fig = sankey.create_sankey()
    fig.write_html("notebooks/job-hunt-sankey.html")
    fig.write_image("notebooks/job-hunt-sankey.png")
    fig.show()
