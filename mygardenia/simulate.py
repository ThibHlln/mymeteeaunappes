import subprocess
import os
import re
import glob
import pandas as pd
import evalhyd
from matplotlib import pyplot as plt

from ._convert import (
    convert_to_rga_content, convert_to_gar_content
)


class GardeniaModel(object):

    def __init__(self, tree, working_dir):
        self._tree = tree
        self._working_dir = working_dir

        self.streamflow = None
        self.piezo_level = None

    def run(self, execution_mode: str = 'M', save_outputs: bool = True,
            _verbose: bool = False):
        """Run the simulation with Gardenia.

        :Parameters:

            execution_mode: `str`, optional
                The execution mode to use when calling Gardenia. It
                can be 'M' for silent or 'D' for direct. If not provided,
                silent mode is used.

            save_outputs: `str`, optional
                Whether to try to save the streamflow and/or piezometric
                level as separate CSV files if they are available in
                Gardenia output files. If not provided, set to True.

        :Returns:

            `None`
        """
        separator = '/'

        rga_file = separator.join(['config', "auto.rga"])
        gar_file = separator.join(['config', "auto.gar"])

        # ----------------------------------------------------------------------
        # generate *.rga file
        # ----------------------------------------------------------------------
        rga_text = convert_to_rga_content(
            gar=gar_file, **self._tree
        )

        with open(separator.join([self._working_dir, rga_file]), "w+") as f:
            f.writelines(rga_text)

        # ----------------------------------------------------------------------
        # generate *.gar file
        # ----------------------------------------------------------------------
        gar_text = convert_to_gar_content(
            **self._tree
        )

        with open(separator.join([self._working_dir, gar_file]), "w+") as f:
            f.writelines(gar_text)

        # ----------------------------------------------------------------------
        # run gardenia model
        # ----------------------------------------------------------------------
        msg = subprocess.run(
            [
                f"{os.environ['bin_Garden']}{os.sep}gardenia.exe",
                rga_file, execution_mode
            ],
            cwd=self._working_dir,
            stdout=subprocess.PIPE
        ).stdout.decode('windows-1252')

        if _verbose:
            print(msg)

        # ----------------------------------------------------------------------
        # move output files
        # ----------------------------------------------------------------------
        for f in glob.glob(f'{self._working_dir}{os.sep}*.*'):
            filename = f.split(os.sep)[-1]
            os.replace(
                os.sep.join([self._working_dir, filename]),
                os.sep.join([self._working_dir, 'output', filename])
            )

        # ----------------------------------------------------------------------
        # post-process outputs
        # ----------------------------------------------------------------------
        output_file = os.sep.join([self._working_dir, 'output', "gardesim.prn"])

        beg_river = None
        end_river = None
        beg_piezo = None
        end_piezo = None

        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if re.compile(r'Fin :.*: Débit_Riv').findall(line):
                    end_river = i
                elif re.compile(r': Débit_Riv').findall(line):
                    beg_river = i + 1
                elif re.compile(r'Fin :.*: Niveau_Aquif').findall(line):
                    end_piezo = i
                elif re.compile(r': Niveau_Aquif').findall(line):
                    beg_piezo = i + 1

        with open(output_file, 'r') as f:
            n_lines = len(f.readlines())

        options = dict(
            encoding='windows-1252',
            engine='python',
            parse_dates=[0], date_format='%d/%m/%Y'
        )

        if beg_river and end_river:
            df_river = pd.read_table(
                output_file,
                skiprows=beg_river, skipfooter=n_lines-end_river,
                names=['dt', 'river_sim', 'river_obs'],
                **options
            )
            self.streamflow = df_river
            if save_outputs:
                df_river.to_csv(
                    separator.join(
                        [self._working_dir, "output", "river_sim_obs.csv"]
                    ),
                    index=False
                )

        if beg_piezo and end_piezo:
            df_piezo = pd.read_table(
                output_file,
                skiprows=beg_piezo, skipfooter=n_lines-end_piezo,
                names=['dt', 'piezo_sim', 'piezo_obs'],
                **options
            )
            self.piezo_level = df_piezo
            if save_outputs:
                df_piezo.to_csv(
                    separator.join(
                        [self._working_dir, "output", "piezo_sim_obs.csv"]
                    ),
                    index=False
                )

    def _trim_output_of_spin_up(self, df: pd.DataFrame):
        # retrieve length of spin up run
        spin_up = (
            self._tree['basin_settings']['model']
            ['initialisation']['spinup']['n_years']
        )

        # subset in time to exclude spin up period
        df = df[
            df['dt'] >= (
                    df['dt'].iloc[0] + pd.offsets.DateOffset(years=spin_up)
            )
        ]

        return df

    def evaluate(
            self, variable: str, metric: str,
            transform: str = None, exponent: float = None
    ):
        """ Evaluate the performance between the simulations and the
        observations for a given variable.

        :Parameters:

            variable: `str`
                The model variable to evaluate. It can either be
                'streamflow' or 'piezo_level'.

            metric: `str`
                The evaluation metric to use to compare observations and
                simulations. It can be any metric available in `evalhyd`
                (https://hydrogr.github.io/evalhyd/metrics/deterministic.html)

            transform: `str`, optional
                The transformation function to apply to the observations
                and the predictions before computing the metric. It can
                be 'log', 'inv', 'sqrt', 'pow'. If not provided, no
                transformation is performed.

            exponent: `float`, optional
                The exponent to use if the transform is set to 'pow',
                the power function.

        :Returns:

            `float`
                The value of the evaluation metric.

        """
        if variable not in ['streamflow', 'piezo_level']:
            raise ValueError(f"{repr(variable)} is not supported")

        # collect relevant variable
        df = getattr(self, variable)
        if df is None:
            raise ValueError(f"{repr(variable)} was not computed")

        # subset in time to exclude spin up period
        df = self._trim_output_of_spin_up(df)

        # returned evaluation metric value
        prefix = 'river' if variable == 'streamflow' else 'piezo'

        return evalhyd.evald(
            q_obs=df[f'{prefix}_obs'].values,
            q_prd=df[f'{prefix}_sim'].values,
            metrics=[metric],
            transform=transform, exponent=exponent
        )[0].squeeze()

    def visualise(
            self, variable: str, filename: str = None, fig_size: tuple = None
    ):
        """Visualise the simulations and the observations time series
        for a given variable.

        :Parameters:

            variable: `str`
                The model variable to evaluate. It can either be
                'streamflow' or 'piezo_level'.

            filename: `str`, optional
                The file name to use for storing the visualisation. The
                file extension in the name will control the file format
                generated (e.g. *.pdf, *.png). If not provided, the
                visualisation is only shown and not saved as a file.
                
            fig_size: `tuple`, optional
                The width and the height of the figure as a tuple.
                If not provided, set to (10, 4).

        :Returns:

            `None`

        """
        if variable not in ['streamflow', 'piezo_level']:
            raise ValueError(f"{repr(variable)} is not supported")

        # collect relevant variable
        df = getattr(self, variable)
        if df is None:
            raise ValueError(f"{repr(variable)} was not computed")

        # subset in time to exclude spin up period
        df = self._trim_output_of_spin_up(df)

        # generate plot
        fig, ax = plt.subplots(
            figsize=fig_size if fig_size else (10, 4)
        )

        prefix = 'river' if variable == 'streamflow' else 'piezo'

        ax.plot(
            df['dt'], df[f'{prefix}_obs'], label='observed',
            marker='+', markersize=1.5, linestyle='-'
        )
        ax.plot(
            df['dt'], df[f'{prefix}_sim'], label='simulated'
        )

        ax.set_xlabel('time')

        ax.set_ylabel(
            r'streamflow [m$^3$.s$^{-1}$]' if variable == 'streamflow'
            else f'piezometric level [m NGF]'
        )

        ax.legend(frameon=False)

        # save or show
        if filename is not None:
            fig.savefig(
                os.sep.join([self._working_dir, "output", filename])
            )
        else:
            plt.show()
