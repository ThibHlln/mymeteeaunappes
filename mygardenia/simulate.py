import subprocess
import os
import re
import glob
import pandas as pd

from .convert import (
    convert_to_rga_content, convert_to_gar_content
)


class GardeniaModel(object):

    def __init__(self, tree, working_dir):
        self._tree = tree
        self._working_dir = working_dir

    def run(self, verbose=False):
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
                rga_file, 'M'
            ],
            cwd=self._working_dir,
            stdout=subprocess.PIPE
        ).stdout.decode('windows-1252')

        if verbose:
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
            df_river.to_csv(
                separator.join([self._working_dir, "output", "river_sim_obs.csv"]),
                index=False
            )

        if beg_piezo and end_piezo:
            df_piezo = pd.read_table(
                output_file,
                skiprows=beg_piezo, skipfooter=n_lines-end_piezo,
                names=['dt', 'piezo_sim', 'piezo_obs'],
                **options
            )
            df_piezo.to_csv(
                separator.join([self._working_dir, "output", "piezo_sim_obs.csv"]),
                index=False
            )
