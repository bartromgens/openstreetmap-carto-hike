import logging
import subprocess


def main():
    logging.basicConfig(level=logging.INFO)
    srtm_filepath = "/tmp/srtm_30m.tif"
    contour_dir = "/tmp/srtm_30m_contours_10m"
    download_elevation_data(srtm_filepath)
    generate_contours(srtm_filepath, contour_dir)
    insert_contours_into_db(contour_dir)


def download_elevation_data(filepath):
    logging.info('download_elevation_data')
    command = [
        "eio", "clip",
        "-o", filepath,
        "--bounds", "7.6", "46.4", "7.9", "46.8"  # TODO: get bounds from input args
    ]
    subprocess.run(command)
    logging.info('download_elevation_data done')


def generate_contours(srtm_filepath, output_dir):
    logging.info('generate_contours')
    command = [
        "gdal_contour", "-i", "10", "-a", "height", srtm_filepath, output_dir
    ]
    subprocess.run(command)
    logging.info('generate_contours done')


def insert_contours_into_db(contour_dir):
    logging.info('insert_contours_into_db')
    command = [
        "shp2pgsql",
        "-p",
        "-I",
        "-g", "way",
        "-s", "4326:900913",
        "contour.shp", "contour",
    ]
    ps = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=contour_dir)
    command = [
        "psql",
        "-d", "gis"
    ]
    subprocess.check_output(command, stdin=ps.stdout)
    ps.wait()

    command = [
        "shp2pgsql",
        "-a",
        "-g", "way",
        "-s", "4326:900913",
        "contour.shp", "contour",
    ]
    ps = subprocess.Popen(command, stdout=subprocess.PIPE, cwd=contour_dir)
    command = [
        "psql",
        "-d", "gis"
    ]
    subprocess.check_output(command, stdin=ps.stdout)
    ps.wait()
    logging.info('insert_contours_into_db done')


if __name__ == '__main__':
    main()
