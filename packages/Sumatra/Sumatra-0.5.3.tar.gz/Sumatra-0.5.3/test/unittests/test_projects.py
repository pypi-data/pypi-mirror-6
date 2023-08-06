"""
Unit tests for the sumatra.projects module
"""

from __future__ import with_statement
import shutil
import os, sys
import unittest
import sumatra.projects
from sumatra.projects import Project, load_project


class MockDiffFormatter(object):
    def __init__(self, diff):
        pass
    def format(self, mode):
        return ""
sumatra.projects.get_diff_formatter = lambda: MockDiffFormatter

class MockWorkingCopy(object):
    path = "/path/to/working/copy"
    def has_changed(self):
        return False
    def use_latest_version(self):
        pass
    def current_version(self):
        return 999
    def use_version(self, v):
        pass
    def contains(self, path):
        return True
    def get_username(self):
        return "The Knights Who Say Ni"
        
class MockRepository(object):
    url = "http://svn.example.com"
    
    def __eq__(self, other):
        return self.url == other.url

    def __getstate__(self):
        return {}

    def get_working_copy(self):
        return MockWorkingCopy()


class MockExecutable(object):
    name = "Python"
    path = sys.executable #"/usr/local/bin/python"
    version = sys.version
    requires_script = True
    def write_parameters(self, params, filename):
        pass
    def __getstate__(self):
        return {}


class MockLaunchMode(object):
    def get_platform_information(self):
        return []
    def pre_run(self, prog):
        pass
    def run(self, prog, script, params, append_label):
        return True
    def __getstate__(self):
        return {}
    
    
class MockSet(object):
    def add(self, x):
        self.added = x
    def remove(self, x):
        self.removed = x

    
class MockRecord(object):
    def __init__(self, label):
        self.label = label
        self.tags = MockSet()
    def difference(r1, r2, igm, igf):
        return ""

    
class MockRecordStore(object):
    def save(self, project_name, record):
        pass
    def get(self, project_name, label):
        if label != "none_existent":
            return MockRecord(label=label*2)
        else:
            raise Exception()
    def delete(self, project_name, label):
        self.deleted = label
    def delete_by_tag(self, project_name, tag):
        return "".join(reversed(tag))
    def most_recent(self, project):
        return "last"
    def __getstate__(self):
        return {}


class TestProject(unittest.TestCase):
    
    def tearDown(self):
        if os.path.exists(".smt"):
            shutil.rmtree(".smt")
        if os.path.exists("Data"):
            os.rmdir("Data")
        if os.path.exists("test.py"):
            os.remove("test.py")
    
    def write_test_script(self, filename):
        with open(filename, "w") as f:
            f.write("a=2\n")
    write_test_script.__test__ = False # stop nose treating this as a test
    
    def test__init__with_minimal_arguments(self):
        proj = Project("test_project", record_store=MockRecordStore())
        
    def test__creating_a_second_project_in_the_same_dir_should_raise_an_exception(self):
        proj1 = Project("test_project1", record_store=MockRecordStore())
        self.assertRaises(Exception,Project, "test_project2")

    def test__info(self):
        proj = Project("test_project", record_store=MockRecordStore())
        proj.info()
        
    def test_new_record_with_minimal_args_should_set_defaults(self):
        self.write_test_script("test.py")
        proj = Project("test_project",
                       record_store=MockRecordStore(),
                       default_main_file="test.py",
                       default_executable=MockExecutable(),
                       default_launch_mode=MockLaunchMode(),
                       default_repository=MockRepository())
        rec = proj.new_record()
        self.assertEqual(rec.repository, proj.default_repository)
        self.assertEqual(rec.main_file, "test.py")

    def test_new_record_with_uuid_label_generator_should_generate_unique_id(self):
        self.write_test_script("test.py")
        proj = Project("test_project",
                       record_store=MockRecordStore(),
                       default_main_file="test.py",
                       default_executable=MockExecutable(),
                       default_launch_mode=MockLaunchMode(),
                       default_repository=MockRepository(),
                       label_generator='uuid')
        rec1 = proj.new_record()
        rec2 = proj.new_record()
        self.assertNotEqual(rec1.label, rec2.label)

    def test__update_code(self):
        proj = Project("test_project",
                       record_store=MockRecordStore(),
                       default_repository=MockRepository())
        wc = proj.default_repository.get_working_copy()
        proj.update_code(wc, version=9369835)

    def test_launch(self):
        self.write_test_script("test.py")
        proj = Project("test_project",
                       default_executable=MockExecutable(),
                       default_repository=MockRepository(),
                       default_launch_mode=MockLaunchMode(),
                       record_store=MockRecordStore())
        proj.launch(main_file="test.py")

    def test__get_record__calls_get_on_the_record_store(self):
        proj = Project("test_project",
                       record_store=MockRecordStore())
        self.assertEqual(proj.get_record("foo").label, "foofoo")

    def test__delete_record__calls_delete_on_the_record_store(self):
        proj = Project("test_project",
                       record_store=MockRecordStore())
        proj.delete_record("foo")
        self.assertEqual(proj.record_store.deleted, "foo")
        
    def test__delete_by_tag__calls_delete_by_tag_on_the_record_store(self):
        proj = Project("test_project",
                       record_store=MockRecordStore())
        self.assertEqual(proj.delete_by_tag("foo"), "oof")

    def test__add_comment__should_set_the_outcome_attribute_of_the_record(self):
        proj = Project("test_project",
                       record_store=MockRecordStore())
        proj.add_comment("foo", "comment goes here")
        
    def test__add_tag__should_call_add_on_the_tags_attibute_of_the_record(self):
        proj = Project("test_project",
                       record_store=MockRecordStore())
        proj.add_tag("foo", "new_tag")
        
    def test__remove_tag__should_call_remove_on_the_tags_attibute_of_the_record(self):
        proj = Project("test_project",
                       record_store=MockRecordStore())
        proj.remove_tag("foo", "new_tag")
        
    def test__show_diff(self):
        proj = Project("test_project",
                       record_store=MockRecordStore())
        proj.show_diff("foo", "bar")

    def delete_record__should_update_most_recent(self):
        """see ticket:36."""
        proj = Project("test_project",
                       record_store=MockRecordStore())
        proj.add_record(MockRecord("record1"))
        self.assertEqual(proj._most_recent, "record1")
        proj.add_record(MockRecord("record2"))
        self.assertEqual(proj._most_recent, "record2")
        proj.delete_record("record2")
        self.assertEqual(proj._most_recent, "last") # should really be "record1", but we are not testing RecordStore here



class TestModuleFunctions(unittest.TestCase):
    
    def tearDown(self):
        if os.path.exists(".smt"):
            shutil.rmtree(".smt")
        if os.path.exists("Data"):
            os.rmdir("Data")
    
    def test__load_project__should_return_Project(self):
        proj1 = Project("test_project", record_store=MockRecordStore())
        assert os.path.exists(".smt/project")
        proj2 = load_project()
        self.assertEqual(proj1.name, proj2.name)

    def test__load_project_should_raise_exception_if_no_project_in_current_dir(self):
        self.assertRaises(Exception, load_project)


if __name__ == '__main__':
    unittest.main()
