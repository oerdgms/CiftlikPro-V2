"""Single release identity for runtime, cached assets and Windows packaging."""
import re

VERSION = '2.0.44'
BUILD_LABEL = 'HerdListSimplification'
BASELINE = '2.0.41'
CHANNEL = 'pilot-preparation'
CORE_VERSION = '3.9.23 DEV4 Hotfix1.22cr'
BUILD = f'AppEdition{VERSION}-{BUILD_LABEL}'
CACHE_NAME = f'ciftlikpro-app-edition-{VERSION}'
SETUP_STEM = 'CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_'+VERSION.replace('.', '_')+'_Setup'
SETUP_FILE = SETUP_STEM+'.exe'
ARTIFACT_NAME = f'CiftlikPro-Enterprise-V3.9.23-DEV4-AppEdition-{VERSION}-Windows-Setup'
_ASSET = re.compile(r'(/app-assets/[\w.-]+\.(?:css|js|jpg))(?:\?v=[\w.-]+)?(?=[\x22\x27])')


def version_assets(document):
    """Unify literal asset links emitted by every retained presentation module."""
    return _ASSET.sub(lambda match: match.group(1)+'?v='+VERSION, document)


def metadata():
    return {'app':'CiftlikPro','version':VERSION,'build':BUILD,'channel':CHANNEL,
            'baseline':BASELINE,'core_version':CORE_VERSION,'cache_name':CACHE_NAME,
            'setup_file':SETUP_FILE,'artifact_name':ARTIFACT_NAME}
