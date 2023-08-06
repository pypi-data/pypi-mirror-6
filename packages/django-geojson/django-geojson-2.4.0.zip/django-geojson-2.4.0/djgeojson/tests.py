import json

from django.test import TestCase
from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError
from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString, Point, GeometryCollection
from django.utils.encoding import smart_text

from .templatetags.geojson_tags import geojsonfeature
from .serializers import Serializer
from .views import GeoJSONLayerView
from .fields import GeoJSONField, GeoJSONFormField, geojson_geometry


settings.SERIALIZATION_MODULES = {'geojson': 'djgeojson.serializers'}


class PictureMixin(object):

    @property
    def picture(self):
        return 'image.png'


class Route(PictureMixin, models.Model):
    name = models.CharField(max_length=20)
    geom = models.LineStringField(spatial_index=False, srid=4326)
    countries = models.ManyToManyField('Country')

    def natural_key(self):
        return self.name

    @property
    def upper_name(self):
        return self.name.upper()

    objects = models.GeoManager()


class Sign(models.Model):
    label = models.CharField(max_length=20)
    route = models.ForeignKey(Route, related_name='signs')

    def natural_key(self):
        return self.label

    @property
    def geom(self):
        return self.route.geom.centroid


class Country(models.Model):
    label = models.CharField(max_length=20)
    geom = models.PolygonField(spatial_index=False, srid=4326)
    objects = models.GeoManager()

    def natural_key(self):
        return self.label


class GeoJsonDeSerializerTest(TestCase):

    def test_basic(self):
        input_geojson = """
        {"type": "FeatureCollection",
         "features": [
            { "type": "Feature",
                "properties": {"model": "djgeojson.route", "name": "green", "upper_name": "RED"},
                "id": 1,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [0.0, 0.0],
                        [1.0, 1.0]
                    ]
                }
            },
            { "type": "Feature",
                "properties": {"model": "djgeojson.route", "name": "blue"},
                "id": 2,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [0.0, 0.0],
                        [1.0, 1.0]
                    ]
                }
            }
        ]}"""

        # Deserialize into a list of objects
        objects = list(serializers.deserialize('geojson', input_geojson))

        # Were three objects deserialized?
        self.assertEqual(len(objects), 2)

        # Did the objects deserialize correctly?
        self.assertEqual(objects[1].object.name, "blue")
        self.assertEqual(objects[0].object.upper_name, "GREEN")
        self.assertEqual(objects[0].object.geom,
                         LineString((0.0, 0.0), (1.0, 1.0)))

    def test_with_model_name_passed_as_argument(self):
        input_geojson = """
        {"type": "FeatureCollection",
         "features": [
            { "type": "Feature",
                "properties": {"name": "bleh"},
                "id": 24,
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [1, 2],
                        [42, 3]
                    ]
                }
            }
        ]}"""

        my_object = list(serializers.deserialize(
            'geojson', input_geojson, model_name='djgeojson.route'))[0].object

        self.assertEqual(my_object.name, "bleh")


class GeoJsonSerializerTest(TestCase):

    def test_basic(self):
        # Stuff to serialize
        route1 = Route.objects.create(
            name='green', geom="LINESTRING (0 0, 1 1)")
        route2 = Route.objects.create(
            name='blue', geom="LINESTRING (0 0, 1 1)")
        route3 = Route.objects.create(name='red', geom="LINESTRING (0 0, 1 1)")

        actual_geojson = json.loads(serializers.serialize(
            'geojson', Route.objects.all(), properties=['name']))
        self.assertEqual(
            actual_geojson, {"crs": {"type": "link", "properties": {"href": "http://spatialreference.org/ref/epsg/4326/", "type": "proj4"}}, "type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "name": "green"}, "id": route1.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "name": "blue"}, "id": route2.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "name": "red"}, "id": route3.pk}]})
        actual_geojson_with_prop = json.loads(
            serializers.serialize(
                'geojson', Route.objects.all(),
                properties=['name', 'upper_name', 'picture']))
        self.assertEqual(actual_geojson_with_prop,
                         {"crs": {"type": "link", "properties": {"href": "http://spatialreference.org/ref/epsg/4326/", "type": "proj4"}}, "type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"picture": "image.png", "model": "djgeojson.route", "upper_name": "GREEN", "name": "green"}, "id": route1.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"picture": "image.png", "model": "djgeojson.route", "upper_name": "BLUE", "name": "blue"}, "id": route2.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"picture": "image.png", "model": "djgeojson.route", "upper_name": "RED", "name": "red"}, "id": route3.pk}]})

    def test_precision(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(
            [{'geom': 'SRID=2154;POINT (1 1)'}], precision=2, crs=False))
        self.assertEqual(
            features, {"type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [-1.36, -5.98]}, "type": "Feature", "properties": {}}]})

    def test_simplify(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(
            [{'geom': 'SRID=4326;LINESTRING (1 1, 1.5 1, 2 3, 3 3)'}], simplify=0.5, crs=False))
        self.assertEqual(
            features, {"type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[1.0, 1.0], [2.0, 3.0], [3.0, 3.0]]}, "type": "Feature", "properties": {}}]})

    def test_force2d(self):
        serializer = Serializer()
        features2d = json.loads(serializer.serialize(
            [{'geom': 'SRID=4326;POINT Z (1 2 3)'}],
            force2d=True, crs=False))
        self.assertEqual(
            features2d, {"type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [1.0, 2.0]}, "type": "Feature", "properties": {}}]})

    def test_pk_property(self):
        route = Route.objects.create(name='red', geom="LINESTRING (0 0, 1 1)")
        serializer = Serializer()
        features2d = json.loads(serializer.serialize(
            Route.objects.all(), properties=['id'], crs=False))
        self.assertEqual(
            features2d, {"type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "id": route.pk}, "id": route.pk}]})

    def test_geometry_property(self):
        class Basket(models.Model):

            @property
            def geom(self):
                return GeometryCollection(LineString((3, 4, 5), (6, 7, 8)), Point(1, 2, 3), srid=4326)

        serializer = Serializer()
        features = json.loads(
            serializer.serialize([Basket()], crs=False, force2d=True))
        expected_content = {"type": "FeatureCollection", "features": [{"geometry": {"type": "GeometryCollection", "geometries": [{"type": "LineString", "coordinates": [[3.0, 4.0], [6.0, 7.0]]}, {"type": "Point", "coordinates": [1.0, 2.0]}]}, "type": "Feature", "properties": {"id": None}}]}
        self.assertEqual(features, expected_content)

    def test_none_geometry(self):
        class Empty(models.Model):
            geom = None
        serializer = Serializer()
        features = json.loads(serializer.serialize([Empty()], crs=False))
        self.assertEqual(
            features, {
                "type": "FeatureCollection",
                "features": [{
                    "geometry": None,
                    "type": "Feature",
                    "properties": {"id": None}}]
            })

    def test_bbox_auto(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize([{'geom': 'SRID=4326;LINESTRING (1 1, 3 3)'}],
                                                   bbox_auto=True, crs=False))
        self.assertEqual(
            features, {
                "type": "FeatureCollection",
                "features": [{
                    "geometry": {"type": "LineString", "coordinates": [[1.0, 1.0], [3.0, 3.0]]},
                    "type": "Feature",
                    "properties": {},
                    "bbox": [1.0, 1.0, 3.0, 3.0]
                }]
            })


class ForeignKeyTest(TestCase):

    def setUp(self):
        self.route = Route.objects.create(
            name='green', geom="LINESTRING (0 0, 1 1)")
        Sign(label='A', route=self.route).save()

    def test_serialize_foreign(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(Sign.objects.all(), properties=['route']))
        self.assertEqual(
            features, {"crs": {"type": "link", "properties": {"href": "http://spatialreference.org/ref/epsg/4326/", "type": "proj4"}}, "type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [0.5, 0.5]}, "type": "Feature", "properties": {"route": 1, "model": "djgeojson.sign"}, "id": self.route.pk}]})

    def test_serialize_foreign_natural(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(
            Sign.objects.all(), use_natural_keys=True, properties=['route']))
        self.assertEqual(
            features, {"crs": {"type": "link", "properties": {"href": "http://spatialreference.org/ref/epsg/4326/", "type": "proj4"}}, "type": "FeatureCollection", "features": [{"geometry": {"type": "Point", "coordinates": [0.5, 0.5]}, "type": "Feature", "properties": {"route": "green", "model": "djgeojson.sign"}, "id": self.route.pk}]})


class ManyToManyTest(TestCase):

    def setUp(self):
        country1 = Country(label='C1', geom="POLYGON ((0 0,1 1,0 2,0 0))")
        country1.save()
        country2 = Country(label='C2', geom="POLYGON ((0 0,1 1,0 2,0 0))")
        country2.save()

        self.route1 = Route.objects.create(
            name='green', geom="LINESTRING (0 0, 1 1)")
        self.route2 = Route.objects.create(
            name='blue', geom="LINESTRING (0 0, 1 1)")
        self.route2.countries.add(country1)
        self.route3 = Route.objects.create(
            name='red', geom="LINESTRING (0 0, 1 1)")
        self.route3.countries.add(country1)
        self.route3.countries.add(country2)

    def test_serialize_manytomany(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(
            Route.objects.all(), properties=['countries']))
        self.assertEqual(
            features, {"crs": {"type": "link", "properties": {"href": "http://spatialreference.org/ref/epsg/4326/", "type": "proj4"}}, "type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "countries": []}, "id": self.route1.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "countries": [1]}, "id": self.route2.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "countries": [1, 2]}, "id": self.route3.pk}]})

    def test_serialize_manytomany_natural(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(
            Route.objects.all(), use_natural_keys=True, properties=['countries']))
        self.assertEqual(
            features, {"crs": {"type": "link", "properties": {"href": "http://spatialreference.org/ref/epsg/4326/", "type": "proj4"}}, "type": "FeatureCollection", "features": [{"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "countries": []}, "id": self.route1.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "countries": ["C1"]}, "id": self.route2.pk}, {"geometry": {"type": "LineString", "coordinates": [[0.0, 0.0], [1.0, 1.0]]}, "type": "Feature", "properties": {"model": "djgeojson.route", "countries": ["C1", "C2"]}, "id": self.route3.pk}]})


class ReverseForeignkeyTest(TestCase):

    def setUp(self):
        self.route = Route(name='green', geom="LINESTRING (0 0, 1 1)")
        self.route.save()
        self.sign1 = Sign.objects.create(label='A', route=self.route)
        self.sign2 = Sign.objects.create(label='B', route=self.route)
        self.sign3 = Sign.objects.create(label='C', route=self.route)

    def test_relation_set(self):
        self.assertEqual(len(self.route.signs.all()), 3)

    def test_serialize_reverse(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(
            Route.objects.all(), properties=['signs']))
        self.assertEqual(
            features, {
                "crs": {
                    "type": "link", "properties": {
                        "href": "http://spatialreference.org/ref/epsg/4326/",
                        "type": "proj4"
                    }
                },
                "type": "FeatureCollection",
                "features": [{
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[0.0, 0.0], [1.0, 1.0]]
                    },
                    "type": "Feature",
                    "properties": {
                        "model": "djgeojson.route",
                        "signs": [
                            self.sign1.pk,
                            self.sign2.pk,
                            self.sign3.pk]},
                    "id": self.route.pk
                }]
            })

    def test_serialize_reverse_natural(self):
        serializer = Serializer()
        features = json.loads(serializer.serialize(
            Route.objects.all(), use_natural_keys=True, properties=['signs']))
        self.assertEqual(
            features, {
                "crs": {
                    "type": "link",
                    "properties": {
                        "href": "http://spatialreference.org/ref/epsg/4326/",
                        "type": "proj4"
                    }
                },
                "type": "FeatureCollection",
                "features": [{
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                    "type": "Feature",
                    "properties": {
                        "model": "djgeojson.route",
                        "signs": ["A", "B", "C"]},
                    "id": self.route.pk
                }]
            })


class GeoJsonTemplateTagTest(TestCase):

    def test_single(self):
        r = Route(name='red', geom="LINESTRING (0 0, 1 1)")
        feature = json.loads(geojsonfeature(r))
        self.assertEqual(
            feature, {
                "crs": {
                    "type": "link",
                    "properties": {
                        "href": "http://spatialreference.org/ref/epsg/4326/",
                        "type": "proj4"
                    }
                },
                "type": "FeatureCollection",
                "features": [{
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                    "type": "Feature", "properties": {}}]
            })

    def test_queryset(self):
        route1 = Route.objects.create(
            name='green', geom="LINESTRING (0 0, 1 1)")
        route2 = Route.objects.create(
            name='blue', geom="LINESTRING (0 0, 1 1)")
        route3 = Route.objects.create(name='red', geom="LINESTRING (0 0, 1 1)")

        feature = json.loads(geojsonfeature(Route.objects.all()))
        self.assertEqual(
            feature, {
                "crs": {
                    "type": "link", "properties": {
                        "href": "http://spatialreference.org/ref/epsg/4326/",
                        "type": "proj4"
                    }
                },
                "type": "FeatureCollection",
                "features": [
                    {
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[0.0, 0.0], [1.0, 1.0]]
                        },
                        "type": "Feature",
                        "properties": {
                            "model": "djgeojson.route"
                        },
                        "id": route1.pk
                    },
                    {
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[0.0, 0.0], [1.0, 1.0]]
                        },
                        "type": "Feature",
                        "properties": {"model": "djgeojson.route"},
                        "id": route2.pk
                    },
                    {
                        "geometry": {"type": "LineString",
                                     "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                        "type": "Feature",
                        "properties": {"model": "djgeojson.route"},
                        "id": route3.pk
                    }
                ]
            })

    def test_feature(self):
        r = Route(name='red', geom="LINESTRING (0 0, 1 1)")
        feature = json.loads(geojsonfeature(r.geom))
        self.assertEqual(
            feature, {
                "geometry": {"type": "LineString",
                             "coordinates": [[0.0, 0.0], [1.0, 1.0]]},
                "type": "Feature", "properties": {}
            })


class ViewsTest(TestCase):

    def setUp(self):
        self.route = Route(name='green', geom="LINESTRING (0 0, 1 1)")
        self.route.save()

    def test_view_default_options(self):
        view = GeoJSONLayerView(model=Route)
        view.object_list = []
        response = view.render_to_response(context={})
        geojson = json.loads(smart_text(response.content))
        self.assertEqual(geojson['features'][0]['geometry']['coordinates'],
                         [[0.0, 0.0], [1.0, 1.0]])

    def test_view_can_control_properties(self):
        klass = type('FullGeoJSON', (GeoJSONLayerView,),
                     {'properties': ['name']})
        view = klass(model=Route)
        view.object_list = []
        response = view.render_to_response(context={})
        geojson = json.loads(smart_text(response.content))
        self.assertEqual(geojson['features'][0]['properties']['name'],
                         'green')


class Address(models.Model):
    geom = GeoJSONField()


class ModelFieldTest(TestCase):
    def setUp(self):
        self.address = Address()
        self.address.geom = {'type': 'Point', 'coordinates': [0, 0]}
        self.address.save()

    def test_models_can_have_geojson_fields(self):
        saved = Address.objects.get(id=self.address.id)
        self.assertDictEqual(saved.geom, self.address.geom)

    def test_default_form_field_is_geojsonfield(self):
        field = self.address._meta.get_field('geom').formfield()
        self.assertTrue(isinstance(field, GeoJSONFormField))

    def test_default_form_field_has_geojson_validator(self):
        field = self.address._meta.get_field('geom').formfield()
        self.assertEqual(field.validators, [geojson_geometry])

    def test_form_field_raises_if_invalid_type(self):
        field = self.address._meta.get_field('geom').formfield()
        self.assertRaises(ValidationError, field.clean,
                          {'type': 'FeatureCollection', 'foo': 'bar'})

    def test_form_field_raises_if_type_missing(self):
        field = self.address._meta.get_field('geom').formfield()
        self.assertRaises(ValidationError, field.clean,
                          {'foo': 'bar'})

    def test_field_can_be_serialized(self):
        serializer = Serializer()
        geojson = serializer.serialize(Address.objects.all(), crs=False)
        features = json.loads(geojson)
        self.assertEqual(
            features, {
                u'type': u'FeatureCollection',
                u'features': [{
                    u'id': self.address.id,
                    u'type': u'Feature',
                    u'geometry': {u'type': u'Point', u'coordinates': [0, 0]},
                    u'properties': {
                        u'model': u'djgeojson.address'
                    }
                }]
            })

    def test_field_can_be_deserialized(self):
        input_geojson = """
        {"type": "FeatureCollection",
         "features": [
            { "type": "Feature",
                "properties": {"model": "djgeojson.address"},
                "id": 1,
                "geometry": {
                    "type": "Point",
                    "coordinates": [0.0, 0.0]
                }
            }
        ]}"""
        objects = list(serializers.deserialize('geojson', input_geojson))
        self.assertEqual(objects[0].object.geom,
                         {'type': 'Point', 'coordinates': [0, 0]})
