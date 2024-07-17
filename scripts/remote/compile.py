import argparse
import subprocess

import pickle as pkl

from dependency_loader import DependencyLoader


class MaMiCoCompiler:
    def __init__(self, config: str = None, config_filepath: str = None, plugin_path: str = None):
        self.config = config
        self.config_filepath = config_filepath
        self.plugin_path = plugin_path
        with open(self.config_filepath, 'rb') as config_file:
            self.user_config = pkl.load(config_file)

    def compile_mamico(self):
        ########################################
        ## C/C++ Compiler
        ########################################
        c_compiler_loader = DependencyLoader(
            dependency_name="C/C++ Compiler",
            load=self.user_config.get("need_c_compiler"),
            commands=[
                "module load gcc/12"
            ])
        c_compiler_command = c_compiler_loader(verbose=False)
        print(c_compiler_command)

        ########################################
        # CMake
        ########################################
        cmake_loader = DependencyLoader(
            dependency_name="CMake",
            load=self.user_config.get("need_cmake"),
            commands=[
                "module load cmake"
            ])
        cmake_command = cmake_loader(verbose=False)
        print(cmake_command)

        ########################################
        # MPI
        ########################################
        mpi_loader = DependencyLoader(
            dependency_name="MPI",
            load=self.user_config.get("need_mpi"),
            commands=[
                "module load mpi",
                "module load openmpi",
                "module load mpich",
                "module load intelmpi",
                "module load oneAPI"
            ])
        mpi_command = mpi_loader(verbose=False)
        print(mpi_command)

        ########################################
        # Eigen3
        ########################################
        eigen_loader = DependencyLoader(
            dependency_name="Eigen3",
            load=self.user_config.get("need_eigen3"),
            commands=[
                "module load eigen3",
                "module load eigen"
            ])
        eigen_command = eigen_loader(verbose=False)
        print(eigen_command)

        ########################################
        # Pybind11
        ########################################
        pybind11_loader = DependencyLoader(
            dependency_name="Pybind11",
            load=self.user_config.get("need_pybind11"),
            commands=[
                "module load pybind11",
                "module load pybind",
                "module load py-pybind11"
            ])
        pybind11_command = pybind11_loader(verbose=False)
        print(pybind11_command)

        ########################################
        # LS1 Mardyn
        ########################################
        ls1_compiler = DependencyLoader(
            dependency_name="ls1-mardyn",
            load=self.user_config.get("use_ls1"),
            commands=[
                "module load ls1-mardyn"
            ])
        ls1_command = ls1_compiler(verbose=False)
        print(ls1_command)

        print(self.config)

        try:
            output = subprocess.run(
                f"module load cmake; module load gcc/gcc-12.1.0; cd {self.plugin_path}/MaMiCo/{self.user_config.get('mamico_checksum')}; mkdir -p build; cd build; cmake ..; make;",
                cwd=f"{self.plugin_path}/MaMiCo", shell=True, check=True)
            print(output)
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            return
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog='MaMiCo Compilation Script',
                    description='Automating dependency loading and MaMiCo compilation.')
    
    parser.add_argument('--config_filepath',
                        required=True,
                        help="Path to the mamico_user_config.yml file containing information about dependencies and compilation flags.")
    parser.add_argument('--config',
                        required=True,
                        help="Name of the configuration.")
    parser.add_argument('--plugin_path',
                        required=True,
                        help="Path to the FabMaMiCo plugin directory.")
    
    args = parser.parse_args()

    compiler = MaMiCoCompiler(config=args.config, config_filepath=args.config_filepath, plugin_path=args.plugin_path)
    print(compiler.user_config)

    compiler.compile_mamico()

    print("Done")

