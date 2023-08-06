import os

from concurrent.futures import ProcessPoolExecutor

from .loadump import ensure_dir
from .loadump import i_walk_dir_for_filepaths_names
from .loadump import i_get_csv_data
from .loadump import write_as_csv


def csv_file_to_file(csv_rows_consumer, out_prefix, out_dir, file_path_name):
    """
    Consume the file at file_path_name as a csv file, passing
    it through csv_rows_consumer, writing the results
    as a csv file into out_dir as the same name, lowered, and prefixed.

    :param csv_rows_consumer: consumes data_items yielding collection for each
    :param out_prefix: :class: `str` prefix out_file_name
    :param out_dir: :class: `str` directory to write output file to
    :param file_path_name: :class: `str` path to input csv file
    """
    data_path, data_file_name = file_path_name
    data_items = i_get_csv_data(data_path)
    ensure_dir(out_dir)
    out_filename = os.path.join(
        out_dir, '{}{}'.format(
            out_prefix, data_file_name.lower()))
    write_as_csv(csv_rows_consumer(data_items), out_filename)


def pool_run_files_to_files(file_to_file, in_dir):
    """
    With a multi-process pool, map files in in_dir over
    file_to_file function.

    :param file_to_file: callable that takes file paths.
    :param in_dir: path to process all files from
    """
    results = i_walk_dir_for_filepaths_names(in_dir)

    with ProcessPoolExecutor() as pool:
        list(pool.map(file_to_file, results))
