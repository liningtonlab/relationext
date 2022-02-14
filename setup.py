import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
'argcomplete>=1.10.3',
'beautifulsoup4>=4.8.2',
'blis>=0.7.5',
'catalogue>=2.0.6',
'certifi>=2021.10.8',
'chardet>=3.0.4',
'charset-normalizer>=2.0.11',
'click>=7.1.2',
'compressed-rtf>=1.0.6',
'conllu>=4.4.1',
'cymem>=2.0.6',
'docx2txt>=0.8',
'ebcdic>=1.1.1',
'EbookLib>=0.17.1',
'en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0-py3-none-any.whl',
'en-ner-eco-biobert @ https://github.com/nleguillarme/taxonerd/releases/download/v1.3.0/en_ner_eco_biobert-1.0.0.tar.gz',
'en-ner-eco-md @ https://github.com/nleguillarme/taxonerd/releases/download/v1.3.0/en_ner_eco_md-1.0.0.tar.gz',
'extract-msg>=0.28.7',
'filelock>=3.4.2',
'huggingface-hub>=0.0.12',
'idna>=3.3',
'IMAPClient>=2.1.0',
'Jinja2>=3.0.3',
'joblib>=1.1.0',
'lxml>=4.7.1',
'MarkupSafe>=2.0.1',
'murmurhash>=1.0.6',
'nltk>=3.7',
'nmslib>=2.1.1',
'numpy>=1.22.2',
'olefile>=0.46',
'packaging>=21.3',
'pandas>=1.4.0',
'pathy>=0.6.1',
'pdfminer.six>=20191110',
'Pillow>=9.0.1',
'preshed>=3.0.6',
'psutil>=5.9.0',
'pybind11>=2.6.1',
'pycryptodome>=3.14.1',
'pydantic>=1.8.2',
'pyparsing>=3.0.7',
'pysbd>=0.3.4',
'python-dateutil>=2.8.2',
'python-pptx>=0.6.21',
'pytz>=2021.3',
'pytz-deprecation-shim>=0.1.0.post0',
'PyYAML>=6.0',
'regex>=2022.1.18',
'requests>=2.27.1',
'sacremoses>=0.0.47',
'scikit-learn>=1.0.2',
'scipy==1.7.3',
'scispacy>=0.4.0',
'six>=1.12.0',
'smart-open>=5.2.1',
'sortedcontainers>=2.4.0',
'soupsieve>=2.3.1',
'spacy>=3.0.7',
'spacy-alignments>=0.8.4',
'spacy-legacy>=3.0.8',
'spacy-transformers>=1.0.4',
'SpeechRecognition>=3.8.1',
'srsly>=2.4.2',
'taxonerd==1.1.1',
'textract>=1.6.4',
'thinc>=8.0.13',
'threadpoolctl>=3.1.0',
'tokenizers>=0.10.3',
'torch>=1.10.2',
'tqdm>=4.62.3',
'transformers>=4.9.2',
'typer>=0.3.2',
'typing_extensions>=4.0.1',
'tzdata>=2021.5',
'tzlocal>=4.1',
'urllib3>=1.26.8',
'wasabi>=0.9.0',
'xlrd>=1.2.0',
'XlsxWriter>=3.0.2']



setuptools.setup(
    include_package_data=True,
    name='relationext',
    version='0.2.3',
    author='liningtonlabs',
    author_email='liningtonlabstest@gmail.com',
    description='Testing installation of Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/liningtonlab/relationext',
    license='MIT',
    packages=['relationext'],
    install_requires=requirements,
)