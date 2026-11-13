import csv
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import skipUnless

from django.test import SimpleTestCase
from pyproj.transformer import TransformerGroup

from disturbance.components.proposals.models import Proposal


@skipUnless(shutil.which('ogr2ogr'), 'ogr2ogr is required')
class ShapefileSrsTests(SimpleTestCase):
    def convert_shapefile(self, source_crs, point):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            csv_path = path / 'input.csv'
            shp_path = path / 'input.shp'
            x, y = point
            with csv_path.open('w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['WKT', 'id'])
                writer.writerow([
                    f'POLYGON(({x} {y},{x + 0.001} {y},{x + 0.001} {y + 0.001},{x} {y}))',
                    1,
                ])
            subprocess.run(
                ['ogr2ogr', '-f', 'ESRI Shapefile', '-a_srs', f'EPSG:{source_crs}',
                 str(shp_path), str(csv_path), '-oo', 'GEOM_POSSIBLE_NAMES=WKT'],
                check=True, capture_output=True,
            )
            args = Proposal._shapefile_srs_args(str(shp_path))
            result = subprocess.run(
                ['ogr2ogr', *args, '-f', 'GeoJSON', '/vsistdout/', str(shp_path)],
                check=True, capture_output=True,
            )
            return args, json.loads(result.stdout)

    def test_gda94_output_crs_and_coordinate_order(self):
        cases = [
            (28350, (688530.153167, 6315362.967412)),
            (28351, (688530.153167, 6315362.967412)),
            (4283, (119.0, -33.0)),
        ]
        for source_crs, point in cases:
            with self.subTest(source_crs=source_crs):
                args, geojson = self.convert_shapefile(source_crs, point)
                self.assertEqual(args[:3], ['-t_srs', 'EPSG:4326', '-ct'])
                self.assertEqual(
                    geojson['crs']['properties']['name'],
                    'urn:ogc:def:crs:OGC:1.3:CRS84',
                )
                transformer = next(
                    transformer for transformer in TransformerGroup(
                        source_crs, 4326, always_xy=True,
                    ).transformers
                    if transformer.description == 'GDA94 to WGS 84 (2)'
                    or any(op.name == 'GDA94 to WGS 84 (2)' for op in transformer.operations)
                )
                expected_lon, expected_lat = transformer.transform(*point)
                lon, lat = geojson['features'][0]['geometry']['coordinates'][0][0]
                self.assertAlmostEqual(lon, expected_lon, places=9)
                self.assertAlmostEqual(lat, expected_lat, places=9)
                if source_crs == 28350:
                    self.assertAlmostEqual(lon, 119.0245425889661, places=9)
                    self.assertAlmostEqual(lat, -33.28431749835277, places=9)

    def test_non_gda94_keeps_default_target(self):
        args, geojson = self.convert_shapefile(7850, (688530.153167, 6315362.967412))
        self.assertEqual(args, ['-t_srs', 'EPSG:4326'])
        self.assertEqual(
            geojson['crs']['properties']['name'],
            'urn:ogc:def:crs:OGC:1.3:CRS84',
        )
