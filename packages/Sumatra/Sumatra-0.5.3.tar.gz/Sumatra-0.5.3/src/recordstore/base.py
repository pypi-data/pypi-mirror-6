"""
Provides base RecordStore class.
"""

from sumatra.recordstore import serialization


class RecordStore(object):
    """
    Base class for record store implementations.
    """
    
    def list_projects(self):
        """Return the names of all projects that have records in this store."""
        raise NotImplementedError

    def save(self, project_name, record):
        """Store the given record under the given project."""
        raise NotImplementedError
        
    def get(self, project_name, label):
        """Retrieve the record with the given label from the given project."""
        raise NotImplementedError
    
    def list(self, project_name, tags=None):
        """
        Return a list of records for the given project.
        
        If *tags* is not provided, list all records, otherwise list only records
        that have been tagged with one or more of the tags.
        """
        raise NotImplementedError
    
    def labels(self, project_name):
        """Return the labels of all records in the given project."""
        raise NotImplementedError
    
    def delete(self, project_name, label):
        """Delete the record with the given label from the given project."""
        raise NotImplementedError

    def delete_all(self):
        """Delete all records from the store."""
        raise NotImplementedError
        
    def delete_by_tag(self, project_name, tag):
        """Delete all records from the given project that have been tagged with the given tag."""
        raise NotImplementedError
        
    def most_recent(self, project_name):
        """Return the most recent record from the given project."""
        raise NotImplementedError
    
    def export(self, project_name, indent=2):
        """Export store contents as JSON."""
        return "[" + ",\n".join(serialization.encode_record(record, indent=indent)
                                for record in self.list(project_name)) + "]"

    def import_(self, project_name, content):
        """Import records in JSON format."""
        records = serialization.decode_records(content)
        for record in records:
            # need to check for duplicate record labels?
            self.save(project_name, record)

    def sync(self, other, project_name):
        """
        Synchronize two record stores so that they contain the same records for
        a given project.
        
        Where the two stores have the same label (within a project) for
        different records, those records will not be synced. The method
        returns a list of non-synchronizable records (empty if the sync worked
        perfectly).
        """
        # what to do about syncing different Sumatra versions? Need to think about
        # schema versioning
        self_labels = set(self.labels(project_name))
        other_labels = set(other.labels(project_name))
        only_in_self = self_labels.difference(other_labels)
        only_in_other = other_labels.difference(self_labels)
        in_both = self_labels.intersection(other_labels)
        non_synchronizable = []
        for label in in_both:
            if self.get(project_name, label) != other.get(project_name, label):
                non_synchronizable.append(label)
        for label in only_in_self:
            other.save(project_name, self.get(project_name, label))
        for label in only_in_other:
            self.save(project_name, other.get(project_name, label))
        return non_synchronizable
    
    def sync_all(self, other):
        """Synchronize all records from all projects between two record stores."""
        all_projects = set(self.list_projects()).union(other.list_projects())
        for project_name in all_projects:
            self.sync(other, project_name)
            
    def has_project(self, project_name):
        """Does the store contain any records for the given project?"""
        raise NotImplementedError
    
    def list_projects(self, project_name):
        """Return the names of all projects that have records in the store."""
        raise NotImplementedError


class RecordStoreAccessError(OSError):
    pass
