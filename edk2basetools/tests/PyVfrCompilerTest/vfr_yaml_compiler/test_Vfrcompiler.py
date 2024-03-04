import pytest
import os


@pytest.mark.usefixtures('vfr_compiler')
class TestVfrCompiler:
    def test_vfr_preprocess(self):
        filename = self.compiler.Options.InputFileName
        print('filename: ', filename)
        self.compiler.PreProcess()

    def test_vfr_compiler(self):
        self.compiler.Compile()
        assert os.path.exists(self.compiler.Options.JsonFileName)

    def test_vfr_GenBinaryFiles(self):
        self.compiler.GenBinaryFiles()
        assert os.path.exists(self.compiler.Options.PkgOutputFileName)
        assert os.path.exists(self.compiler.Options.COutputFileName)
        assert os.path.exists(self.compiler.Options.RecordListFileName)

    def test_vfr_DumpSourceYaml(self):
        self.compiler.DumpSourceYaml()
        assert os.path.exists(self.compiler.Options.YamlFileName)

    def test_vfr_lst_file(self):
        with open(self.compiler.Options.RecordListFileName, 'r') as file:
            pyVfr_opcode_list = self.get_opcode_list(file)
        with open(os.path.join(os.path.dirname(self.compiler.Options.RecordListFileName),
                               os.path.basename(self.compiler.Options.RecordListFileName).split('_')[1]), 'r') as f:
            cVfr_opcode_list = self.get_opcode_list(f)

        for i, opcode in enumerate(pyVfr_opcode_list):
            assert opcode == cVfr_opcode_list[i]

    @classmethod
    def get_opcode_list(cls, file):
        all_opcode_record_list = list()
        start_opcode_flags = False
        for line in file.readline():
            if '#' in line or line == '\n':
                continue
            if 'All Opcode Record List' in line:
                start_opcode_flags = True
                continue
            if start_opcode_flags and '>' in line:
                all_opcode_record_list.append(line)
                continue
            if 'Total Size of all record' in line:
                break
        return all_opcode_record_list

    # Parse list

if __name__ == '__main__':
    pytest.main(['-vs', 'test_Vfrcompiler.py'])
