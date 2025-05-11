import plotly.graph_objects as go
import pandas as pd
import numpy as np

import matplotlib
import matplotlib.colors as mcolors


class JobHuntSankey:
    ''' Sankey diagram describing job hunt. Each --- corresponds a differente stage of the application process (e.g. Application, Interview 1, Interview 2, ..., Status).

    Attributes
    ---------- 
    data : pd.DataFrame
        Dataframe where each new entry corresponds to a single application and must contain the following columns:
            - Platform (str): Platform through which the application was made.
            - Nb. Interviews (int): Number of interviews already completed.
            - Status (str): Current application status, e.g. Rejected, Waiting, Offer, etc.

    Methods
    -------
    create_sankey() :
        Create and plot Sankey diagram.
    '''

    def __init__(self, data):
        self.max_nb_interviews = data['Nb. Interviews'].max()
        self.data = data.copy()
        self.links = None
        self.label_to_index = {}
        self.all_labels = []

    def _generate_interview_columns(self):
        ''' From the number of interviews performed, create a sequence of columns (i.e. "Interview 1", "Interview 2", etc), where each entry has an "Interview n" (in the corresponding column) or NA (in the remaining columns) according to the current interview status. The new columns are added to self.data.'''
        for n in range(self.max_nb_interviews):
            self.data[f'Interview {n+1}'] = np.where(
                self.data['Nb. Interviews'] > n, f'Interview {n+1}', pd.NA
            )
        self.data = self.data[['Platform'] + [
            f'Interview {n+1}' for n in range(self.max_nb_interviews)] + ['Status']]

    def _generate_link_colors(self):
        cmap = matplotlib.colormaps.get_cmap('tab20c')
        return [mcolors.to_hex(cmap(i)) for i in range(len(self.links))]

    def generate_links(self):
        ''' Create links dataframe with the counts for each sequential step in the job hunt. E.g. Applications-LinkedIn: 2, LinkedIn-Interview 1: 1, LinkedIn-Rejected: 1, Interview 1-Interview 2: 1, Interview 2-Waiting: 1.'''
        data_aux = self.data.copy()
        links = []
        for n in range(self.max_nb_interviews):
            links += self._get_consecutive_cols_counts(
                data_aux[pd.isna(data_aux[f'Interview {n+1}'])].dropna(axis=1)
            )
            data_aux = data_aux.dropna(subset=f'Interview {n+1}')

        links += self._get_consecutive_cols_counts(data_aux)
        links = pd.concat([
            self.data["Platform"].value_counts().rename_axis("target").reset_index(name="value").assign(source="Applications")] + links
        ).reset_index(drop=True)

        self.links = links[['source', 'target', 'value']].groupby(
            ['source', 'target'], as_index=False)['value'].sum()

    def _get_consecutive_cols_counts(self, df):
        return [df.groupby([df.columns[n], df.columns[n+1]]).size().rename_axis(["source", "target"]).reset_index(name="value") for n in range(len(df.columns)-1)]

    def _map_labels_to_indices(self):
        self.all_labels = pd.unique(
            self.links[['source', 'target']].values.ravel())
        self.label_to_index = {label: idx for idx,
                               label in enumerate(self.all_labels)}
        self.links['source_idx'] = self.links['source'].map(
            self.label_to_index)
        self.links['target_idx'] = self.links['target'].map(
            self.label_to_index)

    def build_figure(self, title):
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=self.all_labels,
                color=self._generate_link_colors()
            ),
            link=dict(
                source=self.links['source_idx'].tolist(),
                target=self.links['target_idx'].tolist(),
                value=self.links['value'].tolist(),
                # color=['lightgray'] * len(self.links)
            )
        )])
        fig.update_layout(title_text=title, font_size=15)
        return fig

    def create_sankey(self, title='Job Hunt Sankey Diagram'):
        self._generate_interview_columns()
        self.generate_links()
        self._map_labels_to_indices()
        return self.build_figure(title)


data = pd.DataFrame(
    data=[['A', 'LinkedIn', 0, 'Rejected'],
          ['B', 'LinkedIn', 1, 'Rejected'],
          ['C', 'LinkedIn', 2, 'Waiting'],
          ['D', 'Stepstone', 2, 'Offer']],
    columns=['Entry', 'Platform', 'Nb. Interviews', 'Status'])

sankey = JobHuntSankey(data)
fig = sankey.create_sankey()
fig.show()
