import os
from fabric.api import run, settings, abort


class Stack(object):
    """
    Representation of a stack of projects/services of the build server.
    """
    def __init__(self, domain, stack_version, operator=None, meta_path=None):
        self.version = stack_version
        self.domain = domain

        if operator is None:
            self.operator = StackOperator(meta_path)
        else:
            self.operator = operator

    def add_package(self, name, version, file_name):
        """
        Add created package to stack and reference packages.
        """
        self.operator.add_reference_package(name, version, file_name)
        self.operator.add_stack_package(self, name, version)

    def is_persisted(self):
        """
        Check if stack is already created.
        """
        return self.operator.test_stack_exists(self)

    def clone_from(self, old_stack):
        """
        Clone an old stack into a new one (even if exists already).
        """
        self.operator.copy_old_stack(old_stack, self)

    def persist(self):
        """
        Persists the stack info.
        """
        self.operator.persist_stack(self)


class StackOperator(object):
    """
    Process action related to the stack. In this case on the File system.
    """

    def __init__(self, target_folder):
        self.target_folder = target_folder

    def _get_reference_package_folder(self, name, version):
        return os.path.join(self.target_folder, "packages", name, "version", version)

    def _get_stack_folder(self, domain, stack_version):
        return os.path.join(self.target_folder, "domain", domain, "stacks", stack_version)

    def _get_stack_package_folder(self, domain, stack_version, pkg_name):
        return os.path.join(self._get_stack_folder(domain, stack_version), "packages", pkg_name)


    def test_stack_exists(self, stack):
        """
        Check if stack folder exists on the filesystem.
        """
        stack_path = self._get_stack_folder(stack.domain, stack.version)

        with settings(warn_only=True):
            if run("test -d %s" % stack_path).failed:
                return False
        return True

    def copy_old_stack(self, old_stack, new_stack):
        """
        Copy stack folder into new one.
        """
        new_stack_path = self._get_stack_folder(new_stack.domain, new_stack.version)
        old_stack_path = self._get_stack_folder(old_stack.domain, old_stack.version)

        if not self.test_stack_exists(old_stack):
            abort("%s:%s does not exist under %s" % (old_stack.domain, old_stack.version, old_stack_path))
        run("mkdir -p %s" % new_stack_path)
        run("cp -R %s/* %s" % (old_stack_path, new_stack_path))


    def persist_stack(self, new_stack):
        """
        Create empty folder.
        """
        new_stack_path = self._get_stack_folder(new_stack.domain, new_stack.version)
        run("mkdir -p %s/packages/" % new_stack_path)
        

    def add_reference_package(self, name, version, file_name):
        """
        Register this package in the references packages tree
        """
        folder_dst = self._get_reference_package_folder(name, version)
        run("mkdir -p %s" % folder_dst)
        run("echo %s > %s/file" % (file_name, folder_dst))


    def add_stack_package(self, stack, pkg_name, pkg_version):
        """
        Registers a built package in the stack.
        """
        folder_dst = self._get_stack_package_folder(stack.domain, stack.version, pkg_name)
        run("mkdir -p %s" % folder_dst)
        run("echo %s > %s/version" % (pkg_version, folder_dst))