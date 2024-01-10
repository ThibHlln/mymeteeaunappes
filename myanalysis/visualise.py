import os
import matplotlib.pyplot as plt
import pandas as pd

from ._read import read_prn_file


def plot_time_series(
        working_dir: str,
        rainfall_filename: str = None,
        pet_filename: str = None,
        streamflow_filename: str = None,
        piezo_level_filename: str = None,
        plot_filename: str = None,
        rainfall_info: str = None,
        pet_info: str = None,
        streamflow_info: str = None,
        piezo_level_info: str = None,
        fig_size: tuple = None,
        start: str = None,
        end: str = None,
        rainfall_secondary_frequency: str = None,
        pet_secondary_frequency: str = None
) -> None:
    """Plot the observations time series against one another in a single
    figure.

    :Parameters:

        working_dir: `str`
            The file path the working directory where the data is stored
            in the 'data' subdirectory.

        rainfall_filename: `str`, optional
            The name of the file containing the rainfall data. If not
            provided, no rainfall data will be plotted.

        pet_filename: `str`, optional
            The name of the file containing the potential evapotranspiration
            data. If not provided, no potential evapotranspiration data
            will be plotted.

        streamflow_filename: `str`, optional
            The name of the file containing the streamflow data. If not
            provided, no streamflow data will be plotted.

        piezo_level_filename: `str`, optional
            The name of the file containing the piezometric level data.
            If not provided, no potential evapotranspiration data will
            be plotted.

        plot_filename: `str`, optional
            The file name to use for storing the visualisation in the
            'output' subdirectory. The file extension in the name will
            control the file format generated (e.g. *.pdf, *.png). If
            not provided, the visualisation is only shown and not saved
            as a file.

        rainfall_info: `str`, optional
            Information specific about the rainfall data to display
            as comment at the top of the plot. If not provided,
            nothing is displayed for the rainfall data.

        pet_info: `str`, optional
            Information specific about the potential evapotranspiration
            data to display as comment at the top of the plot. If not
            provided, nothing is displayed for the potential
            evapotranspiration data.

        streamflow_info: `str`, optional
            Information specific about the streamflow data to display
            as comment at the top of the plot. If not provided,
            nothing is displayed for the streamflow data.

        piezo_level_info: `str`, optional
            Information specific about the piezometric level data
            to display as comment at the top of the plot. If not
            provided, nothing is displayed for the potential
            evapotranspiration data.

        fig_size: `tuple`, optional
            The width and the height of the figure as a tuple.
            If not provided, set to (10, 4).

        start: `str`, optional
            The start date to use for the temporal axis of the plot. The
            date must be specified in a string following the ISO 8601-1:2019
            standard, i.e. “YYYY-MM-DD” (e.g. the 21st of May 2007 is
            “2007-05-21”). If not provided, the earliest date in the
            available data is used.

        end: `str`, optional
            The end date to use for the temporal axis of the plot. The
            date must be specified in a string following the ISO 8601-1:2019
            standard, i.e. “YYYY-MM-DD” (e.g. the 21st of May 2007 is
            “2007-05-21”). If not provided, the earliest date in the
            available data is used.

        rainfall_secondary_frequency: `str`, optional
            Another frequency (in addition to the daily frequency)
            to display on a secondary axis of the rainfall plot.
            For example, it can be 'A-JUL' (i.e. annual ending at the
            end of July = hydrogeological year), 'A-SEP' (i.e. annual
            ending at the end of September = hydrological year),
            'A' (i.e. annual = calendar year), 'M' (i.e. monthly), etc.
            If not provided, no secondary plot is displayed.

        pet_secondary_frequency: `str`, optional
            Another frequency (in addition to the daily frequency)
            to display on a secondary axis of the potential evapotranspiration
            plot. For example, it can be 'A-JUL' (i.e. annual ending at the
            end of July = hydrogeological year), 'A-SEP' (i.e. annual
            ending at the end of September = hydrological year),
            'A' (i.e. annual = calendar year), 'M' (i.e. monthly), etc.
            If not provided, no secondary plot is displayed.

    :Returns:

        `None`
    """

    # read in the data time series as dataframes
    df_rainfall = None
    if rainfall_filename is not None:
        df_rainfall = read_prn_file(
            working_dir, rainfall_filename, 'Pluie', None
        )

    df_pet = None
    if pet_filename is not None:
        df_pet = read_prn_file(
            working_dir, pet_filename, 'ETP', None
        )

    df_streamflow = None
    if streamflow_filename is not None:
        df_streamflow = read_prn_file(
            working_dir, streamflow_filename, 'Debit', -2
        )

    df_piezo_level = None
    if piezo_level_filename is not None:
        df_piezo_level = read_prn_file(
            working_dir, piezo_level_filename, 'Niveau', 9999
        )

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
        if rainfall_secondary_frequency:
            # compute summarised data at given frequency
            df_rainfall_summary = df_rainfall.groupby(
                pd.Grouper(key='Date', freq=rainfall_secondary_frequency)
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
        if pet_secondary_frequency:
            # compute summarised data at given frequency
            df_pet_summary = df_pet.groupby(
                pd.Grouper(key='Date', freq=pet_secondary_frequency)
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

    # optionally add supplementary information about data
    fig.suptitle(
        "; ".join(
            [
                f"{v}: {i}" for v, i in {
                    'Pluie': rainfall_info,
                    'ETP': pet_info,
                    'Débit': streamflow_info,
                    'Niveau': piezo_level_info,
                }.items() if i is not None
            ]
        ),
        fontsize='medium', fontstyle='italic'
    )

    # save or show
    if plot_filename is not None:
        fig.savefig(
            os.sep.join([working_dir, "output", plot_filename])
        )
    else:
        plt.show()
