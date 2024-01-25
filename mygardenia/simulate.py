import subprocess
import os
import pathlib
import re
import glob
import pandas as pd

from ._convert import (
    convert_to_rga_content, convert_to_gar_content,
    parse_gar_content
)
from .configure import GardeniaTree
from .postprocess import evaluate, visualise


def _manage_working_directory(working_dir: str):
    # create working directory and 'config' subdirectory if they do not exist
    (
        pathlib.Path(os.path.join(working_dir, 'config'))
        .mkdir(parents=True, exist_ok=True)
    )
    # create working directory and 'data' subdirectory if they do not exist
    (
        pathlib.Path(os.path.join(working_dir, 'data'))
        .mkdir(parents=True, exist_ok=True)
    )
    # create working directory and 'output' subdirectory if they do not exist
    (
        pathlib.Path(os.path.join(working_dir, 'output'))
        .mkdir(parents=True, exist_ok=True)
    )


class GardeniaModel(object):

    def __init__(self, tree: GardeniaTree, working_dir: str):
        """Initialise a wrapper for a simulation with the Gardenia model.

        :Parameters:

            tree: `GardeniaTree`
                The Gardenia tree containing all the settings and parameters
                to be given to the Gardenia model.

            working_dir: `str`
                The path to the directory containing the simulation data,
                the potential configuration files and the future simulation
                output.

        :Returns:

            `GardeniaModel`

        **Examples**

        >>> t = GardeniaTree()
        >>> m = GardeniaModel(t, working_dir='examples/my-example')
        """
        self._tree = tree

        _manage_working_directory(working_dir)
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

        **Examples**

        >>> t = GardeniaTree(
        ...     catchment='examples/my-example/config/bassin.toml',
        ...     settings='examples/my-example/config/reglages.toml'
        ... )
        >>> m = GardeniaModel(t, working_dir='examples/my-example')
        >>> m.run(save_outputs=True)
        """
        separator = '/'

        rga_file = separator.join(['config', "auto.rga"])
        gar_file = separator.join(['config', "auto.gar"])

        # ---------------------------------------------------------------------
        # generate *.rga file
        # ---------------------------------------------------------------------
        rga_text = convert_to_rga_content(
            gar=gar_file, **self._tree
        )

        with open(separator.join([self._working_dir, rga_file]), "w+") as f:
            f.writelines(rga_text)

        # ---------------------------------------------------------------------
        # generate *.gar file
        # ---------------------------------------------------------------------
        gar_text = convert_to_gar_content(
            **self._tree
        )

        with open(separator.join([self._working_dir, gar_file]), "w+") as f:
            f.writelines(gar_text)

        # ---------------------------------------------------------------------
        # generate *.toml file
        # ---------------------------------------------------------------------
        self._tree.to_toml(filepath=os.path.join(self._working_dir, 'config'))

        # ---------------------------------------------------------------------
        # run gardenia model
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # move output files
        # ---------------------------------------------------------------------
        for f in glob.glob(f'{self._working_dir}{os.sep}*.*'):
            filename = f.split(os.sep)[-1]
            os.replace(
                os.path.join(self._working_dir, filename),
                os.path.join(self._working_dir, 'output', filename)
            )

        # ---------------------------------------------------------------------
        # generate a *.toml file from the *.out file
        # ---------------------------------------------------------------------
        gar_file = os.path.join(
            self._working_dir, 'output', "gardepara.out"
        )

        gar_tree = GardeniaTree()
        gar_tree.update(parse_gar_content(gar_file))

        gar_tree.to_toml(
            filepath=os.path.join(self._working_dir, 'output'),
            filename='keep.toml'
        )

        # ---------------------------------------------------------------------
        # post-process outputs if they exist
        # ---------------------------------------------------------------------
        output_file = os.path.join(
            self._working_dir, 'output', "gardesim.prn"
        )

        if save_outputs and not pathlib.Path(output_file).is_file():
            raise RuntimeError(
                'outputs cannot be saved because *gardesim.prn* '
                'does not exist'
            )

        beg_river = None
        end_river = None
        beg_piezo = None
        end_piezo = None

        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if re.compile(r'Fin :.*: Débit_Riv\n').findall(line):
                    end_river = i
                elif re.compile(r': Débit_Riv\n').findall(line):
                    beg_river = i + 1
                elif re.compile(r'Fin :.*: Niveau_Aquif\n').findall(line):
                    end_piezo = i
                elif re.compile(r': Niveau_Aquif\n').findall(line):
                    beg_piezo = i + 1

        with open(output_file, 'r') as f:
            n_lines = len(f.readlines())

        if not bool(int(self._tree['general_settings']['forecast_run'])):
            # in simulation mode
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
        else:
            # in forecast mode
            options = dict(
                encoding='windows-1252',
                engine='python', header=None,
                parse_dates=[0], date_format='%d/%m/%Y'
            )

            span = int(
                self._tree['basin_settings']['time']['forecast']['span']
            )

            if beg_river and end_river:
                df_river_top = pd.read_table(
                    output_file,
                    skiprows=beg_river,
                    skipfooter=n_lines-end_river+span+2,
                    names=['dt', 'river_sim', 'river_obs'],
                    **options
                )
                
                df_river_btm = pd.read_table(
                    output_file,
                    skiprows=end_river-span-1,
                    skipfooter=n_lines-end_river,
                    names=['dt', 'river_sim', 'river_obs',
                           'river_frc_no-rain', 'river_frc_10%-dry',
                           'river_frc_20%-dry', 'river_frc_50%',
                           'river_frc_20%-wet', 'river_frc_10%-wet'],
                    **options
                )

                df_river = pd.concat([df_river_top, df_river_btm], axis=0)

                if save_outputs:
                    df_river.to_csv(
                        separator.join(
                            [self._working_dir, "output",
                             "river_sim_obs_frc.csv"]
                        ),
                        index=False
                    )

            if beg_piezo and end_piezo:
                df_piezo_top = pd.read_table(
                    output_file,
                    skiprows=beg_piezo,
                    skipfooter=n_lines-end_piezo+span+2,
                    names=['dt', 'piezo_sim', 'piezo_obs'],
                    **options
                )
                
                df_piezo_btm = pd.read_table(
                    output_file,
                    skiprows=end_piezo-span-1,
                    skipfooter=n_lines-end_piezo,
                    names=['dt', 'piezo_sim', 'piezo_obs',
                           'piezo_frc_no-rain', 'piezo_frc_10%-dry',
                           'piezo_frc_20%-dry', 'piezo_frc_50%',
                           'piezo_frc_20%-wet', 'piezo_frc_10%-wet'],
                    **options
                )
                
                df_piezo = pd.concat([df_piezo_top, df_piezo_btm], axis=0)

                if save_outputs:
                    df_piezo.to_csv(
                        separator.join(
                            [self._working_dir, "output",
                             "piezo_sim_obs_frc.csv"]
                        ),
                        index=False
                    )

    def evaluate(
            self, variable: str, metric: str, period: str = None,
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

            period: `str`, optional
                The period to consider for the computation of the evaluation
                metric. It can either be 'calib' (only the period used for
                calibration is considered, excluding the initialisation
                period) or 'eval' (only the tail period left aside and not
                used for the calibration is considered). If not provided,
                set to default value 'calib'.

            transform: `str`, optional
                The transformation function to apply to the observations
                and the predictions before computing the metric. It can
                be 'log', 'inv', 'sqrt', 'pow'. If not provided, no
                transformation is performed.

            exponent: `float`, optional
                The exponent to use if the transform is set to 'pow',
                the power function.

        :Returns:

            `numpy.ndarray`
                The array containing the value(s) of the evaluation metric.

        **Examples**

        >>> t = GardeniaTree(
        ...     catchment='examples/my-example/config/bassin.toml',
        ...     settings='examples/my-example/config/reglages.toml'
        ... )
        >>> m = GardeniaModel(t, working_dir='examples/my-example')
        >>> m.run(save_outputs=True)
        >>> m.evaluate('streamflow', 'KGE')
        array(0.74406113)
        >>> m.evaluate('piezo_level', 'NSE', transform='sqrt')
        array(-436.91149994)
        """
        return evaluate(
            working_dir=self._working_dir, variable=variable, metric=metric,
            period=period, transform=transform, exponent=exponent
        )

    def visualise(
            self, variable: str, period: str = None, depth: int = None,
            filename: str = None, fig_size: tuple = None,
            colors: list = None, return_fig: bool = False
    ):
        """Visualise the simulations and the observations time series
        for a given variable.

        :Parameters:

            variable: `str`
                The model variable to evaluate. It can either be
                'streamflow' or 'piezo_level'.

            period: `str`, optional
                The period to consider for the visualisation. It can
                either be 'calib' (only the period used for calibration
                is considered, excluding the initialisation period) or
                'eval' (only the tail period left aside and not used for
                the calibration is considered). If not provided, set to
                default value 'calib'. Note that for a forecast run, this
                parameter is ignored.

            depth: `int`, optional
                The number of days to consider for the visualisation of
                a forecast run (including the forecast span). If not
                provided, only the forecast span is displayed. Note that
                for a simulation run, this parameter is ignored.

            filename: `str`, optional
                The file name to use for storing the visualisation. The
                file extension in the name will control the file format
                generated (e.g. *.pdf, *.png). If not provided, the
                visualisation is only shown and not saved as a file.
                
            fig_size: `tuple`, optional
                The width and the height of the figure as a tuple.
                If not provided, set to (10, 4).

            colors: `list`, optional
                The list of colors to use for displaying the different
                forecasts. It must be the name length and order as the
                forecasts (i.e. 6, no-rain 10%-dry, 20%-dry, 50%,
                20%-wet, 10%-wet). If not provided, a shade of green is
                used. Note, this parameter is only used in case of a
                forecast run.

            return_fig: `bool`, optional
                Whether to return the figure object used to generate the
                plot. If not provided, it is not returned.

        :Returns:

            `None` or `matplotlib.figure.Figure`
                The figure used to create the plot to use if further
                customisation is necessary.

        **Examples**

        >>> t = GardeniaTree(
        ...     catchment='examples/my-example/config/bassin.toml',
        ...     settings='examples/my-example/config/reglages.toml'
        ... )
        >>> m = GardeniaModel(t, working_dir='examples/my-example')
        >>> m.run(save_outputs=True)
        >>> m.visualise('streamflow', filename='my-debit.pdf')
        >>> m.visualise('piezo_level', filename='my-niveau.png')
        """
        return visualise(
            working_dir=self._working_dir, variable=variable,
            period=period, depth=depth,
            filename=filename, fig_size=fig_size, colors=colors,
            return_fig=return_fig
        )
