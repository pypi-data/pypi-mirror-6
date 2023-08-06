from distutils.core import setup, Extension

with open('README') as file:
    readme = file.read()

setup(
    name             = 'ufal.nametag',
    version          = '1.0.0.1',
    description      = 'Bindings to NameTag library',
    long_description = readme,
    author           = 'Milan Straka',
    author_email     = 'straka@ufal.mff.cuni.cz',
    url              = 'http://ufal.mff.cuni.cz/nametag',
    license          = 'LGPL',
    py_modules       = ['ufal.nametag'],
    ext_modules      = [Extension(
        'ufal_nametag',
        ['nametag/bilou/bilou_probabilities.cpp','nametag/bilou/ner_sentence.cpp','nametag/classifier/network_classifier.cpp','nametag/features/entity_processor.cpp','nametag/features/entity_processor_instances.cpp','nametag/features/feature_templates.cpp','nametag/features/sentence_processor.cpp','nametag/features/sentence_processor_instances.cpp','nametag/morphodita/morpho/czech_morpho.cpp','nametag/morphodita/morpho/english_morpho.cpp','nametag/morphodita/morpho/english_morpho_guesser.cpp','nametag/morphodita/morpho/external_morpho.cpp','nametag/morphodita/morpho/generic_morpho.cpp','nametag/morphodita/morpho/morpho.cpp','nametag/morphodita/morpho/morpho_statistical_guesser.cpp','nametag/morphodita/morpho/tag_filter.cpp','nametag/morphodita/tagger/tagger.cpp','nametag/morphodita/tagset_converter/identity_tagset_converter.cpp','nametag/morphodita/tagset_converter/pdt_to_conll2009_tagset_converter.cpp','nametag/morphodita/tagset_converter/tagset_converter.cpp','nametag/morphodita/tokenizer/czech_tokenizer.cpp','nametag/morphodita/tokenizer/english_tokenizer.cpp','nametag/morphodita/tokenizer/generic_tokenizer.cpp','nametag/morphodita/tokenizer/tokenizer.cpp','nametag/morphodita/tokenizer/utf8_tokenizer.cpp','nametag/morphodita/tokenizer/vertical_tokenizer.cpp','nametag/morphodita/utils/compressor_load.cpp','nametag/morphodita/utils/lzma/LzmaDec.cpp','nametag/morphodita/utils/persistent_unordered_map.cpp','nametag/morphodita/utils/utf8.cpp','nametag/morphodita/version/version.cpp','nametag/nametag_python.cpp','nametag/ner/bilou_ner.cpp','nametag/ner/czech_ner.cpp','nametag/ner/english_ner.cpp','nametag/ner/entity_map.cpp','nametag/ner/generic_ner.cpp','nametag/ner/ner.cpp','nametag/tagger/external_tagger.cpp','nametag/tagger/morphodita_tagger.cpp','nametag/tagger/tagger.cpp','nametag/tagger/trivial_tagger.cpp','nametag/tokenizer/tokenizer.cpp','nametag/utils/compressor_load.cpp','nametag/utils/distribution.cpp','nametag/utils/input.cpp','nametag/utils/lzma/LzmaDec.cpp','nametag/utils/url_detector.cpp','nametag/utils/utf8.cpp','nametag/version/version.cpp'],
        language = 'c++',
        include_dirs = ['nametag/include'],
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
