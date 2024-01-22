import os
import matplotlib.pyplot as plt
import pandas as pd
import evalhyd

from .configure import GardeniaTree


def _trim_output_of_spin_up(df: pd.DataFrame, tree: GardeniaTree):
    # retrieve length of spin up run
    spin_up = int(
        tree['basin_settings']['model']
        ['initialisation']['spinup']['n_years']
    )

    # subset in time to exclude spin up period
    df = df[
        df['dt'] >= (
                df['dt'].iloc[0] + pd.offsets.DateOffset(years=spin_up)
        )
    ]

    return df


def _select_calib_or_eval_period(
        df: pd.DataFrame, tree: GardeniaTree, period: str = 'calib'
):
    # retrieve length of evaluation period
    evaluation = int(
        tree['basin_settings']['model']
        ['calibration']['n_tail_years_to_trim']
    )

    if (period == 'eval') and (evaluation == 0):
        raise RuntimeError(
            "no data kept aside for an evaluation period"
        )

    # subset in time to exclude spin up period
    if evaluation >= 0:
        # it is a number of years that is provided (e.g. 5)
        swap_date = (
            df['dt'].iloc[-1] - pd.offsets.DateOffset(years=evaluation)
        )
    else:
        # it is a year that is provided (e.g. -2024)
        swap_date = (
            pd.to_datetime(f'{-evaluation}-12-31')
        )

    if period == 'calib':
        df = df[df['dt'] <= swap_date]
    elif period == 'eval':
        df = df[df['dt'] > swap_date]
    else:
        raise ValueError(
            f"period {repr(period)} is not valid, "
            f"it must either be 'calib' or 'eval'"
        )

    return df


def _select_forecast_period(
        df: pd.DataFrame, span: int, depth: int = None
):
    # subset in time to keep only forecast period or given depth
    df = df[
        df['dt'] > df['dt'].iloc[-1] - pd.offsets.DateOffset(
            days=depth if depth else span + 1
        )
    ]

    return df


def evaluate(
        working_dir: str, variable: str, metric: str, period: str = None,
        transform: str = None, exponent: float = None
):
    """ Evaluate the performance between the simulations and the
    observations for a given variable.

    :Parameters:

        working_dir: `str`
            The path to the directory containing the subdirectories
            *config* and *output* (containing the simulation output).

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
    if variable not in ['streamflow', 'piezo_level']:
        raise ValueError(f"{repr(variable)} is not supported")

    prefix = 'river' if variable == 'streamflow' else 'piezo'

    auto_toml = os.sep.join([working_dir, 'config', 'auto.toml'])

    tree = GardeniaTree(catchment=auto_toml, settings=auto_toml)

    # collect relevant variable
    df = pd.read_csv(
        os.sep.join([working_dir, 'output', f'{prefix}_sim_obs.csv']),
        parse_dates=['dt']
    )

    # subset in time to exclude spin up period
    df = _trim_output_of_spin_up(df, tree)

    # choose between the calibration period
    # and a potential evaluation period
    df = _select_calib_or_eval_period(
        df, tree, period=(period if period else 'calib')
    )

    # returned evaluation metric value
    prefix = 'river' if variable == 'streamflow' else 'piezo'

    return evalhyd.evald(
        q_obs=df[f'{prefix}_obs'].values,
        q_prd=df[f'{prefix}_sim'].values,
        metrics=[metric],
        transform=transform, exponent=exponent
    )[0].squeeze()


def visualise(
        working_dir: str, variable: str, period: str = None,
        depth: int = None, filename: str = None,
        fig_size: tuple = None, return_fig: bool = False
):
    """Visualise the simulations and the observations time series
    for a given variable.

    :Parameters:

        working_dir: `str`
            The path to the directory containing the subdirectories
            *config* and *output* (containing the simulation output).

        variable: `str`
            The model variable to evaluate. It can either be
            'streamflow' or 'piezo_level'.

        period: `str`, optional
            The period to consider for the visualisation. It can either
            be 'calib' (only the period used for calibration is considered,
            excluding the initialisation period) or 'eval' (only the tail
            period left aside and not used for the calibration is considered).
            If not provided, set to default value 'calib'. Note that for a
            forecast run, this parameter is ignored.

        depth: `int`, optional
            The number of days to consider for the visualisation of a
            forecast run (including the forecast span). If not provided,
            only the forecast span is displayed. Note that for a simulation
            run, this parameter is ignored.

        filename: `str`, optional
            The file name to use for storing the visualisation. The
            file extension in the name will control the file format
            generated (e.g. *.pdf, *.png). If not provided, the
            visualisation is only shown and not saved as a file.

        fig_size: `tuple`, optional
            The width and the height of the figure as a tuple.
            If not provided, set to (10, 4).

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
    if variable not in ['streamflow', 'piezo_level']:
        raise ValueError(f"{repr(variable)} is not supported")

    prefix = 'river' if variable == 'streamflow' else 'piezo'

    auto_toml = os.sep.join([working_dir, 'config', 'auto.toml'])

    tree = GardeniaTree(catchment=auto_toml, settings=auto_toml)

    if not bool(int(tree['general_settings']['forecast_run'])):
        # in simulation mode
        # collect relevant variable
        df = pd.read_csv(
            os.sep.join([working_dir, 'output', f'{prefix}_sim_obs.csv']),
            parse_dates=['dt']
        )

        # subset in time to exclude spin up period
        df = _trim_output_of_spin_up(df, tree)

        # choose between the calibration period
        # and a potential evaluation period
        df = _select_calib_or_eval_period(
            df, tree, period=(period if period else 'calib')
        )

        # generate plot
        fig, ax = plt.subplots(
            figsize=fig_size if fig_size else (10, 4)
        )

        ax.plot(
            df['dt'], df[f'{prefix}_obs'], label='observed',
            marker='+', markersize=1.5, linestyle='-',
            color='black'
        )
        ax.plot(
            df['dt'], df[f'{prefix}_sim'], label='simulated',
            color='tab:blue' if variable == 'streamflow' else 'tab:purple'
        )

        ax.set_xlabel('time')

        ax.set_ylabel(
            r'streamflow [m$^3$.s$^{-1}$]' if variable == 'streamflow'
            else f'piezometric level [m NGF]'
        )

        ax.legend(frameon=False)
    else:
        # in forecast mode
        # collect relevant variable
        df = pd.read_csv(
            os.sep.join([working_dir, 'output', f'{prefix}_sim_obs_frc.csv']),
            parse_dates=['dt']
        )

        # subset in time
        span = int(tree['basin_settings']['time']['forecast']['span'])

        df = _select_forecast_period(df, span, depth)

        # choose between the calibration period
        # and a potential evaluation period
        df = _select_calib_or_eval_period(
            df, tree, period=(period if period else 'calib')
        )

        # generate plot
        fig, ax = plt.subplots(
            figsize=fig_size if fig_size else (10, 4)
        )

        ax.plot(
            df['dt'], df[f'{prefix}_obs'], label='observed',
            marker='+', markersize=1.5, linestyle='-',
            color='black'
        )

        if depth:
            if depth > span:
                ax.plot(
                    df['dt'], df[f'{prefix}_sim'], label='simulated',
                    color=(
                        'tab:blue' if variable == 'streamflow'
                        else 'tab:purple'
                    )
                )

        colors = plt.get_cmap('Greens', 7)

        for i, scn in enumerate(
                ['no-rain', '10%-dry', '20%-dry', '50%', '20%-wet', '10%-wet'],
                start=1
        ):
            ax.plot(
                df['dt'], df[f'{prefix}_frc_{scn}'], label=f'forecast {scn}',
                color=colors(i)
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
            os.sep.join([working_dir, "output", filename])
        )
    else:
        plt.show()

    plt.close()

    # optionally return the figure
    if return_fig:
        return fig
