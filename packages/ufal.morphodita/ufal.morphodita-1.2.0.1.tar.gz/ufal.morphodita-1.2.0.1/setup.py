from distutils.core import setup, Extension

with open('README') as file:
    readme = file.read()

setup(
    name             = 'ufal.morphodita',
    version          = '1.2.0.1',
    description      = 'Bindings to MorphoDiTa library',
    long_description = readme,
    author           = 'Milan Straka',
    author_email     = 'straka@ufal.mff.cuni.cz',
    url              = 'http://ufal.mff.cuni.cz/morphodita',
    license          = 'LGPL',
    py_modules       = ['ufal.morphodita'],
    ext_modules      = [Extension(
        'ufal_morphodita',
        ['morphodita/morpho/czech_morpho.cpp','morphodita/morpho/english_morpho.cpp','morphodita/morpho/english_morpho_guesser.cpp','morphodita/morpho/external_morpho.cpp','morphodita/morpho/generic_morpho.cpp','morphodita/morpho/morpho.cpp','morphodita/morpho/morpho_statistical_guesser.cpp','morphodita/morpho/tag_filter.cpp','morphodita/morphodita_python.cpp','morphodita/tagger/tagger.cpp','morphodita/tagset_converter/identity_tagset_converter.cpp','morphodita/tagset_converter/pdt_to_conll2009_tagset_converter.cpp','morphodita/tagset_converter/strip_lemma_comment_tagset_converter.cpp','morphodita/tagset_converter/strip_lemma_id_tagset_converter.cpp','morphodita/tagset_converter/tagset_converter.cpp','morphodita/tokenizer/czech_tokenizer.cpp','morphodita/tokenizer/english_tokenizer.cpp','morphodita/tokenizer/generic_tokenizer.cpp','morphodita/tokenizer/tokenizer.cpp','morphodita/tokenizer/utf8_tokenizer.cpp','morphodita/tokenizer/vertical_tokenizer.cpp','morphodita/utils/compressor_load.cpp','morphodita/utils/lzma/LzmaDec.cpp','morphodita/utils/persistent_unordered_map.cpp','morphodita/utils/utf8.cpp','morphodita/version/version.cpp'],
        language = 'c++',
        include_dirs = ['morphodita/include'],
        extra_compile_args = ['-std=c++11', '-fvisibility=hidden'],
        extra_link_args = ['-s'])],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries'
    ]
)
