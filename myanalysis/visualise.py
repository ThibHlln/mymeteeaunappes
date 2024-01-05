import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_time_series(
        working_dir: str,
        rainfall_filename: str = None,
        pet_filename: str = None,
        streamflow_filename: str = None,
        piezo_level_filename: str = None,
        fig_size: tuple = None,
        start: str = None,
        end: str = None,
        rainfall_summary: str = None,
        pet_summary: str = None,
        plot_filename: str = None
) -> None:
    # read in the data time series as dataframes
    csv_read_params = dict(
        delimiter='\t', parse_dates=['Date'], date_format='%d/%m/%Y'
    )

    df_rainfall = None
    if rainfall_filename is not None:
        df_rainfall = pd.read_csv(
            os.sep.join([working_dir, 'data', rainfall_filename]),
            **csv_read_params
        )

    df_pet = None
    if pet_filename is not None:
        df_pet = pd.read_csv(
            os.sep.join([working_dir, 'data', pet_filename]),
            **csv_read_params
        )

    df_streamflow = None
    if streamflow_filename is not None:
        df_streamflow = pd.read_csv(
            os.sep.join([working_dir, 'data', streamflow_filename]),
            **csv_read_params
        )
        # deal with missing values
        df_streamflow.loc[df_streamflow['Debit'] == -2, 'Debit'] = np.nan

    df_piezo_level = None
    if piezo_level_filename is not None:
        df_piezo_level = pd.read_csv(
            os.sep.join([working_dir, 'data', piezo_level_filename]),
            **csv_read_params
        )
        # deal with missing values
        df_piezo_level.loc[df_piezo_level['Niveau'] == 9999, 'Niveau'] = np.nan

    # determine common start and end for time series
    df = (
        df_rainfall if df_rainfall is not None
        else df_pet if df_pet is not None
        else df_streamflow if df_streamflow is not None
        else df_piezo_level
    )
    if df is not None:
        start = (
            df['Date'].iloc[0] if (start is None)
            else pd.to_datetime(start)
        )
        end = (
            df['Date'].iloc[-1] if (end is None)
            else pd.to_datetime(end)
        )
    else:
        raise RuntimeError('no data provided, nothing to plot')

    # set up the plot
    fig = plt.figure(
        figsize=fig_size if fig_size else (10, 4),
        layout="constrained"
    )
    spec = fig.add_gridspec(ncols=1, nrows=100)

    ax0 = fig.add_subplot(spec[:25, 0])
    ax1 = fig.add_subplot(spec[25:75, 0])
    ax2 = fig.add_subplot(spec[75:, 0])

    # plot
    if df_rainfall is not None:
        if rainfall_summary:
            # compute summarised data at given frequency
            df_rainfall_summary = df_rainfall.groupby(
                pd.Grouper(key='Date', freq=rainfall_summary)
            ).sum().reset_index()

            ax0b = ax0.twinx()

            intervals = df_rainfall_summary['Date'].diff()
            intervals[0] = (
                    df_rainfall_summary['Date'].values[0]
                    - df_rainfall['Date'].values[0]
            )

            ax0b.bar(
                df_rainfall_summary['Date'], df_rainfall_summary['Pluie'],
                color='tab:cyan', alpha=0.2, width=-intervals, align='edge'
            )

            ax0b.invert_yaxis()
            ax0b.set_xlim(start, end)
            ax0b.set_ylabel(
                'Σ Pluie\n[mm]', color='tab:cyan', alpha=0.3,
                rotation=270, verticalalignment='bottom'
            )

        df_rainfall = (
            df_rainfall.loc[df_rainfall['Date'].between(start, end)]
        )

        ax0.bar(
            df_rainfall['Date'], df_rainfall['Pluie'],
            color='tab:cyan', width=pd.Timedelta(days=1)
        )

    ax0.invert_yaxis()
    ax0.set_xlim(start, end)
    ax0.set_ylabel('Pluie\n[mm]', color='tab:cyan')
    ax0.set_xticklabels([])

    if df_streamflow is not None:
        df_streamflow = (
            df_streamflow.loc[df_streamflow['Date'].between(start, end)]
        )
        ax1.plot(
            df_streamflow['Date'], df_streamflow['Debit'],
            marker='+', markersize=1.5, color='tab:blue'
        )
    ax1.set_xlim(start, end)
    ax1.set_ylabel('Débit\n[m$^{3}$.s$^{-1}$]', color='tab:blue')
    ax1.set_xticklabels([])

    ax1b = ax1.twinx()
    if df_piezo_level is not None:
        df_piezo_level = (
            df_piezo_level.loc[df_piezo_level['Date'].between(start, end)]
        )

        ax1b.plot(
            df_piezo_level['Date'], df_piezo_level['Niveau'],
            marker='+', markersize=1.5, color='tab:purple'
        )
    ax1b.set_xlim(start, end)
    ax1b.set_ylabel(
        'Niveau\n[m NGF]', color='tab:purple',
        rotation=270, verticalalignment='bottom'
    )

    if df_pet is not None:
        if pet_summary:
            # compute summarised data at given frequency
            df_pet_summary = df_pet.groupby(
                pd.Grouper(key='Date', freq=pet_summary)
            ).sum().reset_index()

            ax2b = ax2.twinx()

            intervals = df_pet_summary['Date'].diff()
            intervals[0] = (
                    df_pet_summary['Date'].values[0]
                    - df_pet['Date'].values[0]
            )

            ax2b.bar(
                df_pet_summary['Date'], df_pet_summary['ETP'],
                color='tab:pink', alpha=0.2, width=-intervals, align='edge'
            )

            ax2b.set_xlim(start, end)
            ax2b.set_ylabel(
                'Σ ETP\n[mm]', color='tab:pink', alpha=0.3,
                rotation=270, verticalalignment='bottom'
            )
        
        df_pet = (
            df_pet.loc[df_pet['Date'].between(start, end)]
        )
        ax2.bar(
            df_pet['Date'], df_pet['ETP'],
            color='tab:pink', width=pd.Timedelta(days=1)
        )
    ax2.set_xlim(start, end)
    ax2.set_ylabel('ETP\n[mm]', color='tab:pink')

    # save or show
    if plot_filename is not None:
        fig.savefig(
            os.sep.join([working_dir, "output", plot_filename])
        )
    else:
        plt.show()
