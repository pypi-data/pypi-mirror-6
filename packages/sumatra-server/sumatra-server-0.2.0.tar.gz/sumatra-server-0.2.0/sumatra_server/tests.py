
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

try:
    import json
except ImportError:
    import django.utils.simplejson as json
import base64


OK = 200
CREATED = 201
UNAUTHORIZED = 401
NOT_FOUND = 404
NO_CONTENT = 204


def deunicode(v):
    """Convert unicode keys and values to str"""
    if isinstance(v, dict):
        new_v = {}
        for kk, vv in v.items():
            new_v[str(kk)] = deunicode(vv)
    elif isinstance(v, unicode):
        new_v = str(v)
    elif isinstance(v, list):
        new_v = [deunicode(d) for d in v]
    else:
        new_v = v
    return new_v


class BaseTestCase(TestCase):
    fixtures = ['haggling', 'permissions']

    def setUp(self):
        # thanks to Thomas Pelletier for this function
        # http://thomas.pelletier.im/OK9/12/test-your-django-piston-api-with-auth/
        self.client = Client()
        auth = '%s:%s' % ('testuser', 'abc123')
        auth = 'Basic %s' % base64.encodestring(auth)
        auth = auth.strip()
        self.extra = {
            'HTTP_AUTHORIZATION': auth,
        }

    def assertMimeType(self, response, desired_mimetype):
        mimetype, charset = response["Content-Type"].split(";")
        self.assertEqual(mimetype, desired_mimetype)


class ProjectListHandlerTest(BaseTestCase):

    def test_GET_authenticated(self):
        prj_list_uri = reverse("sumatra-project-list")
        response = self.client.get(prj_list_uri, {}, **self.extra)
        self.failUnlessEqual(response.status_code, OK)
        self.assertMimeType(response, "application/json")
        data = json.loads(response.content)
        assert isinstance(data, list)
        self.assertEqual(len(data), 2)
        uris = {prj["uri"] for prj in data}
        self.assertEqual(uris,
                         {"http://testserver%sTestProject/" % prj_list_uri,
                          "http://testserver%sTestProject2/" % prj_list_uri})

    def test_GET_anonymous(self):
        prj_list_uri = reverse("sumatra-project-list")
        response = self.client.get(prj_list_uri, {})
        self.failUnlessEqual(response.status_code, OK)
        self.assertMimeType(response, "application/json")
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["uri"],
                         "http://testserver%sTestProject2/" % prj_list_uri)

    def test_GET_format_html(self):
        self.client.login(username="testuser", password="abc123")
        prj_list_uri = reverse("sumatra-project-list")
        response = self.client.get(prj_list_uri, {"format": "html"})
        self.failUnlessEqual(response.status_code, OK)
        self.assertMimeType(response, "text/html")


class ProjectHandlerTest(BaseTestCase):

    def test_GET_private_authenticated(self):
        prj_uri = reverse("sumatra-project",
                          kwargs={"project": "TestProject"})
        response = self.client.get(prj_uri, {}, **self.extra)
        # print response.content
        self.assertEqual(response.status_code, OK)
        self.assertMimeType(response, "application/json")
        data = json.loads(response.content)
        assert isinstance(data, dict)
        self.assertEqual(data["id"], "TestProject")
        assert "testuser" in data["access"]
        assert "anonymous" not in data["access"]
        assert isinstance(data["records"], list)
        # check we can also access all the records contained in this project
        for record in data["records"]:
            touch = self.client.get(record, {}, **self.extra)  # should perhaps add support for HEAD to the server
            self.assertEqual(touch.status_code, OK)

    def test_GET_public_authenticated(self):
        prj_uri = reverse("sumatra-project",
                          kwargs={"project": "TestProject2"})
        response = self.client.get(prj_uri, {}, **self.extra)
        self.assertEqual(response.status_code, OK)
        self.assertMimeType(response, "application/json")
        data = json.loads(response.content)
        self.assertEqual(data["id"], "TestProject2")
        assert "anonymous" in data["access"]
        # check we can also access all the records contained in this project
        for record in data["records"]:
            touch = self.client.get(record, {}, **self.extra)
            self.assertEqual(touch.status_code, OK)

    def test_GET_public_anonymous(self):
        prj_uri = reverse("sumatra-project",
                          kwargs={"project": "TestProject2"})
        response = self.client.get(prj_uri, {})
        self.assertEqual(response.status_code, OK)
        data = json.loads(response.content)
        self.assertEqual(data["id"], "TestProject2")
        assert "access" not in data
        # check we can also access all the records contained in this project
        for record in data["records"]:
            touch = self.client.get(record, {})
            self.assertEqual(touch.status_code, OK)

    def test_GET_private_anonymous(self):
        prj_uri = reverse("sumatra-project",
                          kwargs={"project": "TestProject"})
        response = self.client.get(prj_uri, {})
        self.assertEqual(response.status_code, UNAUTHORIZED)

    def test_GET_nonexistent(self):
        prj_uri = reverse("sumatra-project",
                          kwargs={"project": "TestProject999"})
        response = self.client.get(prj_uri, {})
        self.assertEqual(response.status_code, NOT_FOUND)


class RecordHandlerTest(BaseTestCase):

    def test_GET_no_data(self):
        label = "haggling"
        rec_uri = reverse("sumatra-record",
                          kwargs={"project": "TestProject",
                                  "label": label})
        response = self.client.get(rec_uri, {}, **self.extra)
        # print response.content
        self.assertEqual(response.status_code, OK)
        self.assertMimeType(response, "application/json")
        data = json.loads(response.content)
        assert isinstance(data, dict)
        self.assertEqual(data["label"], label)
        self.assertEqual(set(data.keys()),
                         set(("executable", "label", "reason",
                              "duration", "executable", "repository",
                              "main_file", "version", "parameters",
                              "launch_mode", "datastore", "outcome",
                              "output_data", "timestamp", "tags", "diff",
                              "user", "dependencies", "platforms",
                              "project_id", "input_data", "input_datastore",
                              "script_arguments", "stdout_stderr")))
        #import pdb; pdb.set_trace()
        self.assertEqual(data["tags"], ["foobar"])
        self.assertEqual(data["output_data"][0]["path"], "example2.dat")
        self.assertIsInstance(data["output_data"][0]["metadata"], dict)

    def test_GET_format_html(self):
        self.extra = {}  # use Django auth, not HTTP Basic
        self.client.login(username="testuser", password="abc123")
        label = "haggling"
        rec_uri = reverse("sumatra-record",
                          kwargs={"project": "TestProject",
                                  "label": label})
        response = self.client.get(rec_uri, {"format": "html"}, **self.extra)
        self.failUnlessEqual(response.status_code, OK)
        self.assertMimeType(response, "text/html")

    def test_GET_not_authenticated(self):
        label = "haggling"
        rec_uri = reverse("sumatra-record",
                          kwargs={"project": "TestProject",
                                  "label": label})
        response = self.client.get(rec_uri, {})
        print response.content
        self.assertEqual(response.status_code, UNAUTHORIZED)

    def test_GET_nonexistent_record(self):
        label = "iquegfxnqiuehfiomehxgo"
        rec_uri = reverse("sumatra-record",
                          kwargs={"project": "TestProject",
                                  "label": label})
        response = self.client.get(rec_uri, {}, **self.extra)
        self.failUnlessEqual(response.status_code, NOT_FOUND)

    def test_GET_Accept_html(self):
        self.extra = {}  # use Django auth, not HTTP Basic
        self.client.login(username="testuser", password="abc123")
        label = "haggling"
        rec_uri = reverse("sumatra-record",
                          kwargs={"project": "TestProject",
                                  "label": label})
        response = self.client.get(rec_uri, {}, Accept="text/html", **self.extra)
        self.failUnlessEqual(response.status_code, OK)
        self.assertMimeType(response, "text/html")

    def test_PUT_new_record_json(self):
        new_record = {
            "label": "abcdef",
            "reason": "uygnougy",
            "duration": 32.1,
            "executable": {
                "path": "lgljgkjhk",
                "version": "iugnogn",
                "name": "kljhnhn",
                "options": "dfgdfg"
            },
            "repository": {
                "url": "iuhnhc;<s",
                "type": "iufvbfgbjlml",
                "upstream": None
            },
            "main_file": "OIYUGUIYFU",
            "version": "LUGNYGNYGu",
            "parameters": {
                "content": "oignuguygnug",
                "type": "hjgjgn65878",
            },
            "input_data": [{
                "path": "sfgshaeth",
                "digest": "abcdef0123456789",
                "metadata": {}
            }],
            "script_arguments": "p8yupyrprutot",
            "launch_mode": {
                "type": "OIUNIU6nkjgbun",
                "parameters": {},
            },
            "datastore": {
                "type": "mosigcqpoejf;",
                "parameters": {
                    "root": "/path/to/output/data"
                }
            },
            "input_datastore": {
                "type": "mosigcqpoejf;",
                "parameters": {
                    "root": "/path/to/input/data"
                },
            },
            "outcome": "mihiuhpoip",
            "stdout_stderr": "erawoiawof23",
            "output_data": [{
                "path": "iugbufuyfiutyfitfy",
                "digest": "0123456789abcdef",
                "metadata": {}
            }],
            "timestamp": "2010-07-11T22:50:00",
            "tags": ["abcd", "efgh", "ijklm", "tag with spaces"],
            "diff": "+++---",
            "user": "gnugynygy",
            "dependencies": [{
                "path": "moh,oh",
                "version": "liuhiuhiu",
                "name": "mohuuyfbn",
                "module": "ouitfvbtfky",
                "diff": "liugnig,lug",
                "source": None,
            }],
            "platforms": [{
                "system_name": "liugiuyhiuyg",
                "ip_addr": "igng,iihih,i",
                "architecture_bits": "vmsilughcqioej;",
                "machine": "cligcnquefgx",
                "architecture_linkage": "uygbytfkg",
                "version": "luyhtdkguhl,h",
                "release": "lufuytdydy",
                "network_name": "ouifbf67",
                "processor": "iugonuyginugugu"
            }],
        }
        prj_uri = reverse("sumatra-project",
                          kwargs={"project": "TestProject"})
        rec_uri = "%s%s/" % (prj_uri, new_record["label"])
        response = self.client.put(rec_uri, data=json.dumps(new_record),
                                   content_type="application/json", **self.extra)
        print response.content
        self.assertEqual(response.status_code, CREATED)

        response = self.client.get(rec_uri, {}, **self.extra)
        self.assertEqual(response.status_code, OK)
        # pprint(deunicode(json.loads(response.content)))
        new_record.update(project_id="TestProject")
        self.maxDiff = None
        #import pdb; pdb.set_trace()
        self.assertEqual(new_record, deunicode(json.loads(response.content)))

    def test_PUT_existing_record_json(self):
        prj_uri = reverse("sumatra-project",
                          kwargs={"project": "TestProject"})
        rec_uri = "%s%s/" % (prj_uri, "haggling")
        update = {
            "reason": "reason goes here",
            "outcome": "comments on outcome go here",
            "tags": ["tagA", "tagB", "tagC", "tag D"],
            "version": "this should not be updated"
        }
        response = self.client.put(rec_uri, data=json.dumps(update),
                                   content_type="application/json", **self.extra)
        print response.content
        self.assertEqual(response.status_code, OK)

        response = self.client.get(rec_uri, {}, **self.extra)
        self.assertEqual(response.status_code, OK)
        data = json.loads(response.content)
        assert isinstance(data, dict)
        self.assertEqual(data["label"], "haggling")
        self.assertEqual(data["reason"], update["reason"])
        self.assertEqual(data["outcome"], update["outcome"])
        self.assertEqual(set(data["tags"]), set(update["tags"]))
        self.assertNotEqual(set(data["version"]), set(update["version"]))

    def test_DELETE_existing_record(self):
        label = "20111013-172503"
        rec_uri = reverse("sumatra-record",
                          kwargs={"project": "TestProject",
                                  "label": label})
        response = self.client.get(rec_uri, {}, **self.extra)
        self.assertEqual(response.status_code, OK)

        response = self.client.delete(rec_uri, {}, **self.extra)
        self.assertEqual(response.status_code, NO_CONTENT)

        response = self.client.get(rec_uri, {}, **self.extra)
        self.assertEqual(response.status_code, NOT_FOUND)

    def test_DELETE_nonexistent_record(self):
        label = "mochirsueghcnisuercgheiosg"
        rec_uri = reverse("sumatra-record",
                          kwargs={"project": "TestProject",
                                  "label": label})
        response = self.client.delete(rec_uri, {}, **self.extra)
        self.assertEqual(response.status_code, NOT_FOUND)
