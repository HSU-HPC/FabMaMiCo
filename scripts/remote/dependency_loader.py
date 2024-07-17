import subprocess


class DependencyLoader:
    def __init__(self, dependency_name, load, commands=[], test_cmd=None):
        self.dependency_name = dependency_name
        self.load = load
        self.commands = commands
        self.test_cmd = test_cmd


    def __call__(self, verbose: bool = False):
        return self._load(verbose=verbose)


    def _load(self, verbose: bool = False):
        if self.load == None:
            print(f"A: Skipping loading of {self.dependency_name}.")
            return ""

        if type(self.load) == str:
            try:
                out = subprocess.run(self.load, shell=True, check=True)
                if verbose: print(out)
                return self.load
            except subprocess.CalledProcessError as e:
                print(f"{self.dependency_name} is not available via '{self.load}'.")
                if verbose: print(e.stderr)
                raise Exception(f"Could not load dependency {self.dependency_name}.")

        if type(self.load) == bool:
            if not self.load:
                print(f"B: Skipping loading of {self.dependency_name}.")
                return ""
            else: 
                for command in self.commands:
                    try:
                        out = subprocess.run(command, shell=True, check=True)
                        if verbose: print(out)
                        return command
                    except subprocess.CalledProcessError as e:
                        print(f"{self.dependency_name} is not available via '{command}'.")
                        if verbose: print(e.stderr)
                raise Exception(f"Could not load dependency {self.dependency_name}.\n" \
                    "None of the commands provided worked.")

        raise Exception(f"Could not load dependency {self.dependency_name}.\n" \
            "The 'need_c_compiler' attribute must be a string or a boolean.")