# -*- coding: utf-8 -*-
import pytest
import sys
import os
import re
import copy

from configparser import ConfigParser

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from VfrCompiler.IfrCompiler import VfrCompiler, CmdParser

workspace = os.path.dirname(
    os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))).lower()

#
# Parser makefile re
#
outputDirRe = re.compile('^OUTPUT_DIR =')
debugDirRe = re.compile('^DEBUG_DIR =')
incRe = re.compile('^INC =')
pyvfrRe = re.compile('\$\(PYVFR\)')
moduleNameRe = re.compile('^MODULE_NAME =')

vfr_compilers = list()


class Namespace:
    args_data = {
        'AutoDefault': None,
        'CPreprocessorOptions': None,
        'CheckDefault': None,
        'CreateIfrPkgFile': None,
        'CreateJsonFile': None,
        'CreateRecordListFile': None,
        'CreateYamlFile': None,
        'IncludePaths': None,
        'InputFileName': None,
        'LanuchVfrCompiler': True,
        'LanuchYamlCompiler': False,
        'ModuleName': '',
        'OldOutputDirectory': None,
        'OutputDirectory': None,
        'OverrideClassGuid': None,
        'SkipCPreprocessor': None,
        'StringFileName': None,
        'WarningAsError': None,
        'Workspace': None
    }

    def __init__(self, **kwargs):
        self.args_data.update(kwargs)

    def get_argv(self):
        argv = 1
        for key in self.args_data.keys():
            self.__setattr__(key, self.args_data[key])
            if self.args_data[key]:
                argv += 1
        return argv


def preprocess_data_of_pytestini():
    vfr_compilers.clear()
    conf = ConfigParser()
    conf.read(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pytest.ini'))
    vars = conf.items('target_floder')

    makefiles = list()
    for floder_path in vars[0][1].strip().split(','):
        if not os.path.isabs(floder_path.replace('\n', '')):
            file_path = os.path.join(os.path.dirname(__file__),
                                     floder_path.replace('\n', ''), 'Makefile')

            if os.path.isfile(file_path) and os.path.exists(file_path):
                makefiles.append(file_path)

    for makefile in list(set(makefiles)):
        with open(makefile, 'r') as file:
            makefile = file.readlines()
            flag = False
            scops = dict()
            incs = list()
            lanuch = ''
            for line in makefile:
                if '#' in line:
                    continue
                elif re.match(
                        moduleNameRe, line):
                    lines = line.split('=')
                    scops[lines[0].strip()] = lines[-1].strip().replace('\n',
                                                                        '')
                    flag = False
                elif re.match(outputDirRe, line) or re.match(debugDirRe,
                                                             line):
                    lines = line.split('=')
                    values = lines[-1].strip().split(os.sep)
                    scops[lines[0].strip()] = os.path.join(
                        os.path.dirname(__file__), values[-2], values[-1])
                    flag = False
                elif re.match(incRe, line):
                    flag = True
                    continue
                elif '=' in line:
                    flag = False
                elif re.search(pyvfrRe, line):
                    filename = os.path.join(scops["DEBUG_DIR"].replace("DEBUG",''), os.path.basename(line.split(' ')[1]))
                    lanuch = line.split(' ')[-1].strip()
                    if 'InputFileName' in scops.keys():
                        newScops = scops.copy()
                        newScops['InputFileName'] = filename
                        if lanuch == '--vfr':
                            newScops['LanuchVfrCompiler'] = True
                            newScops['LanuchYamlCompiler'] = False
                            vfr_compilers.append(newScops)
                        continue
                    scops['InputFileName'] = filename


                else:
                    if flag:
                        incs.append(line.replace('\\\n', '').strip())

            if lanuch == '--vfr':
                scops['LanuchVfrCompiler'] = True
                scops['LanuchYamlCompiler'] = False
                vfr_compilers.append(scops)

    return vfr_compilers


@pytest.fixture(scope='class', params=preprocess_data_of_pytestini())
def vfr_compiler(request):
    # Type args
    args = Namespace(
        InputFileName=request.param['InputFileName'],
        OutputDirectory=request.param['OutputDirectory'] if request.param.get(
            'OutputDirectory') else request.param.get(
            'OUTPUT_DIR'),
        ModuleName=request.param['ModuleName'] if request.param.get(
            'ModuleName') else request.param.get('MODULE_NAME'),
        LanuchVfrCompiler=request.param['LanuchVfrCompiler'],
        LanuchYamlCompiler=request.param['LanuchYamlCompiler'],
        Workspace=request.param.get('Workspace', workspace),
    )
    argv = args.get_argv()
    cmd = CmdParser(args, argv)
    if request.param['LanuchVfrCompiler']:  # LanuchVfrCompiler
        compiler = VfrCompiler(cmd)
        request.cls.compiler = compiler
        yield
        if os.path.exists(compiler.Options.LanuchVfrCompiler):
            os.remove(compiler.Options.JsonFileName)
        if os.path.exists(compiler.Options.PkgOutputFileName):
            os.remove(compiler.Options.PkgOutputFileName)
        if os.path.exists(compiler.Options.RecordListFileName):
            os.remove(compiler.Options.RecordListFileName)
        if os.path.exists(compiler.Options.COutputFileName):
            os.remove(compiler.Options.COutputFileName)
        if os.path.exists(compiler.Options.YamlFileName):
            os.remove(compiler.Options.YamlFileName)


packNumberInput = [
    [os.path.join(os.path.dirname(__file__), "TestVfrSourceFile/PackNumber.i"), 1],
    [os.path.join(os.path.dirname(__file__), "TestVfrSourceFile/PackNumber1.i"), ],
    [os.path.join(os.path.dirname(__file__), "TestVfrSourceFile/PackNumber2.i"), ]
]


@pytest.fixture(scope='function', params=packNumberInput)
def PragmaPackNumber(request):
    return request.param


PackStackInput = [
    [os.path.join(os.path.dirname(__file__), 'TestVfrSourceFile/PackStackpush.i'), 'testPush', 8],
    [os.path.join(os.path.dirname(__file__), 'TestVfrSourceFile/PackStackPop.i'), 'testPop', 8],
]
@pytest.fixture(scope='function', params=PackStackInput)
def PragmaPackStack(request):
    return request.param