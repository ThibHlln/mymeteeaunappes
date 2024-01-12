import os
from glob import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def _collect_list_working_dirs(
        history_dir: str
):
    # collect list of working directories contained in history directory
    working_dirs = sorted(glob(f'{history_dir}/V*'))

    if len(working_dirs) < 1:
        raise RuntimeError(
            'no directory named V# found in history directory'
        )

    return working_dirs


def _collect_simulation_history(
        var: str,
        history_dir: str
) -> pd.DataFrame:
    # collect list of working directories contained in history directory
    working_dirs = _collect_list_working_dirs(history_dir)

    # collect all time series
    df = pd.read_csv(
        f"{working_dirs[0]}/output/{var}_sim_obs.csv",
        parse_dates=['dt']
    )
    df = df.set_index('dt')
    df = df[[f'{var}_obs', f'{var}_sim']]
    df = df.rename(columns={f'{var}_sim': f'{var}_sim_V0'})

    for i, working_dir in enumerate(working_dirs[1:]):
        df_ = pd.read_csv(
            f"{working_dir}/output/{var}_sim_obs.csv",
            parse_dates=['dt']
        )
        df_ = df_.set_index('dt')
        df_ = df_[[f'{var}_sim']]
        df_.columns = [f'{var}_sim_V{i + 1}']

        df = pd.concat([df, df_], axis=1)

    df = df.reset_index(drop=False, names='dt')

    return df


def plot_simulation_history(
        variable: str,
        history_dir: str,
        plot_filename: str = None,
        fig_size: tuple = None
) -> None:
    """Plot the evolution of the simulation time series for a given
    variable between the different version iterations.

    :Parameters:

        variable: `str`
            The model variable to display. It can either be
            'streamflow' or 'piezo_level'.

        history_dir: `str`
            The path to the history directory containing a collection
            of subdirectories that are independent working directories
            (i.e. they follow the config/data/output internal structure).
            The working directories must be named following the convention
            V#, where # is a number starting from 0, and going with
            integer increments.

            See below the structure and naming conventions that the
            history directory must follow:

                <history_dir>
                ├── V0
                │   ├── config
                │   ├── data
                │   └── output
                ├── V1
                │   ├── config
                │   ├── data
                │   └── output
                ┆   ···
                └── VN
                    ├── config
                    ├── data
                    └── output

        plot_filename: `str`, optional
            The file name to use for storing the visualisation at the
            root of the history directory. The file extension in the
            name will control the file format generated (e.g. *.pdf,
            *.png). If not provided, the visualisation is only shown
            and not saved as a file.

        fig_size: `tuple`, optional
            The width and the height of the figure as a tuple.
            If not provided, set to (10, 4).

    :Returns:

        `None`
    """
    # check variable value
    if variable not in ['streamflow', 'piezo_level']:
        raise ValueError(f"{repr(variable)} is not supported")

    # map variable value to shortname
    var = 'river' if variable == 'streamflow' else 'piezo'

    # collect all time series
    df = _collect_simulation_history(var, history_dir)

    # initialise figure
    fig, ax = plt.subplots(
        figsize=fig_size if fig_size else (10, 4)
    )

    # plot observations time series
    ax.plot(
        df['dt'], df[f'{var}_obs'], label='obs',
        marker='+', markersize=1.5, linestyle='-', color='black'
    )

    # plot simulations time series
    n_sim = df.shape[1] - 2

    alphas = np.linspace(start=0.2, stop=1, num=n_sim)

    for i in range(n_sim):
        ax.plot(
            df['dt'], df[f'{var}_sim_V{i}'], label=f'sim V{i}', linestyle='-',
            color='tab:blue' if variable == 'streamflow' else 'tab:purple',
            alpha=alphas[i]
        )

    ax.set_ylabel(
        r'streamflow [m$^3$.s$^{-1}$]' if variable == 'streamflow'
        else f'piezometric level [m NGF]'
    )

    plt.legend(frameon=False)

    # save or show
    if plot_filename is not None:
        fig.savefig(
            os.sep.join([history_dir, "output", plot_filename])
        )
    else:
        plt.show()


def _collect_prn_history(
        history_dir: str, filename: str,
        skip_top: int, skip_bottom: int,
        skip_left: int, skip_right: int,
        header: int | list

):
    # collect list of working directories contained in history directory
    working_dirs = _collect_list_working_dirs(history_dir)

    # collect all performances
    df = pd.read_table(
        f"{working_dirs[0]}/output/{filename}",
        delimiter='\t', encoding='cp1252',
        header=header, skiprows=skip_top, skipfooter=skip_bottom,
        engine='python'
    )
    df = df.iloc[:, skip_left:-skip_right]
    df.index = ['V0']

    for i, working_dir in enumerate(working_dirs[1:]):
        df_ = pd.read_table(
            f"{working_dir}/output/{filename}",
            delimiter='\t', encoding='cp1252',
            header=header, skiprows=skip_top, skipfooter=skip_bottom,
            engine='python'
        )
        df_ = df_.iloc[:, skip_left:-skip_right]
        df_.index = [f'V{i + 1}']

        df = pd.concat([df, df_], axis=0)

    return df


def collect_performance_history(
        history_dir: str
) -> pd.DataFrame:
    """Gather the evolution of the simulation performances between the
    different version iterations.

    :Parameters:

        history_dir: `str`
            The path to the history directory containing a collection
            of subdirectories that are independent working directories
            (i.e. they follow the config/data/output internal structure).
            The working directories must be named following the convention
            V#, where # is a number starting from 0, and going with
            integer increments.

            See below the structure and naming conventions that the
            history directory must follow:

                <history_dir>
                ├── V0
                │   ├── config
                │   ├── data
                │   └── output
                ├── V1
                │   ├── config
                │   ├── data
                │   └── output
                ┆   ···
                └── VN
                    ├── config
                    ├── data
                    └── output

    :Returns:

        `pd.DataFrame`
            The dataframe containing the history of performance values.
    """
    return _collect_prn_history(
        history_dir=history_dir, filename='tabl_criter.prn',
        header=0, skip_top=2, skip_bottom=40, skip_left=1, skip_right=2
    )


def collect_parameters_history(
        history_dir: str
) -> pd.DataFrame:
    """Gather the evolution of the model parameter values between the
    different version iterations.

    :Parameters:

        history_dir: `str`
            The path to the history directory containing a collection
            of subdirectories that are independent working directories
            (i.e. they follow the config/data/output internal structure).
            The working directories must be named following the convention
            V#, where # is a number starting from 0, and going with
            integer increments.

            See below the structure and naming conventions that the
            history directory must follow:

                <history_dir>
                ├── V0
                │   ├── config
                │   ├── data
                │   └── output
                ├── V1
                │   ├── config
                │   ├── data
                │   └── output
                ┆   ···
                └── VN
                    ├── config
                    ├── data
                    └── output

    :Returns:

        `pd.DataFrame`
            The dataframe containing the history of model parameter values.
    """
    return _collect_prn_history(
        history_dir=history_dir, filename='tabl_param.prn',
        header=[0, 1], skip_top=2, skip_bottom=24, skip_left=1, skip_right=2
    )
